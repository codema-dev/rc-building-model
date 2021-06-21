import numpy as np
import pandas as pd


ADJUSTED_MONTHLY_INTERNAL_TEMPERATURE = pd.Series(
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

MEAN_MONTHLY_EXTERNAL_TEMPERATURE = pd.Series(
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

DELTA_T_BY_MONTH = (
    ADJUSTED_MONTHLY_INTERNAL_TEMPERATURE - MEAN_MONTHLY_EXTERNAL_TEMPERATURE
)

HOURS_PER_MONTH = pd.Series(
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


def _calculate_heat_loss_kwh(heat_loss_coefficient, delta_t, hours):
    # NOTE: all arrays must be the same length!
    broadcasted_delta_t = np.tile(delta_t, len(heat_loss_coefficient))
    broadcasted_hours_per_month = np.tile(hours, len(heat_loss_coefficient))
    broadcasted_heat_loss_coefficient = np.repeat(
        heat_loss_coefficient, len(hours)
    ).to_numpy()

    heat_loss_w = broadcasted_heat_loss_coefficient * broadcasted_delta_t
    w_to_kwh = 1 / 1000
    return heat_loss_w * w_to_kwh * broadcasted_hours_per_month


def calculate_heat_loss_per_year(
    heat_loss_coefficient,
    delta_t=DELTA_T_BY_MONTH,
    hours=HOURS_PER_MONTH,
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

    heat_loss_kwh = _calculate_heat_loss_kwh(
        heat_loss_coefficient=heat_loss_coefficient,
        delta_t=delta_t,
        hours=hours,
    )

    heat_loss_kwh_for_heating_months = pd.Series(
        heat_loss_kwh, index=months * len(heat_loss_coefficient)
    ).loc[heating_months]
    new_index = (
        heat_loss_kwh_for_heating_months.reset_index().groupby("index").cumcount()
    )
    heat_loss_kwh_for_heating_months.index = new_index
    return heat_loss_kwh_for_heating_months.sum(level=0).round()
