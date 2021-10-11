import numpy as np
import pandas as pd


def _calculate_heat_loss_kwh(heat_loss_coefficient, delta_t, hours):
    # NOTE: all arrays must be the same length!
    broadcasted_delta_t = np.tile(delta_t, len(heat_loss_coefficient))
    broadcasted_hours = np.tile(hours, len(heat_loss_coefficient))
    broadcasted_heat_loss_coefficient = np.repeat(heat_loss_coefficient, len(hours))
    w_to_kwh = 1 / 1000
    return (
        broadcasted_heat_loss_coefficient
        * broadcasted_delta_t
        * broadcasted_hours
        * w_to_kwh
    )


def _calculate_heat_loss_per_year_on_monthly_averages(
    heat_loss_coefficient,
    internal_temperatures=None,
    external_temperatures=None,
):
    # heating_months are ["jan", "feb", "mar", "apr", "may", "oct", "nov", "dec"]
    heating_hours = np.array(
        [d * 24 for d in (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)]
    )
    heating_hours[5:9] = 0

    if internal_temperatures is None:
        internal_temperatures = np.array(
            [
                17.72,
                17.73,
                17.85,
                17.95,
                18.15,
                18.35,
                18.50,
                18.48,
                18.33,
                18.11,
                17.88,
                17.77,
            ]
        )

    if external_temperatures is None:
        external_temperatures = np.array(
            [
                5.3,
                5.5,
                7.0,
                8.3,
                11.0,
                13.5,
                15.5,
                15.2,
                13.3,
                10.4,
                7.5,
                6.0,
            ]
        )
    delta_t = internal_temperatures - external_temperatures

    heat_loss_kwh = _calculate_heat_loss_kwh(
        heat_loss_coefficient=heat_loss_coefficient,
        delta_t=delta_t,
        hours=heating_hours,
    )
    return heat_loss_kwh.sum(level=0).round()


def calculate_heat_loss_per_year(
    heat_loss_coefficient, internal_temperatures, external_temperatures, how="monthly"
):
    _function_map = {"monthly": _calculate_heat_loss_per_year_on_monthly_averages}
    _calc = _function_map[how]
    return _calc(heat_loss_coefficient, internal_temperatures, external_temperatures)
