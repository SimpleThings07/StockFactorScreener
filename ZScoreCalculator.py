# encoding: utf-8
"""
ZScoreCalculator.py - cross-sectional z-score normalisation for StockFactorScreener
-------------------------------------------------------------------------------
This helper module is designed to be imported by **StockFactorScreener.py** once
all raw factor values for every ticker are collected. It provides three public
functions that return a *dict* mapping `ticker -> composite z-score`.

    • calc_value_z_scores(stock_list)
    • calc_profitability_z_scores(stock_list)
    • calc_growth_z_scores(stock_list)

Each helper collects the relevant raw metrics across the *whole* universe,
computes z-scores, then averages them (skipping NaNs) to get the composite.
The individual z-scores for every sub-metric are also returned in a nested
structure should you want more granular reporting.

The module is **pure numpy / std-lib** - no extra deps - and is defensive about
missing values & zero standard deviations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Callable, Any
import math
import numpy as np


# ---------------------------------------------------------------------------
# internal helpers
# ---------------------------------------------------------------------------

def _nan_safe(value: Any) -> float:
    """Convert *None*, *math.nan* or non‑numerics to *np.nan* – else cast to *float*."""
    try:
        return np.nan if value is None or math.isnan(float(value)) else float(value)
    except (ValueError, TypeError):
        return np.nan


def _zscore(column: np.ndarray) -> np.ndarray:
    """Classic population z‑score with **nan** handling.

    If the column has fewer than 2 valid observations or zero std, returns an
    array of *np.nan* so the composite mean can just ignore it.
    """
    mask = ~np.isnan(column)
    if mask.sum() < 2:
        return np.full_like(column, np.nan, dtype=float)
    mu = column[mask].mean()
    sigma = column[mask].std(ddof=0)
    if sigma == 0:
        return np.full_like(column, np.nan, dtype=float)
    out = (column - mu) / sigma
    out[~mask] = np.nan
    return out


# ---------------------------------------------------------------------------
# dataclasses for optional detailed output
# ---------------------------------------------------------------------------

@dataclass
class MetricZVector:
    """Holds raw & z-scored vectors for one ticker (optional debugging use)."""

    raw: Dict[str, float] = field(default_factory=dict)
    zscores: Dict[str, float] = field(default_factory=dict)

@dataclass
class ZScoreResult:
    """Composite score plus subs."""

    composite: float
    detail: MetricZVector

# Type alias: ticker -> ZScoreResult
ZScoreDict = Dict[str, ZScoreResult]


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------

def calc_value_z_scores(stocks: List["Stock"], value_cfg) -> ZScoreDict:  # noqa: F821
    """Compute composite value z-scores using (Trailing P/E, Forward P/E, EBIT/TEV).

    For the two *P/E* ratios **lower is better**, so we invert them (multiply by
    -1) before computing the z-score to align the direction with 'higher is
    cheaper' logic used by other factors.
    """
    # gather columns
    tickers, pe_t, pe_f, ebit_tev, pb_ratio = [], [], [], [], []

    # Iterate over all stocks
    for stock in stocks:

        tickers.append(stock.ticker)
        value_metrics = stock.value_metrics

        pe_t.append(_nan_safe(getattr(value_metrics, "pe_trailing", np.nan)))
        pe_f.append(_nan_safe(getattr(value_metrics, "pe_forward", np.nan)))
        ebit_tev.append(_nan_safe(getattr(value_metrics, "ebit_to_tev", np.nan)))
        pb_ratio.append(_nan_safe(getattr(value_metrics, "pb_ratio", np.nan)))

    # Invert ratios since lower is better for P/E and P/B ratios.
    pe_t_inv = np.multiply(pe_t, -1)
    pe_f_inv = np.multiply(pe_f, -1)
    pb_inv   = np.multiply(pb_ratio, -1)

    z_pe_t   = _zscore(np.array(pe_t_inv))
    z_pe_f   = _zscore(np.array(pe_f_inv))
    z_ebit   = _zscore(np.array(ebit_tev))
    z_pb     = _zscore(np.array(pb_inv))

    composite = np.nanmean(np.vstack([z_pe_t, z_pe_f, z_ebit, z_pb]), axis=0)

    return {
        tkr: ZScoreResult(
            composite=float(composite) if not math.isnan(composite) else np.nan,
            detail=MetricZVector(
                raw={
                    "PE_trailing": pe_t[i],
                    "PE_forward":  pe_f[i],
                    "EBIT_to_TEV": ebit_tev[i],
                    "PB_ratio":    pb_ratio[i],
                },
                zscores={
                    "z_PE_trailing": z_pe_t[i],
                    "z_PE_forward":  z_pe_f[i],
                    "z_EBIT_to_TEV": z_ebit[i],
                    "z_PB_ratio":    z_pb[i],
                },
            ),
        )
        for i, tkr in enumerate(tickers)
    }



def calc_profitability_z_scores(stocks: List["Stock"], profitability_cfg : dict) -> ZScoreDict:  # noqa: F821

    # TODO: use profit_cfg to configure the metrics to be used. See implementation of 'calc_value_z_scores' for more details.

    """Composite profitability z‑scores (GPOA, ROE, ROA, CFOA, Gross‑Margin)."""
    metrics = ["gpoa_ttm", "roe_ttm", "roa_ttm", "cfoa", "gpmar_ttm"]
    return _generic_group_z(stocks, "profitability_metrics", metrics)



def calc_growth_z_scores(stocks: List["Stock"], growth_cfg : dict) -> ZScoreDict:  # noqa: F821

    # TODO: use growth_cfg to configure the metrics to be used. See implementation of 'calc_value_z_scores' for more details.

    """Composite profitability‑growth z‑scores (Δ‑GPOA, Δ‑ROE, Δ‑ROA, Δ‑CFOA, Δ‑GMAR)."""
    metrics = [
        "gpoa_growth",
        "roe_growth",
        "roa_growth",
        "cfoa_growth",
        "gpmar_growth",
    ]
    return _generic_group_z(stocks, "growth_metrics", metrics)

# ---------------------------------------------------------------------------
# generic extractor used by the last two public helpers
# ---------------------------------------------------------------------------

def _generic_group_z(stocks: List["Stock"], attr_group: str, fields: List[str]) -> ZScoreDict:  # noqa: F821
    tickers = [s.ticker for s in stocks]
    # Build matrix shape (len(fields), len(stocks))
    raw_matrix = []
    for field in fields:
        col = []
        for s in stocks:
            group_obj = getattr(s, attr_group)
            col.append(_nan_safe(getattr(group_obj, field, np.nan)))
        raw_matrix.append(col)

    raw_np = np.array(raw_matrix, dtype=float)
    z_np   = np.vstack([_zscore(col) for col in raw_np])
    composite = np.nanmean(z_np, axis=0)

    results: ZScoreDict = {}
    for i, tkr in enumerate(tickers):
        raw_dict  = {fields[j]: raw_np[j, i] for j in range(len(fields))}
        z_dict    = {f"z_{fields[j]}": z_np[j, i] for j in range(len(fields))}
        results[tkr] = ZScoreResult(
            composite=float(composite[i]) if not math.isnan(composite[i]) else np.nan,
            detail=MetricZVector(raw=raw_dict, zscores=z_dict),
        )
    return results