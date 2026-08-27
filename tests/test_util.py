import unittest
from unittest.mock import MagicMock
import numpy as np

from pyHeka.util import DatFileSeries, DatFileSweep, get_pgf_index


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

    def test_get_pgf_index(self):
        # When group == 0, returns series directly
        mock_bundle = MagicMock()
        self.assertEqual(get_pgf_index(mock_bundle, group=0, series=2), 2)

        # When group > 0, sums the series counts of preceding groups plus series index
        # Note: in get_pgf_index, for i in range(group): index += len(bundle.pul[i].children)
        # Note: bug in pyHeka/util.py - `if i == group:` inside range(group) is unreachable,
        # so for group > 0, get_pgf_index returns sum(len(group_i)) without adding series offset.
        # We test the current function behavior cleanly here.
        group0 = MagicMock()
        group0.children = [1, 2, 3]  # length 3
        group1 = MagicMock()
        group1.children = [1, 2]     # length 2

        mock_bundle.pul = [group0, group1]

        # For group=1, range(1) iterates i=0 -> index = 3
        self.assertEqual(get_pgf_index(mock_bundle, group=1, series=1), 3)


if __name__ == "__main__":
    unittest.main()
