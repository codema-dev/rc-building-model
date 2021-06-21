import numpy as np
import pandas as pd
import pytest

from rc_building_model import dim


@pytest.fixture
def building_fabric():
    floor_uvalue = pd.Series([0.14])
    roof_uvalue = pd.Series([0.11])
    wall_uvalue = pd.Series([0.13])
    window_uvalue = pd.Series([0.87])
    door_uvalue = pd.Series([1.5])
    thermal_bridging_factor = pd.Series([0.05])
    effective_air_rate_change = pd.Series([0.5])

    return (
        floor_uvalue,
        roof_uvalue,
        wall_uvalue,
        window_uvalue,
        door_uvalue,
        thermal_bridging_factor,
        effective_air_rate_change,
    )


@pytest.fixture
def building_area():
    floor_area = pd.Series([63])
    roof_area = pd.Series([63])
    wall_area = pd.Series([85.7])
    window_area = pd.Series([29.6])
    door_area = pd.Series([1.85])

    return floor_area, roof_area, wall_area, window_area, door_area


@pytest.fixture
def building_floor_dimensions():
    ground_floor_area = pd.Series([63])
    ground_floor_height = pd.Series([2.4])
    first_floor_area = pd.Series([63])
    first_floor_height = pd.Series([2.7])
    second_floor_area = pd.Series([np.nan])
    second_floor_height = pd.Series([np.nan])
    third_floor_area = pd.Series([np.nan])
    third_floor_height = pd.Series([np.nan])

    return (
        ground_floor_area,
        ground_floor_height,
        first_floor_area,
        first_floor_height,
        second_floor_area,
        second_floor_height,
        third_floor_area,
        third_floor_height,
    )


@pytest.fixture
def building_volume(building_floor_dimensions):
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

    return dim.calculate_building_volume(
        ground_floor_area=ground_floor_area,
        ground_floor_height=ground_floor_height,
        first_floor_area=first_floor_area,
        first_floor_height=first_floor_height,
        second_floor_area=second_floor_area,
        second_floor_height=second_floor_height,
        third_floor_area=third_floor_area,
        third_floor_height=third_floor_height,
    )


@pytest.fixture
def building_floor_dimensions_approx():

    no_of_storeys = pd.Series([2])
    assumed_floor_height = pd.Series([2.5])
    return no_of_storeys, assumed_floor_height
