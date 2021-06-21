import numpy as np
from numpy.testing import assert_array_almost_equal
import pandas as pd
from pandas.testing import assert_series_equal
import pytest

from rc_building_model import htuse


@pytest.fixture
def delta_t_by_month():
    return pd.Series(
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


@pytest.fixture
def hours_per_month():
    return pd.Series(
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


def test_calculate_heat_loss_kwh(delta_t_by_month, hours_per_month):
    """Output is approx equivalent to DEAP 4.2.0 example A"""
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
        delta_t=delta_t_by_month,
        hours=hours_per_month,
    )

    assert_array_almost_equal(output, expected_output)


def test_heat_loss_per_year(delta_t_by_month, hours_per_month):
    heat_loss_coefficient = pd.Series(
        [
            121,
            150,
        ]
    )
    expected_output = pd.Series([7232, 8965], dtype="float64")

    output = htuse.calculate_heat_loss_per_year(
        heat_loss_coefficient=heat_loss_coefficient,
        delta_t=delta_t_by_month,
        hours=hours_per_month,
    )

    assert_series_equal(output, expected_output)
