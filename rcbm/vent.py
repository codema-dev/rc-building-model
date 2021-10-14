import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
import pandera as pa
from pandera.typing import Series

STRUCTURE_TYPES = [
    "unknown",
    "masonry",
    "timber_or_steel",
    "concrete",
]

FLOOR_TYPES = ["none", "sealed", "unsealed"]

VENTILATION_METHODS = [
    "positive_input_ventilation_from_loft",
    "natural_ventilation",
    "mechanical_ventilation_no_heat_recovery",
    "mechanical_ventilation_heat_recovery",
    "positive_input_ventilation_from_outside",
]


is_number = pa.Check(is_numeric_dtype, name="is_number")


def schema(name: str) -> pa.SeriesSchema:
    _schemas = {
        "no_openings": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "building_volume": pa.SeriesSchema(
            checks=[is_number, pa.Check.not_equal_to(0)],
            nullable=False,
        ),
        "infiltration_rate_due_to_opening": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "is_draught_lobby": pa.SeriesSchema(
            bool,
            nullable=False,
        ),
        "infiltration_rate_due_to_draught_lobby": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "no_storeys": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "infiltration_rate_due_to_height": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "structure_type": pa.SeriesSchema(
            str,
            checks=pa.Check.isin(STRUCTURE_TYPES),
            nullable=False,
        ),
        "infiltration_rate_due_to_structure_type": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "is_floor_suspended": pa.SeriesSchema(
            str,
            checks=pa.Check.isin(FLOOR_TYPES),
            nullable=False,
        ),
        "infiltration_rate_due_to_suspended_floor": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "percentage_draught_stripped": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "infiltration_rate_due_to_draught": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "permeability_test_result": pa.SeriesSchema(
            checks=is_number,
            nullable=True,
        ),
        "infiltration_rate_due_to_structure": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "no_sides_sheltered": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "ventilation_method": pa.SeriesSchema(
            str,
            checks=pa.Check.isin(VENTILATION_METHODS),
            nullable=False,
        ),
        "infiltration_rate": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
        "heat_exchanger_efficiency": pa.SeriesSchema(
            checks=is_number,
            nullable=True,
        ),
        "effective_air_rate_change": pa.SeriesSchema(
            checks=is_number,
            nullable=False,
        ),
    }
    return _schemas[name]


@pa.check_io(
    no_openings=schema("no_openings"),
    building_volume=schema("building_volume"),
    out=schema("infiltration_rate_due_to_opening"),
)
def calculate_infiltration_rate_due_to_opening(
    no_openings: Series, building_volume: Series, ventilation_rate: int
) -> Series:
    return no_openings * ventilation_rate / building_volume


def calculate_infiltration_rate_due_to_chimneys(
    no_chimneys: Series, building_volume: Series, ventilation_rate: int = 40
) -> Series:
    return calculate_infiltration_rate_due_to_opening(
        no_chimneys, building_volume, ventilation_rate
    )


def calculate_infiltration_rate_due_to_open_flues(
    no_chimneys: Series, building_volume: Series, ventilation_rate: int = 20
) -> Series:
    return calculate_infiltration_rate_due_to_opening(
        no_chimneys, building_volume, ventilation_rate
    )


def calculate_infiltration_rate_due_to_fans(
    no_chimneys: Series, building_volume: Series, ventilation_rate: int = 10
) -> Series:
    return calculate_infiltration_rate_due_to_opening(
        no_chimneys, building_volume, ventilation_rate
    )


def calculate_infiltration_rate_due_to_room_heaters(
    no_chimneys: Series, building_volume: Series, ventilation_rate: int = 40
) -> Series:
    return calculate_infiltration_rate_due_to_opening(
        no_chimneys, building_volume, ventilation_rate
    )


@pa.check_io(
    is_draught_lobby=schema("is_draught_lobby"),
    out=schema("infiltration_rate_due_to_draught_lobby"),
)
def calculate_infiltration_rate_due_to_draught_lobby(
    is_draught_lobby: Series,
) -> Series:
    return is_draught_lobby.map({True: 0, False: 0.05})


def calculate_infiltration_rate_due_to_openings(
    building_volume: Series,
    no_chimneys: Series,
    no_open_flues: Series,
    no_fans: Series,
    no_room_heaters: Series,
    is_draught_lobby: Series,
) -> Series:
    return (
        calculate_infiltration_rate_due_to_chimneys(no_chimneys, building_volume)
        + calculate_infiltration_rate_due_to_open_flues(no_open_flues, building_volume)
        + calculate_infiltration_rate_due_to_fans(no_fans, building_volume)
        + calculate_infiltration_rate_due_to_room_heaters(
            no_room_heaters, building_volume
        )
        + calculate_infiltration_rate_due_to_draught_lobby(is_draught_lobby)
    )


@pa.check_io(
    no_storeys=schema("no_storeys"),
    out=schema("infiltration_rate_due_to_height"),
)
def calculate_infiltration_rate_due_to_height(no_storeys: Series) -> Series:
    return (no_storeys - 1) * 0.1


@pa.check_io(
    structure_type=schema("structure_type"),
    out=schema("infiltration_rate_due_to_structure_type"),
)
def calculate_infiltration_rate_due_to_structure_type(
    structure_type: Series, unknown_structure_infiltration_rate: float = 0.35
) -> Series:
    infiltration_rate_map = {
        "unknown": unknown_structure_infiltration_rate,
        "masonry": 0.35,
        "timber_or_steel": 0.25,
        "concrete": 0,
    }
    return structure_type.map(infiltration_rate_map)


@pa.check_io(
    is_floor_suspended=schema("is_floor_suspended"),
    out=schema("infiltration_rate_due_to_suspended_floor"),
)
def calculate_infiltration_rate_due_to_suspended_floor(
    is_floor_suspended: Series,
) -> Series:
    infiltration_rate_map = {"none": 0, "sealed": 0.1, "unsealed": 0.2}
    return is_floor_suspended.map(infiltration_rate_map)


@pa.check_io(
    percentage_draught_stripped=schema("percentage_draught_stripped"),
    out=schema("infiltration_rate_due_to_draught"),
)
def calculate_infiltration_rate_due_to_draught(
    percentage_draught_stripped: Series,
) -> Series:
    return 0.25 - (0.2 * (percentage_draught_stripped / 100))


@pa.check_io(
    permeability_test_result=schema("permeability_test_result"),
    out=schema("infiltration_rate_due_to_structure"),
)
def calculate_infiltration_rate_due_to_structure(
    permeability_test_result: Series,
    no_storeys: Series,
    percentage_draught_stripped: Series,
    is_floor_suspended: Series,
    structure_type: Series,
) -> Series:
    theoretical_infiltration_rate = (
        calculate_infiltration_rate_due_to_height(no_storeys)
        + calculate_infiltration_rate_due_to_structure_type(structure_type)
        + calculate_infiltration_rate_due_to_suspended_floor(is_floor_suspended)
        + calculate_infiltration_rate_due_to_draught(percentage_draught_stripped)
    )
    infiltration_rate_is_available = permeability_test_result.notna()
    return pd.Series(
        np.where(
            infiltration_rate_is_available,
            permeability_test_result,
            theoretical_infiltration_rate,
        )
    )


@pa.check_io(
    no_sides_sheltered=schema("no_sides_sheltered"),
)
def calculate_infiltration_rate_adjustment_factor(
    no_sides_sheltered: Series,
) -> Series:
    return 1 - no_sides_sheltered * 0.075


def calculate_infiltration_rate(
    no_sides_sheltered: Series,
    building_volume: Series,
    no_chimneys: Series,
    no_open_flues: Series,
    no_fans: Series,
    no_room_heaters: Series,
    is_draught_lobby: Series,
    permeability_test_result: Series,
    no_storeys: Series,
    percentage_draught_stripped: Series,
    is_floor_suspended: Series,
    structure_type: Series,
) -> Series:
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
    return infiltration_rate * calculate_infiltration_rate_adjustment_factor(
        no_sides_sheltered
    )


def _calculate_natural_ventilation_air_rate_change(
    infiltration_rate: Series,
) -> Series:
    return infiltration_rate.where(
        infiltration_rate > 1, 0.5 + (infiltration_rate ** 2) * 0.5
    )


def _calculate_loft_ventilation_air_rate_change(
    infiltration_rate: Series, building_volume: Series
) -> Series:
    return (
        _calculate_natural_ventilation_air_rate_change(infiltration_rate)
        + 20 / building_volume
    )


def _calculate_outside_ventilation_air_rate_change(
    infiltration_rate: Series,
) -> Series:
    return np.maximum([0.5] * len(infiltration_rate), infiltration_rate + 0.25)


def _calculate_mech_ventilation_air_rate_change(
    infiltration_rate: Series,
) -> Series:
    return infiltration_rate + 0.5


def _calculate_heat_recovery_ventilation_air_rate_change(
    infiltration_rate: Series,
    heat_exchanger_efficiency: Series,
) -> Series:
    return infiltration_rate + 0.5 * (1 - heat_exchanger_efficiency / 100)


@pa.check_io(
    ventilation_method=schema("ventilation_method"),
    building_volume=schema("building_volume"),
    infiltration_rate=schema("infiltration_rate"),
    heat_exchanger_efficiency=schema("heat_exchanger_efficiency"),
    out=schema("effective_air_rate_change"),
)
def calculate_effective_air_rate_change(
    ventilation_method: Series,
    building_volume: Series,
    infiltration_rate: Series,
    heat_exchanger_efficiency: Series,
) -> Series:
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
    building_volume: Series,
    effective_air_rate_change: Series,
    ventilation_heat_loss_constant: float = 0.33,  # SEAI, DEAP 4.2.0
) -> Series:
    return building_volume * ventilation_heat_loss_constant * effective_air_rate_change
