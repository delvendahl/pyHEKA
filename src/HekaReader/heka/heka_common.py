import collections
import datetime
import re
import struct
import dataclasses

import numpy as np


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
        # Optimization: in most cases it's just HekaEpoch + stored_time
        # and it falls within reasonable range.

        # --- HEKA 1990 epoch ---
        c = HekaEpoch + datetime.timedelta(seconds=stored_time)

        now = datetime.datetime.now(tz=utc)
        lower = datetime.datetime(1990, 1, 1, tzinfo=utc)
        upper = now + datetime.timedelta(days=7)

        if lower < c < upper:
            return c.replace(tzinfo=None)

        WinEpoch = datetime.datetime(1601, 1, 1, tzinfo=utc)
        MacEpoch = datetime.datetime(1904, 1, 1, tzinfo=utc)
        windows_offset = 7980681600.0
        seconds_1904_to_1990 = 2713910400.0  # (HekaEpoch - MacEpoch).total_seconds()

        candidates = []
        wrap = 2**32
        if stored_time > wrap:
            t = stored_time + windows_offset
            candidates.append(WinEpoch + datetime.timedelta(seconds=t))

        candidates.append(c)  # already there but for completeness

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
    """
    Units: V/A
    """
    # Original units: mV/pA
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
    field_info = None
    size_check = None
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

        fmt = ""
        cls._fields_parsed = []

        if dataclasses.is_dataclass(cls):
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
        else:
            if cls.field_info is not None:
                for items in cls.field_info:
                    if len(items) == 3:
                        name, ifmt, func = items
                    else:
                        name, ifmt = items
                        func = True

                    if isinstance(ifmt, type) and issubclass(ifmt, Struct):
                        func = (ifmt, func)
                        ifmt = f"{ifmt.size()}s"
                    elif re.match(r"\d*[xcbB?hHiIlLqQfdspP]", ifmt) is None:
                        raise TypeError(f'Unsupported format string "{ifmt}"')

                    cls._fields_parsed.append((name, ifmt, func))
                    fmt += ifmt

        cls._le_struct = struct.Struct("<" + fmt)
        cls._be_struct = struct.Struct(">" + fmt)
        if cls.size_check is not None:
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
