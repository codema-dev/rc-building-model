import pandas as pd


def calculate_fabric_heat_loss(
    roof_area,
    roof_uvalue,
    wall_area,
    wall_uvalue,
    floor_area,
    floor_uvalue,
    window_area,
    window_uvalue,
    door_area,
    door_uvalue,
    thermal_bridging_factor=0.05,
):
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


def _raise_for_zero_floor_areas(floor_areas):
    is_zero_floor_area = (floor_areas == 0) | (floor_areas.isnull())
    if is_zero_floor_area.any():
        raise ZeroDivisionError(
            "Cannot divide heat_loss_coefficient by zero"
            " - please remove any zero floor areas!"
        )


def calculate_heat_loss_parameter(
    fabric_heat_loss: pd.Series,
    ventilation_heat_loss: pd.Series,
    total_floor_area: pd.Series,
) -> pd.DataFrame:
    _raise_for_zero_floor_areas(total_floor_area)
    heat_loss_coefficient = fabric_heat_loss + ventilation_heat_loss
    return heat_loss_coefficient / total_floor_area
