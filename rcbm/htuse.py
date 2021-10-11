import numpy as np
import pandas as pd


def _calculate_heat_loss_kwh(heat_loss_coefficient, delta_t, hours):
    # NOTE: all arrays must be the same length!
    broadcasted_delta_t = np.tile(delta_t, len(heat_loss_coefficient))
    broadcasted_hours = np.tile(hours, len(heat_loss_coefficient))
    broadcasted_heat_loss_coefficient = np.repeat(heat_loss_coefficient, len(hours))
    heat_loss_w = broadcasted_heat_loss_coefficient * broadcasted_delta_t
    w_to_kwh = 1 / 1000
    return heat_loss_w * w_to_kwh * broadcasted_hours


def _calculate_heat_loss_per_year_on_monthly_averages(
    heat_loss_coefficient,
    internal_temperatures=None,
    external_temperatures=None,
):
    months = [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ]
    heating_months = ["jan", "feb", "mar", "apr", "may", "oct", "nov", "dec"]
    hours = pd.Series(
        [d * 24 for d in [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]],
        index=[
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ],
    )

    if internal_temperatures is None:
        internal_temperatures = pd.Series(
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
            ],
            index=[
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
            ],
        )

    if external_temperatures is None:
        external_temperatures = pd.Series(
            [5.3, 5.5, 7.0, 8.3, 11.0, 13.5, 15.5, 15.2, 13.3, 10.4, 7.5, 6.0],
            index=[
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
            ],
        )

    delta_t = internal_temperatures - external_temperatures

    heat_loss_kwh = _calculate_heat_loss_kwh(
        heat_loss_coefficient=heat_loss_coefficient,
        delta_t=delta_t,
        hours=hours,
    )
    heat_loss_kwh.index = months * len(heat_loss_coefficient)
    heat_loss_kwh_for_heating_months = heat_loss_kwh.loc[heating_months]
    new_index = (
        heat_loss_kwh_for_heating_months.reset_index().groupby("index").cumcount()
    )
    heat_loss_kwh_for_heating_months.index = new_index
    return heat_loss_kwh_for_heating_months.sum(level=0).round()


def calculate_heat_loss_per_year(
    heat_loss_coefficient, internal_temperatures, external_temperatures, how="monthly"
):
    _function_map = {"monthly": _calculate_heat_loss_per_year_on_monthly_averages}
    _calc = _function_map[how]
    return _calc(heat_loss_coefficient, internal_temperatures, external_temperatures)
