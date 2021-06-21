import pandas as pd
from pandas.testing import assert_series_equal


def test_calculate_building_volume(building_floor_dimensions, building_volume):
    """Output is equivalent to DEAP 4.2.0 example A"""
    (
        ground_floor_area,
        ground_floor_height,
        first_floor_area,
        first_floor_height,
        second_floor_area,
        second_floor_height,
        third_floor_area,
        third_floor_height,
    ) = building_floor_dimensions

    expected_output = pd.Series([321], dtype="int64")

    output = building_volume
    rounded_output = output.round().astype("int64")

    assert_series_equal(rounded_output, expected_output)
