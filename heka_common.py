import numpy as np
import re
import struct
import collections
import datetime

def cstr(byt):
    """Convert C string bytes to python string.
    """
    try:
        ind = byt.index(b'\0')
    except ValueError:
        return byt
    return byt[:ind].decode('utf-8', errors='ignore')

def cbyte(byt):
    """Convert C string byte to python integer.
    """
    try:
        return byt[0]
    except (ValueError, IndexError):
        return byt

def cchar(byt):
    """Convert C char byte to python string.
    """
    return byt.decode('utf-8', errors='ignore')

def heka_time_to_datetime(stored_time):
    ''' convert HEKA time to a datetime object (v1000) '''
    WinEpoch = datetime.datetime(1601, 1, 1)
    MacEPoch = datetime.datetime(1904, 1, 1)

    windows_offset = 7980681600.0
    JanFirst1990 = 1580970496.0
    wrap = 2**32

    if stored_time > wrap:   # almost certainly Windows
        t = stored_time + windows_offset
        return WinEpoch + datetime.timedelta(seconds=t)
    else:                    # likely Mac
        t = stored_time - JanFirst1990
        return MacEPoch + datetime.timedelta(seconds=t)

def heka_time_to_date_v2000(time):
    ''' convert HEKA time to a date string (v2000) '''
    time -= 1580970496 # JanFirst1990
    if time < 0:
        time += 4294967296 # HIGH_DWORD
    time += 9561652096 # MAC_BASE

    ref = datetime.datetime(1601, 1, 1) # Windows reference date
    conv_time = datetime.timedelta(seconds=time)

    return (ref + conv_time).strftime("%d-%b-%Y %H:%M:%S.%f")

def timer_timestamp(total_seconds: float) -> str:
    ''' Converts seconds to a string representation of a HH:MM:SS.ms timestamp '''
    hours, remainder = divmod(total_seconds, 60*60)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = (seconds % 1) * 1000

    return f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{milliseconds:.0f}'

def getFromList(lst, index):
    try:
        return lst[index]
    except IndexError:
        return f"Unknown (value: {index})"

def getAmplifierType(byte):
    return getFromList(["EPC7", "EPC8", "EPC9", "EPC10", "EPC10Plus", "EPC10_USB"], byte)

def getADBoard(byte):
    return getFromList(["ITC16", "ITC18", "LIH1600", "LIH 8+8"], byte)

def getRecordingMode(byte):
    return getFromList(["InOut", "OnCell", "OutOut", "WholeCell", "CClamp", "VClamp", "NoMode"], byte)

def getDataFormat(byte):
    return getFromList(["int16", "int32", "real32", "real64"], byte)

def getSegmentClass(byte):
    return getFromList(["Constant", "Ramp", "Continuous", "ConstSine", "Squarewave", "Chirpwave"], byte)

def getStoreType(byte):
    return getFromList(["NoStore", "Store", "StoreStart", "StoreEnd"], byte)

def getIncrementMode(byte):
    return getFromList(["Inc", "Dec", "IncInterleaved", "DecInterleaved",
                        "Alternate", "LogInc", "LogDec", "LogIncInterleaved",
                        "LogDecInterleaved", "LogAlternate", "Toggle"], byte)

def getSourceType(byte):
    return getFromList(["Constant", "Hold", "Parameter"], byte)

def getAmplifierGain(byte):
    """
    Units: V/A
    """
    # Original units: mV/pA
    return getFromList([1e-3/1e-12 * x for x in
                       [0.005, 0.010, 0.020, 0.050, 0.1, 0.2,
                        0.5, 1, 2, 5, 10, 20,
                        50, 100, 200, 500, 1000, 2000]], byte)

def convertDataFormatToNP(dataFormat):
    d = {"int16": np.int16,
         "int32": np.int32,
         "real32": np.float32,
         "real64": np.float64}
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
    d = {}
    d["IsLittleEndian"] = bool(byte & (1 << 0))
    d["IsLeak"] = bool(byte & (1 << 1))
    d["IsVirtual"] = bool(byte & (1 << 2))
    d["IsImon"] = bool(byte & (1 << 3))
    d["IsVmon"] = bool(byte & (1 << 4))
    d["Clip"] = bool(byte & (1 << 5))
    return d

def convertStimToDacID(byte):
    d = {}
    d["UseStimScale"] = bool(byte & (1 << 0))
    d["UseRelative"] = bool(byte & (1 << 1))
    d["UseFileTemplate"] = bool(byte & (1 << 2))
    d["UseForLockIn"] = bool(byte & (1 << 3))
    d["UseForWavelength"] = bool(byte & (1 << 4))
    d["UseScaling"] = bool(byte & (1 << 5))
    d["UseForChirp"] = bool(byte & (1 << 6))
    d["UseForImaging"] = bool(byte & (1 << 7))
    return d

def getSquareKind(byte):
    return getFromList(["Common Frequency"], byte)

def getChirpKind(byte):
    return getFromList(["Linear", "Exponential", "Spectroscopic"], byte)

def getTriggerKind(byte):
    return getFromList(["None", "Series", "Sweep", "SweepNoLeak"], byte)

class Struct():
    field_info = None
    size_check = None
    _fields_parsed = None

    def __init__(self, data, endian='<'):
        field_info = self._field_info()
        if not isinstance(data, (str, bytes)):
            data = data.read(self._le_struct.size)
        if endian == '<':
            items = self._le_struct.unpack(data)
        elif endian == '>':
            items = self._be_struct.unpack(data)
        else:
            raise ValueError('Invalid endian: %s' % endian)

        fields = collections.OrderedDict()

        i = 0
        for name, fmt, func in field_info:
            if len(fmt) == 1 or fmt[-1] == 's':
                item = items[i]
                i += 1
            else:
                n = int(fmt[:-1])
                item = items[i:i+n]
                i += n

            if isinstance(func, tuple):
                substr, func = func
                item = substr(item, endian)

            if func is None:
                continue
            if func is not True:
                item = func(item)
            fields[name] = item
            setattr(self, name, item)

        self.fields = fields

    @classmethod
    def _field_info(cls):
        if cls._fields_parsed is not None:
            return cls._fields_parsed

        fmt = ''
        fields = []
        if cls.field_info is not None:
            for items in cls.field_info:
                if len(items) == 3:
                    name, ifmt, func = items
                else:
                    name, ifmt = items
                    func = True

                if isinstance(ifmt, type) and issubclass(ifmt, Struct):
                    func = (ifmt, func)
                    ifmt = '%ds' % ifmt.size()
                elif re.match(r'\d*[xcbB?hHiIlLqQfdspP]', ifmt) is None:
                    raise TypeError('Unsupported format string "%s"' % ifmt)

                fields.append((name, ifmt, func))
                fmt += ifmt
        cls._le_struct = struct.Struct('<' + fmt)
        cls._be_struct = struct.Struct('>' + fmt)
        cls._fields_parsed = fields
        if cls.size_check is not None:
            assert cls._le_struct.size == cls.size_check, \
                "{} expected vs. {}".format(
                    cls.size_check, cls._le_struct.size)
        return fields

    @classmethod
    def size(cls):
        cls._field_info()
        return cls._le_struct.size

    @classmethod
    def array(cls, x):
        return type(cls.__name__+'[%d]' % x, (StructArray,),
                    {'item_struct': cls, 'array_size': x})

    def __str__(self, indent=0):
        indent_str = '    '*indent
        r = indent_str + '%s(\n' % self.__class__.__name__
        if not hasattr(self, 'fields'):
            r = r[:-1] + '<initializing>)'
            return r
        for k, v in self.fields.items():
            if isinstance(v, Struct):
                r += indent_str + '    %s = %s\n' % \
                    (k, v.__str__(indent=indent+1).lstrip())
            else:
                r += indent_str + '    %s = %r\n' % (k, v)
        r += indent_str + ')'
        return r

    def get_fields(self):
        fields = self.fields.copy()
        for k,v in fields.items():
            if isinstance(v, StructArray):
                fields[k] = [x.get_fields() for x in v.array]
            elif isinstance(v, Struct):
                fields[k] = v.get_fields()
        return fields

class StructArray(Struct):
    item_struct = None
    array_size = None

    def __init__(self, data, endian='<'):
        if not isinstance(data, (str, bytes)):
            data = data.read(self.size())
        items = []
        isize = self.item_struct.size()
        for i in range(self.array_size):
            d = data[:isize]
            data = data[isize:]
            items.append(self.item_struct(d, endian))
        self.array = items

    def __getitem__(self, i):
        return self.array[i]

    @classmethod
    def size(self):
        return self.item_struct.size() * self.array_size

    def __repr__(self, indent=0):
        r = '    '*indent + '%s(\n' % self.__class__.__name__
        for item in self.array:
            r += item.__repr__(indent=indent+1) + ',\n'
        r += '    '*indent + ')'
        return r

class TreeNode(Struct):
    def __init__(self, fh, pul, level=0):
        self.level = level
        self.children = []
        endian = pul.endian

        realsize = pul.level_sizes[level]
        structsize = self.size()
        data = fh.read(realsize)
        diff = structsize - realsize
        if diff > 0:
            data = data + b'\0'*diff
        else:
            data = data[:structsize]

        Struct.__init__(self, data, endian)

        nchild = struct.unpack(endian + 'i', fh.read(4))[0]

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
        ind = '    '*indent
        srep = Struct.__repr__(self, indent)[:-1]
        srep += ind + '    children = %d,\n' % len(self)
        srep += ind + ')'
        return srep

class Data(object):
    def __init__(self, bundle, offset=0, size=None):
        self.bundle = bundle
        self.offset = offset

    def __getitem__(self, *args):
        index = args[0]
        assert len(index) == 4
        pul = self.bundle.pul
        trace = pul[index[0]][index[1]][index[2]][index[3]]
        fh = self.bundle.fh
        fh.seek(trace.Data)
        dtype = np.dtype(convertDataFormatToNP(trace.DataFormat))
        if not trace.DataKind['IsLittleEndian']:
            dtype = dtype.newbyteorder('>')
        data = np.fromfile(fh, count=trace.DataPoints, dtype=dtype)
        return (data * trace.DataScaler).astype(np.float64)
