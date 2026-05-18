import pytest
import numpy as np
import pandas as pd
from backend.models.optimizer import optimize_portfolio
from backend.models.risk import RiskQuestion, calculate_risk_score, risk_label


def make_prices(n_assets=3, n_days=252):
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=n_days)
    tickers = ["AAPL", "MSFT", "GOOGL"][:n_assets]
    data = {t: 100 * (1 + np.random.randn(n_days) * 0.015).cumprod() for t in tickers}
    return pd.DataFrame(data, index=dates)


def test_optimize_returns_correct_keys():
    result = optimize_portfolio(make_prices(), risk_score=5)
    assert "weights" in result
    assert "expected_annual_return_pct" in result
    assert "annual_volatility_pct" in result
    assert "sharpe_ratio" in result


def test_weights_sum_to_one():
    result = optimize_portfolio(make_prices(), risk_score=5)
    assert abs(sum(result["weights"].values()) - 1.0) < 0.01


def test_conservative_has_lower_volatility_than_aggressive():
    prices = make_prices()
    conservative = optimize_portfolio(prices, risk_score=2)
    aggressive = optimize_portfolio(prices, risk_score=9)
    assert conservative["annual_volatility_pct"] <= aggressive["annual_volatility_pct"]


def _make_risk_question(a_val=2, b_val=2, c_val=2, d_correct=True):
    from backend.models.risk import SectionA, SectionB, SectionC, SectionD
    return RiskQuestion(
        section_a=SectionA(a1=a_val, a2=a_val, a3=a_val, a4=a_val, a5=a_val, a6=a_val, a7=a_val, a8=a_val),
        section_b=SectionB(b1=b_val, b2=b_val, b3=b_val, b4=""),
        section_c=SectionC(c1=c_val, c2=c_val, c3=c_val, c4=c_val, c5=c_val, c6=c_val),
        section_d=SectionD(d11=d_correct, d12=d_correct, d13=d_correct, d14=d_correct, d15=d_correct),
    )


def test_risk_score_bounds():
    for val in [1, 2, 3, 4]:
        q = _make_risk_question(a_val=val, b_val=val, c_val=val)
        score, kl = calculate_risk_score(q)
        assert 8 <= score <= 68
        assert kl in ("none", "basic", "expert")


def test_risk_label():
    assert risk_label(26) == "Low (Defensive)"
    assert risk_label(42) == "Medium (Conservative)"
    assert risk_label(56) == "Medium-High (Balanced)"
    assert risk_label(68) == "High (Aggressive)"
