import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from HekaReader import Bundle


class TestBundleLogic(unittest.TestCase):
    def test_unsupported_version_initialization(self):
        # Test initialization with an invalid/unsupported DAT format
        # If we return a small string or mock read that doesn't match b"DAT2"
        mock_file = MagicMock()
        mock_file.read.return_value = b"BAD!"

        with patch("builtins.open", return_value=mock_file):
            with self.assertRaises(ValueError) as context:
                Bundle("dummy.dat")
            self.assertIn("No support for other files than 'DAT2' format", str(context.exception))

    def test_unsupported_heka_version_name(self):
        # Test signature b"DAT2" but version name that is unknown
        mock_file = MagicMock()
        # First read of 4 bytes is 'DAT2'
        # Next seek is to 8
        # Next read of 32 bytes is version
        def side_effect(size):
            if size == 4:
                return b"DAT2"
            elif size == 32:
                return b"v999.0_unknown_version_name\0\0\0"
            return b""

        mock_file.read.side_effect = side_effect

        with patch("builtins.open", return_value=mock_file):
            with self.assertRaises(ValueError) as context:
                Bundle("dummy.dat")
            self.assertIn("Unsupported file version", str(context.exception))

    def test_context_manager_behavior(self):
        # Mock file handle to see if it closes upon exit
        mock_file = MagicMock()
        mock_file.read.side_effect = lambda size: b"DAT2" if size == 4 else (b"1.6.0 [Build 1066]" + b"\0"*14 if size == 32 else b"")
        mock_file.seek = MagicMock()

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


if __name__ == "__main__":
    unittest.main()
