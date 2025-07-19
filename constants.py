# constants.py

# --- Atlas Earth Parcel Constants ---
# Base rent per second for each parcel type (universal across regions).
# CONFIRMED: 8 zeros after the decimal for the base rates.
PARCEL_RATES_PER_SECOND = {
    "common": 0.0000000011, # 8 zeros
    "rare": 0.0000000016,  # 8 zeros
    "epic": 0.0000000022,  # 8 zeros
    "legendary": 0.0000000044, # 8 zeros
}

# Passport/Badge boost percentages based on badge count.
# Key: Badges required, Value: Boost percentage (e.g., 0.05 for 5%).
BADGE_BOOST_TIERS = {
    0: 0.0, 1: 0.05, 10: 0.10, 15: 0.15, 20: 0.20, 30: 0.25,
    40: 0.30, 50: 0.35, 60: 0.40, 70: 0.45, 80: 0.50, 90: 0.55,
    100: 0.60, 110: 0.65, 120: 0.70, 130: 0.75, 140: 0.80, 150: 0.85,
}

# Regional Ad Boost Multipliers based on total parcel count.
# Derived from the provided country flag images.
# Each region has a list of dictionaries, where each dictionary represents a tier:
# {'min': min_parcels, 'max': max_parcels, 'multiplier': boost_multiplier}
REGIONAL_AD_BOOST_DATA = {
    "United States": [
        {'min': 1, 'max': 150, 'multiplier': 30},
        {'min': 151, 'max': 220, 'multiplier': 20},
        {'min': 221, 'max': 290, 'multiplier': 15},
        {'min': 291, 'max': 365, 'multiplier': 12},
        {'min': 366, 'max': 435, 'multiplier': 10},
        {'min': 436, 'max': 545, 'multiplier': 8},
        {'min': 546, 'max': 625, 'multiplier': 7},
        {'min': 626, 'max': 730, 'multiplier': 6},
        {'min': 731, 'max': 875, 'multiplier': 5},
        {'min': 876, 'max': 1100, 'multiplier': 4},
        {'min': 1101, 'max': 1500, 'multiplier': 3},
        {'min': 1501, 'max': 3000, 'multiplier': 2},
        {'min': 3001, 'max': 6000, 'multiplier': 2}, # Adjusted range to make it distinct
        {'min': 6001, 'max': 999999, 'multiplier': 2}, # Catch-all for higher parcels
    ],
    "Australia, Canada, Ireland, New Zealand, South Africa, United Kingdom": [
        {'min': 1, 'max': 60, 'multiplier': 20},
        {'min': 61, 'max': 100, 'multiplier': 15},
        {'min': 101, 'max': 150, 'multiplier': 10},
        {'min': 151, 'max': 180, 'multiplier': 8},
        {'min': 181, 'max': 220, 'multiplier': 7},
        {'min': 221, 'max': 250, 'multiplier': 6},
        {'min': 251, 'max': 300, 'multiplier': 5},
        {'min': 301, 'max': 350, 'multiplier': 4},
        {'min': 351, 'max': 450, 'multiplier': 3},
        {'min': 451, 'max': 3000, 'multiplier': 2},
        {'min': 3001, 'max': 6000, 'multiplier': 2},
        {'min': 6001, 'max': 999999, 'multiplier': 2},
    ],
    "Mexico": [
        {'min': 1, 'max': 50, 'multiplier': 20},
        {'min': 51, 'max': 85, 'multiplier': 15},
        {'min': 86, 'max': 100, 'multiplier': 12},
        {'min': 101, 'max': 140, 'multiplier': 8},
        {'min': 141, 'max': 175, 'multiplier': 7},
        {'min': 176, 'max': 225, 'multiplier': 5},
        {'min': 226, 'max': 300, 'multiplier': 4},
        {'min': 301, 'max': 1000, 'multiplier': 3},
        {'min': 1001, 'max': 3000, 'multiplier': 2},
        {'min': 3001, 'max': 6000, 'multiplier': 2},
        {'min': 6001, 'max': 999999, 'multiplier': 2},
    ],
    "France, Germany, Italy, Spain": [
        {'min': 1, 'max': 70, 'multiplier': 20},
        {'min': 71, 'max': 100, 'multiplier': 15},
        {'min': 101, 'max': 135, 'multiplier': 10},
        {'min': 136, 'max': 170, 'multiplier': 8},
        {'min': 171, 'max': 200, 'multiplier': 7},
        {'min': 201, 'max': 250, 'multiplier': 6},
        {'min': 251, 'max': 300, 'multiplier': 5},
        {'min': 301, 'max': 350, 'multiplier': 4},
        {'min': 351, 'max': 400, 'multiplier': 3},
        {'min': 401, 'max': 1000, 'multiplier': 2},
        {'min': 1001, 'max': 3000, 'multiplier': 2},
        {'min': 3001, 'max': 6000, 'multiplier': 2},
        {'min': 6001, 'max': 999999, 'multiplier': 2},
    ],
    "Japan, South Korea, United Arab Emirates": [
        {'min': 1, 'max': 50, 'multiplier': 20},
        {'min': 51, 'max': 70, 'multiplier': 15},
        {'min': 71, 'max': 105, 'multiplier': 12},
        {'min': 106, 'max': 130, 'multiplier': 8},
        {'min': 131, 'max': 150, 'multiplier': 7},
        {'min': 151, 'max': 175, 'multiplier': 6},
        {'min': 176, 'max': 200, 'multiplier': 5},
        {'min': 201, 'max': 225, 'multiplier': 4},
        {'min': 226, 'max': 300, 'multiplier': 3},
        {'min': 301, 'max': 1000, 'multiplier': 2},
        {'min': 1001, 'max': 3000, 'multiplier': 2},
        {'min': 3001, 'max': 6000, 'multiplier': 2},
        {'min': 6001, 'max': 999999, 'multiplier': 2},
    ],
    "Brazil": [
        {'min': 1, 'max': 60, 'multiplier': 20},
        {'min': 61, 'max': 75, 'multiplier': 15},
        {'min': 76, 'max': 100, 'multiplier': 12},
        {'min': 101, 'max': 120, 'multiplier': 10},
        {'min': 121, 'max': 150, 'multiplier': 8},
        {'min': 151, 'max': 200, 'multiplier': 6},
        {'min': 201, 'max': 250, 'multiplier': 5},
        {'min': 251, 'max': 300, 'multiplier': 4},
        {'min': 301, 'max': 1000, 'multiplier': 3},
        {'min': 1001, 'max': 3000, 'multiplier': 2},
        {'min': 3001, 'max': 6000, 'multiplier': 2},
        {'min': 6001, 'max': 999999, 'multiplier': 2},
    ],
    "Denmark, Finland, Iceland, Norway, Sweden": [
        {'min': 1, 'max': 30, 'multiplier': 15},
        {'min': 31, 'max': 50, 'multiplier': 12},
        {'min': 51, 'max': 70, 'multiplier': 8},
        {'min': 71, 'max': 105, 'multiplier': 5},
        {'min': 106, 'max': 130, 'multiplier': 4},
        {'min': 131, 'max': 150, 'multiplier': 3},
        {'min': 151, 'max': 250, 'multiplier': 2},
        {'min': 251, 'max': 300, 'multiplier': 2},
        {'min': 301, 'max': 400, 'multiplier': 2},
        {'min': 401, 'max': 1000, 'multiplier': 2},
        {'min': 1001, 'max': 3000, 'multiplier': 2},
        {'min': 3001, 'max': 6000, 'multiplier': 2},
        {'min': 6001, 'max': 999999, 'multiplier': 2},
    ],
}

# Other global constants
SUPER_RENT_BOOST_MULTIPLIER = 50 # 50x for SRB events
PAY_PER_BOOST_SECONDS = 30 # Assumed duration of a single ad boost (e.g., 30 seconds)

# Time constants for calculations
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * 60
SECONDS_PER_DAY = SECONDS_PER_HOUR * 24
SECONDS_PER_WEEK = SECONDS_PER_DAY * 7

# Average days per month/year over a leap year cycle (for long-term projections)
AVG_DAYS_PER_MONTH = 365.25 / 12
AVG_DAYS_PER_YEAR = 365.25

# SRB Event specific constants (for long-term monthly/yearly projections)
SRB_HOURS_PER_MONTH = 64
SRB_HOURS_PER_YEAR = SRB_HOURS_PER_MONTH * 12

# Parcel probabilities for 'mixed' calculations
PARCEL_PROBABILITIES = {
    "common": 0.50, # 50% probability for common parcels
    "rare": 0.30,   # 30% probability for rare parcels
    "epic": 0.15,   # 15% probability for epic parcels
    "legendary": 0.05, # 5% probability for legendary parcels
}