"""
cohort_analysis.py

Runs cohort retention / activation analysis and saves figures and outputs.

Run:
  python -m src.cohort_analysis

Notes:
- This file was auto-generated from a Jupyter notebook and lightly cleaned for GitHub use.
"""

from __future__ import annotations

from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# --- Repo paths ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
FIG_DIR = PROJECT_ROOT / "reports" / "figures"

DATA_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    import pandas as pd
    from google.colab import drive
    drive.mount('/content/drive')

    users = pd.read_csv("/content/drive/MyDrive/cohort-retention-analysis/data/users.csv")
    events = pd.read_csv("/content/drive/MyDrive/cohort-retention-analysis/data/events.csv")

    print(users.shape, events.shape)

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import pandas as pd

    # Ensure datetime
    users["signup_date"] = pd.to_datetime(users["signup_date"])
    events["event_ts"] = pd.to_datetime(events["event_ts"])

    # Cohort month (signup month)
    users["cohort_month"] = users["signup_date"].dt.to_period("M").dt.to_timestamp()

    # Event month (activity month)
    events["event_month"] = events["event_ts"].dt.to_period("M").dt.to_timestamp()

    # Join cohort_month onto events
    events = events.merge(users[["user_id", "cohort_month"]], on="user_id", how="left")

    # Cohort index = months since signup cohort (0 = signup month)
    events["cohort_index"] = (
        (events["event_month"].dt.year - events["cohort_month"].dt.year) * 12
        + (events["event_month"].dt.month - events["cohort_month"].dt.month)
    )

    print(events[["user_id", "cohort_month", "event_month", "cohort_index"]].head())
    print("cohort_index min/max:", events["cohort_index"].min(), events["cohort_index"].max())

    # -----------------------------
    # Notebook logic
    # -----------------------------

    events.head(20)

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # STEP 3: Build Retention Table
    # ---------------------------------

    # 1 Count unique active users by cohort + cohort_index
    cohort_data = (
        events.groupby(["cohort_month", "cohort_index"])["user_id"]
        .nunique()
        .reset_index()
    )

    cohort_data.head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # 2️ Pivot into matrix format
    cohort_pivot = cohort_data.pivot(
        index="cohort_month",
        columns="cohort_index",
        values="user_id"
    )

    cohort_pivot.head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # 3️ Get cohort sizes (Month 0 users)
    cohort_sizes = cohort_pivot.iloc[:, 0]

    # 4️ Divide by cohort size to get retention rate
    retention_table = cohort_pivot.divide(cohort_sizes, axis=0)

    retention_table.head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    retention_display = (retention_table * 100).round(1).astype(str) + "%"
    retention_display.head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import numpy as np
    import matplotlib.pyplot as plt

    # --- choose display window ---
    max_month = 12                    # show cohort_index 0..12
    last_n_cohorts = 18               # show most recent 18 signup cohorts

    ret = (retention_table * 100).round(1)

    # Keep only desired columns/rows
    ret = ret.loc[:, ret.columns <= max_month]
    ret = ret.tail(last_n_cohorts)

    # Mask missing cells (these are cohorts that haven't reached that month yet)
    masked = np.ma.masked_invalid(ret.values)

    plt.figure(figsize=(13, 7))
    cmap = plt.cm.viridis.copy()
    cmap.set_bad(color="lightgray")   # color for missing cells

    img = plt.imshow(masked, aspect="auto", cmap=cmap, vmin=0, vmax=100)
    plt.colorbar(img, label="Retention (%)")

    plt.title("Cohort Retention Heatmap (Monthly)")
    plt.xlabel("Months Since Signup (Cohort Index)")
    plt.ylabel("Signup Cohort Month")

    # Ticks
    plt.xticks(ticks=np.arange(ret.shape[1]), labels=ret.columns.tolist())
    plt.yticks(
        ticks=np.arange(ret.shape[0]),
        labels=[d.strftime("%Y-%m") for d in ret.index]
    )

    # Annotate only first 0..6 months (keeps it readable)
    annot_upto = min(12, ret.shape[1])
    for i in range(ret.shape[0]):
        for j in range(annot_upto):
            val = ret.iat[i, j]
            if not np.isnan(val):
                plt.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=8)

    plt.tight_layout()
    plt.savefig("/content/drive/MyDrive/cohort-retention-analysis/figures/cohort_heatmap.png")
    plt.show()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import matplotlib.pyplot as plt

    # Compute average retention across cohorts
    avg_retention = retention_table.mean()

    # Limit to first 12 months
    avg_retention = avg_retention.loc[avg_retention.index <= 12] * 100

    plt.figure(figsize=(8, 5))
    plt.plot(avg_retention.index, avg_retention.values, marker="o")

    plt.title("Average Monthly Retention Curve")
    plt.xlabel("Months Since Signup")
    plt.ylabel("Retention (%)")
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("/content/drive/MyDrive/cohort-retention-analysis/figures/retention_curve.png")
    plt.show()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # Merge acquisition channel onto events
    events = events.merge(
        users[["user_id", "acquisition_channel"]],
        on="user_id",
        how="left"
    )

    events[["user_id", "acquisition_channel"]].head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # STEP 6: Retention by Acquisition Channel
    # ---------------------------------

    # Count unique active users by channel + cohort_index
    channel_data = (
        events.groupby(["acquisition_channel", "cohort_index"])["user_id"]
        .nunique()
        .reset_index(name="active_users")
    )

    # Get total users per channel (Month 0 baseline)
    channel_sizes = (
        users.groupby("acquisition_channel")["user_id"]
        .nunique()
    )

    # Pivot into matrix
    channel_pivot = channel_data.pivot(
        index="acquisition_channel",
        columns="cohort_index",
        values="active_users"
    )

    # Convert to retention rate
    channel_retention = channel_pivot.divide(channel_sizes, axis=0)

    channel_retention.head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))

    for channel in channel_retention.index:
        plt.plot(
            channel_retention.columns,
            channel_retention.loc[channel] * 100,
            marker='o',
            label=channel
        )

    plt.title("Retention Curves by Acquisition Channel")
    plt.xlabel("Months Since Signup")
    plt.ylabel("Retention (%)")
    plt.legend()
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import numpy as np
    import matplotlib.pyplot as plt

    # Limit to first 6 months for readability
    max_month = 6
    retention_subset = channel_retention.loc[:, :max_month] * 100

    channels = retention_subset.index
    months = retention_subset.columns

    x = np.arange(len(months))
    width = 0.8 / len(channels)  # dynamic bar width

    plt.figure(figsize=(10, 6))

    for i, channel in enumerate(channels):
        plt.bar(
            x + i * width,
            retention_subset.loc[channel],
            width=width,
            label=channel
        )

    plt.xticks(x + width * (len(channels) - 1) / 2, months)
    plt.xlabel("Months Since Signup")
    plt.ylabel("Retention (%)")
    plt.title("Retention by Acquisition Channel (First 6 Months)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # STEP 8A: Create funding segment
    # ---------------------------------

    # Identify deposit users
    deposit_users = events[events["event_name"] == "deposit"]["user_id"].unique()

    # Identify direct deposit users
    dd_users = events[events["event_name"] == "direct_deposit_received"]["user_id"].unique()

    def funding_segment(user_id):
        if user_id in dd_users:
            return "direct_deposit"
        elif user_id in deposit_users:
            return "deposit_only"
        else:
            return "no_funding"

    users["funding_segment"] = users["user_id"].apply(funding_segment)

    users["funding_segment"].value_counts()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # STEP 8B: Retention by Funding Segment
    # ---------------------------------

    # Merge funding segment onto events
    events = events.merge(
        users[["user_id", "funding_segment"]],
        on="user_id",
        how="left"
    )

    # Count active users by funding segment + cohort_index
    funding_data = (
        events.groupby(["funding_segment", "cohort_index"])["user_id"]
        .nunique()
        .reset_index(name="active_users")
    )

    # Get total users per funding segment
    funding_sizes = (
        users.groupby("funding_segment")["user_id"]
        .nunique()
    )

    # Pivot
    funding_pivot = funding_data.pivot(
        index="funding_segment",
        columns="cohort_index",
        values="active_users"
    )

    # Convert to retention rate
    funding_retention = funding_pivot.divide(funding_sizes, axis=0)

    funding_retention.head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import numpy as np
    import matplotlib.pyplot as plt

    # Limit to first 6 months
    max_month = 12
    funding_subset = funding_retention.loc[:, :max_month] * 100

    segments = funding_subset.index
    months = funding_subset.columns

    x = np.arange(len(months))
    width = 0.8 / len(segments)

    plt.figure(figsize=(10, 6))

    for i, segment in enumerate(segments):
        plt.bar(
            x + i * width,
            funding_subset.loc[segment],
            width=width,
            label=segment
        )

    plt.xticks(x + width * (len(segments) - 1) / 2, months)
    plt.xlabel("Months Since Signup")
    plt.ylabel("Retention (%)")
    plt.title("Retention by Funding Segment (First 6 Months)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("/content/drive/MyDrive/cohort-retention-analysis/figures/funding_retention.png")
    plt.show()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # STEP 8D: 3-Month Retention Comparison
    # ---------------------------------

    month = 3

    retention_3m = (funding_retention[month] * 100).round(1)

    print("3-Month Retention by Funding Segment:")
    print(retention_3m)

    # Calculate lift vs no_funding
    baseline = retention_3m["no_funding"]

    lift = (retention_3m - baseline).round(1)

    print("\nLift vs No Funding:")
    print(lift)

    # -----------------------------
    # Notebook logic
    # -----------------------------

    cohort_sizes = (
        users.groupby("cohort_month")["user_id"]
        .nunique()
        .sort_index()
    )

    cohort_sizes.head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import matplotlib.pyplot as plt
    import pandas as pd

    # Ensure datetime index
    cohort_sizes.index = pd.to_datetime(cohort_sizes.index)

    # Rolling average
    rolling_avg = cohort_sizes.rolling(window=3).mean()

    plt.figure(figsize=(12, 6))

    # Bars
    plt.bar(
        cohort_sizes.index,
        cohort_sizes.values,
        alpha=0.6
    )

    # Trend line
    plt.plot(
        rolling_avg.index,
        rolling_avg.values,
        color="black",
        linewidth=3,
        label="3-Month Rolling Avg"
    )

    plt.title("Monthly Cohort Size with Trend")
    plt.xlabel("Signup Month")
    plt.ylabel("Number of Users")

    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Notebook logic
    # -----------------------------



    month = 3

    month3_retention = (retention_table[month] * 100).round(1)

    month3_retention.head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import matplotlib.pyplot as plt
    import pandas as pd

    # Ensure datetime index
    month3_retention.index = pd.to_datetime(month3_retention.index)

    # Rolling average for smoothing
    rolling_avg = month3_retention.rolling(window=3).mean()

    plt.figure(figsize=(12, 6))

    # Bars (actual values)
    plt.bar(
        month3_retention.index,
        month3_retention.values,
        alpha=0.6
    )

    # Trend line
    plt.plot(
        rolling_avg.index,
        rolling_avg.values,
        color="black",
        linewidth=3,
        label="3-Month Rolling Avg"
    )

    plt.title("Month 3 Retention by Signup Cohort")
    plt.xlabel("Signup Month")
    plt.ylabel("Retention (%)")

    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Notebook logic
    # -----------------------------


    # First funding timestamp per user
    first_funding = (
        events[events["event_name"].isin(["deposit", "direct_deposit_received"])]
        .groupby("user_id")["event_ts"]
        .min()
    )

    # Merge onto users
    users = users.merge(
        first_funding.rename("first_funding_ts"),
        on="user_id",
        how="left"
    )

    # Calculate days to activation
    users["days_to_funding"] = (
        users["first_funding_ts"] - users["signup_date"]
    ).dt.days

    users[["user_id", "days_to_funding"]].head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import matplotlib.pyplot as plt
    import numpy as np

    # Remove users who never funded
    funded_users = users["days_to_funding"].dropna()

    plt.figure(figsize=(10, 5))

    plt.hist(
        funded_users,
        bins=30
    )

    plt.title("Distribution of Days to First Funding")
    plt.xlabel("Days Since Signup")
    plt.ylabel("Number of Users")

    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    print("Median days to funding:", int(np.median(funded_users)))
    print("Mean days to funding:", round(np.mean(funded_users), 1))

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # STEP 4A: Activation Speed Buckets
    # ---------------------------------

    def activation_bucket(days):
        if pd.isna(days):
            return "no_funding"
        elif days <= 7:
            return "0-7 days"
        elif days <= 14:
            return "8-14 days"
        else:
            return "15-30 days"

    users["activation_bucket"] = users["days_to_funding"].apply(activation_bucket)

    users["activation_bucket"].value_counts()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # STEP 4B: 3-Month Retention by Activation Speed
    # ---------------------------------

    bucket_order = ["0-7 days", "8-14 days", "15-30 days", "no_funding"]
    users["activation_bucket"] = pd.Categorical(users["activation_bucket"], categories=bucket_order, ordered=True)

    # Month 3 window = days 60–89 since signup
    users["signup_date"] = pd.to_datetime(users["signup_date"])
    events["event_ts"] = pd.to_datetime(events["event_ts"])

    events_m = events.merge(users[["user_id", "signup_date"]], on="user_id", how="left")
    events_m["days_since_signup"] = (events_m["event_ts"] - events_m["signup_date"]).dt.days

    active_month3 = events_m.loc[
        (events_m["days_since_signup"] >= 60) & (events_m["days_since_signup"] < 90),
        "user_id"
    ].unique()

    users["active_month3"] = users["user_id"].isin(active_month3)

    activation_retention = (
        users.groupby("activation_bucket", observed=True)["active_month3"]
        .mean().mul(100).round(0).fillna(0).astype(int).astype(str) + "%"
    )

    activation_retention

    # -----------------------------
    # Notebook logic
    # -----------------------------

    activation_retention_numeric = (
        activation_retention.astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    activation_retention_numeric = pd.to_numeric(activation_retention_numeric, errors="coerce")

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import os
    import matplotlib.pyplot as plt

    os.makedirs("figures", exist_ok=True)

    plt.figure(figsize=(8,5))
    activation_retention_numeric.plot(kind="bar")

    plt.title("Month 3 Retention by Activation Timing")
    plt.xlabel("Activation Bucket")
    plt.ylabel("Month 3 Retention (%)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("/content/drive/MyDrive/cohort-retention-analysis/figures/activation_bucket.png")
    plt.show()


if __name__ == "__main__":
    main()
