import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from rcbm import vent


def test_calculate_infiltration_rate_due_to_openings():
    """Output is equivalent to DEAP 4.2.0 example A"""
    building_volume = pd.Series([321, 0, 100, 200])
    no_chimneys = pd.Series([0, 0, 0, 1])
    no_open_flues = pd.Series([0, 0, 0, 1])
    no_fans = pd.Series([1, 0, 0, 1])
    no_room_heaters = pd.Series([0, 0, 0, 1])
    is_draught_lobby = pd.Series(["NO", "NO", "YES", "NO"])
    expected_output = pd.Series([0.08, 0, 0, 0.6])

    output = vent._calculate_infiltration_rate_due_to_openings(
        building_volume=building_volume,
        no_chimneys=no_chimneys,
        no_open_flues=no_open_flues,
        no_fans=no_fans,
        no_room_heaters=no_room_heaters,
        is_draught_lobby=is_draught_lobby,
        draught_lobby_boolean=vent.YES_NO,
    )

    assert_series_equal(output.round(2), expected_output)


def test_calculate_infiltration_rate_due_to_structure():
    """Output is equivalent to DEAP 4.2.0 example A"""
    is_permeability_tested = pd.Series(["YES", "NO", "NO"])
    permeability_test_result = pd.Series([0.15, np.nan, np.nan])
    no_storeys = pd.Series([np.nan, 2, 1])
    percentage_draught_stripped = pd.Series([np.nan, 100, 75])
    is_floor_suspended = pd.Series(
        [np.nan, "No                            ", "Yes (Unsealed)                "]
    )
    structure_type = pd.Series(
        [np.nan, "Masonry                       ", "Timber or Steel Frame         "]
    )
    expected_output = pd.Series([0.15, 0.5, 0.55])

    output = vent._calculate_infiltration_rate_due_to_structure(
        is_permeability_tested=is_permeability_tested,
        permeability_test_result=permeability_test_result,
        no_storeys=no_storeys,
        percentage_draught_stripped=percentage_draught_stripped,
        is_floor_suspended=is_floor_suspended,
        structure_type=structure_type,
        suspended_floor_types=vent.SUSPENDED_FLOOR_TYPES,
        structure_types=vent.STRUCTURE_TYPES,
        permeability_test_boolean=vent.YES_NO,
    )

    assert_series_equal(output.round(2), expected_output)


def test_calculate_infiltration_rate(monkeypatch):
    """Output is equivalent to DEAP 4.2.0 example A"""
    no_sides_sheltered = pd.Series([2, 2])

    def _mock_calculate_infiltration_rate_due_to_openings(*args, **kwargs):
        return pd.Series([0.08, 0.08])

    def _mock_calculate_infiltration_rate_due_to_structure(*args, **kwargs):
        return pd.Series([0.15, 0.5])

    monkeypatch.setattr(
        vent,
        "_calculate_infiltration_rate_due_to_openings",
        _mock_calculate_infiltration_rate_due_to_openings,
    )
    monkeypatch.setattr(
        vent,
        "_calculate_infiltration_rate_due_to_structure",
        _mock_calculate_infiltration_rate_due_to_structure,
    )
    expected_output = pd.Series([0.2, 0.49])

    output = vent.calculate_infiltration_rate(
        no_sides_sheltered=no_sides_sheltered,
        building_volume=None,
        no_chimneys=None,
        no_open_flues=None,
        no_fans=None,
        no_room_heaters=None,
        is_draught_lobby=None,
        is_permeability_tested=None,
        permeability_test_result=None,
        no_storeys=None,
        percentage_draught_stripped=None,
        is_floor_suspended=None,
        structure_type=None,
        draught_lobby_boolean=None,
        suspended_floor_types=None,
        structure_types=None,
        permeability_test_boolean=None,
    )

    assert_series_equal(output.round(2), expected_output)


def test_calculate_effective_air_rate_change():
    """Output is equivalent to DEAP 4.2.0 example A"""
    n_methods = 6
    ventilation_method = pd.Series(
        [
            "Natural vent.",
            "Pos input vent.- loft",
            "Pos input vent.- outside",
            "Whole house extract vent.",
            "Bal.whole mech.vent no heat re",
            "Bal.whole mech.vent heat recvr",
        ]
    )
    building_volume = pd.Series([321] * n_methods)
    infiltration_rate = pd.Series([0.2] * n_methods)
    heat_exchanger_efficiency = pd.Series([0] * n_methods)
    expected_output = pd.Series([0.52, 0.58, 0.5, 0.5, 0.7, 0.7])

    output = vent.calculate_effective_air_rate_change(
        ventilation_method=ventilation_method,
        building_volume=building_volume,
        infiltration_rate=infiltration_rate,
        heat_exchanger_efficiency=heat_exchanger_efficiency,
        ventilation_method_names=vent.VENTILATION_METHODS,
    )

    assert_series_equal(output.round(2), expected_output)


def test_calculate_ventilation_heat_loss(monkeypatch):
    """Output is equivalent to DEAP 4.2.0 example A"""
    building_volume = pd.Series([321])
    effective_air_rate_change = pd.Series([0.5])
    ventilation_heat_loss_constant = 0.33
    expected_output = pd.Series([53], dtype="float64")

    output = vent.calculate_ventilation_heat_loss(
        building_volume=building_volume,
        effective_air_rate_change=effective_air_rate_change,
        ventilation_heat_loss_constant=ventilation_heat_loss_constant,
    )

    assert_series_equal(output.round(), expected_output)
