import numpy as np
from numpy.testing import assert_array_almost_equal
import pandas as pd
from pandas.testing import assert_series_equal
import pytest

from rcbm import htuse


def test_calculate_heat_loss_kwh():
    """Output is approx equivalent to DEAP 4.2.0 example A"""
    delta_t = pd.Series(
        [12.42, 12.23, 10.85, 9.65, 7.15, 4.85, 3.0, 3.28, 5.03, 7.71, 10.38, 11.77],
        index=[
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ],
    )
    hours = pd.Series(
        [d * 24 for d in [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]],
        index=[
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ],
    )
    heat_loss_coefficient = pd.Series(
        [
            121,
            150,
        ]
    )
    expected_output = np.array(
        [
            1118.09808,
            994.44576,
            976.7604,
            840.708,
            643.6716,
            422.532,
            270.072,
            295.27872,
            438.2136,
            694.08504,
            904.3056,
            1059.58248,
            1386.072,
            1232.784,
            1210.86,
            1042.2,
            797.94,
            523.8,
            334.8,
            366.048,
            543.24,
            860.436,
            1121.04,
            1313.532,
        ]
    )

    output = htuse._calculate_heat_loss_kwh(
        heat_loss_coefficient=heat_loss_coefficient,
        delta_t=delta_t,
        hours=hours,
    )

    assert_array_almost_equal(output, expected_output)


def test_heat_loss_per_year():
    internal_temperatures = pd.Series(
        [
            17.72,
            17.73,
            17.85,
            17.95,
            18.15,
            18.35,
            18.50,
            18.48,
            18.33,
            18.11,
            17.88,
            17.77,
        ],
        index=[
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ],
    )
    external_temperatures = pd.Series(
        [5.3, 5.5, 7.0, 8.3, 11.0, 13.5, 15.5, 15.2, 13.3, 10.4, 7.5, 6.0],
        index=[
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ],
    )
    heat_loss_coefficient = pd.Series(
        [
            121,
            150,
        ]
    )
    expected_output = pd.Series([7232, 8965], dtype="float64")

    output = htuse.calculate_heat_loss_per_year(
        heat_loss_coefficient=heat_loss_coefficient,
        internal_temperatures=internal_temperatures,
        external_temperatures=external_temperatures,
        how="monthly",
    )

    assert_series_equal(output, expected_output)
