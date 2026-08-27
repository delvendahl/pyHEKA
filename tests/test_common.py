import datetime
import struct
import unittest
from dataclasses import dataclass

import numpy as np

from pyheka.FileFormat.FileFormat_common import (
    RootNode,
    Struct,
    StructArray,
    TreeNode,
    cbyte,
    cchar,
    convertDataFormatToNP,
    convertDataKind,
    convertStimToDacID,
    cstr,
    getADBoard,
    getADCMode,
    getAmplifierGain,
    getAmplifierType,
    getAmplMode,
    getChirpKind,
    getClampMode,
    getCSlowRange,
    getDataFormat,
    getIncrementMode,
    getLeakHoldMode,
    getLeakStoreType,
    getRecordingMode,
    getSegmentClass,
    getSourceType,
    getSquareKind,
    getStoreType,
    getTriggerKind,
    heka_time_to_datetime,
    struct_field,
    timer_timestamp,
)


class TestHekaCommonHelpers(unittest.TestCase):
    def test_cstr(self):
        self.assertEqual(cstr(b"hello\0world"), "hello")
        self.assertEqual(cstr(b"no_null"), b"no_null")
        self.assertEqual(cstr(b"\0start_null"), "")

    def test_cbyte(self):
        self.assertEqual(cbyte(b"A"), 65)
        self.assertEqual(cbyte(65), 65)
        self.assertEqual(cbyte(b""), b"")

    def test_cchar(self):
        self.assertEqual(cchar(b"A"), "A")
        self.assertEqual(cchar(b""), "")

    def test_heka_time_to_datetime(self):
        # Base Heka epoch is 1990-01-01
        # Let's test standard datetime conversion within bounds
        dt = heka_time_to_datetime(0.0)
        self.assertEqual(dt, datetime.datetime(1990, 1, 1))

        # Test within bounds (e.g. 10 years later - late December 1999 due to leap years)
        ten_years_seconds = 10 * 365 * 24 * 3600
        dt_10yr = heka_time_to_datetime(ten_years_seconds)
        self.assertEqual(dt_10yr.year, 1999)

        # Test extreme/wrap behavior or windows epoch
        # Large value > 2**32
        dt_large = heka_time_to_datetime(2**32 + 1000)
        self.assertTrue(isinstance(dt_large, (datetime.datetime, str)))

    def test_timer_timestamp(self):
        delta = timer_timestamp(120.5)
        self.assertEqual(delta, datetime.timedelta(seconds=120.5))

    def test_lookups(self):
        self.assertEqual(getAmplifierType(2), "EPC9")
        self.assertEqual(getAmplifierType(99), "Unknown (value: 99)")

        self.assertEqual(getADBoard(1), "ITC18")
        self.assertEqual(getRecordingMode(3), "WholeCell")
        self.assertEqual(getDataFormat(0), "int16")
        self.assertEqual(getSegmentClass(1), "Ramp")
        self.assertEqual(getStoreType(1), "Store")
        self.assertEqual(getIncrementMode(0), "Inc")
        self.assertEqual(getSourceType(1), "Hold")

        self.assertAlmostEqual(getAmplifierGain(0), 1e-3 / 1e-12 * 0.005)

        self.assertEqual(getCSlowRange(1), "30 pF")
        self.assertEqual(getClampMode(1), "VCMode")
        self.assertEqual(getAmplMode(1), "VCMode")
        self.assertEqual(getLeakHoldMode(1), "Lrel")
        self.assertEqual(getLeakStoreType(1), "StoreAvg")
        self.assertEqual(getADCMode(1), "Analog")
        self.assertEqual(getSquareKind(0), "Common Frequency")
        self.assertEqual(getChirpKind(0), "Linear")
        self.assertEqual(getTriggerKind(1), "Series")

    def test_convert_data_format_to_np(self):
        self.assertEqual(convertDataFormatToNP("int16"), np.int16)
        self.assertEqual(convertDataFormatToNP("int32"), np.int32)
        self.assertEqual(convertDataFormatToNP("real32"), np.float32)
        self.assertEqual(convertDataFormatToNP("real64"), np.float64)

    def test_convert_data_kind(self):
        kind = convertDataKind(1 | 2 | 8)
        self.assertTrue(kind["IsLittleEndian"])
        self.assertTrue(kind["IsLeak"])
        self.assertFalse(kind["IsVirtual"])
        self.assertTrue(kind["IsImon"])
        self.assertFalse(kind["IsVmon"])

    def test_convert_stim_to_dac_id(self):
        dac_id = convertStimToDacID(1 | 4 | 32)
        self.assertTrue(dac_id["UseStimScale"])
        self.assertFalse(dac_id["UseRelative"])
        self.assertTrue(dac_id["UseFileTemplate"])
        self.assertTrue(dac_id["UseScaling"])


# Create a concrete Struct class for testing
@dataclass(init=False, repr=False)
class DummyStruct(Struct):
    id: int = struct_field("i")
    name: str = struct_field("10s", cstr)
    flag: bool = struct_field("?")
    padding: bytes = struct_field("c", None)
    size_check = 16


class TestStructAndArray(unittest.TestCase):
    def test_struct_unpack(self):
        # Format for struct: i (4 bytes), 10s (10 bytes), ? (1 byte), c (1 byte) = 16 bytes total
        data = struct.pack("<i10s?c", 42, b"alice\0\0\0\0\0", True, b"\0")
        s = DummyStruct(data)
        self.assertEqual(s.id, 42)
        self.assertEqual(s.name, "alice")
        self.assertTrue(s.flag)
        self.assertEqual(DummyStruct.size(), 16)

        # Print / repr check
        rep = repr(s)
        self.assertIn("DummyStruct", rep)
        self.assertIn("id = 42", rep)
        self.assertIn("name = 'alice'", rep)

        # get_fields check
        fields = s.get_fields()
        self.assertEqual(fields["id"], 42)
        self.assertEqual(fields["name"], "alice")
        self.assertEqual(fields["flag"], True)

    def test_non_dataclass_raises_type_error(self):
        class InvalidStruct(Struct):
            pass

        with self.assertRaises(TypeError) as ctx:
            InvalidStruct._init_struct_formats()
        self.assertIn("must be decorated with @dataclass", str(ctx.exception))

    def test_struct_array(self):
        # Array of 2 DummyStructs
        DummyArray = DummyStruct.array(2)
        self.assertEqual(DummyArray.size(), 32)

        data = struct.pack(
            "<i10s?c", 1, b"one\0\0\0\0\0\0\0", True, b"\0"
        ) + struct.pack("<i10s?c", 2, b"two\0\0\0\0\0\0\0", False, b"\0")
        arr = DummyArray(data)

        self.assertEqual(len(arr), 2)
        self.assertEqual(arr[0].id, 1)
        self.assertEqual(arr[0].name, "one")
        self.assertEqual(arr[1].id, 2)
        self.assertEqual(arr[1].name, "two")

        # Test iteration
        ids = [item.id for item in arr]
        self.assertEqual(ids, [1, 2])

        rep = repr(arr)
        self.assertIn("DummyStruct[2]", rep)


if __name__ == "__main__":
    unittest.main()
