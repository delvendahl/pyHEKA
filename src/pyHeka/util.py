# from pyHeka.util import *

from dataclasses import dataclass

import numpy as np


@dataclass
class DatFileSeries:
    """
    Represents a series of HEKA .dat files that are part of the same recording session.
    """

    x: np.ndarray  # Time vector
    y: np.ndarray  # Data matrix (channels x time)
    x_unit: str  # Unit of measurement for the time axis
    y_unit: str  # Unit of measurement for the data
    sampling_interval: float  # Sampling interval in seconds
    filename: str  # Name of the file
    series_idx: tuple[int, int]  # (group_index, series_index)


@dataclass
class DatFileSweep:
    """
    Represents a single sweep from a HEKA .dat file.
    """

    x: np.ndarray  # Time vector
    y: np.ndarray  # Data matrix (channels x time)
    x_unit: str  # Unit of measurement for the time axis
    y_unit: str  # Unit of measurement for the data
    sampling_interval: float  # Sampling interval in seconds
    filename: str  # Name of the file
    sweep_idx: tuple[
        int, int, int, int
    ]  # (group_index, series_index, sweep_index, trace_index)
