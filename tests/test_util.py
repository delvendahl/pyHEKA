import unittest
from unittest.mock import MagicMock
import numpy as np

from pyheka.util import DatFileSeries, DatFileSweep


class TestUtil(unittest.TestCase):
    def test_dat_file_series_dataclass(self):
        x = np.array([0.0, 0.1, 0.2])
        y = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        series = DatFileSeries(
            x=x,
            y=y,
            x_unit="s",
            y_unit="A",
            sampling_interval=0.1,
            filename="test.dat",
            series_idx=(0, 1),
        )

        np.testing.assert_array_equal(series.x, x)
        np.testing.assert_array_equal(series.y, y)
        self.assertEqual(series.x_unit, "s")
        self.assertEqual(series.y_unit, "A")
        self.assertEqual(series.sampling_interval, 0.1)
        self.assertEqual(series.filename, "test.dat")
        self.assertEqual(series.series_idx, (0, 1))

    def test_dat_file_sweep_dataclass(self):
        x = np.array([0.0, 0.1])
        y = np.array([1.0, 2.0])
        sweep = DatFileSweep(
            x=x,
            y=y,
            x_unit="s",
            y_unit="A",
            sampling_interval=0.1,
            filename="test.dat",
            sweep_idx=(0, 1, 2, 0),
        )

        np.testing.assert_array_equal(sweep.x, x)
        np.testing.assert_array_equal(sweep.y, y)
        self.assertEqual(sweep.x_unit, "s")
        self.assertEqual(sweep.y_unit, "A")
        self.assertEqual(sweep.sampling_interval, 0.1)
        self.assertEqual(sweep.filename, "test.dat")
        self.assertEqual(sweep.sweep_idx, (0, 1, 2, 0))


if __name__ == "__main__":
    unittest.main()
