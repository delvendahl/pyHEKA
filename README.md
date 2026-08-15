# HekaReader

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org)
[![License: GNU AGPL](https://img.shields.io/badge/License-GNU-yellow.svg)](LICENSE)

`HekaReader` is a lightweight, efficient, and easy-to-use Python library for parsing and reading bundled `.dat` files created by HEKA Patchmaster or Patchmaster Next software. It supports several HEKA file versions including **v9**, **v1000**, and **v2000** formats.

The library allows neuroscience researchers and electrophysiologists to load complex electrophysiology data tree structures directly into Python, access metadata, and read raw traces as NumPy arrays.

---

## Features

- **Multi-version Support:** Automatically detects and reads `v9`, `v1000`, and `v2000` Patchmaster file versions.
- **Efficient Memory Footprint:** Built on highly optimized data structures (e.g., using `StructArray` with indexed slicing for $O(N)$ parsing, and direct attribute lookup instead of bulky internal dictionary storage).
- **Comprehensive Metadata Access:** Easily extract stimulation protocols, group/series/sweep labels, recording modes, and amplifier configurations.
- **Hierarchical Access:** Reflects HEKA's internal structure: Group &rarr; Series &rarr; Sweep &rarr; Trace.
- **NumPy Integration:** Directly access electrophysiology traces as standard NumPy arrays.

---

## Installation

### From Source

Ensure you have Python 3.9+ and `numpy` installed. You can install `HekaReader` from source using `pip`:

```bash
git clone https://github.com/delvendahl/HekaDatReader.git
cd HekaDatReader
pip install .
```

For development work, you can install it in editable mode:

```bash
pip install -e .
```

---

## Example Usage

Here is a quick overview of how to use `HekaReader` to load and inspect your `.dat` files.

### 1. Load a `.dat` Bundle

```python
from HekaReader import Bundle

# Load your HEKA .dat file
bundle = Bundle("path/to/your/file.dat")

# Print basic info about the bundle format and metadata
print(bundle)
```

### 2. Print a Summary of the Bundle

You can quickly get a brief or a detailed summary of the file content, including groups, series, sweeps, and stimulus protocols:

```python
# Print brief summary
bundle.summary()

# Print detailed summary with recording modes and sweep counts
bundle.summary(detailed=True)
```

### 3. Navigate the HEKA Tree Hierarchy

HEKA's pulsed tree maps to standard Python indices:

```python
# Access the pulsed tree
pul = bundle.pul

# Iterate over groups and series
for group in pul.children:
    print(f"Group: {group.Label}")
    for series in group.children:
        print(f"  Series: {series.Label}, Sweeps: {len(series)}")
```

### 4. Fetch Raw Electrophysiological Data

You can load the actual raw trace data into NumPy arrays using the `.data` property:

> [!NOTE]
>Note that data is loaded using Python indices, which are zero-based, while HEKA uses one-based indices.


```python
group_idx = 0
series_idx = 0
sweep_idx = 0
trace_idx = 0

# Retrieve data for the specific trace as a NumPy array
trace_data = bundle.data[group_idx, series_idx, sweep_idx, trace_idx]

print("Shape of trace data array:", trace_data.shape)
print("Trace sample values:", trace_data[:10])
```


---

## Development & Testing

To run the unit tests, run:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```


## Acknowledgements

The code is based on work by Luke Campagnola (https://github.com/campagnola/heka_reader). Additional contributions and improvements have been made to enhance performance, usability, and compatibility with different .dat file versions.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
