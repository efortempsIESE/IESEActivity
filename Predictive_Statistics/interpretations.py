INTERP = {}

INTERP["INTERP_TASK1"] = r"""
### Interpretation — Task 1
**Key numbers (training sample, n = 2,693).** Mean return 0.11 %/day versus a standard deviation of 3.71 %/day;
skewness −0.75, **excess kurtosis 12.5**, worst day −46.5 %; Jarque–Bera rejects normality overwhelmingly.

**(a) Are daily returns predictable from their own history?** Essentially **no**. The ACF of `r_t` is tiny,
and the Ljung–Box test is only marginal (p = 0.031 at 10 lags, p = 0.076 at 20 lags). Any linear
predictability is very small compared with the 3.7 % daily noise and with the mean of 0.11 %, so it
is not something a risk manager could trade or size positions on. (With 2,693 observations even tiny autocorrelations can
reach "significance"; statistical significance is not economic usefulness.)

**(b) Is there volatility clustering?** **Yes, strongly.** Squared returns are highly autocorrelated
(ACF clearly positive across 30 lags; Ljung–Box on `r²` = 93.9 at 10 lags, p ≈ 0) and Engle's ARCH-LM
test rejects "no ARCH effects" (LM = 47.2 at 5 lags, 74.2 at 10 lags, p < 1e-8). The plots show it directly: calm
spells (e.g. 2023–24) alternate with violent ones (2017–18, March 2020, 2021). Direction
is nearly unpredictable, but **the size of the next move is partly predictable** — that is the forecasting opportunity.

**(c) What does an ARCH-LM rejection establish — and not?**
* *Establishes:* in-sample, squared (demeaned) returns are serially dependent, i.e. the conditional variance
  is time-varying and (statistically) related to past shocks.
* *Does not establish:* that a particular model (ARCH/GARCH) is the right one; how large or economically useful the
  predictability is; that it is **stable over time**; or that forecasts will be accurate **out of sample**. A
  rejection can also be driven by a few extreme observations or a structural break in the variance level.
  It is a necessary condition for volatility forecasting, not evidence of forecast quality.
"""

INTERP["INTERP_TASK2"] = r"""
### Interpretation — Task 2
**Fit.** GARCH(1,1) beats ARCH(1) decisively: log-likelihood −7,164.6 vs −7,307.1, AIC 14,337 vs 14,620,
BIC 14,361 vs 14,638 (≈ 285 AIC points better for just one extra parameter). A single lag of the squared shock
cannot capture how long Bitcoin's volatility episodes last; the lagged variance term `β σ²_{t−1}` does that parsimoniously.

**Economic meaning of GARCH(1,1) (Normal):** `α̂ = 0.100`, `β̂ = 0.859`, `α̂ + β̂ = 0.958`.
* **Reaction to a new shock (α̂ ≈ 0.10).** Each unit of squared surprise adds ≈ 0.10 to tomorrow's variance.
  A 10 % surprise (ε² = 100) adds about 10 %² to the next-day variance — roughly two-thirds of the long-run level
  (≈ 15.8 %²). Risk reacts noticeably, but is not completely re-set by one day.
* **Persistence (β̂ ≈ 0.86; α̂ + β̂ ≈ 0.96).** Most of yesterday's variance carries over, so volatility is highly persistent:
  the half-life of a volatility shock is `ln(0.5)/ln(0.958) ≈ 16.3 days`. Bitcoin risk shocks fade over weeks, not days.
* Implied long-run variance `ω/(1−α−β) = 15.8 %²` (≈ 3.97 %/day), close to the sample variance 13.8 %², a sanity check that the model is consistent with the data.

**Significance.** Every key variance parameter is significant (ω p = 0.018, α p = 0.019, β t ≈ 19).

**Why this is not yet evidence of forecast accuracy.** (i) These are *in-sample* statistics: parameters are fitted to the same data
they are tested on. (ii) Significance says the true `α, β` are different from 0; it says nothing about the *size* of
the forecast errors — even a correct model leaves a lot of noise because the daily shock `z_t` is random. (iii) The variance is latent: we are
judging it only through noisy proxies. (iv) Parameters may drift (see Part VI), so what was true in 2017–2024 may not hold in 2025–26.
Only a genuine out-of-sample test (Part IV) answers "will it forecast accurately?".
"""

INTERP["INTERP_TASK3"] = r"""
### Interpretation — Task 3
**Fit improves massively with Student-t errors:** log-likelihood −6,831.4 vs −7,164.6 (+333), AIC 13,672.7 vs 14,337.1,
BIC 13,702.2 vs 14,360.7, for a single extra parameter. Every criterion prefers the t.

**Degrees of freedom: ν̂ = 3.18 (s.e. 0.16).** This is extremely heavy-tailed (a Normal corresponds to ν → ∞; ν ≈ 3 means the variance is finite but the
fourth moment — kurtosis — is not). Extreme days such as −46 % are *not* freak events for this distribution. The QQ-plots tell the same story:
the standardized residuals of the Normal model leave the 45° line in both tails, whereas the t-GARCH residuals follow the t-quantile line well.
(The *sample* kurtosis of the t-model residuals, 16.9, is not comparable with a Normal's 3: a t₃ has infinite theoretical kurtosis.)

**Does it change the description of Bitcoin returns?** The *distribution* matters a lot for likelihood-based comparisons, tail probabilities,
VaR/Expected Shortfall and parameter estimates; the *variance recursion* barely changes: the clustering is captured in both
cases (Ljung–Box on `z²` p = 0.86 / 0.90 — no remaining ARCH). Keep the two choices separate:
* **Conditional variance recursion** → *how risk evolves* (GARCH(1,1) in both models).
* **Conditional distribution of z_t** → *how large the surprises relative to σ_t can be* (tails).

**Note on parameters.** Under the t, α̂ falls to 0.073 while β̂ rises to 0.927: the Normal model had to read extreme days as huge
variance jumps; the t attributes them to tail draws. **α̂ + β̂ = 1.000 — the estimate sits on the stationarity boundary** (the `arch` package
constrains α+β ≤ 1; this is an *IGARCH* outcome): shocks to variance never die out on average, the half-life is infinite and
there is no finite unconditional variance (ω is no longer significant, p = 0.14). Practically, forecasts behave like an exponentially weighted moving
average. Standard errors on the boundary are not reliable, a caveat we will carry into Task 6.
"""

INTERP["INTERP_TASK4"] = r"""
### Interpretation — Task 4 (expanding-window GARCH-t vs RV)
| Metric | Value |
|---|---|
| MSE | 48.67 |
| QLIKE | 2.612 |
| Corr(ĥ, RV) | 0.328 |
| Mean forecast / Mean RV | 7.12 / 5.38 (≈ **+32 % too high**) |

**What each statistic says.**
* **MSE** — average squared distance in %² units. It is dominated by a few extreme-RV days (RV has a very long right tail), so it is noisy and rewards getting the
  *spikes* right.
* **QLIKE** — penalises *ratios* `RV/ĥ`, is scale-free across calm and turbulent periods and penalises under-prediction of risk
  more heavily than over-prediction. It is the preferred loss for variance forecasts because it ranks forecasts correctly even if RV is only a noisy proxy.
* **Correlation** — measures only whether forecasts *move with* RV; it is blind to level and scale.

**Why high correlation can still come with poor MSE/QLIKE.** Correlation is unaffected by adding a constant to the forecasts
or by multiplying them by any scale; MSE and QLIKE are affected by both. A forecast that tracks the *shape* of RV perfectly but is
systematically 30–80 % too large (or too small) still has a high correlation yet loses on MSE and QLIKE. Here
GARCH's average forecast (7.12 %²) is above average RV (5.38 %²): 2025–26 turned out calmer than the 2017–2024 history on which the model was fitted
(average RV in training ≈ 16 %²). The forecast is a bit too "nervous" on average — a **calibration** problem, not only a correlation problem.
Only ~0.33 correlation (≈ 11 % of the variance explained) also tells us that most day-to-day variation in RV remains unexplained.

**If GARCH forecasts high variance and tomorrow is quiet, was the forecast wrong? No — one observation proves nothing.**
`σ²_{t+1|t}` is a *conditional expectation* (the mean of a distribution of possible outcomes), not a promise. A high-variance forecast *should* occasionally be followed by a quiet day
(even a correct model produces many small realised squared returns; with a Normal, the median of `z²` is only ≈ 0.45). In addition, `σ²_{t+1|t}` is **latent**:
RV is only a noisy proxy for it, so a single gap between ĥ and RV mixes forecast error with measurement/sampling noise. Forecasts can only be judged **statistically,
across many days**: average loss, calibration (mean ĥ vs mean RV, ratio `RV/ĥ` ≈ 1 on average), and tests such as Diebold–Mariano for comparing models.
"""

INTERP["INTERP_TASK5"] = r"""
### Interpretation — Task 5 (GARCH-t vs RV-OLS, expanding)
**The regression.** `b̂ = 0.548` (HAC s.e. 0.044, t = 12.5, p ≈ 0), `â = 7.31`, in-sample **R² = 0.29**. About 55 % of
today's realised-variance deviation is still present tomorrow (an AR(1) half-life of only ≈ 1.2 days — fast mean reversion toward the intercept-implied level). The model has a significant but modest explanatory power.

**OOS comparison (same 608 dates, same metrics):**
| Model | MSE | QLIKE | Corr | Mean forecast |
|---|---|---|---|---|
| GARCH-t (expanding) | **48.67** | **2.612** | 0.328 | 7.12 |
| RV-OLS (expanding) | 58.07 | 2.753 | **0.429** | 9.76 |
| (Mean RV) | | | | 5.38 |

* GARCH-t wins on MSE and QLIKE; RV-OLS wins on correlation. This is exactly the correlation-vs-calibration point above: the regression tracks RV's *movements* better but its intercept
  (estimated when volatility was much higher, mean RV ≈ 16) makes forecasts **82 % too high** on average.
* **Diebold–Mariano:** the QLIKE advantage of GARCH is highly significant (mean loss difference −0.14, t = −5.6), while the MSE advantage (−9.4) is **not** significant (p = 0.115): MSE is dominated by a few spike days, so it
  cannot separate the models statistically.

**Dynamics of the forecasts.** RV-OLS is a one-lag filter `a + b·RV_{t}`: it jumps with every noisy RV observation (std of daily forecast changes 4.04) — a single spike
day moves tomorrow's forecast, and then it is gone. GARCH combines the last shock **and** the entire past through `σ²_{t−1}`, so it evolves
smoothly (std of daily changes 1.10) and moves into and out of high-volatility episodes gradually. In that sense GARCH is **more flexible in how it
uses history** (long memory) but **less jumpy**. The plots show it: GARCH follows the slow-moving volatility regime; RV-OLS follows the noise. This
flexibility helped on QLIKE, but it didn't help dramatically on MSE and it didn't improve correlation. Flexibility only turns into accuracy when
the extra structure is actually stable and relevant; here it brings a moderate, metric-dependent gain.

**Two different questions — keep them apart.**
1. *Does today's RV contain statistically significant information about tomorrow's RV?* **Yes**: t = 12.5, R² = 0.29.
2. *Does the resulting model forecast accurately enough to be useful?* **Only moderately**: OOS correlations are 0.33–0.43 (so roughly 10–18 % of RV variation explained),
   and the forecast errors are large relative to the average RV (RMSE ≈ 7 %² against a mean of 5.4 %²).

**Why a significant coefficient doesn't guarantee good OOS performance.** A t-statistic measures how precisely `b` is estimated, not how much unexplained noise remains
(with 2,600 observations even a weak relation is "highly significant"). The estimated relation can also change after the training period (the level of
volatility fell; we will see `b̂` drift to ≈ 0.35 in Part VI), outliers dominate squared-error losses, and in-sample fit is optimistic by construction.
"""

INTERP["INTERP_TASK6"] = r"""
### Interpretation — Task 6 (two-year rolling window)
**(a) Expanding vs rolling.**
| Rule | MSE | QLIKE | Corr | Mean forecast (Mean RV = 5.38) |
|---|---|---|---|---|
| GARCH-t expanding | 48.67 | 2.612 | 0.328 | 7.12 |
| GARCH-t rolling 2y | 47.03 | 2.615 | 0.294 | 6.62 |
| RV-OLS expanding | 58.07 | 2.753 | 0.429 | 9.76 |
| RV-OLS rolling 2y | **38.98** | **2.590** | 0.422 | 5.97 |

* **GARCH hardly cares about the window**: differences are insignificant (DM p = 0.35 for MSE, 0.70 for QLIKE) — its variance recursion re-anchors itself daily.
* **RV-OLS benefits enormously from forgetting distant history** (MSE 58.1 → 39.0, QLIKE 2.753 → 2.590; DM t ≈ −8). Almost all of the gain is **calibration**: the
  average forecast drops from 9.76 to 5.97, almost matching mean RV; correlation is unchanged (0.43 → 0.42).
* The ranking changes: with the expanding window GARCH is better on MSE/QLIKE; with the rolling window RV-OLS has the lowest MSE and QLIKE. However, the
  rolling RV-OLS vs rolling GARCH difference is **not statistically significant at 5 %** (DM p = 0.074 on MSE, 0.105 on QLIKE). So honest conclusion: the two are close on the rolling window.

**(b) Is the RV persistence coefficient stable?** Its **sign and significance** are very stable: the HAC 95 % interval is strictly above zero in **100 %** of the rolling windows.
Its **size** is not: `b̂` ranges from 0.30 to 0.42 (median 0.35), well below the 0.55 estimated on the 2017–2024 sample. So today's RV *always* carries information about tomorrow's, but the
strength of that link differs across the history, and by 2025–26 it is weaker than the older sample suggested.

**(c) How stable is GARCH persistence?** `α̂+β̂` ranges from 0.945 to 1.000 (median 0.978); it is above 0.99 in 44 % of the windows, and `ν̂` moves between about 3.0 and 4.5 (median 3.8). Estimates
close to one imply: (i) very slow decay of volatility shocks (half-life ≈ 31 days at 0.978, ≈ 69 days at 0.99, infinite at 1); (ii) as α+β → 1 (IGARCH), forecasts at long horizons do not revert to a long-run variance
and the model behaves like an EWMA/RiskMetrics filter; (iii) the parameter is **hard to pin down**: our delta-method 95 % band (using `Var(α̂)+Var(β̂)+2Cov(α̂,β̂)`) contains 1 in all windows, so
we cannot distinguish "0.95" from "unit root". The band itself is unreliable near the boundary, since the estimate is constrained at 1. Apparent unit-root persistence can also be an artefact of shifts in the
level of volatility that the model reads as persistence.

**(d) What does a ranking that changes with the window suggest?** Distant history is **not free**: for a model that relies on a fixed level/slope (RV-OLS) it can be actively harmful, because volatility was structurally higher in
2017–2022 than in 2025–26. A model with a self-updating variance state (GARCH) is more robust to the choice of information set. Practical lesson: judge the *forecasting rule* (model + information set), and treat the window as part of the model.

**(e) Does this prove a structural break?** **No.** (1) We never *tested* for a break (no Chow/Bai–Perron-type test) and the rolling estimates vary naturally from window to window through sampling error alone — particularly with heavy tails. (2) Differences between rules in a ~600-day OOS sample are often not statistically significant (see DM).
(3) Alternative explanations: slowly moving volatility level (regimes), time-varying parameters, a misspecified AR(1)/GARCH structure (e.g. long memory), and a few outliers entering/leaving windows. The results
are *consistent with* an evolving volatility environment and say that old data should be used with caution, but they don't identify a break date or mechanism.
"""

INTERP["INTERP_PART7"] = r"""
### Answers to the risk manager's questions
* **Is there a meaningful predictable component?** Yes, but modest. Direction is essentially unpredictable; volatility clusters (ARCH-LM p < 1e-8) and today's RV is significantly related to tomorrow's. Out of sample, forecast correlations with RV are only 0.29–0.43, so most day-to-day variation is unexplained.
* **Does GARCH give economically sensible dynamics?** Yes: reactions to shocks of α ≈ 0.07–0.10, high persistence (≈ 0.96 Normal, ≈ 1 with t), half-lives of weeks. That matches a market where volatility episodes are long-lived.
* **Student-t vs Normal?** The t is clearly preferred (ΔAIC ≈ −664; ν̂ ≈ 3.2): Bitcoin's tails are extremely heavy. This matters most for tail measures (VaR/ES), less for the variance recursion itself.
* **What does the RV comparison say about forecast quality?** Useful but far from perfect. GARCH-t beats the expanding RV-OLS on MSE and (significantly) QLIKE, but both are poorly calibrated on average over this OOS period (GARCH +32 %, expanding OLS +82 %) because 2025–26 was calmer than the history used to fit them.
* **Dynamics: GARCH vs RV-OLS.** GARCH is smooth and long-memory; RV-OLS is a jumpy one-lag filter. The extra flexibility is economically sensible (position sizes shouldn't jump with each noisy RV print) and improves QLIKE against the expanding OLS, but it doesn't deliver large or uniform OOS gains.
* **Significance vs OOS performance.** A t-stat of 12.5 on `b` and highly significant GARCH parameters coexisted with only moderate OOS accuracy and unstable parameters. Judge models by OOS loss (QLIKE/MSE, DM tests), not by in-sample significance.
* **Expanding vs rolling.** Rolling (two years) is preferred: it never hurts GARCH significantly and rescues RV-OLS (MSE −33 %, QLIKE −0.16). Distant history is of little use and may mislead.
* **What can the forecasts be used for?** Relative risk scaling (volatility targeting, position sizing, risk limits, margin buffers) and as an input to VaR/ES — together with a heavy-tailed distribution. Not for precise day-by-day point predictions or timing crashes.
* **Main limitation / uncertainty.** (1) Latent variance measured by a noisy proxy; (2) unstable parameters and near-unit-root persistence; (3) conclusions rest on ~600 OOS days in one regime, and many differences are not statistically significant (e.g. rolling GARCH vs rolling RV-OLS, p ≈ 0.07–0.10); (4) the heavy tails mean rare large shocks will still surprise any forecast.

### Executive recommendation (≤ 150 words)
**Implement tomorrow:** a Student-t GARCH(1,1) re-estimated daily on a two-year rolling window, with the rolling RV regression as a cross-check. Use it to scale positions and set risk limits as volatility rises and falls, not as a precise point forecast or crash predictor. Evidence: volatility is clearly predictable in-sample, but out-of-sample forecast correlation with realized variance is only 0.3–0.4, so most daily variation remains unexplained. GARCH beat the expanding regression on QLIKE; the rolling regression scored best but not significantly better than GARCH, and its forecasts jump daily. Estimated persistence is near one, so shocks fade slowly. **Confidence:** moderate for the direction and relative level of risk, low for precise levels. Re-evaluate monthly, keep buffers in limits, and watch for regime shifts.
"""
