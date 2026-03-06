# Comparative Study: Islamic vs Conventional Banking Risk

## 1) Research question
This project evaluates whether Islamic banks display different leverage and stability patterns relative to conventional peers.

Primary questions:
1. Are Islamic banks less leveraged than conventional banks?
2. Do Islamic banks perform differently during systemic stress periods?
3. How does the profit-and-loss sharing orientation affect risk outcomes?

## 2) Motivation
Islamic banks are constrained by Shariah principles, including the prohibition of interest (riba), stronger asset-backing requirements, and greater emphasis on risk sharing. These features may influence balance-sheet structure, funding composition, and resilience.

## 3) Institutions and sample design
### Islamic examples
- **Al Rajhi Bank** (Saudi Arabia)
- **Dubai Islamic Bank** (UAE)

### Conventional comparison group
Use a matched peer set by:
- geography (GCC/MENA markets first, then broader EM/DM peers),
- size (total assets quantiles),
- business model (retail-focused vs universal bank),
- listing status and reporting frequency.

### Suggested panel setup
- Frequency: annual or quarterly.
- Horizon: at least 10 years if available (to capture normal and stress episodes).
- Unit: bank-year (or bank-quarter).

## 4) Variables
### Core dependent variables (risk/stability)
- **Leverage ratio** = Total liabilities / Total equity.
- **Capital adequacy proxy** = Equity / Total assets.
- **Z-score proxy for stability** = (ROA + Equity/Assets) / sd(ROA).
- **NPL ratio** = Non-performing loans / Gross loans.

### Explanatory variables
- **Islamic dummy** = 1 if Islamic bank, else 0.
- **Crisis dummy** = 1 in crisis years (e.g., 2008-2009, 2020), else 0.
- **Islamic × Crisis interaction** to test differential stress performance.

### Controls
- Bank size (log total assets),
- profitability (ROA),
- liquidity ratio,
- macro controls (GDP growth, inflation, policy rate if relevant).

## 5) Econometric approach
### Baseline fixed-effects panel
\[
Risk_{i,t} = \alpha + \beta_1 Islamic_i + \beta_2 Crisis_t + \beta_3(Islamic_i \times Crisis_t) + \gamma X_{i,t} + \mu_i + \lambda_t + \epsilon_{i,t}
\]

Where:
- \(\mu_i\): bank fixed effects,
- \(\lambda_t\): time fixed effects,
- clustered SEs by bank.

Interpretation:
- \(\beta_1\): structural difference in normal periods,
- \(\beta_3\): relative resilience/vulnerability of Islamic banks in crises.

## 6) Data sources (recommended)
- Banks' annual reports / investor relations.
- Regulatory datasets (central banks, IMF FSI where available).
- Commercial datasets (if accessible): Fitch Connect, S&P Capital IQ, Bloomberg.
- Market indicators: World Bank, IMF, FRED, OECD.

## 7) Expected outputs
1. **Descriptive statistics table** by bank type.
2. **Trend figures** for leverage, ROA, and capital ratios.
3. **Panel regression table** with FE specifications.
4. **Crisis subsample robustness checks**.

## 8) Interpretation guide
Evidence supporting lower risk among Islamic banks would include:
- lower leverage,
- higher equity-to-assets,
- higher Z-score,
- better relative outcomes in crisis years (positive/less negative interaction effect).

## 9) CV signal
This project demonstrates:
- applied econometrics (panel methods),
- financial statement ratio construction,
- policy-relevant comparison of banking models,
- domain knowledge in Islamic finance and risk management.

## 10) Limitations and extensions
- Classification nuances (hybrid business models).
- Accounting comparability across jurisdictions.
- Endogeneity concerns (selection into Islamic model).

Possible extensions:
- Difference-in-differences around specific regulatory reforms,
- propensity-score matched sample,
- alternative stability metrics (distance-to-default, market-based risk).
