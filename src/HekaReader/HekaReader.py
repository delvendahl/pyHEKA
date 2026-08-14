"""
Heka Patchmaster .dat file reader
Adapted from https://github.com/campagnola/heka_reader

Structure definitions adapted from StimFit hekalib.cpp

Brief example::

    # Load a .dat file
    bundle = Bundle(file_name)

    # Select a trace
    trace = bundle.pul[group_ind][series_ind][sweep_ind][trace_ind]

    # Print meta-data for this trace
    print(trace)

    # Load data for this trace
    data = bundle.data[group_id, series_id, sweep_ind, trace_ind]

"""

import re

from heka import Data, heka_v9, heka_v1000, heka_v2000


def read_bundle_header_version(filepath):
    """
    Read the version string from the bundle header of a HEKA .dat file.
    The version string is at byte offset 8, length 32 (null-terminated).
    """
    with open(filepath, "rb") as fh:
        fh.seek(0)
        # Read signature (8s) + version (32s)
        raw = fh.read(40)
        signature = raw[:8].split(b"\x00")[0].decode("utf-8", errors="ignore")
        version_bytes = raw[8:40]
        version_str = version_bytes.split(b"\x00")[0].decode("utf-8", errors="ignore")
    return signature, version_str


def parse_version_number(version_str):
    """
    Parse a HEKA version string into a comparable tuple.

    Handles two formats:
      Old-style: "v2x90.3, 19-Mar-2018"  →  (2, 90, 3)
      Old-style: "v2x65, 19-Dec-2011"    →  (2, 65, 0)
      Old-style: "v2.11, 14-Mar-2006"    →  (2, 11, 0)
      New-style: "1.5.0 [Build 1061]"    →  (1, 5, 0)  (new-style flag)
      New-style: "1.7.0 [Build 1072]"    →  (1, 7, 0)  (new-style flag)

    Returns (version_tuple, is_new_style)
    """
    version_str = version_str.strip()

    # --- New-style: "X.Y.Z [Build NNNN]" ---
    # These are Patchmaster NEXT versions (1.x.x)
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", version_str)
    if m:
        major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return (major, minor, patch), True

    # --- Old-style: "v2x90.3, ..." or "v2x65, ..." or "v2.11, ..." ---
    # Strip leading 'v' and take everything before the comma
    core = version_str.split(",")[0].strip()
    core = core.removeprefix("v")

    # Replace 'x' with '.' (v2x65 → 2.65, v2x90.3 → 2.90.3)
    core = core.replace("x", ".")

    parts = core.split(".")
    nums = []
    for p in parts:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)

    # Pad to at least 3 elements
    while len(nums) < 3:
        nums.append(0)

    return tuple(nums[:3]), False


def determine_format_version(version_str):
    """
    Determine the HEKA file format version (v9, v1000, or v2000)
    from the bundle header version string.

    Rules (based on known version mappings):
      Old-style v2x90.2 and below  → v9
      Old-style v2x90.3 and above  → v1000
      New-style 1.5.0 and below    → v1000
      New-style 1.6.0 and above    → v2000

    Returns an integer: 9, 1000, or 2000.
    """
    (major, minor, patch), is_new_style = parse_version_number(version_str)

    if is_new_style:
        # New-style "1.x.y [Build NNNN]" — Patchmaster NEXT
        if (major, minor) >= (1, 6):
            return 2000
        else:
            return 1000
    else:
        # Old-style "v2xNN" or "v2.NN"
        # v2x90.2 and below → v9
        # v2x90.3 and above → v1000
        if (major, minor, patch) <= (2, 90, 2):
            return 9
        else:
            return 1000


def get_file_format_version(filepath):
    """
    High-level function: read a .dat file and return the format version
    as an integer (9, 1000, or 2000).
    """
    signature, version_str = read_bundle_header_version(filepath)

    if signature != "DAT2":
        raise ValueError(
            f"Unsupported file signature '{signature}'. "
            f"Only 'DAT2' (bundled) files are supported. "
            f"DAT1 (unbundled) files must be converted in Patchmaster first."
        )

    return determine_format_version(version_str)


class Bundle:
    """
    Represent a PATCHMASTER tree file in memory
    """

    def __init__(self, file_name):
        self.file_name = file_name
        self.fh = open(self.file_name, "rb")
        try:
            self._parse()
        except BaseException:
            self.fh.close()
            raise

    def _parse(self):
        FORMAT_MAP = {
            "v9": heka_v9,
            "v1000": heka_v1000,
            "v2000": heka_v2000,
        }
        self.file_format = f"v{get_file_format_version(self.file_name)}"
        self.v = FORMAT_MAP.get(self.file_format)

        self.item_classes = {
            ".pul": self.v.Pulsed,
            ".dat": Data,
            ".amp": self.v.Amplifier,
            ".pgf": self.v.Stimulus,
        }

        # read Endianness from file header
        self.fh.seek(0)
        self.endian = "<"
        self.header = self.v.BundleHeader(self.fh, self.endian)
        if not self.header.IsLittleEndian:
            self.endian = ">"
            self.fh.seek(0)
            self.header = self.v.BundleHeader(self.fh, self.endian)

        # catalog extensions of bundled items
        self.catalog = {}
        for item in self.header.BundleItems:
            item.instance = None
            ext = item.Extension
            self.catalog[ext] = item

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False  # don't suppress exceptions

    def close(self):
        if hasattr(self, "fh") and self.fh:
            self.fh.close()

    @property
    def pul(self):
        """The Pulsed object from this bundle."""
        return self._get_item_instance(".pul")

    @property
    def data(self):
        """The Data object from this bundle."""
        return self._get_item_instance(".dat")

    @property
    def amp(self):
        """The Amplifier object from this bundle."""
        return self._get_item_instance(".amp")

    @property
    def pgf(self):
        """The PGF object from this bundle."""
        return self._get_item_instance(".pgf")

    def _get_item_instance(self, ext):
        if ext not in self.catalog:
            return None
        item = self.catalog[ext]
        if item.instance is None:
            cls = self.item_classes[ext]
            item.instance = cls(self, item.Start, item.Length)
        return item.instance

    def __repr__(self):
        return (
            f"Bundle(file_name={self.file_name!r}, "
            f"format={self.file_format!r}, "
            f"endian={self.endian!r}, "
            f"version={self.header.Version!r}, "
            f"items={list(self.catalog.keys())!r})"
        )

    def summary(self, detailed=False):
        """Print a summary of the bundle content."""
        print(f"File: {self.file_name}")
        print(f"Format: {self.file_format}")
        print(f"Version: {self.header.Version}")
        print(f"Time: {self.header.Time}")
        print("-" * 40)

        pgf = self.pgf
        if pgf is not None:
            protocols = [p.EntryName for p in pgf.children]
            # get only unique protocols
            protocols = list(dict.fromkeys(protocols))
            print(f"PGF Protocols: {', '.join(protocols)}")
            print("-" * 40)

        pul = self.pul
        if pul is not None:
            print("Data Content:")
            for i, group in enumerate(pul.children):
                print(f"Group {i + 1}: {group.Label} ({len(group.children)} series)")
                if detailed:
                    for j, series in enumerate(group.children):
                        mode = "Unknown"
                        try:
                            # Use RecordingMode of the first trace of the first sweep
                            mode = series.children[0].children[0].RecordingMode
                        except (AttributeError, IndexError):
                            pass
                        print(
                            f"    Series {j + 1}: {series.Label} (Mode: {mode}, {len(series)} sweeps)"
                        )
        print("-" * 40)
