import streamlit as st
import plotly.express as px
import pandas as pd

from data import (
    NEIGHBORHOODS, TRANSPORT, CAR_COSTS, UTILITIES,
    FOOD, LIFESTYLE, SPENDING_STYLE_INDEX,
)

st.set_page_config(
    page_title="Madison, WI Expense Estimator",
    page_icon="🏙️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Calculation engine
# ---------------------------------------------------------------------------

def compute_expenses(
    neighborhood, unit_type, style_idx, transport_choice,
    dining_out_frequency, gym_choice, streaming_choices,
    healthcare, parking, num_people,
):
    style_key = ["frugal", "moderate", "comfortable"][style_idx]
    expenses = {}

    # Rent
    expenses["Rent"] = NEIGHBORHOODS[neighborhood][unit_type][style_idx]

    # Utilities
    expenses["Utilities"] = (
        UTILITIES["electric_gas_avg"]
        + UTILITIES["internet"]
        + UTILITIES["renters_insurance"]
    )

    # Transportation
    t = TRANSPORT[transport_choice]
    if transport_choice == "Own Car":
        neighborhood_parking = NEIGHBORHOODS[neighborhood]["parking_monthly"]
        transport_cost = (
            CAR_COSTS["gas_monthly"]
            + CAR_COSTS["insurance_monthly"]
            + CAR_COSTS["maintenance_monthly"]
            + neighborhood_parking
        )
    else:
        transport_cost = t["monthly_fixed"] + t["monthly_variable"]
    expenses["Transportation"] = transport_cost

    # Parking (independent slider — user may pay for a spot regardless of transit choice)
    expenses["Parking"] = parking

    # Groceries
    expenses["Groceries"] = FOOD["groceries"][style_key]

    # Dining out
    cost_per_meal = FOOD["dining_out_cost_per_meal"][style_key]
    expenses["Dining Out"] = dining_out_frequency * cost_per_meal

    # Coffee
    expenses["Coffee / Cafes"] = FOOD["coffee"][style_key]

    # Healthcare
    expenses["Healthcare"] = healthcare

    # Gym
    expenses["Gym / Fitness"] = LIFESTYLE["gym"][gym_choice]

    # Streaming
    expenses["Streaming"] = sum(LIFESTYLE["streaming"][s] for s in streaming_choices)

    # Entertainment
    expenses["Entertainment"] = LIFESTYLE["entertainment_misc"][style_key]

    # Personal care
    expenses["Personal Care"] = LIFESTYLE["personal_care"][style_key]

    # Clothing
    expenses["Clothing"] = LIFESTYLE["clothing"][style_key]

    return expenses


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Your Situation")

    # Housing
    st.subheader("🏠 Housing")
    neighborhood = st.selectbox("Neighborhood", options=list(NEIGHBORHOODS.keys()))
    st.caption(NEIGHBORHOODS[neighborhood]["description"])

    unit_type = st.radio("Unit type", options=["studio", "1BR", "2BR"], horizontal=True)

    spending_style = st.select_slider(
        "Spending style",
        options=["Frugal", "Moderate", "Comfortable"],
        value="Moderate",
    )
    style_idx = SPENDING_STYLE_INDEX[spending_style]

    st.divider()

    # Transportation
    st.subheader("🚌 Transportation")
    transport_choice = st.selectbox("Primary transport", options=list(TRANSPORT.keys()))
    st.caption(TRANSPORT[transport_choice]["notes"])

    parking = st.slider(
        "Monthly parking cost ($)",
        min_value=0, max_value=250, value=0, step=10,
        help="Garage, surface lot, or street permit — independent of your transit choice.",
    )

    st.divider()

    # Food
    st.subheader("🍽️ Food")
    dining_out_frequency = st.slider("Dining out (times / month)", 0, 20, 4)

    st.divider()

    # Health
    st.subheader("🏥 Healthcare")
    healthcare = st.slider(
        "Monthly healthcare cost ($)",
        min_value=0, max_value=800, value=150, step=10,
        help="Insurance premiums, copays, prescriptions, dental, vision.",
    )

    st.divider()

    # Lifestyle
    st.subheader("🎬 Lifestyle")
    gym_choice = st.selectbox("Gym / fitness", options=list(LIFESTYLE["gym"].keys()))

    streaming_choices = st.multiselect(
        "Streaming services",
        options=list(LIFESTYLE["streaming"].keys()),
        default=["Netflix", "Spotify"],
    )

    st.divider()

    # Household
    st.subheader("👤 Household")
    num_people = st.number_input(
        "Number of people", min_value=1, max_value=6, value=1, step=1
    )
    if num_people > 1:
        st.info("Multi-person cost splitting is coming soon!")


# ---------------------------------------------------------------------------
# Compute
# ---------------------------------------------------------------------------

expenses = compute_expenses(
    neighborhood, unit_type, style_idx, transport_choice,
    dining_out_frequency, gym_choice, streaming_choices,
    healthcare, parking, num_people,
)

total_monthly = sum(expenses.values())
total_annual = total_monthly * 12

# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

st.title("🏙️ Madison, WI Monthly Expense Estimator")
st.caption(
    f"**{neighborhood}** · {unit_type} · {spending_style} lifestyle · "
    f"{transport_choice.split('(')[0].strip()}"
)

# Summary metrics
col1, col2, col3 = st.columns(3)
col1.metric("Monthly Total", f"${total_monthly:,.0f}")
col2.metric("Annual Total", f"${total_annual:,.0f}")
col3.metric("Daily Average", f"${total_monthly / 30.44:.0f}")

st.divider()

# Breakdown + chart
left_col, right_col = st.columns([1, 1.6])

with left_col:
    st.subheader("Monthly Breakdown")
    for category, amount in expenses.items():
        if amount > 0:
            pct = (amount / total_monthly) * 100
            st.write(f"**{category}** — ${amount:,.0f}  *(${pct:.0f}%)*")
    st.markdown(f"**Total: ${total_monthly:,.0f}**")

with right_col:
    st.subheader("Spending by Category")
    df = (
        pd.DataFrame({"Category": list(expenses.keys()), "Amount": list(expenses.values())})
        .query("Amount > 0")
        .sort_values("Amount", ascending=True)
    )

    fig = px.bar(
        df,
        x="Amount",
        y="Category",
        orientation="h",
        text="Amount",
        color="Amount",
        color_continuous_scale="Blues",
    )
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=10, r=40, t=10, b=10),
        xaxis_title="$ / month",
        yaxis_title=None,
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Savings Goal
# ---------------------------------------------------------------------------

st.subheader("💰 Savings Goal")

income_col, savings_col = st.columns(2)

with income_col:
    gross_income = st.number_input(
        "Monthly gross income ($)",
        min_value=0, max_value=50000, value=5000, step=100, format="%d",
    )
    tax_rate = st.slider(
        "Estimated effective tax rate (%)", min_value=0, max_value=40, value=22, step=1
    )

with savings_col:
    net_income = gross_income * (1 - tax_rate / 100)
    monthly_savings = net_income - total_monthly
    savings_rate = (monthly_savings / net_income * 100) if net_income > 0 else 0

    st.metric("Est. Net Monthly Income", f"${net_income:,.0f}")
    st.metric(
        "Projected Monthly Savings",
        f"${monthly_savings:,.0f}",
        delta=f"{savings_rate:.1f}% savings rate",
    )
    st.metric("Projected Annual Savings", f"${monthly_savings * 12:,.0f}")

    if monthly_savings < 0:
        st.error("Expenses exceed net income at current settings.")
    elif savings_rate < 10:
        st.warning("Savings rate below 10% — consider adjusting spending.")
    elif savings_rate >= 20:
        st.success("Solid savings rate — on track for financial health!")

st.divider()

st.caption(
    "Data based on 2024–2025 Madison, WI market estimates. "
    "Rent ranges from Zillow / Apartments.com comps. "
    "Transit costs from Madison Metro. "
    "Utility estimates from MG&E residential averages. "
    "All figures are estimates for planning purposes only."
)
