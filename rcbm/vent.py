"""
Replicate DEAP 4.2.2 Vent Excel calculations

Assumptions:

Structure Types
- Unknown are Masonry as 82/96 buildings are masonry
- Concrete has an infiltration rate of 0
"""
from decimal import DivisionByZero

import numpy as np
import pandas as pd


def _calculate_infiltration_rate_due_to_opening(
    no_openings: pd.Series, building_volume: pd.Series, ventilation_rate: int
) -> pd.Series:
    is_building_volume_zero = building_volume == 0
    if is_building_volume_zero.any():
        raise DivisionByZero(
            "Please remove buildings with zero volume, otherwise they will have an"
            " infinite infiltration rate!"
        )
    return no_openings * ventilation_rate / building_volume


def calculate_infiltration_rate_due_to_chimneys(
    no_chimneys: pd.Series, building_volume: pd.Series, ventilation_rate: int = 40
) -> pd.Series:
    return _calculate_infiltration_rate_due_to_opening(
        no_chimneys, building_volume, ventilation_rate
    )


def calculate_infiltration_rate_due_to_open_flues(
    no_chimneys: pd.Series, building_volume: pd.Series, ventilation_rate: int = 20
) -> pd.Series:
    return _calculate_infiltration_rate_due_to_opening(
        no_chimneys, building_volume, ventilation_rate
    )


def calculate_infiltration_rate_due_to_fans(
    no_chimneys: pd.Series, building_volume: pd.Series, ventilation_rate: int = 10
) -> pd.Series:
    return _calculate_infiltration_rate_due_to_opening(
        no_chimneys, building_volume, ventilation_rate
    )


def calculate_infiltration_rate_due_to_room_heaters(
    no_chimneys: pd.Series, building_volume: pd.Series, ventilation_rate: int = 40
) -> pd.Series:
    return _calculate_infiltration_rate_due_to_opening(
        no_chimneys, building_volume, ventilation_rate
    )


def calculate_infiltration_rate_due_to_draught_lobby(
    is_draught_lobby: pd.Series,
) -> pd.Series:
    yes_or_no_map = {"YES": True, "NO": False}
    return is_draught_lobby.map(yes_or_no_map).map({True: 0, False: 0.05})


def calculate_infiltration_rate_due_to_openings(
    building_volume: pd.Series,
    no_chimneys: pd.Series,
    no_open_flues: pd.Series,
    no_fans: pd.Series,
    no_room_heaters: pd.Series,
    is_draught_lobby: pd.Series,
) -> pd.Series:
    return (
        calculate_infiltration_rate_due_to_chimneys(no_chimneys, building_volume)
        + calculate_infiltration_rate_due_to_open_flues(no_open_flues, building_volume)
        + calculate_infiltration_rate_due_to_fans(no_fans, building_volume)
        + calculate_infiltration_rate_due_to_room_heaters(
            no_room_heaters, building_volume
        )
        + calculate_infiltration_rate_due_to_draught_lobby(is_draught_lobby)
    )


def calculate_infiltration_rate_due_to_height(no_storeys: pd.Series) -> pd.Series:
    return (no_storeys - 1) * 0.1


def calculate_infiltration_rate_due_to_structure_type(
    structure_type: pd.Series, unknown_structure_infiltration_rate: float = 0.35
) -> pd.Series:
    acceptable_structure_types = [
        "unknown",
        "masonry",
        "timber_or_steel",
        "concrete",
    ]
    if not np.in1d(structure_type.unique(), acceptable_structure_types).all():
        raise ValueError(
            f"Only {acceptable_structure_types} structure types are supported!"
            " Please rename your structure types to match these, or if it is"
            " is another type entirely either fork this repository or submit a"
            " pull request to implement it!"
        )
    infiltration_rate_map = {
        "unknown": unknown_structure_infiltration_rate,
        "masonry": 0.35,
        "timber_or_steel": 0.25,
        "concrete": 0,
    }
    return structure_type.map(infiltration_rate_map)


def calculate_infiltration_rate_due_to_suspended_floor(
    is_floor_suspended: pd.Series,
) -> pd.Series:
    acceptable_suspended_floor_types = ["none", "sealed", "unsealed"]
    if not np.in1d(is_floor_suspended.unique(), acceptable_suspended_floor_types).all():
        raise ValueError(
            f"Only {acceptable_suspended_floor_types} floor types are supported!"
            " Please rename your floor types to match these, or if it is"
            " is another type entirely either fork this repository or submit a"
            " pull request to implement it!"
        )
    infiltration_rate_map = {"none": 0, "sealed": 0.1, "unsealed": 0.2}
    return is_floor_suspended.map(infiltration_rate_map)


def calculate_infiltration_rate_due_to_draught(
    percentage_draught_stripped: pd.Series,
) -> pd.Series:
    return 0.25 - (0.2 * (percentage_draught_stripped / 100))


def calculate_infiltration_rate_due_to_structure(
    permeability_test_result: pd.Series,
    no_storeys: pd.Series,
    percentage_draught_stripped: pd.Series,
    is_floor_suspended: pd.Series,
    structure_type: pd.Series,
) -> pd.Series:
    theoretical_infiltration_rate = (
        calculate_infiltration_rate_due_to_height(no_storeys)
        + calculate_infiltration_rate_due_to_structure_type(structure_type)
        + calculate_infiltration_rate_due_to_suspended_floor(is_floor_suspended)
        + calculate_infiltration_rate_due_to_draught(percentage_draught_stripped)
    )
    infiltration_rate_is_available = permeability_test_result > 0
    return pd.Series(
        np.where(
            infiltration_rate_is_available,
            permeability_test_result,
            theoretical_infiltration_rate,
        )
    )


def calculate_infiltration_rate_adjustment_factor(
    infiltration_rate: pd.Series, no_sides_sheltered: pd.Series
) -> pd.Series:
    return infiltration_rate * (1 - no_sides_sheltered * 0.075)


def calculate_infiltration_rate(
    no_sides_sheltered: pd.Series,
    building_volume: pd.Series,
    no_chimneys: pd.Series,
    no_open_flues: pd.Series,
    no_fans: pd.Series,
    no_room_heaters: pd.Series,
    is_draught_lobby: pd.Series,
    permeability_test_result: pd.Series,
    no_storeys: pd.Series,
    percentage_draught_stripped: pd.Series,
    is_floor_suspended: pd.Series,
    structure_type: pd.Series,
) -> pd.Series:
    infiltration_rate_due_to_openings = calculate_infiltration_rate_due_to_openings(
        building_volume=building_volume,
        no_chimneys=no_chimneys,
        no_open_flues=no_open_flues,
        no_fans=no_fans,
        no_room_heaters=no_room_heaters,
        is_draught_lobby=is_draught_lobby,
    )

    infiltration_rate_due_to_structure = calculate_infiltration_rate_due_to_structure(
        permeability_test_result=permeability_test_result,
        no_storeys=no_storeys,
        percentage_draught_stripped=percentage_draught_stripped,
        is_floor_suspended=is_floor_suspended,
        structure_type=structure_type,
    )

    infiltration_rate = (
        infiltration_rate_due_to_openings + infiltration_rate_due_to_structure
    )
    return calculate_infiltration_rate_adjustment_factor(
        infiltration_rate, no_sides_sheltered
    )


def _calculate_natural_ventilation_air_rate_change(
    infiltration_rate: pd.Series,
) -> pd.Series:
    return infiltration_rate.where(
        infiltration_rate > 1, 0.5 + (infiltration_rate ** 2) * 0.5
    )


def _calculate_loft_ventilation_air_rate_change(
    infiltration_rate: pd.Series, building_volume: pd.Series
) -> pd.Series:
    return (
        _calculate_natural_ventilation_air_rate_change(infiltration_rate)
        + 20 / building_volume
    )


def _calculate_outside_ventilation_air_rate_change(
    infiltration_rate: pd.Series,
) -> pd.Series:
    return np.maximum([0.5] * len(infiltration_rate), infiltration_rate + 0.25)


def _calculate_mech_ventilation_air_rate_change(
    infiltration_rate: pd.Series,
) -> pd.Series:
    return infiltration_rate + 0.5


def _calculate_heat_recovery_ventilation_air_rate_change(
    infiltration_rate: pd.Series,
    heat_exchanger_efficiency: pd.Series,
) -> pd.Series:
    return infiltration_rate + 0.5 * (1 - heat_exchanger_efficiency / 100)


def calculate_effective_air_rate_change(
    ventilation_method: pd.Series,
    building_volume: pd.Series,
    infiltration_rate: pd.Series,
    heat_exchanger_efficiency: pd.Series,
) -> pd.Series:
    acceptable_ventilation_methods = [
        "positive_input_ventilation_from_loft",
        "natural_ventilation",
        "mechanical_ventilation_no_heat_recovery",
        "mechanical_ventilation_heat_recovery",
        "positive_input_ventilation_from_outside",
    ]
    if not np.in1d(ventilation_method.unique(), acceptable_ventilation_methods).all():
        raise ValueError(
            f"Only {acceptable_ventilation_methods} ventilation methods are supported!"
            " Please rename your ventilation methods to match these, or if it is"
            " is another method entirely either fork this repository or submit a"
            " pull request to implement it!"
        )

    natural = _calculate_natural_ventilation_air_rate_change(
        infiltration_rate[ventilation_method == "natural_ventilation"]
    )
    loft = _calculate_loft_ventilation_air_rate_change(
        infiltration_rate[ventilation_method == "positive_input_ventilation_from_loft"],
        building_volume[ventilation_method == "positive_input_ventilation_from_loft"],
    )
    outside = _calculate_outside_ventilation_air_rate_change(
        infiltration_rate[
            ventilation_method == "positive_input_ventilation_from_outside"
        ]
    )
    mechanical = _calculate_mech_ventilation_air_rate_change(
        infiltration_rate[
            ventilation_method == "mechanical_ventilation_no_heat_recovery"
        ]
    )
    heat_recovery = _calculate_heat_recovery_ventilation_air_rate_change(
        infiltration_rate[ventilation_method == "mechanical_ventilation_heat_recovery"],
        heat_exchanger_efficiency[
            ventilation_method == "mechanical_ventilation_heat_recovery"
        ],
    )
    return pd.concat([natural, loft, outside, mechanical, heat_recovery]).sort_index()


def calculate_ventilation_heat_loss_coefficient(
    building_volume: pd.Series,
    effective_air_rate_change: pd.Series,
    ventilation_heat_loss_constant: float = 0.33,  # SEAI, DEAP 4.2.0
) -> pd.Series:
    return building_volume * ventilation_heat_loss_constant * effective_air_rate_change
