def calculate_building_volume(
    ground_floor_area=None,
    ground_floor_height=None,
    first_floor_area=None,
    first_floor_height=None,
    second_floor_area=None,
    second_floor_height=None,
    third_floor_area=None,
    third_floor_height=None,
    no_of_storeys=None,
    floor_area=None,
    assumed_floor_height=None,
):
    if ground_floor_area is not None:
        building_volume = (
            ground_floor_area * ground_floor_height
            + first_floor_area.fillna(0) * first_floor_height.fillna(0)
            + second_floor_area.fillna(0) * second_floor_height.fillna(0)
            + third_floor_area.fillna(0) * third_floor_height.fillna(0)
        )
    elif no_of_storeys is not None:
        building_volume = floor_area * no_of_storeys * assumed_floor_height
    else:
        raise ValueError(
            "Must specify either 'no_of_storeys'"
            "or floor areas & heights to calculate building volume!"
        )

    return building_volume