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

# Global styles: expander header size + allow sticky positioning inside Streamlit's layout
st.markdown("""
<style>
details summary p,
.streamlit-expanderHeader p {
    font-size: 1.15rem !important;
    font-weight: 600 !important;
}
/* Unset overflow so position:sticky works inside Streamlit's block container */
.appview-container .main .block-container {
    overflow: unset !important;
}
/* Sticky summary bar */
#summary-bar {
    position: -webkit-sticky;
    position: sticky;
    top: 3.2rem;
    z-index: 9900;
    background: #ffffff;
    border-bottom: 2px solid #dee2e6;
    border-radius: 0 0 8px 8px;
    padding: 12px 24px;
    margin-bottom: 1rem;
    box-shadow: 0 3px 10px rgba(0,0,0,0.10);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 28px;
}
[data-theme="dark"] #summary-bar {
    background: #0e1117;
    border-bottom-color: #333;
}
.summary-label {
    font-size: 0.7em;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 2px;
}
.summary-value {
    font-size: 1.65em;
    font-weight: 700;
    color: #111;
    line-height: 1.1;
}
.summary-caption {
    color: #555;
    font-size: 0.88em;
    border-left: 2px solid #dee2e6;
    padding-left: 24px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state — lets map clicks update the neighborhood selectbox
# ---------------------------------------------------------------------------
if "neighborhood" not in st.session_state:
    st.session_state.neighborhood = list(NEIGHBORHOODS.keys())[0]
if "_map_click" not in st.session_state:
    st.session_state._map_click = None

# Apply any pending map-click selection BEFORE widgets are rendered
if st.session_state._map_click is not None:
    st.session_state.neighborhood = st.session_state._map_click
    st.session_state._map_click = None

# ---------------------------------------------------------------------------
# Calculation engine
# ---------------------------------------------------------------------------

def compute_expenses(
    neighborhood, unit_type, style_idx, transport_choice,
    dining_out_frequency, gym_choice, streaming_choices,
    healthcare, parking, other_entertainment,
):
    style_key = ["frugal", "moderate", "comfortable"][style_idx]
    expenses = {}

    nbhd_data = NEIGHBORHOODS[neighborhood]
    expenses["Rent"] = nbhd_data[unit_type][style_idx]

    # Energy scales by neighborhood building age/efficiency and unit size;
    # internet and renters insurance are flat regardless of location or unit size.
    utility_factor = nbhd_data.get("utility_factor", 1.0)
    unit_energy_factor = {"studio": 0.80, "1BR": 1.0, "2BR": 1.22}[unit_type]
    expenses["Utilities"] = round(
        UTILITIES["electric_gas_avg"] * utility_factor * unit_energy_factor
        + UTILITIES["internet"]
        + UTILITIES["renters_insurance"]
    )

    t = TRANSPORT[transport_choice]
    if transport_choice == "Own Car":
        transport_cost = (
            CAR_COSTS["gas_monthly"]
            + CAR_COSTS["insurance_monthly"]
            + CAR_COSTS["maintenance_monthly"]
        )
    else:
        transport_cost = t["monthly_fixed"] + t["monthly_variable"]
    expenses["Transportation"] = transport_cost

    expenses["Parking"] = parking
    expenses["Groceries"] = round(FOOD["groceries"][style_key] * nbhd_data.get("grocery_factor", 1.0))
    expenses["Dining Out"] = dining_out_frequency * FOOD["dining_out_cost_per_meal"][style_key]
    expenses["Coffee / Cafes"] = FOOD["coffee"][style_key]
    expenses["Healthcare"] = healthcare
    expenses["Gym / Fitness"] = LIFESTYLE["gym"][gym_choice]
    expenses["Streaming"] = sum(LIFESTYLE["streaming"][s] for s in streaming_choices)
    expenses["Entertainment"] = LIFESTYLE["entertainment_misc"][style_key]
    expenses["Other Entertainment"] = other_entertainment
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
    st.title("Your Living Preferences")

    st.subheader("🏠 Housing")
    _HIDDEN = {"Allied / Dunn's Marsh"}
    _nbhd_opts = [n for n in NEIGHBORHOODS if n not in _HIDDEN]
    neighborhood = st.selectbox(
        "Neighborhood",
        options=_nbhd_opts,
        index=_nbhd_opts.index(st.session_state.neighborhood),
    )
    st.session_state.neighborhood = neighborhood  # keep in sync with map clicks
    st.caption(NEIGHBORHOODS[neighborhood]["description"])
    unit_type_display = st.radio("Unit type", options=["Studio", "1BR", "2BR"], index=1, horizontal=True)
    unit_type = "studio" if unit_type_display == "Studio" else unit_type_display
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
        help="Garage, lot, or street permit. Typical ranges: Downtown $100–150, east/west sides $30–60, suburban $0.",
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
    other_entertainment = st.slider(
        "Other entertainment ($/month)", min_value=0, max_value=300, value=0, step=10,
        help="Concert tickets, events, hobbies, sports, etc.",
    )

    st.divider()

    st.subheader("💰 Annual Savings")
    annual_cash_savings = st.select_slider(
        "Annual cash savings target",
        options=[0, 5000, 10000, 15000, 20000, 25000, 30000],
        value=5000,
        format_func=lambda x: f"${x:,}",
    )
    annual_retirement = st.select_slider(
        "Annual pre-tax retirement savings",
        options=[0, 5000, 10000, 15000, 20000, 25000, 30000],
        value=0,
        format_func=lambda x: f"${x:,}",
    )
    tax_rate = st.slider(
        "Effective tax rate (%)", min_value=15, max_value=30, value=20, step=1,
        help="Rough guide: Low income = 17%,  Middle income = 23%,  High income = 30%",
    )



# ---------------------------------------------------------------------------
# Compute current neighborhood
# ---------------------------------------------------------------------------

expenses = compute_expenses(
    neighborhood, unit_type, style_idx, transport_choice,
    dining_out_frequency, gym_choice, streaming_choices,
    healthcare, parking, other_entertainment,
)

total_monthly = sum(expenses.values())
total_annual = total_monthly * 12

# Required income (computed here so sticky bar can display it)
monthly_cash_savings = annual_cash_savings / 12
monthly_retirement = annual_retirement / 12
net_needed = total_monthly + monthly_cash_savings
taxable_gross_monthly = net_needed / (1 - tax_rate / 100)
required_gross_monthly = taxable_gross_monthly + monthly_retirement
required_gross_annual = required_gross_monthly * 12

# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

st.title("🏙️ Madison, WI Monthly Expense Estimator")

# Sticky summary bar
st.markdown(
    f"""
    <div id="summary-bar">
        <div>
            <div class="summary-label">Total Monthly Exp</div>
            <div class="summary-value">${total_monthly:,.0f}</div>
        </div>
        <div>
            <div class="summary-label">Total Annual Exp</div>
            <div class="summary-value">${total_annual:,.0f}</div>
        </div>
        <div>
            <div class="summary-label">Est. Annual Income Needed</div>
            <div class="summary-value">${required_gross_annual:,.0f}</div>
        </div>
        <div class="summary-caption">
            <b>{neighborhood}</b> &nbsp;·&nbsp; {unit_type_display} &nbsp;·&nbsp; {spending_style} &nbsp;·&nbsp; {transport_choice.split('(')[0].strip()}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Collapsible: Monthly Spending Chart
# ---------------------------------------------------------------------------

with st.expander("📊 Monthly Spending Chart", expanded=True):
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
        margin=dict(l=10, r=80, t=10, b=10),
        xaxis_title="$ / month", yaxis_title=None, height=460,
        xaxis=dict(range=[0, df["Amount"].max() * 1.35]),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Required Income Estimator
# ---------------------------------------------------------------------------

with st.expander("💰 Required Income Estimator", expanded=True):
    st.markdown(
        "Based on your expenses and savings goals (set in the sidebar), "
        "here's the gross income you'd need to comfortably live in this area."
    )

    st.metric("Required Annual Gross Income", f"${required_gross_annual:,.0f}")
    st.metric("Required Monthly Gross", f"${required_gross_monthly:,.0f}")
    st.metric("Monthly Left After Taxes/Expenses", f"${monthly_cash_savings:,.0f}  (cash savings)")

st.divider()

# ---------------------------------------------------------------------------
# Neighborhood Map
# ---------------------------------------------------------------------------

with st.expander("🗺️ Neighborhood Cost Map", expanded=True):
    st.markdown(
        "Estimated **monthly total cost** across Madison neighborhoods for your selected "
        f"unit type (**{unit_type_display}**) and spending style (**{spending_style}**). "
        "Hover a region for details. Your selected neighborhood is highlighted."
    )

    # Build per-neighborhood data for the map
    map_rows = []
    other_costs = non_rent_total(expenses)

    for nbhd_name, nbhd_data in NEIGHBORHOODS.items():
        if nbhd_name in _HIDDEN:
            continue
        rent = nbhd_data[unit_type][style_idx]
        estimated_total = rent + other_costs + nbhd_data.get("non_rent_adj", 0)
        map_rows.append({
            "Neighborhood": nbhd_name,
            "lat": nbhd_data["lat"],
            "lon": nbhd_data["lon"],
            "Monthly Rent": rent,
            "Non-rent Exp": estimated_total - rent,
            "Est. Monthly Total": estimated_total,
        })

    map_df = pd.DataFrame(map_rows)

    fig_map = px.choropleth_map(
        map_df,
        geojson=NEIGHBORHOOD_GEOJSON,
        locations="Neighborhood",
        featureidkey="id",
        color="Est. Monthly Total",
        color_continuous_scale=[
            [0.0, "#6ec050"],   # deep green           (low cost)
            [0.5, "#ffd633"],   # rich gold-yellow     (median)
            [1.0, "#ff9a00"],   # deep amber-orange    (high cost)
        ],
        hover_name="Neighborhood",
        hover_data={
            "Neighborhood": False,
            "Monthly Rent": ":$,.0f",
            "Non-rent Exp": ":$,.0f",
            "Est. Monthly Total": ":$,.0f",
        },
        zoom=11.0,
        center={"lat": 43.075, "lon": -89.420},
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
        coloraxis_colorbar=dict(title="Est. Monthly Total ($)"),
    )

    event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", key="nbhd_map")
    # If the user clicked a neighborhood polygon, update the selectbox
    try:
        if event.selection.points:
            clicked = event.selection.points[0].get("location")
            if clicked and clicked in NEIGHBORHOODS and clicked != st.session_state.neighborhood:
                st.session_state._map_click = clicked
                st.rerun()
    except AttributeError:
        pass

st.divider()

st.caption(
    "Data based on 2024–2025 Madison, WI market estimates. "
    "Rent ranges from Zillow / Apartments.com comps. "
    "Transit costs from Madison Metro. "
    "Utility estimates from MG&E residential averages. "
    "All figures are estimates for planning purposes only."
)
