import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from HekaReader import Bundle


class TestIntegrationHekaReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dat_filepath = os.path.join(os.path.dirname(__file__), "2026-05-19_001.dat")

    def test_real_file_load_and_basic_metadata(self):
        # Ensure the test file exists
        self.assertTrue(os.path.exists(self.dat_filepath), "Test dat file does not exist!")

        with Bundle(self.dat_filepath) as bundle:
            # Check basic properties
            self.assertEqual(bundle.file_format, "v1000")
            self.assertEqual(bundle.endian, "<")
            self.assertEqual(bundle.header.Version, "v2x90.5, 09-Apr-2019")
            self.assertIn(".dat", bundle.catalog)
            self.assertIn(".pul", bundle.catalog)
            self.assertIn(".pgf", bundle.catalog)
            self.assertIn(".amp", bundle.catalog)

            # Check repr string
            rep = repr(bundle)
            self.assertIn("Bundle(file_name=", rep)
            self.assertIn("format='v1000'", rep)

    def test_real_file_heka_tree_navigation(self):
        with Bundle(self.dat_filepath) as bundle:
            pul = bundle.pul
            self.assertIsNotNone(pul)

            # Test TreeNode iteration and __len__
            self.assertEqual(len(pul), 1)  # 1 Group Record
            group = pul[0]
            self.assertEqual(group.Label, "E-1")
            self.assertEqual(len(group), 5)  # 5 Series Records

            # Series: 1. conti_vc, 2. iv_vc, 3. pulse_leak_vc, 4. conti_cc, 5. step_cc
            series_labels = [s.Label for s in group]
            self.assertEqual(
                series_labels,
                ["conti_vc", "iv_vc", "pulse_leak_vc", "conti_cc", "step_cc"]
            )

            # Check Sweep counts (via actual child counts vs metadata)
            series_1 = group[0]
            self.assertEqual(len(series_1), 2)  # actual sweep count
            # Verify NumberSweeps metadata might match or be inaccurate as per HEKA specs
            self.assertEqual(series_1.NumberSweeps, 2)

            # Let's verify RecordingMode for first trace of first sweep of the series
            sweep_1 = series_1[0]
            self.assertEqual(len(sweep_1), 1)  # 1 trace in the sweep
            trace_1 = sweep_1[0]
            self.assertEqual(trace_1.RecordingMode, "WholeCell")

    def test_real_file_stimulus_and_amplifiers(self):
        with Bundle(self.dat_filepath) as bundle:
            # Stimulus tree (.pgf)
            pgf = bundle.pgf
            self.assertIsNotNone(pgf)
            self.assertGreater(len(pgf), 0)

            # The name of PGF protocols is in EntryName of StimulationRecord
            protocol_names = [stim.EntryName for stim in pgf.children]
            self.assertIn("conti_vc", protocol_names)
            self.assertIn("iv_vc", protocol_names)

            # Amplification (.amp)
            amp = bundle.amp
            self.assertIsNotNone(amp)
            self.assertGreater(len(amp), 0)

    def test_real_file_raw_data_reading(self):
        with Bundle(self.dat_filepath) as bundle:
            data_reader = bundle.data
            self.assertIsNotNone(data_reader)

            # Read raw data for Group 0, Series 1 (iv_vc), Sweep 0, Trace 0
            # Let's find index in the group/series/sweep/trace levels:
            # Group 0: "E-1"
            # Series 1: "iv_vc"
            # Sweep 0
            # Trace 0
            data = bundle.data[0, 1, 0, 0]

            self.assertIsInstance(data, np.ndarray)
            self.assertEqual(data.dtype, np.float64)
            self.assertGreater(len(data), 0)

            # Verify coordinate indexing error handling
            with self.assertRaises(IndexError):
                _ = bundle.data[0, 1]  # Must be length 4 tuple


if __name__ == "__main__":
    unittest.main()
