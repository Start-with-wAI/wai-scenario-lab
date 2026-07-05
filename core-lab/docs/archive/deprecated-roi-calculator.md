# Archived Deprecated ROI Calculator Test Reference

The Model Context Protocol (MCP) server `roi_calculator_server.py` and its tests have been deprecated and removed from the active runtime and test suite to enforce wAI's non-financial calculation boundary.

The project now uses strictly time-loss/observation-based metrics and completely avoids calculating monetary opportunity costs, dollar savings, or marketing equity.

Below is the archived legacy test code from `test_roi_calculator.py` for historical reference:

```python
import pytest
from mcp_server.roi_calculator_server import (
    calculate_task_tax,
    calculate_brain_fog_impact,
    calculate_content_factory_value,
)

def test_calculate_task_tax() -> None:
    # F = 1.0, M = 30.0, rate = 50.0
    # H_annual = (1 * 52 * 30) / 60 = 26.0
    # annual_cost = 26 * 50 = 1300
    res = calculate_task_tax(1.0, 30.0, 50.0)
    assert res["annual_hours_lost"] == 26.0
    assert res["one_year_opportunity_cost"] == 1300.0
    assert res["three_year_opportunity_cost"] == 3900.0
    assert res["five_year_opportunity_cost"] == 6500.0

def test_calculate_brain_fog_impact() -> None:
    # captured = 5, lost = 10, reconstruct = 15.0
    # total = 15, capture_yield = (5 / 15) * 100 = 33.33
    # H_wasted = (10 * 52 * 15.0) / 60 = 130.0
    res = calculate_brain_fog_impact(5, 10, 15.0)
    assert res["capture_yield"] == 33.33
    assert res["annual_reconstruction_hours_wasted"] == 130.0

def test_calculate_brain_fog_impact_zero() -> None:
    # Test division by zero handling
    res = calculate_brain_fog_impact(0, 0, 15.0)
    assert res["capture_yield"] == 0.0
    assert res["annual_reconstruction_hours_wasted"] == 0.0

def test_calculate_content_factory_value() -> None:
    # posts = 2.0, asset_type = "Proposal Templates" (value = 300)
    # weekly_equity = 2 * 300 = 600
    # annual_equity = 600 * 52 = 31200
    res = calculate_content_factory_value(2.0, "Proposal Templates")
    assert res["weekly_marketing_equity"] == 600.0
    assert res["annual_marketing_equity"] == 31200.0

    # Test casing and normalization
    res_lower = calculate_content_factory_value(1.0, "  blog post  ")
    assert res_lower["weekly_marketing_equity"] == 200.0

def test_calculate_content_factory_value_invalid() -> None:
    with pytest.raises(ValueError):
        calculate_content_factory_value(1.0, "Invalid Asset")
```
