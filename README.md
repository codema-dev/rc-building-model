# rc-building-model

[![PyPI version shields.io](https://img.shields.io/pypi/v/rcbm.svg)](https://pypi.python.org/pypi/rcbm/)
[![PyPI license](https://img.shields.io/pypi/l/rcbm.svg)](https://pypi.python.org/pypi/rcbm/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rcbm.svg)](https://pypi.python.org/pypi/rcbm/)

A Resistance Capacitance (RC) Model for the Simulation of Building Stock Energy Usage.

Adapted from SEAI's Dwelling Energy Assessment Procedure (DEAP) which is based on both the European Standard IS EN 13790: 2004 and the UK’s Standard Assessment Procedure (SAP). 

> Inspired by [RC_BuildingSimulator](https://github.com/architecture-building-systems/RC_BuildingSimulator) and [CityEnergyAnalyst](https://github.com/architecture-building-systems/CityEnergyAnalyst)

## setup

```bash
pip install codema-dev-tasks
```

## to do

- [x] Annual fabric heat loss coefficient 
- [x] Annual ventilation heat loss coefficient
- [x] Heat Loss Indicator (HLI) - used in Ireland to evaluate heat pump viability
- [x] Annual heat loss based on average monthly temperatures - defaults to DEAP values
- [ ] Annual heat loss based on hourly temperatures - need a simple API for hourly temperature data
- [ ] Impact of fabric upgrade on BER Rating
- [ ] Impact of ventilation upgrade on BER Rating
- [ ] **Getting Started** documentation
