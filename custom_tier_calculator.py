# custom_tier_calculator.py

import tkinter as tk
from tkinter import ttk, messagebox
from widgets import IntegerEntry

import constants
import utils

class CustomTierCalculator:
    def __init__(self, parent_frame, get_user_inputs_callback):
        self.parent_frame = parent_frame
        self.get_user_inputs_callback = get_user_inputs_callback

        # Tkinter variables for inputs and outputs specific to this tab
        self.custom_parcel_count_var = tk.StringVar(value="0") # Input for custom parcel count
        self.custom_ad_boost_multiplier_label = None
        self.custom_base_earnings_label = None
        self.custom_boosted_earnings_label = None

        self._create_widgets()

    def _create_widgets(self):
        # Input for Custom Parcel Count
        input_frame = ttk.LabelFrame(self.parent_frame, text="Custom Parcel Tier Input")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Enter Custom Parcel Count:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Use a standard Tkinter Entry for now, and bind its update.
        # If the IntegerEntry from main.py becomes a shared utility, we can refactor.
        #self.custom_parcel_entry = ttk.Entry(input_frame, width=10, textvariable=self.custom_parcel_count_var)
        self.custom_parcel_entry = IntegerEntry(input_frame, width=10, textvariable=self.custom_parcel_count_var)
        self.custom_parcel_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        # self.custom_parcel_entry.bind("<KeyRelease>", self._on_input_change) # Update on key release
        # self.custom_parcel_entry.bind("<FocusOut>", self._on_input_change)   # Update on losing focus
        # self.custom_parcel_entry.bind("<Return>", self._on_input_change)     # Update on Enter key

        # Output Section
        output_frame = ttk.LabelFrame(self.parent_frame, text="Custom Tier Calculations")
        output_frame.pack(padx=10, pady=10, fill="x")

        header_font = ("Helvetica", 10, "bold")
        value_font = ("Courier", 10) # Monospace font for numerical alignment

        # Headers
        ttk.Label(output_frame, text="Metric", font=header_font).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(output_frame, text="Value", font=header_font, anchor="e").grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        row_idx = 1

        # Ad Boost Multiplier
        ttk.Label(output_frame, text="Ad Boost Multiplier:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=1)
        self.custom_ad_boost_multiplier_label = ttk.Label(output_frame, text="N/A", anchor="e", font=value_font)
        self.custom_ad_boost_multiplier_label.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=1)
        row_idx += 1

        # Base Earnings (per month, assuming 24/7 unboosted)
        ttk.Label(output_frame, text="Est. Base Monthly Earnings:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=1)
        self.custom_base_earnings_label = ttk.Label(output_frame, text="$0.00", anchor="e", font=value_font)
        self.custom_base_earnings_label.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=1)
        row_idx += 1

        # Boosted Earnings (per month, assuming 24/7 boosted at custom tier)
        ttk.Label(output_frame, text="Est. Boosted Monthly Earnings:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=1)
        self.custom_boosted_earnings_label = ttk.Label(output_frame, text="$0.00", anchor="e", font=value_font)
        self.custom_boosted_earnings_label.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=1)
        row_idx += 1

        # Configure columns to expand
        output_frame.grid_columnconfigure(0, weight=0, minsize=180)
        output_frame.grid_columnconfigure(1, weight=1, minsize=150)

    # def _on_input_change(self, event=None):
    #     """Called when the custom parcel count input changes."""
    #     self.update_display()

    def update_display(self):
        """Updates the calculations and display for the custom tier."""
        user_inputs = self.get_user_inputs_callback()
        if user_inputs is None:
            self._clear_labels()
            return

        try:
            custom_parcel_count_str = self.custom_parcel_count_var.get()
            custom_parcel_count = int(custom_parcel_count_str) if custom_parcel_count_str.strip() != "" else 0
            if custom_parcel_count < 0:
                raise ValueError("Negative parcel count")
            
            # Clean the input field display
            if custom_parcel_count_str != str(custom_parcel_count):
                self.custom_parcel_count_var.set(str(custom_parcel_count))

        except ValueError:
            self._clear_labels()
            # messagebox.showerror("Input Error", "Custom Parcel Count must be a non-negative whole number.")
            return

        # Get the user's current parcel types to calculate base rate
        # For custom tier, we assume the user has a mix of parcels that sum up to custom_parcel_count
        # We need a way to estimate the base earnings per second for 'custom_parcel_count'
        # A simple approach is to use the average rate per parcel from constants.
        # Or, we can assume all are common parcels for simplicity if not specified.
        # For now, let's assume a common parcel rate for the custom count.
        # A more advanced version might ask for the distribution of parcels for the custom count.

        # To simplify, let's use the current user's parcel types to calculate the base rate per parcel
        # and then scale it to the custom parcel count.
        # Or, even simpler: just use the common parcel rate for the custom count.
        
        # Let's use a simplified base rate calculation for the custom tier:
        # Assume common parcel rate for the custom count for base earnings calculation
        # This is a simplification; a real app might need parcel type distribution for custom tiers.
        base_rate_per_common_parcel_per_second = constants.PARCEL_RATES_PER_SECOND['common']
        estimated_base_earnings_per_second_custom_tier = base_rate_per_common_parcel_per_second * custom_parcel_count

        # Apply user's current badge boost (from main app inputs) to the base rate
        base_rate_with_badge_per_second = estimated_base_earnings_per_second_custom_tier * \
                                          utils.get_passport_boost_multiplier(user_inputs["badge_count"])
        if user_inputs["fictive_badge_boost_enabled"]:
            base_rate_with_badge_per_second = estimated_base_earnings_per_second_custom_tier * (1.0 + user_inputs["fictive_badge_boost_percent"])


        # Calculate Ad Boost Multiplier for the custom parcel count and selected region
        custom_ad_boost_multiplier = utils.get_ad_boost_multiplier(custom_parcel_count, user_inputs["selected_region"])
        
        # Calculate the fully boosted rate per second at this custom tier
        # This is the rate when ad boost is active at the custom tier.
        fully_boosted_rate_per_second_custom_tier = base_rate_with_badge_per_second * custom_ad_boost_multiplier
        
        # If SRB is forced in main inputs, apply SRB multiplier instead
        if user_inputs["srb_boost_enabled"]:
            fully_boosted_rate_per_second_custom_tier = base_rate_with_badge_per_second * constants.SUPER_RENT_BOOST_MULTIPLIER

        # Calculate estimated monthly earnings
        # Base monthly earnings (unboosted, but with badge boost)
        est_base_monthly_earnings = utils.convert_seconds_to_timeframe(base_rate_with_badge_per_second, 'month')

        # Boosted monthly earnings (considering user's boost hours and SRB events)
        # This part reuses the logic from CurrentEarningsCalculator for consistency
        total_monthly_seconds = constants.AVG_DAYS_PER_MONTH * constants.SECONDS_PER_DAY
        srb_seconds_monthly = constants.SRB_HOURS_PER_MONTH * constants.SECONDS_PER_HOUR
        
        normal_ad_boost_seconds_monthly = min(user_inputs["boost_hours"] * constants.SECONDS_PER_HOUR * constants.AVG_DAYS_PER_MONTH,
                                              total_monthly_seconds - srb_seconds_monthly)
        normal_ad_boost_seconds_monthly = max(0, normal_ad_boost_seconds_monthly)

        unboosted_seconds_monthly = max(0, total_monthly_seconds - srb_seconds_monthly - normal_ad_boost_seconds_monthly)

        if user_inputs["srb_boost_enabled"]:
            est_boosted_monthly_earnings = fully_boosted_rate_per_second_custom_tier * total_monthly_seconds
        else:
            est_boosted_monthly_earnings = \
                (base_rate_with_badge_per_second * unboosted_seconds_monthly) + \
                (fully_boosted_rate_per_second_custom_tier * normal_ad_boost_seconds_monthly) + \
                (base_rate_with_badge_per_second * constants.SUPER_RENT_BOOST_MULTIPLIER * srb_seconds_monthly) # SRB time uses SRB rate

        # Update labels
        self.custom_ad_boost_multiplier_label.config(text=f"{custom_ad_boost_multiplier:.2f}x")
        self.custom_base_earnings_label.config(text=f"${est_base_monthly_earnings:.8f}")
        self.custom_boosted_earnings_label.config(text=f"${est_boosted_monthly_earnings:.8f}")

    def _clear_labels(self):
        self.custom_ad_boost_multiplier_label.config(text="N/A")
        self.custom_base_earnings_label.config(text="$0.00")
        self.custom_boosted_earnings_label.config(text="$0.00")

    def get_export_data(self):
        """Returns the custom tier data in a dictionary format for export."""
        data = {
            "custom_parcel_count": self.custom_parcel_count_var.get(),
            "custom_ad_boost_multiplier": self.custom_ad_boost_multiplier_label.cget("text"),
            "est_base_monthly_earnings": self.custom_base_earnings_label.cget("text"),
            "est_boosted_monthly_earnings": self.custom_boosted_earnings_label.cget("text"),
        }
        return data
