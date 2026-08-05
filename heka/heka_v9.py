import struct
from typing import ClassVar

from .heka_common import *
from .heka_v1000 import (
    AmplifierState,
    BundleHeader,
    BundleItem,
    LockInParams,
    UserParamDescrType,
)


class TraceRecord(TreeNode):
    field_info: ClassVar[list] = [
        ("Mark", "i"),
        ("Label", "32s", cstr),
        ("TraceID", "i"),
        ("Data", "i"),
        ("DataPoints", "i"),
        ("InternalSolution", "i"),
        ("AverageCount", "i"),
        ("LeakID", "i"),
        ("LeakTraces", "i"),
        ("DataKind", "h", convertDataKind),
        ("Filler1", "h", None),
        ("RecordingMode", "b", getRecordingMode),
        ("AmplIndex", "b"),
        ("DataFormat", "b", getDataFormat),
        ("DataAbscissa", "b"),
        ("DataScaler", "d"),
        ("TimeOffset", "d"),
        ("ZeroData", "d"),
        ("YUnit", "8s", cstr),
        ("XInterval", "d"),
        ("XStart", "d"),
        ("XUnit", "8s", cstr),
        ("YRange", "d"),
        ("YOffset", "d"),
        ("Bandwidth", "d"),
        ("PipetteResistance", "d"),
        ("CellPotential", "d"),
        ("SealResistance", "d"),
        ("CSlow", "d"),
        ("GSeries", "d"),
        ("RsValue", "d"),
        ("GLeak", "d"),
        ("MConductance", "d"),
        ("LinkDAChannel", "i"),
        ("ValidYrange", "?"),
        ("AdcMode", "b", getADCMode),
        ("AdcChannel", "h"),
        ("Ymin", "d"),
        ("Ymax", "d"),
        ("SourceChannel", "i"),
        ("ExternalSolution", "i"),
        ("CM", "d"),
        ("GM", "d"),
        ("Phase", "d"),
        ("DataCRC", "I"),
        ("CRC", "I"),
        ("GS", "d"),
        ("SelfChannel", "i"),
        ("InterleaveSize", "i"),
        ("InterleaveSkip", "i"),
        ("ImageIndex", "i"),
        ("TrMarkers", "10d"),
        ("SECM_X", "d"),
        ("SECM_Y", "d"),
        ("SECM_Z", "d"),
    ]
    size_check = 408


class SweepRecord(TreeNode):
    field_info: ClassVar[list] = [
        ("Mark", "i"),
        ("Label", "32s", cstr),
        ("AuxDataFileOffset", "i"),
        ("StimCount", "i"),
        ("SweepCount", "i"),
        ("Time", "d", heka_time_to_datetime),
        ("Timer", "d", timer_timestamp),
        ("SwUserParams", "4d"),
        ("Temperature", "d"),
        ("OldIntSol", "i"),
        ("OldExtSol", "i"),
        ("DigitalIn", "h"),
        ("SweepKind", "h"),
        ("Filler1", "i", None),
        ("Markers", "4d"),
        ("Filler2", "i", None),
        ("CRC", "I"),
    ]
    size_check = 160


class SeriesRecord(TreeNode):
    field_info: ClassVar[list] = [
        ("Mark", "i"),
        ("Label", "32s", cstr),
        ("Comment", "80s", cstr),
        ("SeriesCount", "i"),
        ("NumberSweeps", "i"),
        ("AmplStateFlag", "i"),
        ("AmplStateRef", "i"),
        ("MethodTag", "i"),
        ("Time", "d", heka_time_to_datetime),
        ("PageWidth", "d"),
        ("UserDescr1", UserParamDescrType.array(4)),
        ("MethodName", "32s", cstr),
        ("PhotoParams1", "4d"),
        ("LockInParams", LockInParams),
        ("AmplifierState", AmplifierState),
        ("Username", "80s", cstr),
        ("PhotoParams2", UserParamDescrType.array(4)),
        ("Filler1", "i", None),
        ("CRC", "I"),
        ("UserParams2", "4d"),
        ("UserParamDescr2", UserParamDescrType.array(4)),
        ("ScanParams", "96s", cstr),
    ]
    size_check = 1408


class GroupRecord(TreeNode):
    field_info: ClassVar[list] = [
        ("Mark", "i"),
        ("Label", "32s", cstr),
        ("Text", "80s", cstr),
        ("ExperimentNumber", "i"),
        ("GroupCount", "i"),
        ("CRC", "I"),
    ]
    size_check = 128


class AmplStateRecord(TreeNode):
    field_info: ClassVar[list] = [
        ("Mark", "i"),
        ("StateCount", "i"),
        ("StateVersion", "b"),
        ("Filler1", "c", None),
        ("Filler2", "c", None),
        ("Filler3", "c", None),
        ("Filler4", "i", None),
        ("LockInParams", LockInParams),
        ("AmplifierState", AmplifierState),
        ("IntSol", "i"),
        ("ExtSol", "i"),
        ("Filler5", "36c", None),
        ("CRC", "I"),
    ]
    size_check = 560


class AmpSeriesRecord(TreeNode):
    field_info: ClassVar[list] = [
        ("Mark", "i"),
        ("StateCount", "i"),
        ("Filler1", "i", None),
        ("CRC", "I"),
    ]
    size_check = 16


class StimulationRecord(TreeNode):
    field_info: ClassVar[list] = [
        ("Mark", "i"),
        ("EntryName", "32s", cstr),
        ("FileName", "32s", cstr),
        ("AnalName", "32s", cstr),
        ("DataStartSegment", "i"),
        ("DataStartTime", "d"),
        ("SampleInterval", "d"),
        ("SweepInterval", "d"),
        ("LeakDelay", "d"),
        ("FilterFactor", "d"),
        ("NumberSweeps", "i"),
        ("NumberLeaks", "i"),
        ("NumberAverages", "i"),
        ("ActualAdcChannels", "i"),
        ("ActualDacChannels", "i"),
        ("ExtTrigger", "b", getTriggerKind),
        ("NoStartWait", "?"),
        ("UseScanRates", "?"),
        ("NoContAq", "?"),
        ("HasLockIn", "?"),
        ("OldStartMacKind", "b"),
        ("OldEndMacKind", "?"),
        ("AutoRange", "b"),
        ("BreakNext", "?"),
        ("IsExpanded", "?"),
        ("LeakCompMode", "?"),
        ("HasChirp", "?"),
        ("OldStartMacro", "32s", cstr),
        ("OldEndMacro", "32s", cstr),
        ("IsGapFree", "?"),
        ("HandledExternally", "?"),
        ("Filler1", "?", None),
        ("Filler2", "?", None),
        ("CRC", "I"),
    ]
    size_check = 248


class ChannelRecord(TreeNode):
    field_info: ClassVar[list] = [
        ("Mark", "i"),
        ("LinkedChannel", "i"),
        ("CompressionFactor", "i"),
        ("YUnit", "8s", cstr),
        ("AdcChannel", "h"),
        ("AdcMode", "b", getADCMode),
        ("DoWrite", "?"),
        ("LeakStore", "b", getLeakStoreType),
        ("AmplMode", "b", getAmplMode),
        ("OwnSegTime", "?"),
        ("SetLastSegVmemb", "?"),
        ("DacChannel", "h"),
        ("DacMode", "b"),
        ("HasLockInSquare", "b"),
        ("RelevantXSegment", "i"),
        ("RelevantYSegment", "i"),
        ("DacUnit", "8s", cstr),
        ("Holding", "d"),
        ("LeakHolding", "d"),
        ("LeakSize", "d"),
        ("LeakHoldMode", "b", getLeakHoldMode),
        ("LeakAlternate", "?"),
        ("AltLeakAveraging", "?"),
        ("LeakPulseOn", "?"),
        ("StimToDacID", "h", convertStimToDacID),
        ("CompressionMode", "h"),
        ("CompressionSkip", "i"),
        ("DacBit", "h"),
        ("HasLockInSine", "?"),
        ("BreakMode", "b"),
        ("ZeroSeg", "i"),
        ("StimSweep", "i"),
        ("Sine_Cycle", "d"),
        ("Sine_Amplitude", "d"),
        ("LockIn_VReversal", "d"),
        ("Chirp_StartFreq", "d"),
        ("Chirp_EndFreq", "d"),
        ("Chirp_MinPoints", "d"),
        ("Square_NegAmpl", "d"),
        ("Square_DurFactor", "d"),
        ("LockIn_Skip", "i"),
        ("Photo_MaxCycles", "i"),
        ("Photo_SegmentNo", "i"),
        ("LockIn_AvgCycles", "i"),
        ("Imaging_RoiNo", "i"),
        ("Chirp_Skip", "i"),
        ("Chirp_Amplitude", "d"),
        ("Photo_Adapt", "b"),
        ("Sine_Kind", "b"),
        ("Chirp_PreChirp", "b"),
        ("Sine_Source", "b"),
        ("Square_NegSource", "b"),
        ("Square_PosSource", "b"),
        ("Chirp_Kind", "b", getChirpKind),
        ("Chirp_Source", "b"),
        ("DacOffset", "d"),
        ("AdcOffset", "d"),
        ("TraceMathFormat", "b"),
        ("HasChirp", "?"),
        ("Square_Kind", "b", getSquareKind),
        ("Filler1", "5c", None),
        ("Square_BaseIncr", "d"),
        ("Square_Cycle", "d"),
        ("Square_PosAmpl", "d"),
        ("CompressionOffset", "i"),
        ("PhotoMode", "i"),
        ("BreakLevel", "d"),
        ("TraceMath", "128s", cstr),
        ("Filler2", "i", None),
        ("CRC", "I"),
    ]
    size_check = 400


class StimSegmentRecord(TreeNode):
    field_info: ClassVar[list] = [
        ("Mark", "i"),
        ("Class", "b", getSegmentClass),
        ("StoreKind", "b", getStoreType),
        ("VoltageIncMode", "b", getIncrementMode),
        ("DurationIncMode", "b", getIncrementMode),
        ("Voltage", "d"),
        ("VoltageSource", "i", getSourceType),
        ("DeltaVFactor", "d"),
        ("DeltaVIncrement", "d"),
        ("Duration", "d"),
        ("DurationSource", "i", getSourceType),
        ("DeltaTFactor", "d"),
        ("DeltaTIncrement", "d"),
        ("Filler1", "i", None),
        ("CRC", "I"),
        ("ScanRate", "d"),
    ]
    size_check = 80


class Pulsed(TreeNode):
    field_info: ClassVar[list] = [
        ("Version", "i"),
        ("Mark", "i"),
        ("VersionName", "32s", cstr),
        ("AuxFileName", "80s", cstr),
        ("RootText", "400s", cstr),
        ("StartTime", "d", heka_time_to_datetime),
        ("MaxSamples", "i"),
        ("CRC", "I"),
        ("Features", "h"),
        ("Filler1", "h", None),
        ("Filler2", "i", None),
        ("TcEnumerator", "32h"),
        ("TcKind", "32b"),
    ]
    size_check = 640

    rectypes: ClassVar[list] = [
        None,
        GroupRecord,
        SeriesRecord,
        SweepRecord,
        TraceRecord,
    ]

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

        self.level_sizes = []
        for i in range(levels):
            size = struct.unpack(self.endian + "i", fh.read(4))[0]
            self.level_sizes.append(size)

        TreeNode.__init__(self, fh, self)


class Amplifier(TreeNode):
    field_info: ClassVar[list] = [
        ("Version", "i"),
        ("Mark", "i"),
        ("VersionName", "32s", cstr),
        ("AmplifierName", "32s", cstr),
        ("Amplifier", "b"),
        ("ADBoard", "b"),
        ("Creator", "b"),
        ("Filler1", "c", None),
        ("CRC", "I"),
    ]
    size_check = 80

    rectypes: ClassVar[list] = [None, AmpSeriesRecord, AmplStateRecord]

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

        self.level_sizes = []
        for i in range(levels):
            size = struct.unpack(self.endian + "i", fh.read(4))[0]
            self.level_sizes.append(size)

        TreeNode.__init__(self, fh, self)


class Stimulus(TreeNode):
    field_info: ClassVar[list] = [
        ("Version", "i"),
        ("Mark", "i"),
        ("VersionName", "32s", cstr),
        ("MaxSamples", "i"),
        ("Filler1", "i", None),
        ("Params", "10d"),
        ("ParamText", "320c", None),
        ("Reserved", "128s", cstr),
        ("Filler2", "i", None),
        ("Reserved2", "560s", None),
        ("CRC", "I"),
    ]
    size_check = 1144

    rectypes: ClassVar[list] = [
        None,
        StimulationRecord,
        ChannelRecord,
        StimSegmentRecord,
    ]

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

        self.level_sizes = []
        for i in range(levels):
            size = struct.unpack(self.endian + "i", fh.read(4))[0]
            self.level_sizes.append(size)

        TreeNode.__init__(self, fh, self)
