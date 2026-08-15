import os
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from HekaReader import Bundle
from HekaReader.HekaReader import determine_format_version


class TestBundleLogic(unittest.TestCase):
    def test_determine_format_version(self):
        # Test old-style and new-style versions
        self.assertEqual(determine_format_version("v2x90.2, 19-Mar-2018"), 9)
        self.assertEqual(determine_format_version("v2x90.3, 19-Mar-2018"), 1000)
        self.assertEqual(determine_format_version("1.5.0 [Build 1061]"), 1000)
        self.assertEqual(determine_format_version("1.7.0 [Build 1072]"), 2000)

    def test_unsupported_version_initialization(self):
        # Test initialization with an invalid/unsupported DAT format
        m_open = mock_open(read_data=b"BAD!    \0\0\0\0\0")
        with patch("builtins.open", m_open):
            with self.assertRaises(ValueError) as context:
                Bundle("dummy.dat")
            self.assertIn("Unsupported file signature", str(context.exception))

    def test_context_manager_behavior(self):
        # Mock file handle to see if it closes upon exit
        # Header version string at byte 8 is 32 bytes.
        header_data = b"DAT2\0\0\0\0" + b"1.6.0 [Build 1066]".ljust(32, b"\0")
        mock_file = MagicMock()
        mock_file.read.side_effect = lambda size: header_data[:size].ljust(size, b"\0")
        mock_file.seek = MagicMock()
        mock_file.__enter__.return_value = mock_file

        # Mock bundle v9/v1000/v2000 headers
        with patch("builtins.open", return_value=mock_file):
            with patch("HekaReader.heka.heka_v2000.BundleHeader") as mock_header_cls:
                mock_header = MagicMock()
                mock_header.IsLittleEndian = True
                mock_header.BundleItems = []
                mock_header_cls.return_value = mock_header

                with Bundle("dummy.dat") as bundle:
                    self.assertEqual(bundle.file_format, "v2000")

                # Check that close was called on the file handle upon exiting with-block
                mock_file.close.assert_called()

    def test_bundle_header_str(self):
        dat_file = os.path.join(os.path.dirname(__file__), "2026-05-19_001.dat")
        if os.path.exists(dat_file):
            with Bundle(dat_file) as bundle:
                header_str = str(bundle.header)
                self.assertIn("BundleHeader(", header_str)
                self.assertIn("BundleItem[12](", header_str)


if __name__ == "__main__":
    unittest.main()
