from dataclasses import dataclass
from typing import Any, ClassVar

from pyHeka.FileFormat.FileFormat_common import (
    AmpSeriesRecord,
    ChannelRecord,
    LockInParams,
    Pulsed as BasePulsed,
    Amplifier as BaseAmplifier,
    Stimulus as BaseStimulus,
    StimSegmentRecord,
    Struct,
    TreeNode,
    UserParamDescrType,
    cstr,
    getADBoard,
    getADCMode,
    getAmplifierGain,
    getAmplifierType,
    getCSlowRange,
    getClampMode,
    getDataFormat,
    getRecordingMode,
    heka_time_to_datetime,
    struct_field,
    convertDataKind,
)
from pyHeka.FileFormat.FileFormat_v1000 import (
    GroupRecord,
    SweepRecord,
    StimulationRecord as BaseStimulationRecord,
)


@dataclass(init=False, repr=False)
class BundleItem(Struct):
    Start: int = struct_field("q")
    Length: int = struct_field("q")
    Extension: str = struct_field("8s", cstr)
    size_check = 24


@dataclass(init=False, repr=False)
class BundleHeader(Struct):
    Signature: str = struct_field("8s", cstr)
    Version: str = struct_field("32s", cstr)
    Time: float = struct_field("d", heka_time_to_datetime)
    Items: int = struct_field("i")
    IsLittleEndian: bool = struct_field("?")
    Reserved: str = struct_field("3s", None)
    FileFormat: int = struct_field("i")
    Reserved2: str = struct_field("4s", None)
    BundleItems: float = struct_field(BundleItem.array(12))
    size_check = 352


@dataclass(init=False, repr=False)
class TraceRecord(TreeNode):
    Mark: int = struct_field("i")
    Label: str = struct_field("32s", cstr)
    TraceID: int = struct_field("i")
    Data: int = struct_field("q")
    DataPoints: int = struct_field("q")
    InternalSolution: int = struct_field("i")
    AverageCount: int = struct_field("i")
    LeakID: int = struct_field("i")
    LeakTraces: int = struct_field("i")
    DataKind: int = struct_field("h", convertDataKind)
    UseXStart: bool = struct_field("?")
    TcKind: int = struct_field("b")
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
    DataCRC: int = struct_field("i")
    CRC: int = struct_field("I")
    GS: float = struct_field("d")
    SelfChannel: int = struct_field("i")
    InterleaveSize: int = struct_field("q")
    InterleaveSkip: int = struct_field("q")
    ImageIndex: int = struct_field("i")
    TrMarkers: float = struct_field("10d")
    SECM_X: float = struct_field("d")
    SECM_Y: float = struct_field("d")
    SECM_Z: float = struct_field("d")
    TrHolding: float = struct_field("d")
    TcEnumerator: int = struct_field("i")
    XTrace: int = struct_field("i")
    IntSolValue: float = struct_field("d")
    ExtSolValue: float = struct_field("d")
    IntSolName: str = struct_field("32s", cstr)
    ExtSolName: str = struct_field("32s", cstr)
    DataPedestal: float = struct_field("d")
    size_check = 528


@dataclass(init=False, repr=False)
class AmplifierState(Struct):
    StateVersion: str = struct_field("8s", cstr)
    RealCurrentGain: float = struct_field("d")
    RealF2Bandwidth: float = struct_field("d")
    F2Frequency: float = struct_field("d")
    RsValue: float = struct_field("d")
    RsFraction: float = struct_field("d")
    GLeak: float = struct_field("d")
    CFastAmp1: float = struct_field("d")
    CFastAmp2: float = struct_field("d")
    CFastTau: float = struct_field("d")
    CSlow: float = struct_field("d")
    GSeries: float = struct_field("d")
    StimDacScale: float = struct_field("d")
    CCStimScale: float = struct_field("d")
    VHold: float = struct_field("d")
    LastVHold: float = struct_field("d")
    VpOffset: float = struct_field("d")
    VLiquidJunction: float = struct_field("d")
    CCIHold: float = struct_field("d")
    CSlowStimVolts: float = struct_field("d")
    CCTrackVHold: float = struct_field("d")
    TimeoutLength: float = struct_field("d")
    SearchDelay: float = struct_field("d")
    MConductance: float = struct_field("d")
    MCapacitance: float = struct_field("d")
    SerialNumber: str = struct_field("8s", cstr)
    E9Boards: int = struct_field("h")
    CSlowCycles: int = struct_field("h")
    IMonAdc: int = struct_field("h")
    VMonAdc: int = struct_field("h")
    MuxAdc: int = struct_field("h")
    TstDac: int = struct_field("h")
    StimDac: int = struct_field("h")
    StimDacOffset: int = struct_field("h")
    MaxDigitalBit: int = struct_field("h")
    HasCFastHigh: int = struct_field("b")
    CFastHigh: int = struct_field("b")
    HasBathSense: int = struct_field("b")
    BathSense: int = struct_field("b")
    HasF2Bypass: int = struct_field("b")
    sF2Mode: int = struct_field("b")
    AmplKind: int = struct_field("b", getAmplifierType)
    IsEpc9N: int = struct_field("b")
    ADBoard: int = struct_field("b", getADBoard)
    BoardVersion: int = struct_field("b")
    ActiveE9Board: int = struct_field("b")
    Mode: int = struct_field("b", getClampMode)
    Range: int = struct_field("b")
    F2Response: int = struct_field("b")
    RsOn: int = struct_field("b")
    CSlowRange: int = struct_field("b", getCSlowRange)
    CCRange: int = struct_field("b")
    CCGain: int = struct_field("b")
    CSlowToTstDac: int = struct_field("b")
    StimPath: int = struct_field("b")
    CCTrackTau: int = struct_field("b")
    WasClipping: int = struct_field("b")
    RepetitiveCSlow: int = struct_field("b")
    LastCSlowRange: int = struct_field("b", getCSlowRange)
    Old1: int = struct_field("b", None)
    CanCCFast: int = struct_field("b")
    CanLowCCRange: int = struct_field("b")
    CanHighCCRange: int = struct_field("b")
    CanCCTracking: int = struct_field("b")
    HasVmonPath: int = struct_field("b")
    HasNewCCMode: int = struct_field("b")
    Selector: int = struct_field("b")
    HoldInverted: int = struct_field("b")
    AutoCFast: bool = struct_field("?")
    AutoCSlow: bool = struct_field("?")
    HasVmonX100: int = struct_field("b")
    TestDacOn: int = struct_field("b")
    QMuxAdcOn: int = struct_field("b")
    RealImon1Bandwidth: float = struct_field("d")
    StimScale: float = struct_field("d")
    Gain: int = struct_field("b", getAmplifierGain)
    Filter1: int = struct_field("b")
    StimFilterOn: int = struct_field("b")
    RsSlow: int = struct_field("b")
    Old2: int = struct_field("b", None)
    CCCFastOn: bool = struct_field("?")
    CCFastSpeed: int = struct_field("b")
    F2Source: int = struct_field("b")
    TestRange: int = struct_field("b")
    TestDacPath: int = struct_field("b")
    MuxChannel: int = struct_field("b")
    MuxGain64: int = struct_field("b")
    VmonX100: int = struct_field("b")
    IsQuadro: int = struct_field("b")
    F1Mode: int = struct_field("b")
    Old3: int = struct_field("b", None)
    StimFilterHz: float = struct_field("d")
    RsTau: float = struct_field("d")
    DacToAdcDelay: float = struct_field("d")
    InputFilterTau: float = struct_field("d")
    OutputFilterTau: float = struct_field("d")
    VmonFactor: float = struct_field("d", None)
    CalibDate: str = struct_field("16s", cstr)
    VmonOffset: float = struct_field("d")
    EEPROMKind: int = struct_field("b")
    VrefX2: int = struct_field("b")
    HasVrefX2AndF2Vmon: int = struct_field("b")
    Spare1: int = struct_field("b", None)
    Spare2: int = struct_field("b", None)
    Spare3: int = struct_field("b", None)
    Spare4: int = struct_field("b", None)
    Spare5: int = struct_field("b", None)
    CCStimDacScale: float = struct_field("d")
    VmonFiltBandwidth: float = struct_field("d")
    VmonFiltFrequency: float = struct_field("d")
    size_check = 400


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
    UserDescr1: Any = struct_field(UserParamDescrType.array(2))
    Filler1: Any = struct_field(UserParamDescrType.array(2))
    MethodName: str = struct_field("32s", cstr)
    PhotoParams1: float = struct_field("4d")
    LockInParams: LockInParams = struct_field(LockInParams)
    AmplifierState: AmplifierState = struct_field(AmplifierState)
    Username: str = struct_field("80s", cstr)
    PhotoParams2: Any = struct_field(UserParamDescrType.array(4))
    Filler2: int = struct_field("i", None)
    CRC: int = struct_field("I")
    UserParams2: float = struct_field("4d")
    UserParamDescr2: Any = struct_field(UserParamDescrType.array(4))
    ScanParams: float = struct_field("12d")
    UserDescr2: Any = struct_field(UserParamDescrType.array(8))
    size_check = 1728


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
class StimulationRecord(BaseStimulationRecord):
    DataStartTime: float = struct_field("d", heka_time_to_datetime)


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
