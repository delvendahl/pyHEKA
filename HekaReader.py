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

from heka import Data
from heka import heka_v1000
from heka import heka_v2000
from heka import heka_v9


class Bundle(object):
    """
    Represent a PATCHMASTER tree file in memory
    """

    def __init__(self, file_name):
        self.file_name = file_name
        self.fh = open(self.file_name, 'rb')

        if self.fh.read(4) != b'DAT2':
            raise ValueError(f"No support for other files than 'DAT2' format")

        self.fh.seek(8)
        version = self.fh.read(32).decode('utf-8', errors='ignore').rstrip('\0')

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

        v2000_versions = ["1.6.0 [Build 1066]"]

        if version in v1000_versions:
            self.file_format = 'v1000'
            self.v = heka_v1000
        elif version in v2000_versions:
            self.file_format = 'v2000'
            self.v = heka_v2000
        elif version in v9_versions:
            self.file_format = 'v9'
            self.v = heka_v9
        else:
            if version.startswith("1.6") or version.startswith("1.7") or version.startswith("1.8"):
                self.file_format = 'v2000'
                self.v = heka_v2000
            else:
                self.file_format = 'unsupported'
                raise ValueError(f"Unsupported file version: {version}")
        
        self.item_classes = {
            '.pul': self.v.Pulsed,
            '.dat': Data,
            '.amp': self.v.Amplifier,
            '.pgf': self.v.Stimulus,
        }
        
        # read Endianness from file header
        self.fh.seek(0)
        endian = '<'
        self.header = self.v.BundleHeader(self.fh, endian)
        if not self.header.IsLittleEndian:
            self.endian = '>'
            self.fh.seek(0)
            self.header = self.v.BundleHeader(self.fh, self.endian)

        # catalog extensions of bundled items
        self.catalog = {}
        for item in self.header.BundleItems:
            item.instance = None
            ext = item.Extension
            self.catalog[ext] = item

    def close(self):
        if hasattr(self, 'fh') and self.fh:
            self.fh.close()

    @property
    def pul(self):
        """The Pulsed object from this bundle.
        """
        return self._get_item_instance('.pul')
    
    @property
    def data(self):
        """The Data object from this bundle.
        """
        return self._get_item_instance('.dat')

    @property
    def amp(self):
        """The Amplifier object from this bundle.
        """
        return self._get_item_instance('.amp')

    @property
    def pgf(self):
        """The PGF object from this bundle.
        """
        return self._get_item_instance('.pgf')

    def _get_item_instance(self, ext):
        if ext not in self.catalog:
            return None
        item = self.catalog[ext]
        if item.instance is None:
            cls = self.item_classes[ext]
            item.instance = cls(self, item.Start, item.Length)
        return item.instance
        
    def __repr__(self):
        return "Bundle(%r)" % list(self.catalog.keys())

    def summary(self, detailed=False):
        """Print a summary of the bundle content.
        """
        print(f"File: {self.file_name}")
        print(f"Format: {self.file_format}")
        print(f"Version: {self.header.Version}")
        print(f"Time: {self.header.Time}")
        print("-" * 40)

        pgf = self.pgf
        if pgf is not None:
            protocols = [p.EntryName for p in pgf.children]
            print(f"PGF Protocols: {', '.join(protocols)}")
            print("-" * 40)

        pul = self.pul
        if pul is not None:
            print("Data Content:")
            for i, group in enumerate(pul.children):
                print(f"Group {i+1}: {group.Label} ({len(group.children)} series)")
                if detailed:
                    for j, series in enumerate(group.children):
                        mode = "Unknown"
                        try:
                            # Use RecordingMode of the first trace of the first sweep
                            mode = series.children[0].children[0].RecordingMode
                        except (AttributeError, IndexError):
                            pass
                        print(f"    Series {j+1}: {series.Label} (Mode: {mode}, {len(series)} sweeps)")
        print("-" * 40)
