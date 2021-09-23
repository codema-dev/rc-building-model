import pandas as pd


def calculate_fabric_component_heat_loss_coefficient(
    component_area: pd.Series,
    component_uvalue: pd.Series,
    thermal_bridging_factor: float = 0.05,
) -> pd.Series:
    heat_loss_via_plane_element = component_area * component_uvalue
    thermal_bridging = component_area * thermal_bridging_factor
    return thermal_bridging + heat_loss_via_plane_element


def calculate_fabric_heat_loss_coefficient(
    roof_area: pd.Series,
    roof_uvalue: pd.Series,
    wall_area: pd.Series,
    wall_uvalue: pd.Series,
    floor_area: pd.Series,
    floor_uvalue: pd.Series,
    window_area: pd.Series,
    window_uvalue: pd.Series,
    door_area: pd.Series,
    door_uvalue: pd.Series,
    thermal_bridging_factor: float = 0.05,
) -> pd.Series:
    plane_elements_area = roof_area + floor_area + door_area + wall_area + window_area
    thermal_bridging = thermal_bridging_factor * plane_elements_area
    heat_loss_via_plane_elements = (
        wall_area * wall_uvalue
        + roof_area * roof_uvalue
        + floor_area * floor_uvalue
        + window_area * window_uvalue
        + door_area * door_uvalue
    )

    return thermal_bridging + heat_loss_via_plane_elements


def _raise_for_zero_floor_areas(floor_areas: pd.Series) -> None:
    is_zero_floor_area = (floor_areas == 0) | (floor_areas.isnull())
    if is_zero_floor_area.any():
        raise ZeroDivisionError(
            "Cannot divide heat_loss_coefficient by zero"
            " - please remove any zero floor areas!"
        )


def calculate_heat_loss_parameter(
    fabric_heat_loss_coefficient: pd.Series,
    ventilation_heat_loss_coefficient: pd.Series,
    total_floor_area: pd.Series,
) -> pd.Series:
    _raise_for_zero_floor_areas(total_floor_area)
    heat_loss_coefficient = (
        fabric_heat_loss_coefficient + ventilation_heat_loss_coefficient
    )
    return heat_loss_coefficient / total_floor_area
