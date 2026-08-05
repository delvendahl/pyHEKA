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

from heka import Data, heka_v9, heka_v1000, heka_v2000


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
        if self.fh.read(4) != b"DAT2":
            raise ValueError("No support for other files than 'DAT2' format")

        self.fh.seek(8)
        version = (
            self.fh.read(32).decode("ascii", errors="replace").rstrip("\x00").strip()
        )

        v9_versions = [
            "v2.11, 14-Mar-2006",
            "v2x65, 19-Dec-2011",
        ]
        # v2x90.2, 22-Nov-2016 seems to have yet another format

        v1000_versions = [
            "v2x90.3, 19-Mar-2018",
            "v2x90.4, 30-Oct-2018",
            "v2x90.5, 09-Apr-2019",
            "v2x91, 23-Feb-2021",
            "v2x91, 06-Jul-2020",
            "v2x92, 23-February-2023",
            "v2x92, 1-June-2023",
            "1.2.0 [Build 1469]",
            "1.3.0 [Build 1008]",
            "1.4.1 [Build 1036]",
            "1.5.0 [Build 1061]",
        ]

        v2000_versions = [
            "1.6.0 [Build 1066]",
            "1.7.0 [Build 1072]",
        ]

        FORMAT_MAP = {
            "v9": (v9_versions, heka_v9),
            "v1000": (v1000_versions, heka_v1000),
            "v2000": (v2000_versions, heka_v2000),
        }

        self.file_format = None
        self.v = None

        for fmt, (versions, module) in FORMAT_MAP.items():
            if version in versions:
                self.file_format = fmt
                self.v = module
                break

        if self.file_format is None and version.startswith(("1.6", "1.7", "1.8")):
            self.file_format = "v2000"
            self.v = heka_v2000

        if self.file_format is None:
            raise ValueError(f"Unsupported file version: {version!r}")

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
