import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data import (
    NEIGHBORHOODS, NEIGHBORHOOD_GEOJSON, TRANSPORT, CAR_COSTS, UTILITIES,
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

    expenses["Rent"] = NEIGHBORHOODS[neighborhood][unit_type][style_idx]

    expenses["Utilities"] = (
        UTILITIES["electric_gas_avg"]
        + UTILITIES["internet"]
        + UTILITIES["renters_insurance"]
    )

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

    expenses["Parking"] = parking
    expenses["Groceries"] = FOOD["groceries"][style_key]
    expenses["Dining Out"] = dining_out_frequency * FOOD["dining_out_cost_per_meal"][style_key]
    expenses["Coffee / Cafes"] = FOOD["coffee"][style_key]
    expenses["Healthcare"] = healthcare
    expenses["Gym / Fitness"] = LIFESTYLE["gym"][gym_choice]
    expenses["Streaming"] = sum(LIFESTYLE["streaming"][s] for s in streaming_choices)
    expenses["Entertainment"] = LIFESTYLE["entertainment_misc"][style_key]
    expenses["Personal Care"] = LIFESTYLE["personal_care"][style_key]
    expenses["Clothing"] = LIFESTYLE["clothing"][style_key]

    return expenses


def non_rent_total(expenses):
    """Return total of all expense categories except Rent."""
    return sum(v for k, v in expenses.items() if k != "Rent")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Your Situation")

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

    st.subheader("🚌 Transportation")
    transport_choice = st.selectbox("Primary transport", options=list(TRANSPORT.keys()))
    st.caption(TRANSPORT[transport_choice]["notes"])
    parking = st.slider(
        "Monthly parking cost ($)", min_value=0, max_value=250, value=0, step=10,
        help="Garage, surface lot, or street permit — independent of your transit choice.",
    )

    st.divider()

    st.subheader("🍽️ Food")
    dining_out_frequency = st.slider("Dining out (times / month)", 0, 20, 4)

    st.divider()

    st.subheader("🏥 Healthcare")
    healthcare = st.slider(
        "Monthly healthcare cost ($)", min_value=0, max_value=800, value=150, step=10,
        help="Insurance premiums, copays, prescriptions, dental, vision.",
    )

    st.divider()

    st.subheader("🎬 Lifestyle")
    gym_choice = st.selectbox("Gym / fitness", options=list(LIFESTYLE["gym"].keys()))
    streaming_choices = st.multiselect(
        "Streaming services",
        options=list(LIFESTYLE["streaming"].keys()),
        default=["Netflix", "Spotify"],
    )

    st.divider()

    st.subheader("👤 Household")
    num_people = st.number_input(
        "Number of people", min_value=1, max_value=6, value=1, step=1
    )
    if num_people > 1:
        st.info("Multi-person cost splitting is coming soon!")


# ---------------------------------------------------------------------------
# Compute current neighborhood
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

# ---------------------------------------------------------------------------
# Collapsible: Monthly Breakdown + Chart
# ---------------------------------------------------------------------------

with st.expander("📊 Monthly Breakdown & Spending Chart", expanded=True):
    left_col, right_col = st.columns([1, 1.6])

    with left_col:
        st.subheader("Monthly Breakdown")
        for category, amount in expenses.items():
            if amount > 0:
                pct = (amount / total_monthly) * 100
                st.write(f"**{category}** — ${amount:,.0f}  *({pct:.0f}%)*")
        st.markdown(f"**Total: ${total_monthly:,.0f}**")

    with right_col:
        st.subheader("Spending by Category")
        df = (
            pd.DataFrame({
                "Category": list(expenses.keys()),
                "Amount": list(expenses.values()),
            })
            .query("Amount > 0")
            .sort_values("Amount", ascending=True)
        )
        fig = px.bar(
            df, x="Amount", y="Category", orientation="h",
            text="Amount", color="Amount", color_continuous_scale="Blues",
        )
        fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig.update_layout(
            showlegend=False, coloraxis_showscale=False,
            margin=dict(l=10, r=40, t=10, b=10),
            xaxis_title="$ / month", yaxis_title=None, height=420,
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Required Income Estimator
# ---------------------------------------------------------------------------

with st.expander("💰 Required Income Estimator", expanded=True):
    st.markdown(
        "Based on your selected expenses, here's the gross income you'd need "
        "to comfortably live in this area at different savings targets."
    )

    inc_left, inc_right = st.columns(2)

    with inc_left:
        target_savings_rate = st.select_slider(
            "Target monthly savings rate",
            options=[5, 10, 15, 20, 25, 30],
            value=20,
            format_func=lambda x: f"{x}%",
        )
        tax_rate = st.slider(
            "Estimated effective tax rate (%)",
            min_value=0, max_value=40, value=22, step=1,
            help="Combined federal + state. WI state income tax is ~5-7.65%.",
        )

    with inc_right:
        # Required net monthly to cover expenses + hit savings target
        required_net_monthly = total_monthly / (1 - target_savings_rate / 100)
        required_gross_monthly = required_net_monthly / (1 - tax_rate / 100)
        required_gross_annual = required_gross_monthly * 12

        st.metric("Required Annual Gross Income", f"${required_gross_annual:,.0f}")
        st.metric("Required Monthly Gross", f"${required_gross_monthly:,.0f}")
        st.metric("Monthly After Tax (est.)", f"${required_net_monthly:,.0f}")
        st.metric("Monthly Left After Expenses", f"${required_net_monthly - total_monthly:,.0f}  ({target_savings_rate}% saved)")

    # Benchmark table across savings rates
    st.markdown("**Income required at different savings targets:**")
    rows = []
    for rate in [5, 10, 15, 20, 25, 30]:
        net = total_monthly / (1 - rate / 100)
        gross = net / (1 - tax_rate / 100)
        rows.append({
            "Savings Target": f"{rate}%",
            "Required Annual Gross": f"${gross * 12:,.0f}",
            "Required Monthly Gross": f"${gross:,.0f}",
            "Monthly Savings": f"${net - total_monthly:,.0f}",
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Neighborhood Map
# ---------------------------------------------------------------------------

with st.expander("🗺️ Neighborhood Cost Map", expanded=True):
    st.markdown(
        "Estimated **monthly rent** across Madison neighborhoods for your selected "
        f"unit type (**{unit_type}**) and spending style (**{spending_style}**). "
        "Hover a region for details. Your selected neighborhood is highlighted."
    )

    # Build per-neighborhood data for the map
    map_rows = []
    other_costs = non_rent_total(expenses)

    for nbhd_name, nbhd_data in NEIGHBORHOODS.items():
        rent = nbhd_data[unit_type][style_idx]
        estimated_total = rent + other_costs
        map_rows.append({
            "Neighborhood": nbhd_name,
            "lat": nbhd_data["lat"],
            "lon": nbhd_data["lon"],
            "Monthly Rent": rent,
            "Est. Monthly Total": estimated_total,
        })

    map_df = pd.DataFrame(map_rows)

    fig_map = px.choropleth_map(
        map_df,
        geojson=NEIGHBORHOOD_GEOJSON,
        locations="Neighborhood",
        featureidkey="id",
        color="Monthly Rent",
        color_continuous_scale="RdYlGn_r",
        hover_name="Neighborhood",
        hover_data={
            "Neighborhood": False,
            "Monthly Rent": ":$,.0f",
            "Est. Monthly Total": ":$,.0f",
        },
        zoom=10.5,
        center={"lat": 43.090, "lon": -89.430},
        map_style="carto-positron",
        opacity=0.65,
        height=540,
    )

    # Highlight selected neighborhood with a star at its centroid
    selected_row = map_df[map_df["Neighborhood"] == neighborhood].iloc[0]
    fig_map.add_trace(go.Scattermap(
        lat=[selected_row["lat"]],
        lon=[selected_row["lon"]],
        mode="markers+text",
        marker=dict(size=16, color="gold", symbol="star"),
        text=["◀ You"],
        textposition="middle right",
        textfont=dict(size=13, color="#222"),
        hoverinfo="skip",
        showlegend=False,
    ))

    fig_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(title="Monthly Rent ($)"),
    )

    st.plotly_chart(fig_map, use_container_width=True)

st.divider()

st.caption(
    "Data based on 2024–2025 Madison, WI market estimates. "
    "Rent ranges from Zillow / Apartments.com comps. "
    "Transit costs from Madison Metro. "
    "Utility estimates from MG&E residential averages. "
    "All figures are estimates for planning purposes only."
)
