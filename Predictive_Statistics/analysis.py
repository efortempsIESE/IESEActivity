# %% [markdown]
# # Case Study: Forecasting Bitcoin Volatility
# **GARCH, Realized Variance and Out-of-Sample Risk Forecasting — Predictive Statistics in Finance**
#
# This notebook answers every task of the case (Parts I–VII). Each code cell is followed by a short
# explanation of *what the code does* and *what the result means*.
#
# **Roadmap**
# | Part | Question | Tasks |
# |---|---|---|
# | I | Is there volatility to forecast? | 1 |
# | II | ARCH vs GARCH: what do the dynamics mean? | 2 |
# | III | Normal vs Student-t innovations | 3 |
# | IV | Expanding-window GARCH-t forecasts vs realized variance | 4 |
# | V | Simple RV-OLS benchmark | 5 |
# | VI | Two-year rolling window & parameter stability | 6 |
# | VII | Recommendation | – |
#
# **Timing convention (critical).** Everything is "pseudo-out-of-sample": a forecast for day *t+1* only
# uses information up to day *t*. Training sample = up to 31 Dec 2024; OOS = 1 Jan 2025 – 31 Aug 2026.

# %%
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import het_arch, acorr_ljungbox
from arch import arch_model
from joblib import Parallel, delayed

warnings.filterwarnings("ignore")
plt.rcParams.update({"figure.figsize": (11, 4), "axes.grid": True, "grid.alpha": .3,
                     "axes.spines.top": False, "axes.spines.right": False})
pd.set_option("display.float_format", lambda x: f"{x:,.4f}")

TRAIN_END = "2024-12-31"
OOS_START, OOS_END = "2025-01-01", "2026-08-31"

# %% [markdown]
# ## 0. Data loading
# * `r_t = 100·[log P_t − log P_{t−1}]` (percent log returns). The first return is 18 Aug 2017.
# * `RV_t` = sum of the 24 squared hourly returns on day *t* (in %²). It is our **proxy** for the
#   unobservable conditional variance. 29 days have missing RV (`RV_VALID=False`); we never fill them
#   with invented values — they are simply excluded from estimation/evaluation pairs where needed.

# %%
prices = pd.read_csv("data/bitcoin_daily_prices.csv", parse_dates=["Date"]).set_index("Date")["Price"]
rvdf = pd.read_csv("data/bitcoin_realized_variance.csv", parse_dates=["Date"]).set_index("Date")

r = 100 * np.log(prices).diff().dropna()          # daily % log returns
rv = rvdf["RV"].reindex(r.index)                  # realized variance aligned with returns

train = r[:TRAIN_END]
oos_dates = r[OOS_START:OOS_END].index

print(f"Returns: {r.index[0].date()} → {r.index[-1].date()}  (n={len(r)})")
print(f"Training: n={len(train)} | OOS: n={len(oos_dates)} ({oos_dates[0].date()} → {oos_dates[-1].date()})")
print(f"Missing RV: total={rv.isna().sum()}, in training={rv[:TRAIN_END].isna().sum()}, in OOS={rv[OOS_START:].isna().sum()}")

# %% [markdown]
# ---
# # Part I — Is there volatility to forecast?
# ## Task 1 — Explore Bitcoin returns (training sample only)
# We use only data up to 31 Dec 2024 so that no OOS information leaks into our modelling choices.

# %%
fig, ax = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
ax[0].plot(train.index, train, lw=.6); ax[0].set_title("Daily Bitcoin log returns (%)"); ax[0].set_ylabel("%")
ax[1].plot(train.index, rv[:TRAIN_END], lw=.6, color="C3"); ax[1].set_yscale("log")
ax[1].set_title("Realized variance (log scale)"); ax[1].set_ylabel("%² (log)")
plt.tight_layout(); plt.show()

desc = pd.Series({"Mean (%)": train.mean(), "Std dev (%)": train.std(), "Min (%)": train.min(),
                  "Max (%)": train.max(), "Skewness": stats.skew(train),
                  "Excess kurtosis": stats.kurtosis(train)})
jb = stats.jarque_bera(train)
print(desc.to_string()); print(f"\nJarque-Bera = {jb.statistic:,.1f}, p-value = {jb.pvalue:.2e}")

# %% [markdown]
# **What the code does.** Plots returns and (log-scale) realized variance, then reports descriptive
# statistics and the Jarque–Bera normality test.

# %%
fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
plot_acf(train, lags=30, ax=ax[0], title="ACF of returns r_t")
plot_acf(train**2, lags=30, ax=ax[1], title="ACF of squared returns r_t²")
plt.tight_layout(); plt.show()

lb_r = acorr_ljungbox(train, lags=[10, 20])
lb_r2 = acorr_ljungbox(train**2, lags=[10, 20])
arch_lm = {L: het_arch(train - train.mean(), nlags=L)[:2] for L in (5, 10)}
tab = pd.DataFrame({"Ljung-Box r (stat)": lb_r["lb_stat"], "p": lb_r["lb_pvalue"],
                    "Ljung-Box r² (stat)": lb_r2["lb_stat"], "p ": lb_r2["lb_pvalue"]})
print(tab.to_string())
print("\nARCH-LM test on demeaned returns:")
for L, (s, p) in arch_lm.items():
    print(f"  lags={L}: LM = {s:,.1f}, p-value = {p:.2e}")

# %% [markdown]
# **What the code does.** ACF of returns vs squared returns, Ljung–Box tests for serial dependence in
# each, and Engle's ARCH-LM test (regress squared demeaned returns on their own lags).
#
# INTERP_TASK1

# %% [markdown]
# ---
# # Part II — ARCH and GARCH
# ## Task 2 — Why does GARCH help?
# Model: `r_t = μ + ε_t`, `ε_t = σ_t z_t`, with `z_t ~ N(0,1)`.
# * ARCH(1): `σ²_t = ω + α ε²_{t−1}`
# * GARCH(1,1): `σ²_t = ω + α ε²_{t−1} + β σ²_{t−1}`
#
# Estimation is by Gaussian maximum likelihood on the **training sample**.

# %%
def fit(sample, p=1, q=1, dist="normal"):
    am = arch_model(sample, mean="Constant", vol="GARCH", p=p, q=q, dist=dist)
    return am.fit(disp="off", show_warning=False)

arch1 = fit(train, p=1, q=0)
garch_n = fit(train)

def param_table(res):
    return pd.DataFrame({"coef": res.params, "std err": res.std_err, "t": res.tvalues, "p-value": res.pvalues})

print("ARCH(1), Normal\n", param_table(arch1).to_string(), "\n")
print("GARCH(1,1), Normal\n", param_table(garch_n).to_string())

cmp = pd.DataFrame({m: {"Log-lik": x.loglikelihood, "AIC": x.aic, "BIC": x.bic}
                    for m, x in {"ARCH(1)": arch1, "GARCH(1,1)-N": garch_n}.items()}).T
print("\n", cmp.to_string())

a, b = garch_n.params["alpha[1]"], garch_n.params["beta[1]"]
w = garch_n.params["omega"]
pers = a + b
print(f"\nα̂ = {a:.4f} | β̂ = {b:.4f} | α̂+β̂ = {pers:.4f}")
print(f"Half-life of a volatility shock = ln(0.5)/ln(α̂+β̂) = {np.log(.5)/np.log(pers):.1f} days")
print(f"Unconditional variance ω/(1−α−β) = {w/(1-pers):.2f} %²  (sample var of returns = {train.var():.2f} %²)")

# %% [markdown]
# **What the code does.** Fits ARCH(1) and GARCH(1,1) by Gaussian ML, tabulates coefficients with
# standard errors, compares log-likelihood/AIC/BIC, and computes the persistence `α̂+β̂`, the
# half-life `ln(0.5)/ln(α̂+β̂)` and the implied unconditional variance.
#
# INTERP_TASK2

# %% [markdown]
# ---
# # Part III — Does the conditional distribution matter?
# ## Task 3 — Normal vs standardized Student-t GARCH(1,1)
# Two **separate** modelling choices: (i) the *variance recursion* (how σ²_t evolves) and (ii) the
# *distribution of the innovation z_t* (Normal vs fat-tailed t with ν degrees of freedom).

# %%
garch_t = fit(train, dist="t")
print("GARCH(1,1), Student-t\n", param_table(garch_t).to_string())

cmp3 = pd.DataFrame({m: {"Log-lik": x.loglikelihood, "AIC": x.aic, "BIC": x.bic,
                         "alpha": x.params["alpha[1]"], "beta": x.params["beta[1]"],
                         "alpha+beta": x.params["alpha[1]"] + x.params["beta[1]"]}
                     for m, x in {"GARCH-N": garch_n, "GARCH-t": garch_t}.items()}).T
print("\n", cmp3.to_string())

z_n = garch_n.std_resid.dropna(); z_t = garch_t.std_resid.dropna()
print(f"\nStandardized residual excess kurtosis: Normal model = {stats.kurtosis(z_n):.2f}, t model = {stats.kurtosis(z_t):.2f}")
print(f"Ljung-Box p-value on z² (10 lags): N = {acorr_ljungbox(z_n**2, lags=[10])['lb_pvalue'].iloc[0]:.3f}, "
      f"t = {acorr_ljungbox(z_t**2, lags=[10])['lb_pvalue'].iloc[0]:.3f}")

fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
stats.probplot(z_n, dist="norm", plot=ax[0]); ax[0].set_title("QQ-plot std. residuals vs Normal (Normal-GARCH)")
nu = garch_t.params["nu"]
stats.probplot(z_t, dist="t", sparams=(nu,), plot=ax[1]); ax[1].set_title(f"QQ-plot vs Student-t(ν={nu:.1f}) (t-GARCH)")
plt.tight_layout(); plt.show()

# %% [markdown]
# **What the code does.** Re-estimates GARCH(1,1) with standardized Student-t errors, compares fit
# (log-lik/AIC/BIC), and checks the standardized residuals `z_t = ε_t/σ_t` with QQ-plots.
#
# INTERP_TASK3

# %% [markdown]
# ---
# # Part IV — Forecasting a latent variable
# ## Task 4 — Expanding-window one-day-ahead GARCH-t forecasts
# For every OOS date `d` (1 Jan 2025 … 31 Aug 2026):
# 1. estimate GARCH(1,1)-t on returns **strictly before** `d` (i.e. through `d−1`);
# 2. produce the one-step variance forecast `σ̂²_{d|d−1}`;
# 3. compare with `RV_d` once observed.
#
# The same function also supports the **two-year rolling window** used later in Part VI
# (window = `[d − 2 years, d − 1 day]`; for `d = 1 Jan 2025` this is exactly 1 Jan 2023 – 31 Dec 2024).
# We store the parameters and the standard error of `α+β` (delta method using the full parameter
# covariance: `Var(α̂+β̂) = Var(α̂)+Var(β̂)+2Cov(α̂,β̂)`), as needed by Task 6.

# %%
def window(d, mode):
    idx = r.index
    if mode == "expanding":
        return r[idx < d]
    return r[(idx >= d - pd.DateOffset(years=2)) & (idx < d)]

def garch_origin(d, mode):
    s = window(d, mode)
    res = fit(s, dist="t")
    h = res.forecast(horizon=1, reindex=False).variance.iloc[-1, 0]
    p, C = res.params, res.param_cov
    var_pers = C.loc["alpha[1]", "alpha[1]"] + C.loc["beta[1]", "beta[1]"] + 2 * C.loc["alpha[1]", "beta[1]"]
    return dict(date=d, h=h, alpha=p["alpha[1]"], beta=p["beta[1]"], pers=p["alpha[1]"] + p["beta[1]"],
                pers_se=np.sqrt(max(var_pers, 0)), nu=p["nu"], n_obs=len(s), conv=res.convergence_flag)

def run_garch(mode):
    out = Parallel(n_jobs=-1)(delayed(garch_origin)(d, mode) for d in oos_dates)
    return pd.DataFrame(out).set_index("date")

g_exp = run_garch("expanding")
print("Expanding GARCH-t done:", g_exp.shape, "| non-converged fits:", int((g_exp.conv != 0).sum()))
g_exp[["h", "alpha", "beta", "pers", "nu"]].describe().T

# %% [markdown]
# **What the code does.** `window()` picks the information set (all history before `d`, or only the
# last two years). `garch_origin()` re-fits the model and returns the 1-step variance forecast plus the
# parameters. We loop over all 608 OOS dates in parallel — about 600 separate estimations, which is
# why this cell takes a few minutes.

# %%
def evaluate(h, name):
    """MSE, QLIKE, correlation, mean levels — on dates where RV is observed."""
    d = pd.concat([h.rename("h"), rv.rename("rv")], axis=1).dropna()
    d = d[d.h > 0]
    mse = np.mean((d.rv - d.h) ** 2)
    qlike = np.mean(np.log(d.h) + d.rv / d.h)
    return pd.Series({"MSE": mse, "QLIKE": qlike, "Corr": d.h.corr(d.rv),
                      "Mean forecast": d.h.mean(), "Mean RV": d.rv.mean(),
                      "Mean fcst / Mean RV": d.h.mean() / d.rv.mean(), "N": len(d)}, name=name)

ev_garch_exp = evaluate(g_exp.h, "GARCH-t expanding")
print(ev_garch_exp.to_frame().T.to_string())

fig, ax = plt.subplots(2, 1, figsize=(11, 7))
ax[0].plot(rv[OOS_START:], lw=.7, color="C3", label="Realized variance"); ax[0].plot(g_exp.h, lw=1.3, label="GARCH-t forecast")
ax[0].set_title("GARCH-t (expanding) forecast vs realized variance (levels)"); ax[0].legend(); ax[0].set_ylabel("%²")
ax[1].plot(rv[OOS_START:], lw=.7, color="C3"); ax[1].plot(g_exp.h, lw=1.3); ax[1].set_yscale("log")
ax[1].set_title("Same, log scale (easier to see calibration across regimes)")
plt.tight_layout(); plt.show()

# %% [markdown]
# **What the code does.** `evaluate()` computes the three requested metrics plus average forecast vs
# average RV (calibration) on dates with a valid RV. Then it plots forecasts against RV, in levels and
# on a log axis.
#
# INTERP_TASK4

# %% [markdown]
# ---
# # Part V — A simple realized-variance benchmark
# ## Task 5 — RV-OLS: `RV_{t+1} = a + b·RV_t + u_{t+1}`
# Estimated on the training sample (pairs where both RV values exist), with HAC (Newey–West) standard
# errors because RV is persistent and heteroskedastic. Then forecasts over the same OOS dates, using
# only pairs whose *target* date is before the forecast date.
#
# *Missing-RV rule:* if `RV_{d−1}` is missing, the latest available earlier RV is used as the predictor
# (the only information a forecaster would actually have). Evaluation always uses valid `RV_d`.

# %%
HAC_LAGS = 7   # one week of daily data; a conventional choice, no search performed

rv_lag = rv.shift(1)                       # RV_{t-1}, aligned with target RV_t
rv_lag_filled = rv.ffill().shift(1)        # predictor available at forecast origin
pairs = pd.concat([rv.rename("y"), rv_lag.rename("x")], axis=1).dropna()

tr = pairs[:TRAIN_END]
ols_train = sm.OLS(tr.y, sm.add_constant(tr.x)).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
print(ols_train.summary().tables[1])
print(f"\nIn-sample R² = {ols_train.rsquared:.3f}  (N = {int(ols_train.nobs)})")
print(f"Correlation(RV_t, RV_t-1) = {tr.y.corr(tr.x):.3f}")

# %%
def ols_origin(d, mode):
    idx = pairs.index
    mask = idx < d if mode == "expanding" else (idx >= d - pd.DateOffset(years=2)) & (idx < d)
    s = pairs[mask]
    m = sm.OLS(s.y, sm.add_constant(s.x)).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    a_, b_ = m.params["const"], m.params["x"]
    lo, hi = m.conf_int().loc["x"]
    return dict(date=d, h=a_ + b_ * rv_lag_filled[d], a=a_, b=b_, b_lo=lo, b_hi=hi, b_t=m.tvalues["x"], n_obs=len(s))

def run_ols(mode):
    return pd.DataFrame([ols_origin(d, mode) for d in oos_dates]).set_index("date")

o_exp = run_ols("expanding")
print("negative RV-OLS forecasts (expanding):", int((o_exp.h <= 0).sum()))
ev_ols_exp = evaluate(o_exp.h, "RV-OLS expanding")

comp5 = pd.concat([ev_garch_exp, ev_ols_exp], axis=1).T
print(comp5.to_string())

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(rv[OOS_START:], lw=.6, color="C3", alpha=.6, label="Realized variance")
ax.plot(g_exp.h, lw=1.4, label="GARCH-t (expanding)"); ax.plot(o_exp.h, lw=1.0, label="RV-OLS (expanding)")
ax.set_yscale("log"); ax.legend(); ax.set_title("Forecast dynamics: GARCH-t vs RV-OLS (log scale)")
plt.tight_layout(); plt.show()

print("\nStd. dev. of forecasts: GARCH =", round(g_exp.h.std(), 2), "| RV-OLS =", round(o_exp.h.std(), 2),
      "| RV =", round(rv[OOS_START:].std(), 2))
print("Day-to-day forecast change std (smoothness): GARCH =", round(g_exp.h.diff().std(), 2),
      "| RV-OLS =", round(o_exp.h.diff().std(), 2))

# %% [markdown]
# **What the code does.** Regresses `RV_t` on `RV_{t−1}` (HAC errors), reports `b̂`, its significance and
# R². Then `ols_origin()` repeats the estimation at each OOS origin with the information set allowed,
# forecasts `â + b̂·RV_{d−1}`, and we compare with GARCH on the *same* dates and metrics.
#
# ### Formal test of equal predictive accuracy (Diebold–Mariano)
# Differences in average loss can be luck. The DM test regresses the loss differential
# `L_A,t − L_B,t` on a constant with HAC errors; a significantly negative constant means A has lower loss.

# %%
def loss_series(h, kind):
    d = pd.concat([h.rename("h"), rv.rename("rv")], axis=1).dropna()
    d = d[d.h > 0]
    return (d.rv - d.h) ** 2 if kind == "MSE" else np.log(d.h) + d.rv / d.h

def dm(hA, hB, kind):
    la, lb = loss_series(hA, kind), loss_series(hB, kind)
    dd = (la - lb).dropna()
    m = sm.OLS(dd, np.ones(len(dd))).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    return pd.Series({"mean loss diff (A−B)": dd.mean(), "t-stat": m.tvalues.iloc[0], "p-value": m.pvalues.iloc[0]})

dm_tab = pd.DataFrame({k: dm(g_exp.h, o_exp.h, k) for k in ("MSE", "QLIKE")}).T
print("DM test, A = GARCH-t expanding, B = RV-OLS expanding (negative ⇒ GARCH better)")
print(dm_tab.to_string())

# %% [markdown]
# INTERP_TASK5

# %% [markdown]
# ---
# # Part VI — Does distant Bitcoin history still help?
# ## Task 6 — Two-year rolling estimation and parameter stability
# Same OOS dates, but each model is estimated on the **most recent two years only** and the window
# slides forward one day at a time.

# %%
g_roll = run_garch("rolling")
o_roll = run_ols("rolling")
print("window sizes: GARCH", g_roll.n_obs.min(), "-", g_roll.n_obs.max(), "| non-converged:", int((g_roll.conv != 0).sum()))
print("negative RV-OLS rolling forecasts:", int((o_roll.h <= 0).sum()))

evs = pd.concat([ev_garch_exp, evaluate(g_roll.h, "GARCH-t rolling 2y"),
                 ev_ols_exp, evaluate(o_roll.h, "RV-OLS rolling 2y")], axis=1).T
print(evs.to_string())

# %%
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(rv[OOS_START:], lw=.6, color="C3", alpha=.5, label="Realized variance")
for h_, lab in [(g_exp.h, "GARCH-t expanding"), (g_roll.h, "GARCH-t rolling"),
                (o_exp.h, "RV-OLS expanding"), (o_roll.h, "RV-OLS rolling")]:
    ax.plot(h_, lw=1.1, label=lab)
ax.set_yscale("log"); ax.legend(ncol=3); ax.set_title("All four forecasting rules (log scale)")
plt.tight_layout(); plt.show()

dm_rows = {}
for lab, A, B in [("GARCH roll vs GARCH exp", g_roll.h, g_exp.h), ("OLS roll vs OLS exp", o_roll.h, o_exp.h),
                  ("GARCH roll vs OLS roll", g_roll.h, o_roll.h)]:
    for k in ("MSE", "QLIKE"):
        dm_rows[(lab, k)] = dm(A, B, k)
print("DM tests (A − B; negative ⇒ A better)")
print(pd.DataFrame(dm_rows).T.to_string())

# %%
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(o_roll.b, label="b̂ (rolling 2y)"); ax[0].fill_between(o_roll.index, o_roll.b_lo, o_roll.b_hi, alpha=.25, label="HAC 95% CI")
ax[0].plot(o_exp.b, ls="--", color="k", lw=1, label="b̂ (expanding)"); ax[0].axhline(0, color="grey", lw=.8)
ax[0].set_title("RV-OLS persistence coefficient b"); ax[0].legend()
ax[1].plot(g_roll.alpha, label="α"); ax[1].plot(g_roll.beta, label="β"); ax[1].plot(g_roll.pers, label="α+β", color="k")
ax[1].fill_between(g_roll.index, g_roll.pers - 1.96 * g_roll.pers_se, g_roll.pers + 1.96 * g_roll.pers_se, color="k", alpha=.12, label="95% CI of α+β")
ax[1].axhline(1, color="grey", lw=.8, ls=":"); ax[1].set_title("Rolling GARCH-t parameters"); ax[1].legend(ncol=2)
plt.tight_layout(); plt.show()

print("RV-OLS rolling b̂: min %.3f | median %.3f | max %.3f" % (o_roll.b.min(), o_roll.b.median(), o_roll.b.max()))
print("Share of windows with HAC 95%% CI strictly above 0: %.1f%%" % (100 * (o_roll.b_lo > 0).mean()))
print("Rolling GARCH α+β: min %.3f | median %.3f | max %.3f" % (g_roll.pers.min(), g_roll.pers.median(), g_roll.pers.max()))
print("Share of windows with α+β > 0.99: %.1f%% | 95%% CI upper bound ≥ 1: %.1f%%" %
      (100 * (g_roll.pers > .99).mean(), 100 * ((g_roll.pers + 1.96 * g_roll.pers_se) >= 1).mean()))
print("Rolling GARCH ν: min %.1f | median %.1f | max %.1f" % (g_roll.nu.min(), g_roll.nu.median(), g_roll.nu.max()))

# %% [markdown]
# **What the code does.** Re-runs both models on the 2-year window, evaluates all four rules, runs DM
# tests, and plots the rolling `b̂` with its HAC confidence band and the rolling GARCH `α, β, α+β` (with
# the delta-method band for persistence). We summarise the *distribution* of the estimates rather than
# cherry-picking a "best" window, as the case instructs.
#
# INTERP_TASK6

# %% [markdown]
# ---
# # Part VII — Recommendation to the risk manager
#
# INTERP_PART7
