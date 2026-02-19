# Madison, WI Monthly Expense Estimator — Data Layer
# All values are 2024-2025 estimates for Madison, WI market
# Tuple format: (frugal, moderate, comfortable)

SPENDING_STYLE_INDEX = {"Frugal": 0, "Moderate": 1, "Comfortable": 2}

# ---------------------------------------------------------------------------
# Neighborhoods — rent by unit type, monthly parking cost, description
# ---------------------------------------------------------------------------
NEIGHBORHOODS = {
    "Downtown / Capitol Square": {
        "description": "High walkability, close to State St, restaurants, nightlife, and the Capitol.",
        "parking_monthly": 150,
        "studio": (950, 1150, 1400),
        "1BR":    (1200, 1500, 1900),
        "2BR":    (1700, 2100, 2600),
    },
    "Near East Side": {
        "description": "Trendy and bikeable, close to Willy St Co-op, coffee shops, and the lake path.",
        "parking_monthly": 50,
        "studio": (850, 1000, 1250),
        "1BR":    (1050, 1300, 1600),
        "2BR":    (1400, 1700, 2100),
    },
    "Willy Street / Marquette": {
        "description": "Eclectic and walkable neighborhood between the lakes, strong community feel.",
        "parking_monthly": 50,
        "studio": (850, 1000, 1200),
        "1BR":    (1000, 1250, 1550),
        "2BR":    (1350, 1650, 2000),
    },
    "Isthmus / Broom St": {
        "description": "Dense urban corridor between Lake Mendota and Lake Monona, very central.",
        "parking_monthly": 100,
        "studio": (900, 1100, 1350),
        "1BR":    (1100, 1400, 1750),
        "2BR":    (1500, 1900, 2350),
    },
    "University Ave / Campus Area": {
        "description": "High-density student corridor, very walkable, close to UW and Memorial Union.",
        "parking_monthly": 120,
        "studio": (800, 950, 1150),
        "1BR":    (950, 1200, 1450),
        "2BR":    (1300, 1600, 1950),
    },
    "Middleton": {
        "description": "Western neighbor city, quieter residential feel, good access to West Madison employers.",
        "parking_monthly": 0,
        "studio": (800, 950, 1150),
        "1BR":    (1000, 1200, 1500),
        "2BR":    (1300, 1600, 2000),
    },
    "Monona": {
        "description": "Peaceful lakeside community southeast of Madison, mostly single-family and quiet.",
        "parking_monthly": 0,
        "studio": (750, 900, 1100),
        "1BR":    (950, 1150, 1400),
        "2BR":    (1250, 1500, 1850),
    },
}

# ---------------------------------------------------------------------------
# Transportation
# ---------------------------------------------------------------------------
TRANSPORT = {
    "Metro Bus (monthly pass)": {
        "monthly_fixed": 52,
        "monthly_variable": 0,
        "notes": "Madison Metro unlimited monthly pass (2024 rate)",
    },
    "Own Car": {
        "monthly_fixed": 0,
        "monthly_variable": 0,  # calculated from CAR_COSTS + neighborhood parking
        "notes": "Gas + insurance + maintenance + neighborhood parking",
    },
    "Bike / Walk": {
        "monthly_fixed": 10,
        "monthly_variable": 0,
        "notes": "Maintenance amortized; occasional B-Cycle day pass",
    },
    "Hybrid (Bus + occasional rideshare)": {
        "monthly_fixed": 52,
        "monthly_variable": 60,
        "notes": "Metro pass + Lyft/Uber buffer",
    },
}

CAR_COSTS = {
    "gas_monthly": 80,        # ~$3.20/gal, ~25 mpg, ~625 mi/month
    "insurance_monthly": 105, # WI avg, single adult, good driving record
    "maintenance_monthly": 60, # oil changes, tires, etc. amortized
}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
UTILITIES = {
    "electric_gas_avg": 100,   # MG&E annual monthly average (higher in winter)
    "internet": 65,            # Spectrum or TDS standard tier
    "renters_insurance": 15,   # Wisconsin average
}

# ---------------------------------------------------------------------------
# Food
# ---------------------------------------------------------------------------
FOOD = {
    "groceries": {
        "frugal":      200,  # Aldi, Woodman's, heavy meal prep
        "moderate":    320,  # Mix of Woodman's, Festival Foods, Co-op
        "comfortable": 450,  # Whole Foods, Metro Market, premium items
    },
    "dining_out_cost_per_meal": {
        "frugal":      12,   # fast casual (Ian's Pizza, Chipotle)
        "moderate":    25,   # sit-down (Graze, Habaneros, etc.)
        "comfortable": 45,   # nicer spots (Eno Vino, Merchant, etc.)
    },
    "coffee": {
        "frugal":      20,   # mostly home brew
        "moderate":    50,   # 2-3 cafe visits/week (Ancora, Michelangelo's)
        "comfortable": 90,   # daily cafe habit
    },
}

# ---------------------------------------------------------------------------
# Lifestyle
# ---------------------------------------------------------------------------
LIFESTYLE = {
    "gym": {
        "None":                  0,
        "Planet Fitness":        25,
        "UW SERF (non-student)": 35,
        "Madison YMCA":          52,
        "Anytime Fitness":       40,
        "Boutique Studio":      120,
    },
    "streaming": {
        "Netflix":         17,
        "Spotify":         11,
        "Hulu":            18,
        "Max (HBO)":       16,
        "Disney+":         14,
        "YouTube Premium": 14,
        "Apple TV+":       10,
        "Amazon Prime":    15,
    },
    "entertainment_misc": {
        "frugal":      30,   # free events, parks, Terrace, library
        "moderate":    80,   # bars, Mallards games, Overture Center
        "comfortable": 175,  # concerts, theater, regular nights out
    },
    "personal_care": {
        "frugal":      30,
        "moderate":    60,
        "comfortable": 100,
    },
    "clothing": {
        "frugal":      20,
        "moderate":    60,
        "comfortable": 130,
    },
}

# ---------------------------------------------------------------------------
# Future expansion: per-person scaling factors
# ---------------------------------------------------------------------------
PERSON_SCALING = {
    "rent":          1.0,   # same unit, cost doesn't change
    "utilities":     0.15,  # marginal increase per additional person
    "food":          1.0,   # per-person cost stays the same
    "transport":     1.0,   # per-person cost stays the same
    "entertainment": 0.7,   # some economies of scale (shared streaming, etc.)
}
