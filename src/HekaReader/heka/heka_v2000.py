from dataclasses import dataclass, field
from typing import Any, ClassVar
import struct

from .heka_common import *

@dataclass(init=False, repr=False)
class BundleItem(Struct):
    Start: int = field(metadata={"fmt": "q"})
    Length: int = field(metadata={"fmt": "q"})
    Extension: str = field(metadata={"fmt": "8s", "func": cstr})
    size_check = 24

@dataclass(init=False, repr=False)
class BundleHeader(Struct):
    Signature: str = field(metadata={"fmt": "8s", "func": cstr})
    Version: str = field(metadata={"fmt": "32s", "func": cstr})
    Time: float = field(metadata={"fmt": "d", "func": heka_time_to_datetime})
    Items: int = field(metadata={"fmt": "i"})
    IsLittleEndian: bool = field(metadata={"fmt": "?"})
    Reserved: str = field(metadata={"fmt": "3s", "func": None})
    FileFormat: int = field(metadata={"fmt": "i"})
    Reserved2: str = field(metadata={"fmt": "4s", "func": None})
    BundleItems: float = field(metadata={"fmt": BundleItem.array(12)})
    size_check = 352

@dataclass(init=False, repr=False)
class TraceRecord(TreeNode):
    Mark: int = field(metadata={"fmt": "i"})
    Label: str = field(metadata={"fmt": "32s", "func": cstr})
    TraceID: int = field(metadata={"fmt": "i"})
    Data: int = field(metadata={"fmt": "q"})
    DataPoints: int = field(metadata={"fmt": "q"})
    InternalSolution: int = field(metadata={"fmt": "i"})
    AverageCount: int = field(metadata={"fmt": "i"})
    LeakID: int = field(metadata={"fmt": "i"})
    LeakTraces: int = field(metadata={"fmt": "i"})
    DataKind: int = field(metadata={"fmt": "h", "func": convertDataKind})
    UseXStart: bool = field(metadata={"fmt": "?"})
    TcKind: int = field(metadata={"fmt": "b"})
    RecordingMode: int = field(metadata={"fmt": "b", "func": getRecordingMode})
    AmplIndex: int = field(metadata={"fmt": "b"})
    DataFormat: int = field(metadata={"fmt": "b", "func": getDataFormat})
    DataAbscissa: int = field(metadata={"fmt": "b"})
    DataScaler: float = field(metadata={"fmt": "d"})
    TimeOffset: float = field(metadata={"fmt": "d"})
    ZeroData: float = field(metadata={"fmt": "d"})
    YUnit: str = field(metadata={"fmt": "8s", "func": cstr})
    XInterval: float = field(metadata={"fmt": "d"})
    XStart: float = field(metadata={"fmt": "d"})
    XUnit: str = field(metadata={"fmt": "8s", "func": cstr})
    YRange: float = field(metadata={"fmt": "d"})
    YOffset: float = field(metadata={"fmt": "d"})
    Bandwidth: float = field(metadata={"fmt": "d"})
    PipetteResistance: float = field(metadata={"fmt": "d"})
    CellPotential: float = field(metadata={"fmt": "d"})
    SealResistance: float = field(metadata={"fmt": "d"})
    CSlow: float = field(metadata={"fmt": "d"})
    GSeries: float = field(metadata={"fmt": "d"})
    RsValue: float = field(metadata={"fmt": "d"})
    GLeak: float = field(metadata={"fmt": "d"})
    MConductance: float = field(metadata={"fmt": "d"})
    LinkDAChannel: int = field(metadata={"fmt": "i"})
    ValidYrange: bool = field(metadata={"fmt": "?"})
    AdcMode: int = field(metadata={"fmt": "b", "func": getADCMode})
    AdcChannel: int = field(metadata={"fmt": "h"})
    Ymin: float = field(metadata={"fmt": "d"})
    Ymax: float = field(metadata={"fmt": "d"})
    SourceChannel: int = field(metadata={"fmt": "i"})
    ExternalSolution: int = field(metadata={"fmt": "i"})
    CM: float = field(metadata={"fmt": "d"})
    GM: float = field(metadata={"fmt": "d"})
    Phase: float = field(metadata={"fmt": "d"})
    DataCRC: int = field(metadata={"fmt": "i"})
    CRC: int = field(metadata={"fmt": "I"})
    GS: float = field(metadata={"fmt": "d"})
    SelfChannel: int = field(metadata={"fmt": "i"})
    InterleaveSize: int = field(metadata={"fmt": "q"})
    InterleaveSkip: int = field(metadata={"fmt": "q"})
    ImageIndex: int = field(metadata={"fmt": "i"})
    TrMarkers: float = field(metadata={"fmt": "10d"})
    SECM_X: float = field(metadata={"fmt": "d"})
    SECM_Y: float = field(metadata={"fmt": "d"})
    SECM_Z: float = field(metadata={"fmt": "d"})
    TrHolding: float = field(metadata={"fmt": "d"})
    TcEnumerator: int = field(metadata={"fmt": "i"})
    XTrace: int = field(metadata={"fmt": "i"})
    IntSolValue: float = field(metadata={"fmt": "d"})
    ExtSolValue: float = field(metadata={"fmt": "d"})
    IntSolName: str = field(metadata={"fmt": "32s", "func": cstr})
    ExtSolName: str = field(metadata={"fmt": "32s", "func": cstr})
    DataPedestal: float = field(metadata={"fmt": "d"})
    size_check = 528

@dataclass(init=False, repr=False)
class SweepRecord(TreeNode):
    Mark: int = field(metadata={"fmt": "i"})
    Label: str = field(metadata={"fmt": "32s", "func": cstr})
    AuxDataFileOffset: int = field(metadata={"fmt": "i"})
    StimCount: int = field(metadata={"fmt": "i"})
    SweepCount: int = field(metadata={"fmt": "i"})
    Time: float = field(metadata={"fmt": "d", "func": heka_time_to_datetime})
    Timer: float = field(metadata={"fmt": "d", "func": timer_timestamp})
    SwUserParams: float = field(metadata={"fmt": "2d"})
    PipPressure: float = field(metadata={"fmt": "d"})
    RMSNoise: float = field(metadata={"fmt": "d"})
    Temperature: float = field(metadata={"fmt": "d"})
    OldIntSol: int = field(metadata={"fmt": "i"})
    OldExtSol: int = field(metadata={"fmt": "i"})
    DigitalIn: int = field(metadata={"fmt": "h"})
    SweepKind: int = field(metadata={"fmt": "h"})
    DigitalOut: int = field(metadata={"fmt": "h"})
    Filler1: int = field(metadata={"fmt": "h", "func": None})
    Markers: float = field(metadata={"fmt": "4d"})
    Filler2: int = field(metadata={"fmt": "i", "func": None})
    CRC: int = field(metadata={"fmt": "I"})
    SwHolding: float = field(metadata={"fmt": "16d"})
    SwUserParamEx: float = field(metadata={"fmt": "8d"})
    size_check = 352

@dataclass(init=False, repr=False)
class UserParamDescrType(Struct):
    Name: str = field(metadata={"fmt": "32s", "func": cstr})
    Unit: str = field(metadata={"fmt": "8s", "func": cstr})
    size_check = 40

@dataclass(init=False, repr=False)
class AmplifierState(Struct):
    StateVersion: str = field(metadata={"fmt": "8s", "func": cstr})
    RealCurrentGain: float = field(metadata={"fmt": "d"})
    RealF2Bandwidth: float = field(metadata={"fmt": "d"})
    F2Frequency: float = field(metadata={"fmt": "d"})
    RsValue: float = field(metadata={"fmt": "d"})
    RsFraction: float = field(metadata={"fmt": "d"})
    GLeak: float = field(metadata={"fmt": "d"})
    CFastAmp1: float = field(metadata={"fmt": "d"})
    CFastAmp2: float = field(metadata={"fmt": "d"})
    CFastTau: float = field(metadata={"fmt": "d"})
    CSlow: float = field(metadata={"fmt": "d"})
    GSeries: float = field(metadata={"fmt": "d"})
    StimDacScale: float = field(metadata={"fmt": "d"})
    CCStimScale: float = field(metadata={"fmt": "d"})
    VHold: float = field(metadata={"fmt": "d"})
    LastVHold: float = field(metadata={"fmt": "d"})
    VpOffset: float = field(metadata={"fmt": "d"})
    VLiquidJunction: float = field(metadata={"fmt": "d"})
    CCIHold: float = field(metadata={"fmt": "d"})
    CSlowStimVolts: float = field(metadata={"fmt": "d"})
    CCTrackVHold: float = field(metadata={"fmt": "d"})
    TimeoutLength: float = field(metadata={"fmt": "d"})
    SearchDelay: float = field(metadata={"fmt": "d"})
    MConductance: float = field(metadata={"fmt": "d"})
    MCapacitance: float = field(metadata={"fmt": "d"})
    SerialNumber: str = field(metadata={"fmt": "8s", "func": cchar})
    E9Boards: int = field(metadata={"fmt": "h"})
    CSlowCycles: int = field(metadata={"fmt": "h"})
    IMonAdc: int = field(metadata={"fmt": "h"})
    VMonAdc: int = field(metadata={"fmt": "h"})
    MuxAdc: int = field(metadata={"fmt": "h"})
    TstDac: int = field(metadata={"fmt": "h"})
    StimDac: int = field(metadata={"fmt": "h"})
    StimDacOffset: int = field(metadata={"fmt": "h"})
    MaxDigitalBit: int = field(metadata={"fmt": "h"})
    HasCFastHigh: int = field(metadata={"fmt": "b"})
    CFastHigh: int = field(metadata={"fmt": "b"})
    HasBathSense: int = field(metadata={"fmt": "b"})
    BathSense: int = field(metadata={"fmt": "b"})
    HasF2Bypass: int = field(metadata={"fmt": "b"})
    sF2Mode: int = field(metadata={"fmt": "b"})
    AmplKind: int = field(metadata={"fmt": "b", "func": getAmplifierType})
    IsEpc9N: int = field(metadata={"fmt": "b"})
    ADBoard: int = field(metadata={"fmt": "b", "func": getADBoard})
    BoardVersion: int = field(metadata={"fmt": "b"})
    ActiveE9Board: int = field(metadata={"fmt": "b"})
    Mode: int = field(metadata={"fmt": "b", "func": getClampMode})
    Range: int = field(metadata={"fmt": "b"})
    F2Response: int = field(metadata={"fmt": "b"})
    RsOn: int = field(metadata={"fmt": "b"})
    CSlowRange: int = field(metadata={"fmt": "b", "func": getCSlowRange})
    CCRange: int = field(metadata={"fmt": "b"})
    CCGain: int = field(metadata={"fmt": "b"})
    CSlowToTstDac: int = field(metadata={"fmt": "b"})
    StimPath: int = field(metadata={"fmt": "b"})
    CCTrackTau: int = field(metadata={"fmt": "b"})
    WasClipping: int = field(metadata={"fmt": "b"})
    RepetitiveCSlow: int = field(metadata={"fmt": "b"})
    LastCSlowRange: int = field(metadata={"fmt": "b", "func": getCSlowRange})
    Old1: int = field(metadata={"fmt": "b", "func": None})
    CanCCFast: int = field(metadata={"fmt": "b"})
    CanLowCCRange: int = field(metadata={"fmt": "b"})
    CanHighCCRange: int = field(metadata={"fmt": "b"})
    CanCCTracking: int = field(metadata={"fmt": "b"})
    HasVmonPath: int = field(metadata={"fmt": "b"})
    HasNewCCMode: int = field(metadata={"fmt": "b"})
    Selector: int = field(metadata={"fmt": "b"})
    HoldInverted: int = field(metadata={"fmt": "b"})
    AutoCFast: bool = field(metadata={"fmt": "?"})
    AutoCSlow: bool = field(metadata={"fmt": "?"})
    HasVmonX100: int = field(metadata={"fmt": "b"})
    TestDacOn: int = field(metadata={"fmt": "b"})
    QMuxAdcOn: int = field(metadata={"fmt": "b"})
    RealImon1Bandwidth: float = field(metadata={"fmt": "d"})
    StimScale: float = field(metadata={"fmt": "d"})
    Gain: int = field(metadata={"fmt": "b", "func": getAmplifierGain})
    Filter1: int = field(metadata={"fmt": "b"})
    StimFilterOn: int = field(metadata={"fmt": "b"})
    RsSlow: int = field(metadata={"fmt": "b"})
    Old2: int = field(metadata={"fmt": "b", "func": None})
    CCCFastOn: bool = field(metadata={"fmt": "?"})
    CCFastSpeed: int = field(metadata={"fmt": "b"})
    F2Source: int = field(metadata={"fmt": "b"})
    TestRange: int = field(metadata={"fmt": "b"})
    TestDacPath: int = field(metadata={"fmt": "b"})
    MuxChannel: int = field(metadata={"fmt": "b"})
    MuxGain64: int = field(metadata={"fmt": "b"})
    VmonX100: int = field(metadata={"fmt": "b"})
    IsQuadro: int = field(metadata={"fmt": "b"})
    F1Mode: int = field(metadata={"fmt": "b"})
    Old3: int = field(metadata={"fmt": "b", "func": None})
    StimFilterHz: float = field(metadata={"fmt": "d"})
    RsTau: float = field(metadata={"fmt": "d"})
    DacToAdcDelay: float = field(metadata={"fmt": "d"})
    InputFilterTau: float = field(metadata={"fmt": "d"})
    OutputFilterTau: float = field(metadata={"fmt": "d"})
    VmonFactor: float = field(metadata={"fmt": "d", "func": None})
    CalibDate: str = field(metadata={"fmt": "16s", "func": cstr})
    VmonOffset: float = field(metadata={"fmt": "d"})
    EEPROMKind: int = field(metadata={"fmt": "b"})
    VrefX2: int = field(metadata={"fmt": "b"})
    HasVrefX2AndF2Vmon: int = field(metadata={"fmt": "b"})
    Spare1: int = field(metadata={"fmt": "b", "func": None})
    Spare2: int = field(metadata={"fmt": "b", "func": None})
    Spare3: int = field(metadata={"fmt": "b", "func": None})
    Spare4: int = field(metadata={"fmt": "b", "func": None})
    Spare5: int = field(metadata={"fmt": "b", "func": None})
    CCStimDacScale: float = field(metadata={"fmt": "d"})
    VmonFiltBandwidth: float = field(metadata={"fmt": "d"})
    VmonFiltFrequency: float = field(metadata={"fmt": "d"})
    size_check = 400

@dataclass(init=False, repr=False)
class LockInParams(Struct):
    ExtCalPhase: float = field(metadata={"fmt": "d"})
    ExtCalAtten: float = field(metadata={"fmt": "d"})
    PLPhase: float = field(metadata={"fmt": "d"})
    PLPhaseY1: float = field(metadata={"fmt": "d"})
    PLPhaseY2: float = field(metadata={"fmt": "d"})
    UsedPhaseShift: float = field(metadata={"fmt": "d"})
    UsedAttenuation: float = field(metadata={"fmt": "d"})
    Spares2: str = field(metadata={"fmt": "8s", "func": None})
    ExtCalValid: bool = field(metadata={"fmt": "?"})
    PLPhaseValid: bool = field(metadata={"fmt": "?"})
    LockInMode: int = field(metadata={"fmt": "b"})
    CalMode: int = field(metadata={"fmt": "b"})
    Spares: str = field(metadata={"fmt": "28s", "func": None})
    size_check = 96

@dataclass(init=False, repr=False)
class SeriesRecord(TreeNode):
    Mark: int = field(metadata={"fmt": "i"})
    Label: str = field(metadata={"fmt": "32s", "func": cstr})
    Comment: str = field(metadata={"fmt": "80s", "func": cstr})
    SeriesCount: int = field(metadata={"fmt": "i"})
    NumberSweeps: int = field(metadata={"fmt": "i"})
    AmplStateFlag: int = field(metadata={"fmt": "i"})
    AmplStateRef: int = field(metadata={"fmt": "i"})
    MethodTag: int = field(metadata={"fmt": "i"})
    Time: float = field(metadata={"fmt": "d", "func": heka_time_to_datetime})
    PageWidth: float = field(metadata={"fmt": "d"})
    UserDescr1: Any = field(metadata={"fmt": UserParamDescrType.array(2)})
    Filler1: Any = field(metadata={"fmt": UserParamDescrType.array(2)})
    MethodName: str = field(metadata={"fmt": "32s", "func": cstr})
    PhotoParams1: float = field(metadata={"fmt": "4d"})
    LockInParams: LockInParams = field(metadata={"fmt": LockInParams})
    AmplifierState: AmplifierState = field(metadata={"fmt": AmplifierState})
    Username: str = field(metadata={"fmt": "80s", "func": cstr})
    PhotoParams2: Any = field(metadata={"fmt": UserParamDescrType.array(4)})
    Filler2: int = field(metadata={"fmt": "i", "func": None})
    CRC: int = field(metadata={"fmt": "I"})
    UserParams2: float = field(metadata={"fmt": "4d"})
    UserParamDescr2: Any = field(metadata={"fmt": UserParamDescrType.array(4)})
    ScanParams: float = field(metadata={"fmt": "12d"})
    UserDescr2: Any = field(metadata={"fmt": UserParamDescrType.array(8)})
    size_check = 1728

@dataclass(init=False, repr=False)
class GroupRecord(TreeNode):
    Mark: int = field(metadata={"fmt": "i"})
    Label: str = field(metadata={"fmt": "32s", "func": cstr})
    Text: str = field(metadata={"fmt": "80s", "func": cstr})
    ExperimentNumber: int = field(metadata={"fmt": "i"})
    GroupCount: int = field(metadata={"fmt": "i"})
    CRC: int = field(metadata={"fmt": "I"})
    MatrixWidth: float = field(metadata={"fmt": "d"})
    MatrixHeight: float = field(metadata={"fmt": "d"})
    size_check = 144

@dataclass(init=False, repr=False)
class AmplStateRecord(TreeNode):
    Mark: int = field(metadata={"fmt": "i"})
    StateCount: int = field(metadata={"fmt": "i"})
    StateVersion: int = field(metadata={"fmt": "b"})
    Filler1: bytes = field(metadata={"fmt": "c", "func": None})
    Filler2: bytes = field(metadata={"fmt": "c", "func": None})
    Filler3: bytes = field(metadata={"fmt": "c", "func": None})
    Filler4: int = field(metadata={"fmt": "i", "func": None})
    LockInParams: LockInParams = field(metadata={"fmt": LockInParams})
    AmplifierState: AmplifierState = field(metadata={"fmt": AmplifierState})
    IntSol: int = field(metadata={"fmt": "i"})
    ExtSol: int = field(metadata={"fmt": "i"})
    Filler5: bytes = field(metadata={"fmt": "36c", "func": None})
    CRC: int = field(metadata={"fmt": "I"})
    size_check = 560

@dataclass(init=False, repr=False)
class AmpSeriesRecord(TreeNode):
    Mark: int = field(metadata={"fmt": "i"})
    StateCount: int = field(metadata={"fmt": "i"})
    Filler1: int = field(metadata={"fmt": "i", "func": None})
    CRC: int = field(metadata={"fmt": "I"})
    size_check = 16

@dataclass(init=False, repr=False)
class StimulationRecord(TreeNode):
    Mark: int = field(metadata={"fmt": "i"})
    EntryName: str = field(metadata={"fmt": "32s", "func": cstr})
    FileName: str = field(metadata={"fmt": "32s", "func": cstr})
    AnalName: str = field(metadata={"fmt": "32s", "func": cstr})
    DataStartSegment: int = field(metadata={"fmt": "i"})
    DataStartTime: float = field(metadata={"fmt": "d", "func": heka_time_to_datetime})
    SampleInterval: float = field(metadata={"fmt": "d"})
    SweepInterval: float = field(metadata={"fmt": "d"})
    LeakDelay: float = field(metadata={"fmt": "d"})
    FilterFactor: float = field(metadata={"fmt": "d"})
    NumberSweeps: int = field(metadata={"fmt": "i"})
    NumberLeaks: int = field(metadata={"fmt": "i"})
    NumberAverages: int = field(metadata={"fmt": "i"})
    ActualAdcChannels: int = field(metadata={"fmt": "i"})
    ActualDacChannels: int = field(metadata={"fmt": "i"})
    ExtTrigger: int = field(metadata={"fmt": "b", "func": getTriggerKind})
    NoStartWait: bool = field(metadata={"fmt": "?"})
    UseScanRates: bool = field(metadata={"fmt": "?"})
    NoContAq: bool = field(metadata={"fmt": "?"})
    HasLockIn: bool = field(metadata={"fmt": "?"})
    OldStartMacKind: int = field(metadata={"fmt": "b"})
    OldEndMacKind: bool = field(metadata={"fmt": "?"})
    AutoRange: int = field(metadata={"fmt": "b"})
    BreakNext: bool = field(metadata={"fmt": "?"})
    IsExpanded: bool = field(metadata={"fmt": "?"})
    LeakCompMode: bool = field(metadata={"fmt": "?"})
    HasChirp: bool = field(metadata={"fmt": "?"})
    OldStartMacro: str = field(metadata={"fmt": "32s", "func": cstr})
    OldEndMacro: str = field(metadata={"fmt": "32s", "func": cstr})
    IsGapFree: bool = field(metadata={"fmt": "?"})
    HandledExternally: bool = field(metadata={"fmt": "?"})
    Filler1: bool = field(metadata={"fmt": "?", "func": None})
    Filler2: bool = field(metadata={"fmt": "?", "func": None})
    CRC: int = field(metadata={"fmt": "I"})
    size_check = 248

@dataclass(init=False, repr=False)
class ChannelRecord(TreeNode):
    Mark: int = field(metadata={"fmt": "i"})
    LinkedChannel: int = field(metadata={"fmt": "i"})
    CompressionFactor: int = field(metadata={"fmt": "i"})
    YUnit: str = field(metadata={"fmt": "8s", "func": cstr})
    AdcChannel: int = field(metadata={"fmt": "h"})
    AdcMode: int = field(metadata={"fmt": "b", "func": getADCMode})
    DoWrite: bool = field(metadata={"fmt": "?"})
    LeakStore: int = field(metadata={"fmt": "b", "func": getLeakStoreType})
    AmplMode: int = field(metadata={"fmt": "b", "func": getAmplMode})
    OwnSegTime: bool = field(metadata={"fmt": "?"})
    SetLastSegVmemb: bool = field(metadata={"fmt": "?"})
    DacChannel: int = field(metadata={"fmt": "h"})
    DacMode: int = field(metadata={"fmt": "b"})
    HasLockInSquare: int = field(metadata={"fmt": "b"})
    RelevantXSegment: int = field(metadata={"fmt": "i"})
    RelevantYSegment: int = field(metadata={"fmt": "i"})
    DacUnit: str = field(metadata={"fmt": "8s", "func": cstr})
    Holding: float = field(metadata={"fmt": "d"})
    LeakHolding: float = field(metadata={"fmt": "d"})
    LeakSize: float = field(metadata={"fmt": "d"})
    LeakHoldMode: int = field(metadata={"fmt": "b", "func": getLeakHoldMode})
    LeakAlternate: bool = field(metadata={"fmt": "?"})
    AltLeakAveraging: bool = field(metadata={"fmt": "?"})
    LeakPulseOn: bool = field(metadata={"fmt": "?"})
    StimToDacID: int = field(metadata={"fmt": "h", "func": convertStimToDacID})
    CompressionMode: int = field(metadata={"fmt": "h"})
    CompressionSkip: int = field(metadata={"fmt": "i"})
    DacBit: int = field(metadata={"fmt": "h"})
    HasLockInSine: bool = field(metadata={"fmt": "?"})
    BreakMode: int = field(metadata={"fmt": "b"})
    ZeroSeg: int = field(metadata={"fmt": "i"})
    StimSweep: int = field(metadata={"fmt": "i"})
    Sine_Cycle: float = field(metadata={"fmt": "d"})
    Sine_Amplitude: float = field(metadata={"fmt": "d"})
    LockIn_VReversal: float = field(metadata={"fmt": "d"})
    Chirp_StartFreq: float = field(metadata={"fmt": "d"})
    Chirp_EndFreq: float = field(metadata={"fmt": "d"})
    Chirp_MinPoints: float = field(metadata={"fmt": "d"})
    Square_NegAmpl: float = field(metadata={"fmt": "d"})
    Square_DurFactor: float = field(metadata={"fmt": "d"})
    LockIn_Skip: int = field(metadata={"fmt": "i"})
    Photo_MaxCycles: int = field(metadata={"fmt": "i"})
    Photo_SegmentNo: int = field(metadata={"fmt": "i"})
    LockIn_AvgCycles: int = field(metadata={"fmt": "i"})
    Imaging_RoiNo: int = field(metadata={"fmt": "i"})
    Chirp_Skip: int = field(metadata={"fmt": "i"})
    Chirp_Amplitude: float = field(metadata={"fmt": "d"})
    Photo_Adapt: int = field(metadata={"fmt": "b"})
    Sine_Kind: int = field(metadata={"fmt": "b"})
    Chirp_PreChirp: int = field(metadata={"fmt": "b"})
    Sine_Source: int = field(metadata={"fmt": "b"})
    Square_NegSource: int = field(metadata={"fmt": "b"})
    Square_PosSource: int = field(metadata={"fmt": "b"})
    Chirp_Kind: int = field(metadata={"fmt": "b", "func": getChirpKind})
    Chirp_Source: int = field(metadata={"fmt": "b"})
    DacOffset: float = field(metadata={"fmt": "d"})
    AdcOffset: float = field(metadata={"fmt": "d"})
    TraceMathFormat: int = field(metadata={"fmt": "b"})
    HasChirp: bool = field(metadata={"fmt": "?"})
    Square_Kind: int = field(metadata={"fmt": "b", "func": getSquareKind})
    Filler1: bytes = field(metadata={"fmt": "5c", "func": None})
    Square_BaseIncr: float = field(metadata={"fmt": "d"})
    Square_Cycle: float = field(metadata={"fmt": "d"})
    Square_PosAmpl: float = field(metadata={"fmt": "d"})
    CompressionOffset: int = field(metadata={"fmt": "i"})
    PhotoMode: int = field(metadata={"fmt": "i"})
    BreakLevel: float = field(metadata={"fmt": "d"})
    TraceMath: str = field(metadata={"fmt": "128s", "func": cstr})
    Filler2: int = field(metadata={"fmt": "i", "func": None})
    CRC: int = field(metadata={"fmt": "I"})
    size_check = 400

@dataclass(init=False, repr=False)
class StimSegmentRecord(TreeNode):
    Mark: int = field(metadata={"fmt": "i"})
    Class: int = field(metadata={"fmt": "b", "func": getSegmentClass})
    StoreKind: int = field(metadata={"fmt": "b", "func": getStoreType})
    VoltageIncMode: int = field(metadata={"fmt": "b", "func": getIncrementMode})
    DurationIncMode: int = field(metadata={"fmt": "b", "func": getIncrementMode})
    Voltage: float = field(metadata={"fmt": "d"})
    VoltageSource: int = field(metadata={"fmt": "i", "func": getSourceType})
    DeltaVFactor: float = field(metadata={"fmt": "d"})
    DeltaVIncrement: float = field(metadata={"fmt": "d"})
    Duration: float = field(metadata={"fmt": "d"})
    DurationSource: int = field(metadata={"fmt": "i", "func": getSourceType})
    DeltaTFactor: float = field(metadata={"fmt": "d"})
    DeltaTIncrement: float = field(metadata={"fmt": "d"})
    Filler1: int = field(metadata={"fmt": "i", "func": None})
    CRC: int = field(metadata={"fmt": "I"})
    ScanRate: float = field(metadata={"fmt": "d"})
    size_check = 80

@dataclass(init=False, repr=False)
class Pulsed(TreeNode):
    Version: int = field(metadata={"fmt": "i"})
    Mark: int = field(metadata={"fmt": "i"})
    VersionName: str = field(metadata={"fmt": "32s", "func": cstr})
    AuxFileName: str = field(metadata={"fmt": "80s", "func": cstr})
    RootText: str = field(metadata={"fmt": "400s", "func": cstr})
    StartTime: float = field(metadata={"fmt": "d", "func": heka_time_to_datetime})
    MaxSamples: int = field(metadata={"fmt": "i"})
    CRC: int = field(metadata={"fmt": "I"})
    Features: int = field(metadata={"fmt": "h"})
    Filler1: int = field(metadata={"fmt": "h", "func": None})
    Filler2: int = field(metadata={"fmt": "i", "func": None})
    TcEnumerator: int = field(metadata={"fmt": "32h"})
    TcKind: int = field(metadata={"fmt": "32b"})
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

@dataclass(init=False, repr=False)
class Amplifier(TreeNode):
    Version: int = field(metadata={"fmt": "i"})
    Mark: int = field(metadata={"fmt": "i"})
    VersionName: str = field(metadata={"fmt": "32s", "func": cstr})
    AmplifierName: str = field(metadata={"fmt": "32s", "func": cstr})
    Amplifier: int = field(metadata={"fmt": "b"})
    ADBoard: int = field(metadata={"fmt": "b"})
    Creator: int = field(metadata={"fmt": "b"})
    Filler1: bytes = field(metadata={"fmt": "c", "func": None})
    CRC: int = field(metadata={"fmt": "I"})
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

@dataclass(init=False, repr=False)
class Stimulus(TreeNode):
    Version: int = field(metadata={"fmt": "i"})
    Mark: int = field(metadata={"fmt": "i"})
    VersionName: str = field(metadata={"fmt": "32s", "func": cstr})
    MaxSamples: int = field(metadata={"fmt": "i"})
    Filler1: int = field(metadata={"fmt": "i", "func": None})
    Params: float = field(metadata={"fmt": "10d"})
    ParamText: bytes = field(metadata={"fmt": "320c", "func": None})
    Reserved: str = field(metadata={"fmt": "128s", "func": cstr})
    Filler2: int = field(metadata={"fmt": "i", "func": None})
    Reserved2: str = field(metadata={"fmt": "560s", "func": None})
    CRC: int = field(metadata={"fmt": "I"})
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
