"""
Unit tests for pseudothickness_from_ds().

All tests are self-contained: no file I/O, no full Polaris step framework.
A minimal ConfigParser and xarray.Dataset are constructed in each test.
"""

from configparser import ConfigParser

import numpy as np
import pytest
import xarray as xr

from polaris.ocean.vertical.diagnostics import pseudothickness_from_ds


def _make_config(eos_type='teos-10'):
    config = ConfigParser()
    config.add_section('ocean')
    config.set('ocean', 'eos_type', eos_type)
    config.add_section('vertical_grid')
    config.set('vertical_grid', 'pseudothickness_iter_count', '10')
    return config


def _make_ds(surface_pressure=None):
    data_vars: dict = dict(
        restingThickness=(('Time', 'nCells', 'nVertLevels'), [[[10.0, 10.0]]]),
        temperature=(('Time', 'nCells', 'nVertLevels'), [[[3.0, 3.0]]]),
        salinity=(('Time', 'nCells', 'nVertLevels'), [[[35.0, 35.0]]]),
    )
    if surface_pressure is not None:
        data_vars['SurfacePressure'] = ('nCells', [surface_pressure])
    return xr.Dataset(data_vars=data_vars)


def test_raises_without_a_surface_pressure():
    """Rather than invent a surface pressure, which cannot be right for both
    callers, the missing field is reported."""
    with pytest.raises(ValueError, match='requires SurfacePressure'):
        pseudothickness_from_ds(
            _make_ds(),
            config=_make_config(),
            src_var_name='restingThickness',
        )


def test_no_surface_pressure_needed_when_given_explicitly():
    pseudothickness, _ = pseudothickness_from_ds(
        _make_ds(),
        config=_make_config(),
        src_var_name='restingThickness',
        surf_pressure=0.0,
    )
    assert pseudothickness is not None


def test_explicit_surface_pressure_overrides_the_dataset():
    """Resting thicknesses are defined at zero surface pressure, so they must
    not depend on a surface pressure the dataset happens to carry."""
    config = _make_config()
    with_pressure, _ = pseudothickness_from_ds(
        _make_ds(surface_pressure=101325.0),
        config=config,
        src_var_name='restingThickness',
        surf_pressure=0.0,
    )
    without_pressure, _ = pseudothickness_from_ds(
        _make_ds(),
        config=config,
        src_var_name='restingThickness',
        surf_pressure=0.0,
    )
    np.testing.assert_allclose(with_pressure.values, without_pressure.values)


def test_dataset_surface_pressure_is_used_by_default():
    """A surface pressure in the dataset alters the result through the
    pressure dependence of the equation of state."""
    config = _make_config()
    at_zero, _ = pseudothickness_from_ds(
        _make_ds(surface_pressure=101325.0),
        config=config,
        src_var_name='restingThickness',
        surf_pressure=0.0,
    )
    from_ds, _ = pseudothickness_from_ds(
        _make_ds(surface_pressure=101325.0),
        config=config,
        src_var_name='restingThickness',
    )
    assert not np.allclose(at_zero.values, from_ds.values)
