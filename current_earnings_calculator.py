# current_earnings_calculator.py

import tkinter as tk
from tkinter import ttk, messagebox

import constants
import utils

class CurrentEarningsCalculator:
    def __init__(self, parent_frame, get_user_inputs_callback):
        self.parent_frame = parent_frame
        self.get_user_inputs_callback = get_user_inputs_callback

        self._create_widgets()

    def _create_widgets(self):
        row = 0
        header_font = ("Helvetica", 10, "bold")
        value_font = ("Courier", 10) # Courier is a monospace font, vital for number alignment

        # Headers for clarity, now aligned over their columns
        ttk.Label(self.parent_frame, text="Timeframe", font=header_font).grid(row=row, column=0, sticky="w", pady=2, padx=5)
        ttk.Label(self.parent_frame, text="Base Earnings", font=header_font, anchor="e").grid(row=row, column=1, sticky="e", pady=2, padx=5)
        ttk.Label(self.parent_frame, text="With Ad Boost", font=header_font, anchor="e").grid(row=row, column=2, sticky="e", pady=2, padx=5)
        row += 1

        self.earnings_output_labels = {}
        timeframes = ["Second", "Minute", "Hour", "Day", "Week", "Month", "Year"]
        
        for i, tf in enumerate(timeframes):
            # Timeframe label
            ttk.Label(self.parent_frame, text=f"Per {tf}:", font=value_font).grid(row=row + i, column=0, sticky="w", pady=1, padx=5)
            
            # Base Earnings column - now explicitly in column 1
            base_value_label = ttk.Label(self.parent_frame, text="$0.0000000000", anchor="e", font=value_font)
            base_value_label.grid(row=row + i, column=1, sticky="ew", pady=1, padx=(5,5))
            self.earnings_output_labels[f"{tf.lower()}_base"] = base_value_label
            
            # With Ad Boost column - now explicitly in column 2
            boosted_value_label = ttk.Label(self.parent_frame, text="$0.0000000000", anchor="e", font=value_font)
            boosted_value_label.grid(row=row + i, column=2, sticky="ew", pady=1, padx=(5,5))
            self.earnings_output_labels[f"{tf.lower()}_boosted"] = boosted_value_label

        # Configure columns to expand
        # Column 0 (Timeframe) does not expand much
        # Columns 1 and 2 (Base Earnings, With Ad Boost) expand equally
        self.parent_frame.grid_columnconfigure(0, weight=0, minsize=100) # Timeframe column, fixed width
        self.parent_frame.grid_columnconfigure(1, weight=1, minsize=180) # Base Earnings column, expands, increased minsize
        self.parent_frame.grid_columnconfigure(2, weight=1, minsize=180) # With Ad Boost column, expands, increased minsize

    def update_display(self):
        inputs = self.get_user_inputs_callback()
        if inputs is None:
            self._clear_labels()
            return

        parcels = inputs["parcels"]
        total_parcels = inputs["total_parcels"]
        boost_hours = inputs["boost_hours"]
        badge_count = inputs["badge_count"]
        srb_boost_enabled = inputs["srb_boost_enabled"]
        fictive_badge_enabled = inputs["fictive_badge_boost_enabled"]
        fictive_badge_percent = inputs["fictive_badge_boost_percent"]
        selected_region = inputs["selected_region"]

        # --- Base Earnings Calculation (Raw) ---
        raw_base_earnings_per_second = utils.calculate_base_earnings_per_second(parcels)

        # --- Earnings Per Second AFTER Permanent Badge Boost (Base for 'With Ad Boost' calculations) ---
        badge_multiplier = utils.get_passport_boost_multiplier(badge_count)
        if fictive_badge_enabled:
            # Fictive percentage should be treated as a decimal (e.g., 0.25 for 25%)
            badge_multiplier = 1.0 + (fictive_badge_percent / 100.0)
        
        earnings_per_second_after_badges = raw_base_earnings_per_second * badge_multiplier

        # --- Determine the Instantaneous Ad Boost Multiplier ---
        effective_ad_multiplier = 1.0 # Default to 1x if no ad boost or no parcels
        if total_parcels > 0: # Only get a relevant multiplier if parcels exist
            if srb_boost_enabled:
                effective_ad_multiplier = constants.SUPER_RENT_BOOST_MULTIPLIER
            else:
                effective_ad_multiplier = utils.get_ad_boost_multiplier(total_parcels, selected_region)

        # --- Calculate Average Daily Earnings for "With Ad Boost" Column (Short Timeframes) ---
        final_boosted_earnings_per_second = earnings_per_second_after_badges # Default if no boost_hours

        if boost_hours > 0:
            # Rate during boosted hours
            rate_during_ad_boosted_time = earnings_per_second_after_badges * effective_ad_multiplier
            
            # Calculate weighted average based on hours in a 24-hour day
            total_seconds_in_day = constants.SECONDS_PER_DAY
            boosted_seconds = boost_hours * constants.SECONDS_PER_HOUR
            unboosted_seconds = total_seconds_in_day - boosted_seconds

            # Ensure no negative seconds if boost_hours somehow exceeds 24
            if unboosted_seconds < 0:
                unboosted_seconds = 0
                boosted_seconds = total_seconds_in_day # Cap boosted seconds at a full day

            final_boosted_earnings_per_second = (rate_during_ad_boosted_time * boosted_seconds + \
                                                earnings_per_second_after_badges * unboosted_seconds) / total_seconds_in_day
        
        # --- Update Labels for Short Timeframes (Second, Minute, Hour, Day, Week) ---
        timeframes_for_direct_calc = ["second", "minute", "hour", "day", "week"]
        for tf in timeframes_for_direct_calc:
            # "Base Earnings" column shows earnings with only permanent badge boost
            self.earnings_output_labels[f"{tf}_base"].config(
                text=f"${utils.convert_seconds_to_timeframe(earnings_per_second_after_badges, tf):.10f}"
            )
            # "With Ad Boost" column shows the time-averaged earnings (including hourly boost)
            self.earnings_output_labels[f"{tf}_boosted"].config(
                text=f"${utils.convert_seconds_to_timeframe(final_boosted_earnings_per_second, tf):.10f}"
            )

        # --- Monthly and Yearly Calculations for "With Ad Boost" Column ---
        # These calculations factor in both user-defined boost_hours and potential global SRB events (if not forced by user)

        # Define the rates based on the earnings after permanent badge boost
        rate_unboosted_time_actual = earnings_per_second_after_badges
        rate_normal_ad_boosted_time_actual = earnings_per_second_after_badges * effective_ad_multiplier # Use the determined multiplier
        rate_srb_boosted_time_actual = earnings_per_second_after_badges * constants.SUPER_RENT_BOOST_MULTIPLIER

        monthly_ad_boosted_earnings = 0
        yearly_ad_boosted_earnings = 0

        if srb_boost_enabled: # User has checked "Force Super Rent Boost (50x)"
            # If forced, all 'boosted' time based on user input is at 50x. Ignore global SRB constants.
            total_boosted_seconds_daily = boost_hours * constants.SECONDS_PER_HOUR
            total_unboosted_seconds_daily = constants.SECONDS_PER_DAY - total_boosted_seconds_daily

            # Ensure no negative seconds if boost_hours > 24
            if total_unboosted_seconds_daily < 0:
                total_unboosted_seconds_daily = 0
                total_boosted_seconds_daily = constants.SECONDS_PER_DAY

            # Calculate monthly/yearly based purely on user's forced 50x hours
            monthly_ad_boosted_earnings = (rate_srb_boosted_time_actual * total_boosted_seconds_daily * constants.AVG_DAYS_PER_MONTH) + \
                                        (rate_unboosted_time_actual * total_unboosted_seconds_daily * constants.AVG_DAYS_PER_MONTH)
            
            yearly_ad_boosted_earnings = (rate_srb_boosted_time_actual * total_boosted_seconds_daily * constants.AVG_DAYS_PER_YEAR) + \
                                        (rate_unboosted_time_actual * total_unboosted_seconds_daily * constants.AVG_DAYS_PER_YEAR)
        elif boost_hours == 0: # FIX: If no ad boost hours AND not forcing SRB, then show base earnings (after badges)
            monthly_ad_boosted_earnings = utils.convert_seconds_to_timeframe(earnings_per_second_after_badges, 'month')
            yearly_ad_boosted_earnings = utils.convert_seconds_to_timeframe(earnings_per_second_after_badges, 'year')
        else: # User has NOT checked "Force Super Rent Boost (50x)" and has boost_hours > 0
            # Account for user's normal daily ad boost AND global SRB events
            user_boosted_seconds_daily = boost_hours * constants.SECONDS_PER_HOUR
            
            # Monthly Calculation
            total_monthly_seconds = constants.AVG_DAYS_PER_MONTH * constants.SECONDS_PER_DAY
            srb_seconds_monthly = constants.SRB_HOURS_PER_MONTH * constants.SECONDS_PER_HOUR

            # Calculate normal boosted and unboosted time for the month
            # This assumes SRB time takes precedence, then user's boost, then unboosted
            
            # Total seconds from user's daily boost over the month
            monthly_user_boosted_seconds = user_boosted_seconds_daily * constants.AVG_DAYS_PER_MONTH
            
            # Time remaining after accounting for fixed SRB hours
            remaining_seconds_monthly = total_monthly_seconds - srb_seconds_monthly
            
            # Normal boosted time is the lesser of user's total boosted time or remaining time
            normal_boosted_seconds_monthly_capped = min(monthly_user_boosted_seconds, remaining_seconds_monthly)
            
            unboosted_seconds_monthly = total_monthly_seconds - srb_seconds_monthly - normal_boosted_seconds_monthly_capped
            if unboosted_seconds_monthly < 0: unboosted_seconds_monthly = 0 # Defensive check

            monthly_ad_boosted_earnings = \
                (rate_unboosted_time_actual * unboosted_seconds_monthly) + \
                (rate_normal_ad_boosted_time_actual * normal_boosted_seconds_monthly_capped) + \
                (rate_srb_boosted_time_actual * srb_seconds_monthly)

            # Yearly Calculation (similar logic)
            total_yearly_seconds = constants.AVG_DAYS_PER_YEAR * constants.SECONDS_PER_DAY
            srb_seconds_yearly = constants.SRB_HOURS_PER_YEAR * constants.SECONDS_PER_HOUR

            # Total seconds from user's daily boost over the year
            yearly_user_boosted_seconds = user_boosted_seconds_daily * constants.AVG_DAYS_PER_YEAR

            # Time remaining after accounting for fixed SRB hours
            remaining_seconds_yearly = total_yearly_seconds - srb_seconds_yearly
            
            # Normal boosted time is the lesser of user's total boosted time or remaining time
            normal_boosted_seconds_yearly_capped = min(yearly_user_boosted_seconds, remaining_seconds_yearly)
            
            unboosted_seconds_yearly = total_yearly_seconds - srb_seconds_yearly - normal_boosted_seconds_yearly_capped
            if unboosted_seconds_yearly < 0: unboosted_seconds_yearly = 0 # Defensive check

            yearly_ad_boosted_earnings = \
                (rate_unboosted_time_actual * unboosted_seconds_yearly) + \
                (rate_normal_ad_boosted_time_actual * normal_boosted_seconds_yearly_capped) + \
                (rate_srb_boosted_time_actual * srb_seconds_yearly)

        # --- Update Monthly and Yearly Labels ---
        self.earnings_output_labels["month_base"].config(text=f"${utils.convert_seconds_to_timeframe(earnings_per_second_after_badges, 'month'):.8f}")
        self.earnings_output_labels["month_boosted"].config(text=f"${monthly_ad_boosted_earnings:.8f}")

        self.earnings_output_labels["year_base"].config(text=f"${utils.convert_seconds_to_timeframe(earnings_per_second_after_badges, 'year'):.8f}")
        self.earnings_output_labels["year_boosted"].config(text=f"${yearly_ad_boosted_earnings:.8f}")


    def get_export_data(self):
        """Returns the current earnings data in a dictionary format for export."""
        data = {}
        timeframes = ["second", "minute", "hour", "day", "week", "month", "year"]
        for tf in timeframes:
            data[tf] = {
                'base': self.earnings_output_labels[f"{tf}_base"].cget("text"),
                'boosted': self.earnings_output_labels[f"{tf}_boosted"].cget("text")
            }
        return data

    def _clear_labels(self):
        for label in self.earnings_output_labels.values():
            label.config(text="$0.0000000000")