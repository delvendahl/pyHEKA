from dataclasses import dataclass
from typing import Any, ClassVar

from pyheka.FileFormat.FileFormat_common import (
    Amplifier as BaseAmplifier,
)
from pyheka.FileFormat.FileFormat_common import (
    AmpSeriesRecord,
    ChannelRecord,
    LockInParams,
    StimSegmentRecord,
    TreeNode,
    UserParamDescrType,
    convertDataKind,
    cstr,
    getADCMode,
    getDataFormat,
    getRecordingMode,
    getTriggerKind,
    heka_time_to_datetime,
    struct_field,
    timer_timestamp,
)
from pyheka.FileFormat.FileFormat_common import (
    Pulsed as BasePulsed,
)
from pyheka.FileFormat.FileFormat_common import (
    Stimulus as BaseStimulus,
)
from pyheka.FileFormat.FileFormat_v1000 import AmplifierState, BundleHeader, BundleItem


@dataclass(init=False, repr=False)
class TraceRecord(TreeNode):
    Mark: int = struct_field("i")
    Label: str = struct_field("32s", cstr)
    TraceID: int = struct_field("i")
    Data: int = struct_field("i")
    DataPoints: int = struct_field("i")
    InternalSolution: int = struct_field("i")
    AverageCount: int = struct_field("i")
    LeakID: int = struct_field("i")
    LeakTraces: int = struct_field("i")
    DataKind: int = struct_field("h", convertDataKind)
    Filler1: int = struct_field("h", None)
    RecordingMode: int = struct_field("b", getRecordingMode)
    AmplIndex: int = struct_field("b")
    DataFormat: int = struct_field("b", getDataFormat)
    DataAbscissa: int = struct_field("b")
    DataScaler: float = struct_field("d")
    TimeOffset: float = struct_field("d")
    ZeroData: float = struct_field("d")
    YUnit: str = struct_field("8s", cstr)
    XInterval: float = struct_field("d")
    XStart: float = struct_field("d")
    XUnit: str = struct_field("8s", cstr)
    YRange: float = struct_field("d")
    YOffset: float = struct_field("d")
    Bandwidth: float = struct_field("d")
    PipetteResistance: float = struct_field("d")
    CellPotential: float = struct_field("d")
    SealResistance: float = struct_field("d")
    CSlow: float = struct_field("d")
    GSeries: float = struct_field("d")
    RsValue: float = struct_field("d")
    GLeak: float = struct_field("d")
    MConductance: float = struct_field("d")
    LinkDAChannel: int = struct_field("i")
    ValidYrange: bool = struct_field("?")
    AdcMode: int = struct_field("b", getADCMode)
    AdcChannel: int = struct_field("h")
    Ymin: float = struct_field("d")
    Ymax: float = struct_field("d")
    SourceChannel: int = struct_field("i")
    ExternalSolution: int = struct_field("i")
    CM: float = struct_field("d")
    GM: float = struct_field("d")
    Phase: float = struct_field("d")
    DataCRC: int = struct_field("I")
    CRC: int = struct_field("I")
    GS: float = struct_field("d")
    SelfChannel: int = struct_field("i")
    InterleaveSize: int = struct_field("i")
    InterleaveSkip: int = struct_field("i")
    ImageIndex: int = struct_field("i")
    TrMarkers: float = struct_field("10d")
    SECM_X: float = struct_field("d")
    SECM_Y: float = struct_field("d")
    SECM_Z: float = struct_field("d")
    size_check = 408


@dataclass(init=False, repr=False)
class SweepRecord(TreeNode):
    Mark: int = struct_field("i")
    Label: str = struct_field("32s", cstr)
    AuxDataFileOffset: int = struct_field("i")
    StimCount: int = struct_field("i")
    SweepCount: int = struct_field("i")
    Time: float = struct_field("d", heka_time_to_datetime)
    Timer: float = struct_field("d", timer_timestamp)
    SwUserParams: float = struct_field("4d")
    Temperature: float = struct_field("d")
    OldIntSol: int = struct_field("i")
    OldExtSol: int = struct_field("i")
    DigitalIn: int = struct_field("h")
    SweepKind: int = struct_field("h")
    Filler1: int = struct_field("i", None)
    Markers: float = struct_field("4d")
    Filler2: int = struct_field("i", None)
    CRC: int = struct_field("I")
    size_check = 160


@dataclass(init=False, repr=False)
class SeriesRecord(TreeNode):
    Mark: int = struct_field("i")
    Label: str = struct_field("32s", cstr)
    Comment: str = struct_field("80s", cstr)
    SeriesCount: int = struct_field("i")
    NumberSweeps: int = struct_field("i")
    AmplStateFlag: int = struct_field("i")
    AmplStateRef: int = struct_field("i")
    MethodTag: int = struct_field("i")
    Time: float = struct_field("d", heka_time_to_datetime)
    PageWidth: float = struct_field("d")
    UserDescr1: Any = struct_field(UserParamDescrType.array(4))
    MethodName: str = struct_field("32s", cstr)
    PhotoParams1: float = struct_field("4d")
    LockInParams: LockInParams = struct_field(LockInParams)
    AmplifierState: AmplifierState = struct_field(AmplifierState)
    Username: str = struct_field("80s", cstr)
    PhotoParams2: Any = struct_field(UserParamDescrType.array(4))
    Filler1: int = struct_field("i", None)
    CRC: int = struct_field("I")
    UserParams2: float = struct_field("4d")
    UserParamDescr2: Any = struct_field(UserParamDescrType.array(4))
    ScanParams: str = struct_field("96s", cstr)
    size_check = 1408


@dataclass(init=False, repr=False)
class GroupRecord(TreeNode):
    Mark: int = struct_field("i")
    Label: str = struct_field("32s", cstr)
    Text: str = struct_field("80s", cstr)
    ExperimentNumber: int = struct_field("i")
    GroupCount: int = struct_field("i")
    CRC: int = struct_field("I")
    size_check = 128


@dataclass(init=False, repr=False)
class AmplStateRecord(TreeNode):
    Mark: int = struct_field("i")
    StateCount: int = struct_field("i")
    StateVersion: int = struct_field("b")
    Filler1: bytes = struct_field("c", None)
    Filler2: bytes = struct_field("c", None)
    Filler3: bytes = struct_field("c", None)
    Filler4: int = struct_field("i", None)
    LockInParams: LockInParams = struct_field(LockInParams)
    AmplifierState: AmplifierState = struct_field(AmplifierState)
    IntSol: int = struct_field("i")
    ExtSol: int = struct_field("i")
    Filler5: bytes = struct_field("36c", None)
    CRC: int = struct_field("I")
    size_check = 560


@dataclass(init=False, repr=False)
class StimulationRecord(TreeNode):
    Mark: int = struct_field("i")
    EntryName: str = struct_field("32s", cstr)
    FileName: str = struct_field("32s", cstr)
    AnalName: str = struct_field("32s", cstr)
    DataStartSegment: int = struct_field("i")
    DataStartTime: float = struct_field("d")
    SampleInterval: float = struct_field("d")
    SweepInterval: float = struct_field("d")
    LeakDelay: float = struct_field("d")
    FilterFactor: float = struct_field("d")
    NumberSweeps: int = struct_field("i")
    NumberLeaks: int = struct_field("i")
    NumberAverages: int = struct_field("i")
    ActualAdcChannels: int = struct_field("i")
    ActualDacChannels: int = struct_field("i")
    ExtTrigger: int = struct_field("b", getTriggerKind)
    NoStartWait: bool = struct_field("?")
    UseScanRates: bool = struct_field("?")
    NoContAq: bool = struct_field("?")
    HasLockIn: bool = struct_field("?")
    OldStartMacKind: int = struct_field("b")
    OldEndMacKind: bool = struct_field("?")
    AutoRange: int = struct_field("b")
    BreakNext: bool = struct_field("?")
    IsExpanded: bool = struct_field("?")
    LeakCompMode: bool = struct_field("?")
    HasChirp: bool = struct_field("?")
    OldStartMacro: str = struct_field("32s", cstr)
    OldEndMacro: str = struct_field("32s", cstr)
    IsGapFree: bool = struct_field("?")
    HandledExternally: bool = struct_field("?")
    Filler1: bool = struct_field("?", None)
    Filler2: bool = struct_field("?", None)
    CRC: int = struct_field("I")
    size_check = 248


@dataclass(init=False, repr=False)
class Pulsed(BasePulsed):
    rectypes: ClassVar[list] = [
        None,
        GroupRecord,
        SeriesRecord,
        SweepRecord,
        TraceRecord,
    ]


@dataclass(init=False, repr=False)
class Amplifier(BaseAmplifier):
    rectypes: ClassVar[list] = [None, AmpSeriesRecord, AmplStateRecord]


@dataclass(init=False, repr=False)
class Stimulus(BaseStimulus):
    rectypes: ClassVar[list] = [
        None,
        StimulationRecord,
        ChannelRecord,
        StimSegmentRecord,
    ]
