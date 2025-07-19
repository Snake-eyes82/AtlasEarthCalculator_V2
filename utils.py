# utils.py

import constants

def get_passport_boost_multiplier(num_passports):
    """
    Calculates the passport boost multiplier based on the number of passports.
    Uses BADGE_BOOST_TIERS from constants.
    """
    if num_passports < 1:
        return 1.0 # No boost for 0 passports
    
    # Iterate through sorted badge tiers to find the highest applicable boost
    # The tiers are defined as {badge_count: boost_percentage}
    tier_boost_percentage = 0.0
    for tier_count, boost_percent in sorted(constants.BADGE_BOOST_TIERS.items()):
        if num_passports >= tier_count:
            tier_boost_percentage = boost_percent
        else:
            # Since tiers are sorted, if num_passports is less than the current tier_count,
            # it means we've passed the highest applicable tier.
            break 
    return 1.0 + tier_boost_percentage

def get_ad_boost_multiplier(total_parcels, region):
    """
    Returns the ad boost multiplier based on total parcels and selected region.
    Uses REGIONAL_AD_BOOST_DATA from constants.
    """
    region_data = constants.REGIONAL_AD_BOOST_DATA.get(region)
    if not region_data:
        # Fallback to United States data if the selected region's data is missing
        # This should ideally not happen if REGIONAL_AD_BOOST_DATA is complete
        region_data = constants.REGIONAL_AD_BOOST_DATA.get("United States", [])
        if not region_data: # If even US data is missing, return default 1x
            return 1.0

    for tier in region_data:
        if tier['min'] <= total_parcels <= tier['max']:
            return tier['multiplier']
    return 1.0 # Default if no tier matches (e.g., very high parcel count beyond defined tiers)

def get_total_rent_multiplier(total_parcels, badge_count, selected_region, force_srb=False, fictive_badge_enabled=False, fictive_badge_percent=0.0):
    """
    Calculates the total multiplier for rent, combining ad boost (dynamic or SRB) and badge boost.
    This is the multiplier applied to the base rent per second.
    """
    # Get the dynamic ad boost multiplier based on parcel count and region
    ad_boost_multiplier = get_ad_boost_multiplier(total_parcels, selected_region)
    
    # If Super Rent Boost is explicitly forced, override the ad boost multiplier
    if force_srb:
        ad_boost_multiplier = constants.SUPER_RENT_BOOST_MULTIPLIER

    # Calculate badge boost, potentially using a fictive value for "what-if" scenarios
    badge_multiplier_factor = get_passport_boost_multiplier(badge_count)
    if fictive_badge_enabled:
        # If fictive boost is enabled, override the badge multiplier
        badge_multiplier_factor = 1.0 + fictive_badge_percent

    return ad_boost_multiplier * badge_multiplier_factor

def calculate_base_earnings_per_second(parcel_counts):
    """
    Calculates the raw base earnings per second from owned parcels,
    before any multipliers (ad boost, badge boost) are applied.
    """
    total_base_rent = 0
    for p_type, count in parcel_counts.items():
        rate = constants.PARCEL_RATES_PER_SECOND.get(p_type, 0.0)
        total_base_rent += count * rate
    return total_base_rent

def convert_seconds_to_timeframe(seconds_value, timeframe_unit):
    """
    Converts a per-second value to the specified timeframe unit (e.g., 'day', 'month').
    """
    if timeframe_unit == "second":
        return seconds_value
    elif timeframe_unit == "minute":
        return seconds_value * constants.SECONDS_PER_MINUTE
    elif timeframe_unit == "hour":
        return seconds_value * constants.SECONDS_PER_HOUR
    elif timeframe_unit == "day":
        return seconds_value * constants.SECONDS_PER_DAY
    elif timeframe_unit == "week":
        return seconds_value * constants.SECONDS_PER_WEEK
    elif timeframe_unit == "month":
        return seconds_value * constants.AVG_DAYS_PER_MONTH * constants.SECONDS_PER_DAY
    elif timeframe_unit == "year":
        return seconds_value * constants.AVG_DAYS_PER_YEAR * constants.SECONDS_PER_DAY
    else:
        raise ValueError(f"Invalid timeframe unit: {timeframe_unit}")

def get_seconds_in_timeframe(timeframe_unit):
    """
    Returns the total number of seconds in a given timeframe unit.
    """
    if timeframe_unit == "second":
        return 1
    elif timeframe_unit == "minute":
        return constants.SECONDS_PER_MINUTE
    elif timeframe_unit == "hour":
        return constants.SECONDS_PER_HOUR
    elif timeframe_unit == "day":
        return constants.SECONDS_PER_DAY
    elif timeframe_unit == "week":
        return constants.SECONDS_PER_WEEK
    elif timeframe_unit == "month":
        return constants.AVG_DAYS_PER_MONTH * constants.SECONDS_PER_DAY
    elif timeframe_unit == "year":
        return constants.AVG_DAYS_PER_YEAR * constants.SECONDS_PER_DAY
    else:
        raise ValueError(f"Invalid timeframe unit: {timeframe_unit}")

def calculate_average_mixed_parcel_rate_per_second():
    """
    Calculates the weighted average base earnings per second for a 'mixed' parcel,
    based on PARCEL_PROBABILITIES, before any boosts.
    """
    avg_rate = 0
    for parcel_type, rate in constants.PARCEL_RATES_PER_SECOND.items():
        avg_rate += rate * constants.PARCEL_PROBABILITIES[parcel_type]
    return avg_rate
