import os
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from pyheka import Bundle
from pyheka.util import DatFileSeries, DatFileSweep


class TestBundleGetSweepAndGetSeries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dat_filepath = os.path.join(os.path.dirname(__file__), "2026-05-19_001.dat")

    def test_get_sweep_real_file(self):
        with Bundle(self.dat_filepath) as bundle:
            sweep = bundle.get_sweep(
                group_index=0, series_index=1, sweep_index=0, trace_index=0
            )
            self.assertIsInstance(sweep, DatFileSweep)
            self.assertEqual(sweep.filename, "2026-05-19_001.dat")
            self.assertEqual(sweep.sweep_idx, (0, 1, 0, 0))
            self.assertIsInstance(sweep.x, np.ndarray)
            self.assertIsInstance(sweep.y, np.ndarray)
            self.assertEqual(sweep.x.shape, sweep.y.shape)
            self.assertGreater(sweep.sampling_interval, 0)
            self.assertTrue(isinstance(sweep.x_unit, str))
            self.assertTrue(isinstance(sweep.y_unit, str))

    def test_get_sweep_invalid_indices(self):
        with Bundle(self.dat_filepath) as bundle:
            with self.assertRaises(ValueError) as ctx:
                bundle.get_sweep(
                    group_index=99, series_index=0, sweep_index=0, trace_index=0
                )
            self.assertIn(
                "Invalid group_index 99 or series_index 0", str(ctx.exception)
            )

            with self.assertRaises(ValueError) as ctx:
                bundle.get_sweep(
                    group_index=0, series_index=99, sweep_index=0, trace_index=0
                )
            self.assertIn(
                "Invalid group_index 0 or series_index 99", str(ctx.exception)
            )

    def test_get_series_real_file_default(self):
        with Bundle(self.dat_filepath) as bundle:
            # Series 1 ("iv_vc") has multiple sweeps
            series = bundle.get_series(group_index=0, series_index=1, trace_index=0)
            self.assertIsInstance(series, DatFileSeries)
            self.assertEqual(series.filename, "2026-05-19_001.dat")
            self.assertEqual(series.series_idx, (0, 1))
            self.assertEqual(series.y.ndim, 2)  # 2D array (sweeps x time)
            self.assertEqual(len(series.x), series.y.shape[1])
            self.assertGreater(series.sampling_interval, 0)

    def test_get_series_concatenate(self):
        with Bundle(self.dat_filepath) as bundle:
            series_default = bundle.get_series(
                group_index=0, series_index=1, trace_index=0
            )
            series_concat = bundle.get_series(
                group_index=0, series_index=1, trace_index=0, concatenate_sweeps=True
            )
            self.assertIsInstance(series_concat, DatFileSeries)
            self.assertEqual(series_concat.y.ndim, 1)  # 1D array concatenated
            expected_total_len = series_default.y.shape[0] * series_default.y.shape[1]
            self.assertEqual(len(series_concat.y), expected_total_len)
            self.assertEqual(len(series_concat.x), expected_total_len)

    def test_get_series_average(self):
        with Bundle(self.dat_filepath) as bundle:
            series_default = bundle.get_series(
                group_index=0, series_index=1, trace_index=0
            )
            series_avg = bundle.get_series(
                group_index=0, series_index=1, trace_index=0, average_sweeps=True
            )
            self.assertIsInstance(series_avg, DatFileSeries)
            self.assertEqual(series_avg.y.ndim, 1)  # 1D array averaged across sweeps
            expected_mean = np.nanmean(series_default.y, axis=0)
            np.testing.assert_array_almost_equal(series_avg.y, expected_mean)
            self.assertEqual(len(series_avg.x), len(series_avg.y))

    def test_get_series_concatenate_and_average_error(self):
        with Bundle(self.dat_filepath) as bundle:
            with self.assertRaises(ValueError) as ctx:
                bundle.get_series(
                    group_index=0,
                    series_index=1,
                    concatenate_sweeps=True,
                    average_sweeps=True,
                )
            self.assertIn(
                "Cannot concatenate and average at the same time", str(ctx.exception)
            )

    def test_get_series_invalid_indices(self):
        with Bundle(self.dat_filepath) as bundle:
            with self.assertRaises(ValueError) as ctx:
                bundle.get_series(group_index=99, series_index=0)
            self.assertIn(
                "Invalid group_index 99 or series_index 0", str(ctx.exception)
            )

    def test_get_series_padded_sweeps_unequal_length(self):
        # Create mock bundle where sweeps return arrays of different lengths
        mock_bundle = MagicMock()
        mock_bundle.file_name = "mock_file.dat"

        # Mock data indexing
        sweep1 = np.array([1.0, 2.0, 3.0])
        sweep2 = np.array([4.0, 5.0])  # shorter sweep
        mock_bundle.data = {
            (0, 0, 0, 0): sweep1,
            (0, 0, 1, 0): sweep2,
        }

        # Mock pul indexing: pul[group][series] length is 2 sweeps
        mock_series = MagicMock()
        mock_series.__len__.return_value = 2
        mock_trace = MagicMock()
        mock_trace.XUnit = "s"
        mock_trace.YUnit = "A"
        mock_series.__getitem__.return_value = [mock_trace]  # pul[0][0][0][0]

        mock_group = MagicMock()
        mock_group.__getitem__.return_value = mock_series
        mock_pul = MagicMock()
        mock_pul.__getitem__.return_value = mock_group
        mock_bundle.pul = mock_pul

        # Mock pgf sampling interval
        mock_pgf_record = MagicMock()
        mock_pgf_record.SampleInterval = 0.001
        mock_pgf = MagicMock()
        mock_pgf.__getitem__.return_value = mock_pgf_record
        mock_bundle.pgf = mock_pgf

        # Call get_series via method unbound call or bind method
        series_res = Bundle.get_series(
            mock_bundle, group_index=0, series_index=0, trace_index=0
        )

        self.assertEqual(series_res.y.shape, (2, 3))
        # Second sweep should be padded with zero by np.pad
        np.testing.assert_array_equal(series_res.y[0], np.array([1.0, 2.0, 3.0]))
        np.testing.assert_array_equal(series_res.y[1], np.array([4.0, 5.0, 0.0]))


if __name__ == "__main__":
    unittest.main()
