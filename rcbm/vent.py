"""
Replicate DEAP 4.2.2 Vent Excel calculations

Assumptions:

Structure Types
- Unknown are Masonry as 82/96 buildings are masonry
- Concrete has an infiltration rate of 0
"""
import numpy as np
import pandas as pd


VENTILATION_METHODS = {
    "Natural vent.": "natural",
    "Bal.whole mech.vent heat recvr": "mech",
    "Whole house extract vent.": "outside",
    "Pos input vent.- loft": "loft",
    "Pos input vent.- outside": "outside",
    "Bal.whole mech.vent no heat re": "heat_recovery",
}

SUSPENDED_FLOOR_TYPES = {
    "No                            ": "no",
    "Yes (Unsealed)                ": "unsealed",
    "Yes (Sealed)                  ": "sealed",
}

STRUCTURE_TYPES = {
    "Masonry                       ": "masonry",
    "Please select                 ": np.nan,
    "Timber or Steel Frame         ": "timber_or_steel",
    "Insulated Conctete Form       ": "concrete",
}

YES_NO = {"YES": True, "NO": False}


def _calculate_infiltration_rate_due_to_openings(
    building_volume,
    no_chimneys,
    no_open_flues,
    no_fans,
    no_room_heaters,
    is_draught_lobby,
    draught_lobby_boolean,
):
    infiltration_rate_due_to_openings = (
        no_chimneys * 40 + no_open_flues * 20 + no_fans * 10 + no_room_heaters * 40
    )
    is_building_empty = building_volume == 0
    infiltration_rate_due_to_draught_lobby = is_draught_lobby.map(
        draught_lobby_boolean
    ).map({True: 0, False: 0.05})
    return building_volume.where(
        is_building_empty,
        infiltration_rate_due_to_openings / building_volume
        + infiltration_rate_due_to_draught_lobby,
    )


def _calculate_infiltration_rate_due_to_structure(
    is_permeability_tested,
    permeability_test_result,
    no_storeys,
    percentage_draught_stripped,
    is_floor_suspended,
    structure_type,
    suspended_floor_types=SUSPENDED_FLOOR_TYPES,
    structure_types=STRUCTURE_TYPES,
    permeability_test_boolean=YES_NO,
):
    infiltration_rate_due_to_height = (no_storeys - 1) * 0.1
    infiltration_rate_due_to_structure_type = (
        structure_type.map(structure_types)
        .map({"masonry": 0.35, "timber_or_steel": 0.25, "concrete": 0})  # ASSUMPTION:
        .fillna(0.35)  # ASSUMPTION
    )
    infiltration_rate_due_to_suspended_floor = (
        is_floor_suspended.map(suspended_floor_types)
        .map({"no": 0, "sealed": 0.1, "unsealed": 0.2})
        .fillna(0)
    )
    infiltration_rate_due_to_draught = 0.25 - (
        0.2 * (percentage_draught_stripped / 100)
    )
    return permeability_test_result.where(
        is_permeability_tested.map(permeability_test_boolean),
        infiltration_rate_due_to_height
        + infiltration_rate_due_to_structure_type
        + infiltration_rate_due_to_suspended_floor
        + infiltration_rate_due_to_draught,
    )


def calculate_infiltration_rate(
    no_sides_sheltered,
    building_volume,
    no_chimneys,
    no_open_flues,
    no_fans,
    no_room_heaters,
    is_draught_lobby,
    is_permeability_tested,
    permeability_test_result,
    no_storeys,
    percentage_draught_stripped,
    is_floor_suspended,
    structure_type,
    draught_lobby_boolean=YES_NO,
    suspended_floor_types=SUSPENDED_FLOOR_TYPES,
    structure_types=STRUCTURE_TYPES,
    permeability_test_boolean=YES_NO,
):
    infiltration_rate_due_to_openings = _calculate_infiltration_rate_due_to_openings(
        building_volume=building_volume,
        no_chimneys=no_chimneys,
        no_open_flues=no_open_flues,
        no_fans=no_fans,
        no_room_heaters=no_room_heaters,
        is_draught_lobby=is_draught_lobby,
        draught_lobby_boolean=draught_lobby_boolean,
    )

    infiltration_rate_due_to_structure = _calculate_infiltration_rate_due_to_structure(
        is_permeability_tested=is_permeability_tested,
        permeability_test_result=permeability_test_result,
        no_storeys=no_storeys,
        percentage_draught_stripped=percentage_draught_stripped,
        is_floor_suspended=is_floor_suspended,
        structure_type=structure_type,
        suspended_floor_types=suspended_floor_types,
        structure_types=structure_types,
        permeability_test_boolean=permeability_test_boolean,
    )

    infiltration_rate = (
        infiltration_rate_due_to_openings + infiltration_rate_due_to_structure
    )
    return infiltration_rate * (1 - no_sides_sheltered * 0.075)


def _calculate_natural_ventilation_air_rate_change(infiltration_rate):
    return infiltration_rate.where(
        infiltration_rate > 1, 0.5 + (infiltration_rate ** 2) * 0.5
    )


def _calculate_loft_ventilation_air_rate_change(infiltration_rate, building_volume):
    return (
        _calculate_natural_ventilation_air_rate_change(infiltration_rate)
        + 20 / building_volume
    )


def _calculate_outside_ventilation_air_rate_change(infiltration_rate):
    return np.maximum([0.5] * len(infiltration_rate), infiltration_rate + 0.25)


def _calculate_mech_ventilation_air_rate_change(infiltration_rate):
    return infiltration_rate + 0.5


def _calculate_heat_recovery_ventilation_air_rate_change(
    infiltration_rate,
    heat_exchanger_efficiency,
):
    return infiltration_rate + 0.5 * (1 - heat_exchanger_efficiency / 100)


def calculate_effective_air_rate_change(
    ventilation_method,
    building_volume,
    infiltration_rate,
    heat_exchanger_efficiency,
    ventilation_method_names=VENTILATION_METHODS,
):
    methods = ventilation_method.map(ventilation_method_names)
    natural = _calculate_natural_ventilation_air_rate_change(
        infiltration_rate[methods == "natural"]
    )
    loft = _calculate_loft_ventilation_air_rate_change(
        infiltration_rate[methods == "loft"], building_volume[methods == "loft"]
    )
    outside = _calculate_outside_ventilation_air_rate_change(
        infiltration_rate[methods == "outside"]
    )
    mech = _calculate_mech_ventilation_air_rate_change(
        infiltration_rate[methods == "mech"]
    )
    heat_recovery = _calculate_heat_recovery_ventilation_air_rate_change(
        infiltration_rate[methods == "heat_recovery"],
        heat_exchanger_efficiency[methods == "heat_recovery"],
    )
    return pd.concat([natural, loft, outside, mech, heat_recovery]).sort_index()


def calculate_ventilation_heat_loss(
    building_volume,
    effective_air_rate_change,
    ventilation_heat_loss_constant=0.33,  # SEAI, DEAP 4.2.0
):
    return building_volume * ventilation_heat_loss_constant * effective_air_rate_change
