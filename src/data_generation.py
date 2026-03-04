"""
data_generation.py

Generates synthetic data files used for cohort retention and activation analysis.

Run:
  python -m src.data_generation

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
    from google.colab import drive
    drive.mount('/content/drive')

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import pandas as pd
    import numpy as np

    np.random.seed(42)

    # -----------------------
    # CONFIG
    # -----------------------
    n_users = 20000
    start_date = "2023-05-01"
    end_date = "2025-06-30"

    # -----------------------
    # USER IDs
    # -----------------------
    user_ids = [f"U_{i}" for i in range(1, n_users + 1)]

    # -----------------------
    # Signup Dates (spread over 18 months)
    # -----------------------
    signup_dates = pd.to_datetime(
        np.random.choice(
            pd.date_range(start_date, end_date),
            size=n_users
        )
    )

    # -----------------------
    # Acquisition Channels (realistic distribution)
    # -----------------------
    channels = np.random.choice(
        ["paid_search", "paid_social", "organic", "referral", "affiliate"],
        size=n_users,
        p=[0.30, 0.25, 0.20, 0.15, 0.10]
    )

    # -----------------------
    # Device Type
    # -----------------------
    devices = np.random.choice(
        ["ios", "android", "web"],
        size=n_users,
        p=[0.45, 0.40, 0.15]
    )

    # -----------------------
    # Country
    # -----------------------
    countries = np.random.choice(
        ["US", "CA", "UK"],
        size=n_users,
        p=[0.80, 0.10, 0.10]
    )

    # -----------------------
    # Build DataFrame
    # -----------------------
    users = pd.DataFrame({
        "user_id": user_ids,
        "signup_date": signup_dates,
        "acquisition_channel": channels,
        "device_type": devices,
        "country": countries
    })

    users.head()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    users.shape

    # -----------------------------
    # Notebook logic
    # -----------------------------

    #Creating user engagment

    import pandas as pd
    import numpy as np

    np.random.seed(42)

    # We'll collect all events here, then convert to a DataFrame at the end
    events_list = []

    def add_event(user_id, ts, event_name, amount=0.0):
        """Append a single event row to our events_list."""
        events_list.append([user_id, ts, event_name, float(amount)])

    # Events our fintech app can generate
    EVENTS = [
        "app_open",
        "login",
        "deposit",
        "card_swipe",
        "invest_trade",
        "loan_apply",
        "referral_sent",
    ]

    # Channel-based engagement multipliers (simple way to make cohorts differ)
    channel_boost = {
        "referral": 1.20,
        "organic": 1.05,
        "paid_search": 0.95,
        "paid_social": 0.85,
        "affiliate": 0.90
    }

    print("Defined events + function. Ready to generate per-user sequences.")

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # PART 2: Mandatory Onboarding
    # ---------------------------------

    for _, row in users.iterrows():

        user_id = row["user_id"]
        signup_date = pd.to_datetime(row["signup_date"])

        # App open happens within first few hours
        app_open_time = signup_date + pd.Timedelta(hours=np.random.randint(0, 4))
        add_event(user_id, app_open_time, "app_open")

        # Login happens AFTER app open (1–6 hours later)
        login_time = app_open_time + pd.Timedelta(hours=np.random.randint(1, 6))
        add_event(user_id, login_time, "login")

    print("Onboarding events generated.")

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # PART 3: Activation within 30 days
    # (Activation = funding event: deposit OR direct_deposit_received)
    # ---------------------------------

    activation_map = {}          # user_id -> True/False
    act_day_map = {}
    users["days_to_funding"] = np.nan
    funding_type_map = {}        # user_id -> "deposit" | "direct_deposit_received" | None

    for _, row in users.iterrows():
        user_id = row["user_id"]
        signup_date = pd.to_datetime(row["signup_date"])
        channel = row["acquisition_channel"]

        # Probability user funds within 30 days (varies by channel)
        base_p = 0.55
        p_activate = base_p * channel_boost[channel]
        p_activate = float(np.clip(p_activate, 0.15, 0.90))

        activated = (np.random.rand() < p_activate)
        activation_map[user_id] = activated

        if activated:
            # Funding occurs within 30 days
            #act_day = np.random.randint(0, 30)
            act_day = int(np.random.beta(2, 3) * 30)
            act_day_map[user_id] = act_day
            users.loc[users["user_id"] == user_id, "days_to_funding"] = act_day
            act_time = signup_date + pd.Timedelta(days=act_day,
                                                  hours=np.random.randint(8, 22))

            # Most fund via deposit; smaller % via payroll deposit
            act_event = np.random.choice(
                ["deposit", "direct_deposit_received"],
                p=[0.85, 0.15]
            )

            funding_type_map[user_id] = act_event

            if act_event == "deposit":
                amt = np.round(np.random.exponential(150) + 25, 2)
                add_event(user_id, act_time, "deposit", amount=amt)

            else:
                # Payroll deposits are larger
                amt = np.round(np.random.exponential(800) + 300, 2)
                add_event(user_id, act_time, "direct_deposit_received", amount=amt)

        else:
            funding_type_map[user_id] = None
            act_day_map[user_id] = np.nan
            users.loc[users["user_id"] == user_id, "days_to_funding"] = np.nan

    print("Activation funding events added within 30-day window.")

    # -----------------------------
    # Notebook logic
    # -----------------------------

    users["days_to_funding"].isna().mean()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    users["days_to_funding"].dropna().describe()

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # PART 4: Lifespan + Ongoing Activity (with sequencing rules)
    # ---------------------------------


    # Build events df once (faster + cleaner)
    events_df = pd.DataFrame(events_list, columns=["user_id", "event_ts", "event_name", "amount"])
    events_df["event_ts"] = pd.to_datetime(events_df["event_ts"])

    # Helper: first funding time per user (if any)
    first_funding_ts = (
        events_df.query("event_name in ['deposit','direct_deposit_received']")
                 .groupby("user_id")["event_ts"].min()
    )

    for _, row in users.iterrows():
        user_id = row["user_id"]
        signup_date = pd.to_datetime(row["signup_date"])
        channel = row["acquisition_channel"]

        activated = activation_map.get(user_id, False)
        funding_type = funding_type_map.get(user_id, None)  # deposit / direct_deposit_received / None
        funding_ts = first_funding_ts.get(user_id, pd.NaT)

        # Activation timing (must exist from Part 3; safe default)
        act_day = act_day_map.get(user_id, 999)

        # ---- Lifespan logic with activation timing effect ----
        if not activated:
            lifespan_days = int(np.clip(np.random.normal(60, 25), 14, 180))
        else:
            # Base lifespan depending on funding type
            if funding_type == "direct_deposit_received":
                base_lifespan = np.random.gamma(shape=2.5, scale=75)
            else:
                base_lifespan = np.random.gamma(shape=2.0, scale=60)

            # Timing effect
            if act_day <= 3:
                timing_multiplier = 1.15
            elif act_day <= 7:
                timing_multiplier = 1.05
            elif act_day <= 14:
                timing_multiplier = 0.95
            else:
                timing_multiplier = 0.85

            lifespan_days = int(np.clip(base_lifespan * timing_multiplier, 30, 365))

        # ---- Session volume (for everyone) ----
        base_monthly_sessions = (9 if activated else 2.5)

        # Direct deposit tends to increase engagement
        if funding_type == "direct_deposit_received":
            base_monthly_sessions *= 1.3

        base_monthly_sessions *= channel_boost[channel]  # Poisson generates realistic counts

        total_sessions = int(np.clip(
            np.random.poisson(base_monthly_sessions * (lifespan_days / 30)),
            1 if not activated else 3,
            300
        ))

        # ---- Generate ongoing events ----
        for _ in range(total_sessions):
            day_offset = np.random.randint(0, lifespan_days + 1)
            event_time = signup_date + pd.Timedelta(days=day_offset, hours=np.random.randint(0, 24))


            # Insert Month 3 event gate

            days_since_signup = (event_time - signup_date).days

            if 60 <= days_since_signup < 90:  # Month 3 window
                if not activated:
                    if np.random.rand() > 0.20:  # 20% chance active in M3
                        continue
                else:
                    if act_day <= 7:
                          p_active_m3 = 0.80
                    elif act_day <= 14:
                          p_active_m3 = 0.65
                    else:
                          p_active_m3 = 0.50

                    if np.random.rand() > p_active_m3:
                          continue

            # If user is not funded yet, restrict to lightweight events
            if pd.isna(funding_ts) or (event_time < funding_ts):
                event_name = np.random.choice(["app_open", "login"], p=[0.55, 0.45])
                amount = 0.0
                add_event(user_id, event_time, event_name, amount)
                continue

            # After funding, allow card swipes + occasional extra deposits
            event_name = np.random.choice(
                ["app_open", "login", "card_swipe", "deposit"],
                p=[0.35, 0.35, 0.25, 0.05]
            )

            if event_name == "deposit":
                amount = np.round(np.random.exponential(160) + 15, 2)
            elif event_name == "card_swipe":
                amount = np.round(np.random.exponential(28) + 1, 2)
            else:
                amount = 0.0

            add_event(user_id, event_time, event_name, amount)

    print("Ongoing engagement generated with rule: card_swipe only after funding.")

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # PART 5: Late-stage events (loan_apply, referral_sent)
    # ---------------------------------

    for _, row in users.iterrows():
        user_id = row["user_id"]
        signup_date = pd.to_datetime(row["signup_date"])
        channel = row["acquisition_channel"]

        activated = activation_map[user_id]
        funding_type = funding_type_map[user_id]

        # Only funded users can realistically apply for loans / refer
        if not activated:
            continue

        # Loan application: more likely for direct deposit users (stronger relationship)
        base_loan_p = 0.06
        if funding_type == "direct_deposit_received":
            base_loan_p = 0.10

        loan_p = base_loan_p * channel_boost[channel]
        loan_p = float(np.clip(loan_p, 0.01, 0.25))

        if np.random.rand() < loan_p:
            # Happens after day 14, within first 180 days (or earlier if user churns early)
            loan_day = np.random.randint(14, 180)
            loan_time = signup_date + pd.Timedelta(days=loan_day, hours=np.random.randint(10, 18))
            add_event(user_id, loan_time, "loan_apply", amount=0.0)

        # Referral sent: small probability; higher for referral/organic users
        base_ref_p = 0.04
        if channel in ["referral", "organic"]:
            base_ref_p = 0.06

        ref_p = base_ref_p * (1.1 if funding_type == "direct_deposit_received" else 1.0)
        ref_p = float(np.clip(ref_p, 0.01, 0.20))

        if np.random.rand() < ref_p:
            ref_day = np.random.randint(10, 200)
            ref_time = signup_date + pd.Timedelta(days=ref_day, hours=np.random.randint(10, 20))
            add_event(user_id, ref_time, "referral_sent", amount=0.0)

    print("Late-stage events added (loan_apply, referral_sent).")

    # -----------------------------
    # Notebook logic
    # -----------------------------

    #create events in data frame and sort
    events = pd.DataFrame(events_list, columns=["user_id", "event_ts", "event_name", "amount"])
    events["event_ts"] = pd.to_datetime(events["event_ts"])
    events = events.sort_values(["user_id", "event_ts"]).reset_index(drop=True)

    events.head(), events.shape

    # -----------------------------
    # Notebook logic
    # -----------------------------

    # ---------------------------------
    # STEP 5: Apply analysis cutoff date
    # ---------------------------------

    analysis_end_date = pd.to_datetime("2025-12-31")

    # Remove events beyond observation window
    events = events[events["event_ts"] <= analysis_end_date].copy()

    # Optional: also remove users who signed up after cutoff
    users = users[users["signup_date"] <= analysis_end_date].copy()

    print("After applying cutoff:")
    print("users:", users.shape)
    print("events:", events.shape)
    print("New event date range:",
          events["event_ts"].min(),
          "to",
          events["event_ts"].max())

    # -----------------------------
    # Notebook logic
    # -----------------------------

    import os

    project_path = "/content/drive/MyDrive/cohort-retention-analysis"
    data_path = os.path.join(project_path, "data")
    os.makedirs(data_path, exist_ok=True)

    users_file = os.path.join(data_path, "{str(DATA_DIR / "users.csv")}")
    events_file = os.path.join(data_path, "{str(DATA_DIR / "events.csv")}")

    users.to_csv(users_file, index=False)
    events.to_csv(events_file, index=False)

    print("Saved:")
    print(users_file)
    print(events_file)

    print("Quick checks:")
    print("users:", users.shape, "| events:", events.shape)
    print("date range events:", events["event_ts"].min(), "to", events["event_ts"].max())
    print("unique users in events:", events["user_id"].nunique())


if __name__ == "__main__":
    main()
