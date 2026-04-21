
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the current directory to sys.path so we can import HekaReader
sys.path.append(os.getcwd())

from HekaReader import Bundle

class TestBundleSummary(unittest.TestCase):
    def setUp(self):
        # Mocking Bundle.__init__ to avoid file operations
        with patch('HekaReader.open', MagicMock()):
            with patch('heka_v1000.BundleHeader', MagicMock()):
                self.bundle = Bundle.__new__(Bundle)
                self.bundle.file_name = "test_file.dat"
                self.bundle.file_format = "v1000"
                self.bundle.header = MagicMock()
                self.bundle.header.Version = "v2x90.3"
                self.bundle.header.Time = "2023-01-01 12:00:00"

    def test_summary_brief(self):
        # Mocking pgf (Stimulus)
        mock_pgf = MagicMock()
        stim1 = MagicMock()
        stim1.EntryName = "Protocol1"
        stim2 = MagicMock()
        stim2.EntryName = "Protocol2"
        mock_pgf.children = [stim1, stim2]
        self.bundle._get_item_instance = MagicMock(side_effect=lambda ext: mock_pgf if ext == '.pgf' else None)

        # Mocking pul (Pulsed)
        mock_pul = MagicMock()
        group1 = MagicMock()
        group1.Label = "Group1"
        group1.children = [MagicMock(), MagicMock()] # 2 series
        group2 = MagicMock()
        group2.Label = "Group2"
        group2.children = [MagicMock()] # 1 series
        mock_pul.children = [group1, group2]

        def mock_get_item(ext):
            if ext == '.pgf': return mock_pgf
            if ext == '.pul': return mock_pul
            return None

        self.bundle._get_item_instance = MagicMock(side_effect=mock_get_item)

        # We need to capture stdout
        from io import StringIO
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            self.bundle.summary(detailed=False)
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("File: test_file.dat", output)
        self.assertIn("Format: v1000", output)
        self.assertIn("PGF Protocols: Protocol1, Protocol2", output)
        self.assertIn("Group 1: Group1 (2 series)", output)
        self.assertIn("Group 2: Group2 (1 series)", output)

    def test_summary_detailed(self):
        # Mocking pgf
        mock_pgf = MagicMock()
        stim1 = MagicMock()
        stim1.EntryName = "Protocol1"
        mock_pgf.children = [stim1]

        # Mocking pul
        mock_pul = MagicMock()
        group1 = MagicMock()
        group1.Label = "Group1"

        series1 = MagicMock()
        series1.Label = "Series1"
        series1.MethodName = "Method1"
        series1.NumberSweeps = 5

        group1.children = [series1]
        mock_pul.children = [group1]

        def mock_get_item(ext):
            if ext == '.pgf': return mock_pgf
            if ext == '.pul': return mock_pul
            return None

        self.bundle._get_item_instance = MagicMock(side_effect=mock_get_item)

        from io import StringIO
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            self.bundle.summary(detailed=True)
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Group 1: Group1", output)
        self.assertIn("Series 1: Series1 (Method: Method1, 5 sweeps)", output)

if __name__ == '__main__':
    unittest.main()
