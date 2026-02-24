# Cohort Retention & Activation Analysis
## Executive Summary
This project simulates user-level behavioral data to perform a full cohort-based retention analysis. The objective is to understand early lifecycle patterns that drive long-term retention and identify activation behaviors that significantly impact Month 3 retention.

The analysis demonstrates:
- Clear early retention decay patterns
- Meaningful differences by acquisition channel
- Strong retention lift for early funding (activation)
- A measurable relationship between activation timing and 90-day retention

This framework mirrors retention analytics used by fintech or NEO Banks.

## Business Problem

User retention declines rapidly after signup. The business needs to:

- Quantify retention by cohort
- Understand early drop-off behavior
- Identify activation events (“aha moments”)
- Determine which acquisition channels drive higher quality users
- Prioritize product and lifecycle initiatives to improve Month 3 retention

## Dataset & Simulation
The project uses synthetic user-level event data with:

- Signup month
- Acquisition channel (affiliate, organic, paid search, paid social, referral)
- Funding type (deposit only, direct deposit, no funding)
- Event timestamps
- Days to first funding
The simulation incorporates lifecycle decay and behavioral segmentation to resemble real-world fintech or NEO bank patterns.

## Methodology

1. Generate synthetic users across monthly cohorts
2. Simulate events and funding behavior
3. Assign activation buckets based on days to first funding
4. Compute cohort retention table (Month 0–12)
5. Calculate average retention curve
6. Segment retention by:
    - Acquisition channel
    - Funding segment
    - Activation timing

## Key Insights
1. Retention decay is front-loaded (Months 1–3)
2. Direct deposit is a powerful retention accelerator
3. Early activation (< = 7 days) yields highest retention
4. Referral and organic channels drive higher-quality cohorts
5. No-funding users churn rapidly and potentially dilute long-term LTV

## Decision & Rollout Plan (Evidence-Based)

### Recommendation

Prioritize initiatives that increase early funding activation, with the goal of moving more users into the 0–7 day and 8–14 day activation buckets.

### Why (Backed by Results)

- Month 3 retention is strongly linked to activation timing:
    - 0–7 days  >>  77%
    - 8–14 days >>  71%
    - 15–30 days >> 65%
    - No funding >> 12%

- Funding segment differences are material (direct deposit users retain best; no-funding churns fastest).

- Median time to first funding is 11 days, suggesting there is a realistic window to improve early activation with onboarding + lifecycle nudges.

## Guardrails to Monitor

- 7-day retention rate (early quality check)
- Month 3 retention rate (primary retention outcome in this analysis)
- Direct deposit adoption rate (if product goal is to increase high-retention funding segment)
- Support ticket volume (to ensure onboarding nudges don’t increase friction)

## Rollout Plan (Retention-Focused)

Gradual ramp based on retention measurement windows:

- Pilot (10%): Run for long enough to observe 7-day retention and early activation conversion
- Expand (50%): Continue monitoring Month 3 retention trend vs baseline
- Full rollout (100%): Only if Month 3 retention improves (or remains stable) and guardrails stay healthy

Rollback rule: Pause or revert if Month 3 retention declines beyond a defined threshold vs baseline or if support tickets spike.

## Next Experiment

- A/B test onboarding and lifecycle nudges designed to shorten time-to-funding, for example: “Fund account” CTA sequencing
- Incentives or reminders for direct deposit setup
- Channel-specific onboarding messaging (paid vs organic vs referral)

## Tools & Technologies
Python (core analysis), NumPy (statistical computation), Pandas (data manipulation), Matplotlib/Seaborn (visualization)

## Repository Structure

| File                       | Purpose                                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------------------------------- |
| `01_data_generation.ipynb` | Simulates user-level lifecycle, acquisition channels, funding behavior, and retention decay patterns    |
| `02_cohort_analysis.ipynb` | Performs cohort retention analysis, activation segmentation, funding impact analysis, and visualization |


## Reproducibility
To reproduce the full analysis:
1. Run 01_data_generation.ipynb to generate the synthetic user dataset
2. Run 02_cohort_analysis.ipynb to compute cohort tables and generate all visual outputs
All results, retention curves, segmentation comparisons, and activation metrics are generated programmatically.

## Author
Shamsa Khoja
MS Business Analytics, University of Louisville (2025)
www.linkedin.com/in/shamsakhoja
www.github.com/shamsakhoja
