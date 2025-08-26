# Asset Risk Footprint

**What it does:** For each asset **A** in a universe **U**, estimate how much risk it typically brings when it’s included in an equal-weight portfolio of size **K**. The project computes:

- **$E[\sigma \mid A \in P,\ |P|=K]$** — expected portfolio volatility across random EW portfolios that include $A$  
- **$E[\mathrm{MRC}_A]$** — expected **marginal risk contribution** of $A$ in those portfolios  
- **Historical VaR** utilities for any chosen portfolio and date window

**Why it matters.** This gives an “average context” view of an asset’s **risk footprint**—useful for **universe screening**, **position sizing**, and **risk budgeting** without over-fitting to one specific portfolio.

---

## How it works (short)
- **Data → returns.** Load panel (`symbol, date, close`), pivot to prices, compute daily pct-change returns.  
- **Full-history filter.** Keep only names with a complete history over the horizon to avoid irregular gaps.  
- **Risk math.** For a sampled portfolio $P$ with $|P|=K$ and equal weights $w=\tfrac{1}{K}\mathbf{1}$:  
  - Portfolio vol $\;\sigma(P)=\sqrt{w^\top \Sigma_P\, w}\,$  
  - MRC vector $\;\mathrm{MRC}=\dfrac{\Sigma_P\, w}{\sigma(P)}\,$ (take the component for $A$)  
- **Monte Carlo.** Sample many portfolios containing $A$; average $\sigma$ and MRC to get **$E[\sigma \mid A]$** and **$E[\mathrm{MRC}_A]$**, with a standard error for $\sigma$.  
- **VaR.** Historical VaR = empirical $\alpha$-quantile of realized portfolio returns on a chosen window.

---

## Status
- Minimal, reproducible pipeline in pure Python (pandas/numpy).  
- Functions implemented for: universe filtering, $\sigma$, MRC, Monte Carlo estimates, and historical VaR.  

---

## Where this is going (roadmap)
- **Add-Asset Impact:** $\;\Delta\sigma(A \mid P)=\sigma(P \cup \{A\})-\sigma(P)\;$ and its expectation over contexts of size $K-1$.  
- **Better covariances:** Ledoit–Wolf shrinkage, robust estimators, EWMA; sector-neutral / market-neutral options.  
- **Tail risk:** CVaR (Expected Shortfall), block-bootstrap VaR, drawdown metrics, Cornish–Fisher adjustments.  
- **Context control:** stratified / constraint sampling (e.g., by sector, liquidity, max correlation) to reflect real book construction.  
- **Weights:** beyond equal-weight—cap/vol weights, risk parity, min-risk subject to footprint constraints.  
- **Scale & UX:** parallel Monte Carlo, deterministic seeds, cached covariances, simple CLI/notebook for reproducible runs.  

---

## Inputs (brief)
- CSV with `symbol, date, close` (daily).  
- Date range ~multi-year is recommended for stable covariances.

