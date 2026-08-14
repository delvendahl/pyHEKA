import collections
import dataclasses
import datetime
import re
import struct
from dataclasses import dataclass, field

import numpy as np


def struct_field(fmt, func=True):
    """Helper to create a dataclass field with struct format metadata."""
    return field(metadata={"fmt": fmt, "func": func})


def cstr(byt):
    """Convert C string bytes to python string."""
    ind = byt.find(b"\0")
    if ind == -1:
        return byt
    return byt[:ind].decode("utf-8", errors="ignore")


def cbyte(byt):
    """Convert C string byte to python integer."""
    if isinstance(byt, int):
        return byt
    try:
        return byt[0]
    except (ValueError, IndexError):
        return byt


def cchar(byt):
    """Convert C char byte to python string."""
    return byt.decode("utf-8", errors="ignore")


def heka_time_to_datetime(stored_time) -> datetime.datetime:
    """convert HEKA time to a datetime object"""
    utc = datetime.timezone.utc
    HekaEpoch = datetime.datetime(1990, 1, 1, tzinfo=utc)

    try:
        c = HekaEpoch + datetime.timedelta(seconds=stored_time)

        now = datetime.datetime.now(tz=utc)
        lower = datetime.datetime(1990, 1, 1, tzinfo=utc)
        upper = now + datetime.timedelta(days=7)

        if lower < c < upper:
            return c.replace(tzinfo=None)

        WinEpoch = datetime.datetime(1601, 1, 1, tzinfo=utc)
        MacEpoch = datetime.datetime(1904, 1, 1, tzinfo=utc)
        windows_offset = 7980681600.0
        seconds_1904_to_1990 = 2713910400.0

        candidates = []
        wrap = 2**32
        if stored_time > wrap:
            t = stored_time + windows_offset
            candidates.append(WinEpoch + datetime.timedelta(seconds=t))

        candidates.append(c)

        t = stored_time - seconds_1904_to_1990
        candidates.append(MacEpoch + datetime.timedelta(seconds=t))

        for c in candidates:
            if lower < c < upper:
                return c.replace(tzinfo=None)

        return candidates[0].replace(tzinfo=None)

    except OverflowError:
        return f"Invalid time value: {stored_time}"


def timer_timestamp(total_seconds: float) -> datetime.timedelta:
    """Converts seconds to a datetime timedelta object"""
    return datetime.timedelta(seconds=total_seconds)


def getFromList(lst, index):
    try:
        return lst[index]
    except IndexError:
        return f"Unknown (value: {index})"


def getAmplifierType(byte):
    return getFromList(
        ["EPC7", "EPC8", "EPC9", "EPC10", "EPC10Plus", "EPC10_USB"], byte
    )


def getADBoard(byte):
    return getFromList(["ITC16", "ITC18", "LIH1600", "LIH 8+8"], byte)


def getRecordingMode(byte):
    return getFromList(
        ["InOut", "OnCell", "OutOut", "WholeCell", "CClamp", "VClamp", "NoMode"], byte
    )


def getDataFormat(byte):
    return getFromList(["int16", "int32", "real32", "real64"], byte)


def getSegmentClass(byte):
    return getFromList(
        ["Constant", "Ramp", "Continuous", "ConstSine", "Squarewave", "Chirpwave"], byte
    )


def getStoreType(byte):
    return getFromList(["NoStore", "Store", "StoreStart", "StoreEnd"], byte)


def getIncrementMode(byte):
    return getFromList(
        [
            "Inc",
            "Dec",
            "IncInterleaved",
            "DecInterleaved",
            "Alternate",
            "LogInc",
            "LogDec",
            "LogIncInterleaved",
            "LogDecInterleaved",
            "LogAlternate",
            "Toggle",
        ],
        byte,
    )


def getSourceType(byte):
    return getFromList(["Constant", "Hold", "Parameter"], byte)


def getAmplifierGain(byte):
    """Units: V/A"""
    return getFromList(
        [
            1e-3 / 1e-12 * x
            for x in [
                0.005,
                0.010,
                0.020,
                0.050,
                0.1,
                0.2,
                0.5,
                1,
                2,
                5,
                10,
                20,
                50,
                100,
                200,
                500,
                1000,
                2000,
            ]
        ],
        byte,
    )


def convertDataFormatToNP(dataFormat):
    d = {
        "int16": np.int16,
        "int32": np.int32,
        "real32": np.float32,
        "real64": np.float64,
    }
    return d[dataFormat]


def getCSlowRange(byte):
    return getFromList(["Off", "30 pF", "100 pF", "1000 pF"], byte)


def getClampMode(byte):
    return getFromList(["TestMode", "VCMode", "CCMode", "NoMode"], byte)


def getAmplMode(byte):
    return getFromList(["Any", "VCMode", "CCMode", "IDensityMode"], byte)


def getLeakHoldMode(byte):
    return getFromList(["Labs", "Lrel", "LabsLH", "LrelLH"], byte)


def getLeakStoreType(byte):
    return getFromList(["None", "StoreAvg", "StoreEach", "NoStore"], byte)


def getADCMode(byte):
    return getFromList(["AdcOff", "Analog", "Digitals", "Digital", "AdcVirtual"], byte)


def convertDataKind(byte):
    return {
        "IsLittleEndian": bool(byte & 1),
        "IsLeak": bool(byte & 2),
        "IsVirtual": bool(byte & 4),
        "IsImon": bool(byte & 8),
        "IsVmon": bool(byte & 16),
        "Clip": bool(byte & 32),
    }


def convertStimToDacID(byte):
    return {
        "UseStimScale": bool(byte & 1),
        "UseRelative": bool(byte & 2),
        "UseFileTemplate": bool(byte & 4),
        "UseForLockIn": bool(byte & 8),
        "UseForWavelength": bool(byte & 16),
        "UseScaling": bool(byte & 32),
        "UseForChirp": bool(byte & 64),
        "UseForImaging": bool(byte & 128),
    }


def getSquareKind(byte):
    return getFromList(["Common Frequency"], byte)


def getChirpKind(byte):
    return getFromList(["Linear", "Exponential", "Spectroscopic"], byte)


def getTriggerKind(byte):
    return getFromList(["None", "Series", "Sweep", "SweepNoLeak"], byte)


class Struct:
    _fields_parsed = None

    def __init__(self, data, endian="<"):
        cls = self.__class__
        cls._init_struct_formats()
        if not isinstance(data, (str, bytes)):
            data = data.read(cls._le_struct.size)

        struct_obj = cls._le_struct if endian == "<" else cls._be_struct
        items = struct_obj.unpack(data)

        i = 0
        for name, fmt, func in cls._fields_parsed:
            if len(fmt) == 1 or fmt[-1] == "s":
                item = items[i]
                i += 1
            else:
                n = int(fmt[:-1])
                item = items[i : i + n]
                i += n

            if func is not True:
                if isinstance(func, tuple):
                    substr, func = func
                    item = substr(item, endian)

                if func is None:
                    continue

                if callable(func):
                    item = func(item)
                elif func is False:
                    continue

            setattr(self, name, item)

    @classmethod
    def _init_struct_formats(cls):
        # Prevent subclass caching conflicts
        if cls.__dict__.get("_fields_parsed") is not None:
            return

        if not dataclasses.is_dataclass(cls):
            raise TypeError(
                f"Class '{cls.__name__}' must be decorated with @dataclass."
            )

        fmt = ""
        cls._fields_parsed = []

        for f in dataclasses.fields(cls):
            name = f.name
            ifmt = f.metadata.get("fmt")
            if ifmt is None:
                continue
            func = f.metadata.get("func", True)

            if isinstance(ifmt, type) and issubclass(ifmt, Struct):
                func = (ifmt, func)
                ifmt = f"{ifmt.size()}s"
            elif re.match(r"\d*[xcbB?hHiIlLqQfdspP]", ifmt) is None:
                raise TypeError(f'Unsupported format string "{ifmt}"')

            cls._fields_parsed.append((name, ifmt, func))
            fmt += ifmt

        cls._le_struct = struct.Struct("<" + fmt)
        cls._be_struct = struct.Struct(">" + fmt)
        if hasattr(cls, "size_check") and cls.size_check is not None:
            assert cls._le_struct.size == cls.size_check, (
                f"{cls.size_check} expected vs. {cls._le_struct.size}"
            )

    @classmethod
    def size(cls):
        cls._init_struct_formats()
        return cls._le_struct.size

    @classmethod
    def array(cls, x):
        return type(
            f"{cls.__name__}[{x}]",
            (StructArray,),
            {"item_struct": cls, "array_size": x},
        )

    def __str__(self, indent=0):
        cls = self.__class__
        cls._init_struct_formats()
        indent_str = "    " * indent
        r = indent_str + f"{self.__class__.__name__}(\n"
        for name, _, _ in cls._fields_parsed:
            if hasattr(self, name):
                v = getattr(self, name)
                if isinstance(v, Struct):
                    r += (
                        indent_str
                        + f"    {name} = {v.__str__(indent=indent + 1).lstrip()}\n"
                    )
                else:
                    r += indent_str + f"    {name} = {v!r}\n"
        r += indent_str + ")"
        return r

    def __repr__(self, indent=0):
        return self.__str__(indent)

    def get_fields(self):
        cls = self.__class__
        cls._init_struct_formats()
        fields_dict = collections.OrderedDict()
        for name, _, _ in cls._fields_parsed:
            if hasattr(self, name):
                v = getattr(self, name)
                if isinstance(v, StructArray):
                    fields_dict[name] = [x.get_fields() for x in v.array]
                elif isinstance(v, Struct):
                    fields_dict[name] = v.get_fields()
                else:
                    fields_dict[name] = v
        return fields_dict


class StructArray(Struct):
    item_struct = None
    array_size = None

    def __init__(self, data, endian="<"):
        if not isinstance(data, (str, bytes)):
            data = data.read(self.size())
        items = []
        isize = self.item_struct.size()
        for i in range(self.array_size):
            d = data[i * isize : (i + 1) * isize]
            items.append(self.item_struct(d, endian))
        self.array = items

    def __getitem__(self, i):
        return self.array[i]

    def __len__(self):
        return len(self.array)

    def __iter__(self):
        return iter(self.array)

    @classmethod
    def size(cls):
        return cls.item_struct.size() * cls.array_size

    def __repr__(self, indent=0):
        r = "    " * indent + f"{self.__class__.__name__}(\n"
        for item in self.array:
            r += item.__repr__(indent=indent + 1) + ",\n"
        r += "    " * indent + ")"
        return r


class TreeNode(Struct):
    def __init__(self, fh, pul, level=0):
        self.level = level
        self.children = []
        endian = pul.endian

        realsize = pul.level_sizes[level]
        structsize = self.size()
        data = fh.read(realsize)
        if len(data) < structsize:
            data = data + b"\0" * (structsize - len(data))
        else:
            data = data[:structsize]

        Struct.__init__(self, data, endian)

        nchild = struct.unpack(endian + "i", fh.read(4))[0]

        level += 1
        if level >= len(pul.rectypes):
            return
        child_rectype = pul.rectypes[level]
        for i in range(nchild):
            self.children.append(child_rectype(fh, pul, level))

    def __getitem__(self, i):
        return self.children[i]

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return self.children.__iter__()

    def __repr__(self, indent=0):
        ind = "    " * indent
        srep = Struct.__repr__(self, indent)[:-1]
        srep += ind + f"    children = {len(self)},\n"
        srep += ind + ")"
        return srep


class RootNode(TreeNode):
    """Base class for root tree nodes (Pulsed, Amplifier, Stimulus)."""

    def __init__(self, bundle, offset=0, size=None):
        fh = bundle.fh
        fh.seek(offset)

        magic = fh.read(4)
        if magic == b"eerT":
            self.endian = "<"
        elif magic == b"Tree":
            self.endian = ">"
        else:
            raise RuntimeError(f"Bad file magic: {magic}")

        levels = struct.unpack(self.endian + "i", fh.read(4))[0]

        self.level_sizes = [
            struct.unpack(self.endian + "i", fh.read(4))[0] for _ in range(levels)
        ]

        super().__init__(fh, self)


@dataclass(init=False, repr=False)
class UserParamDescrType(Struct):
    Name: str = struct_field("32s", cstr)
    Unit: str = struct_field("8s", cstr)
    size_check = 40


@dataclass(init=False, repr=False)
class LockInParams(Struct):
    ExtCalPhase: float = struct_field("d")
    ExtCalAtten: float = struct_field("d")
    PLPhase: float = struct_field("d")
    PLPhaseY1: float = struct_field("d")
    PLPhaseY2: float = struct_field("d")
    UsedPhaseShift: float = struct_field("d")
    UsedAttenuation: float = struct_field("d")
    Spares2: str = struct_field("8s", None)
    ExtCalValid: bool = struct_field("?")
    PLPhaseValid: bool = struct_field("?")
    LockInMode: int = struct_field("b")
    CalMode: int = struct_field("b")
    Spares: str = struct_field("28s", None)
    size_check = 96


@dataclass(init=False, repr=False)
class StimSegmentRecord(TreeNode):
    Mark: int = struct_field("i")
    Class: int = struct_field("b", getSegmentClass)
    StoreKind: int = struct_field("b", getStoreType)
    VoltageIncMode: int = struct_field("b", getIncrementMode)
    DurationIncMode: int = struct_field("b", getIncrementMode)
    Voltage: float = struct_field("d")
    VoltageSource: int = struct_field("i", getSourceType)
    DeltaVFactor: float = struct_field("d")
    DeltaVIncrement: float = struct_field("d")
    Duration: float = struct_field("d")
    DurationSource: int = struct_field("i", getSourceType)
    DeltaTFactor: float = struct_field("d")
    DeltaTIncrement: float = struct_field("d")
    Filler1: int = struct_field("i", None)
    CRC: int = struct_field("I")
    ScanRate: float = struct_field("d")
    size_check = 80


@dataclass(init=False, repr=False)
class ChannelRecord(TreeNode):
    Mark: int = struct_field("i")
    LinkedChannel: int = struct_field("i")
    CompressionFactor: int = struct_field("i")
    YUnit: str = struct_field("8s", cstr)
    AdcChannel: int = struct_field("h")
    AdcMode: int = struct_field("b", getADCMode)
    DoWrite: bool = struct_field("?")
    LeakStore: int = struct_field("b", getLeakStoreType)
    AmplMode: int = struct_field("b", getAmplMode)
    OwnSegTime: bool = struct_field("?")
    SetLastSegVmemb: bool = struct_field("?")
    DacChannel: int = struct_field("h")
    DacMode: int = struct_field("b")
    HasLockInSquare: int = struct_field("b")
    RelevantXSegment: int = struct_field("i")
    RelevantYSegment: int = struct_field("i")
    DacUnit: str = struct_field("8s", cstr)
    Holding: float = struct_field("d")
    LeakHolding: float = struct_field("d")
    LeakSize: float = struct_field("d")
    LeakHoldMode: int = struct_field("b", getLeakHoldMode)
    LeakAlternate: bool = struct_field("?")
    AltLeakAveraging: bool = struct_field("?")
    LeakPulseOn: bool = struct_field("?")
    StimToDacID: int = struct_field("h", convertStimToDacID)
    CompressionMode: int = struct_field("h")
    CompressionSkip: int = struct_field("i")
    DacBit: int = struct_field("h")
    HasLockInSine: bool = struct_field("?")
    BreakMode: int = struct_field("b")
    ZeroSeg: int = struct_field("i")
    StimSweep: int = struct_field("i")
    Sine_Cycle: float = struct_field("d")
    Sine_Amplitude: float = struct_field("d")
    LockIn_VReversal: float = struct_field("d")
    Chirp_StartFreq: float = struct_field("d")
    Chirp_EndFreq: float = struct_field("d")
    Chirp_MinPoints: float = struct_field("d")
    Square_NegAmpl: float = struct_field("d")
    Square_DurFactor: float = struct_field("d")
    LockIn_Skip: int = struct_field("i")
    Photo_MaxCycles: int = struct_field("i")
    Photo_SegmentNo: int = struct_field("i")
    LockIn_AvgCycles: int = struct_field("i")
    Imaging_RoiNo: int = struct_field("i")
    Chirp_Skip: int = struct_field("i")
    Chirp_Amplitude: float = struct_field("d")
    Photo_Adapt: int = struct_field("b")
    Sine_Kind: int = struct_field("b")
    Chirp_PreChirp: int = struct_field("b")
    Sine_Source: int = struct_field("b")
    Square_NegSource: int = struct_field("b")
    Square_PosSource: int = struct_field("b")
    Chirp_Kind: int = struct_field("b", getChirpKind)
    Chirp_Source: int = struct_field("b")
    DacOffset: float = struct_field("d")
    AdcOffset: float = struct_field("d")
    TraceMathFormat: int = struct_field("b")
    HasChirp: bool = struct_field("?")
    Square_Kind: int = struct_field("b", getSquareKind)
    Filler1: bytes = struct_field("5c", None)
    Square_BaseIncr: float = struct_field("d")
    Square_Cycle: float = struct_field("d")
    Square_PosAmpl: float = struct_field("d")
    CompressionOffset: int = struct_field("i")
    PhotoMode: int = struct_field("i")
    BreakLevel: float = struct_field("d")
    TraceMath: str = struct_field("128s", cstr)
    Filler2: int = struct_field("i", None)
    CRC: int = struct_field("I")
    size_check = 400


@dataclass(init=False, repr=False)
class AmpSeriesRecord(TreeNode):
    Mark: int = struct_field("i")
    StateCount: int = struct_field("i")
    Filler1: int = struct_field("i", None)
    CRC: int = struct_field("I")
    size_check = 16


@dataclass(init=False, repr=False)
class Pulsed(RootNode):
    Version: int = struct_field("i")
    Mark: int = struct_field("i")
    VersionName: str = struct_field("32s", cstr)
    AuxFileName: str = struct_field("80s", cstr)
    RootText: str = struct_field("400s", cstr)
    StartTime: float = struct_field("d", heka_time_to_datetime)
    MaxSamples: int = struct_field("i")
    CRC: int = struct_field("I")
    Features: int = struct_field("h")
    Filler1: int = struct_field("h", None)
    Filler2: int = struct_field("i", None)
    TcEnumerator: int = struct_field("32h")
    TcKind: int = struct_field("32b")
    size_check = 640


@dataclass(init=False, repr=False)
class Amplifier(RootNode):
    Version: int = struct_field("i")
    Mark: int = struct_field("i")
    VersionName: str = struct_field("32s", cstr)
    AmplifierName: str = struct_field("32s", cstr)
    Amplifier: int = struct_field("b")
    ADBoard: int = struct_field("b")
    Creator: int = struct_field("b")
    Filler1: bytes = struct_field("c", None)
    CRC: int = struct_field("I")
    size_check = 80


@dataclass(init=False, repr=False)
class Stimulus(RootNode):
    Version: int = struct_field("i")
    Mark: int = struct_field("i")
    VersionName: str = struct_field("32s", cstr)
    MaxSamples: int = struct_field("i")
    Filler1: int = struct_field("i", None)
    Params: float = struct_field("10d")
    ParamText: bytes = struct_field("320c", None)
    Reserved: str = struct_field("128s", cstr)
    Filler2: int = struct_field("i", None)
    Reserved2: str = struct_field("560s", None)
    CRC: int = struct_field("I")
    size_check = 1144


class Data:
    def __init__(self, bundle, offset=0, size=None):
        self.bundle = bundle
        self.offset = offset

    def __getitem__(self, *args):
        index = args[0]
        if not isinstance(index, tuple) or len(index) != 4:
            raise IndexError(
                "Index must be a tuple of length 4 (group, series, sweep, trace)"
            )
        pul = self.bundle.pul
        trace = pul[index[0]][index[1]][index[2]][index[3]]
        fh = self.bundle.fh
        fh.seek(trace.Data)
        dtype = np.dtype(convertDataFormatToNP(trace.DataFormat))
        if not trace.DataKind["IsLittleEndian"]:
            dtype = dtype.newbyteorder(">")
        data = np.fromfile(fh, count=trace.DataPoints, dtype=dtype)
        return (data * trace.DataScaler).astype(np.float64)
