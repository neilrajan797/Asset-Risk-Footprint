import numpy as np
import pandas as pd
from typing import Iterable, Tuple, List

# ------------------------
# Data prep
# ------------------------
def load_prices(csv_path: str) -> pd.DataFrame:
    """Load CSV with columns ['symbol','date','close'] → pivoted price panel (date index)."""
    df = pd.read_csv(csv_path, usecols=['symbol', 'date', 'close'])
    prices = df.pivot(index='date', columns='symbol', values='close')
    prices.index = pd.to_datetime(prices.index)
    return prices.sort_index()

def full_history_universe(prices: pd.DataFrame) -> pd.Index:
    """Keep only symbols with complete price history (no NaNs)."""
    return prices.columns[prices.notna().mean() == 1.0]

def returns_from_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Simple daily pct-change returns; drops first NaN row."""
    return prices.pct_change().dropna()

# ------------------------
# Risk math
# ------------------------
def subcov(cov: pd.DataFrame, tickers: Iterable[str]) -> np.ndarray:
    """Sub-covariance matrix for list of tickers."""
    P = list(tickers)
    return cov.loc[P, P].to_numpy()

def portfolio_sigma(cov_P: np.ndarray) -> float:
    """Equal-weight portfolio volatility from sub-covariance."""
    k = cov_P.shape[0]
    w = np.ones(k) / k
    return float(np.sqrt(w @ cov_P @ w))

def mrc_for_asset(cov_P: np.ndarray, tickers: List[str], asset: str) -> float:
    """Marginal Risk Contribution for `asset` in equal-weight portfolio `tickers`."""
    k = cov_P.shape[0]
    w = np.ones(k) / k
    sigma_p = float(np.sqrt(w @ cov_P @ w))
    mrc_vec = (cov_P @ w) / sigma_p
    idx = tickers.index(asset)
    return float(mrc_vec[idx])

# ------------------------
# Monte Carlo sampling
# ------------------------
def sample_portfolio_with_asset(universe: pd.Index, asset: str, k: int, rng: np.random.Generator) -> List[str]:
    """Random portfolio of size k that includes `asset`."""
    others = np.array([u for u in universe if u != asset])
    pick = rng.choice(others, size=k-1, replace=False)
    P = list(np.append(pick, asset))
    return P

def expected_sigma_and_se(universe: pd.Index, cov: pd.DataFrame, asset: str, k: int, num_sims: int, seed: int = 42) -> Tuple[float, float]:
    """Monte Carlo estimate of E[sigma | portfolios of size k that include asset]; also returns SE."""
    rng = np.random.default_rng(seed)
    sigmas = np.empty(num_sims, dtype=float)
    for i in range(num_sims):
        P = sample_portfolio_with_asset(universe, asset, k, rng)
        cov_P = subcov(cov, P)
        sigmas[i] = portfolio_sigma(cov_P)
    esig = float(sigmas.mean())
    se = float(sigmas.std(ddof=1) / np.sqrt(num_sims))
    return esig, se

def expected_mrc(universe: pd.Index, cov: pd.DataFrame, asset: str, k: int, num_sims: int, seed: int = 42) -> float:
    """Monte Carlo estimate of E[MRC_asset | portfolios of size k that include asset]."""
    rng = np.random.default_rng(seed)
    vals = np.empty(num_sims, dtype=float)
    for i in range(num_sims):
        P = sample_portfolio_with_asset(universe, asset, k, rng)
        cov_P = subcov(cov, P)
        vals[i] = mrc_for_asset(cov_P, P, asset)
    return float(vals.mean())

# ------------------------
# Historical VaR utilities
# ------------------------
def portfolio_returns(returns: pd.DataFrame, P: List[str], start: str, end: str) -> pd.Series:
    """Equal-weight portfolio returns over [start, end]. Dates as 'YYYY-MM-DD' strings or Timestamps."""
    sub = returns.loc[pd.to_datetime(start):pd.to_datetime(end), P]
    w = np.ones(len(P)) / len(P)
    return sub @ w

def historical_var(returns: pd.DataFrame, P: List[str], start: str, end: str, confidence: float = 0.95) -> float:
    """Historical VaR (positive number) at given confidence over [start, end]."""
    alpha = 1.0 - confidence
    rp = portfolio_returns(returns, P, start, end).values
    q_alpha = float(np.nanquantile(rp, alpha))
    return -q_alpha
