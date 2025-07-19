# next_tier_calculator.py

import tkinter as tk
from tkinter import ttk, messagebox

import constants
import utils

class NextTierCalculator:
    def __init__(self, parent_frame, get_user_inputs_callback):
        self.parent_frame = parent_frame
        self.get_user_inputs_callback = get_user_inputs_callback

        self._create_widgets()

    def _create_widgets(self):
        row = 0
        header_font = ("Helvetica", 10, "bold")
        value_font = ("Courier", 10)

        ttk.Label(self.parent_frame, text="--- Your Current Tier ---", font=header_font).grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 5))
        row += 1
        ttk.Label(self.parent_frame, text="Current Parcel Count:", font=value_font).grid(row=row, column=0, sticky="w", padx=5, pady=1)
        self.current_parcel_count_label = ttk.Label(self.parent_frame, text="N/A", font=value_font)
        self.current_parcel_count_label.grid(row=row, column=1, sticky="ew", padx=5, pady=1)
        row += 1
        ttk.Label(self.parent_frame, text="Current Ad Boost Multiplier:", font=value_font).grid(row=row, column=0, sticky="w", padx=5, pady=1)
        self.current_ad_boost_label = ttk.Label(self.parent_frame, text="N/A", font=value_font)
        self.current_ad_boost_label.grid(row=row, column=1, sticky="ew", padx=5, pady=1)
        row += 1
        ttk.Label(self.parent_frame, text="Current Tier Max Parcels:", font=value_font).grid(row=row, column=0, sticky="w", padx=5, pady=1)
        self.current_tier_max_label = ttk.Label(self.parent_frame, text="N/A", font=value_font)
        self.current_tier_max_label.grid(row=row, column=1, sticky="ew", padx=5, pady=1)
        row += 1

        ttk.Label(self.parent_frame, text="--- Next Ad Boost Tier ---", font=header_font).grid(row=row, column=0, columnspan=2, sticky="w", pady=(15, 5))
        row += 1
        ttk.Label(self.parent_frame, text="Parcels to Next Tier:", font=value_font).grid(row=row, column=0, sticky="w", padx=5, pady=1)
        self.parcels_to_next_tier_label = ttk.Label(self.parent_frame, text="N/A", font=value_font)
        self.parcels_to_next_tier_label.grid(row=row, column=1, sticky="ew", padx=5, pady=1)
        row += 1
        ttk.Label(self.parent_frame, text="Next Tier Multiplier:", font=value_font).grid(row=row, column=0, sticky="w", padx=5, pady=1)
        self.next_tier_multiplier_label = ttk.Label(self.parent_frame, text="N/A", font=value_font)
        self.next_tier_multiplier_label.grid(row=row, column=1, sticky="ew", padx=5, pady=1)
        row += 1
        ttk.Label(self.parent_frame, text="Next Tier Range:", font=value_font).grid(row=row, column=0, sticky="w", padx=5, pady=1)
        self.next_tier_range_label = ttk.Label(self.parent_frame, text="N/A", font=value_font)
        self.next_tier_range_label.grid(row=row, column=1, sticky="ew", padx=5, pady=1)
        row += 1
        ttk.Label(self.parent_frame, text="Est. Daily Earnings at Next Tier Start (with current boosts):", font=value_font).grid(row=row, column=0, sticky="w", padx=5, pady=1)
        self.est_earnings_next_tier_label = ttk.Label(self.parent_frame, text="N/A", font=value_font)
        self.est_earnings_next_tier_label.grid(row=row, column=1, sticky="ew", padx=5, pady=1)
        row += 1

        self.parent_frame.grid_columnconfigure(1, weight=1)

    def update_display(self):
        inputs = self.get_user_inputs_callback()
        if inputs is None:
            self._clear_labels()
            return

        parcels = inputs["parcels"]
        total_parcels = inputs["total_parcels"]
        selected_region = inputs["selected_region"]
        badge_count = inputs["badge_count"]
        boost_hours = inputs["boost_hours"]

        region_data = constants.REGIONAL_AD_BOOST_DATA.get(selected_region)
        if not region_data:
            self._clear_labels()
            messagebox.showwarning("Data Error", f"Ad boost data not found for region: {selected_region}. Displaying N/A.")
            return

        # Calculate raw base earnings per second from current parcels
        raw_base_earnings_per_second = utils.calculate_base_earnings_per_second(parcels)

        current_tier_info = None
        next_tier_info = None
        
        # Find current tier and next tier
        for i, tier in enumerate(region_data):
            if tier['min'] <= total_parcels <= tier['max']:
                current_tier_info = tier
                if i + 1 < len(region_data):
                    next_tier_info = region_data[i+1]
                break
        
        # If no current tier found (e.g., 0 parcels), assume first tier is next
        if not current_tier_info and total_parcels < region_data[0]['min']:
            next_tier_info = region_data[0]
            
        # Update Current Tier Info
        self.current_parcel_count_label.config(text=f"{total_parcels:,}")
        if current_tier_info:
            self.current_ad_boost_label.config(text=f"{current_tier_info['multiplier']}x")
            self.current_tier_max_label.config(text=f"{current_tier_info['max']} parcels")
        else:
            # If current_tier_info is still None, means user is below first tier or above last
            self.current_ad_boost_label.config(text="1x (No Boost / Beyond Last Tier)")
            self.current_tier_max_label.config(text="N/A")

        # Update Next Tier Info
        if next_tier_info:
            parcels_to_next_tier = next_tier_info['min'] - total_parcels
            if parcels_to_next_tier < 0: parcels_to_next_tier = 0 # Should not be negative if logic is correct
            
            self.parcels_to_next_tier_label.config(text=f"{parcels_to_next_tier:,}")
            self.next_tier_multiplier_label.config(text=f"{next_tier_info['multiplier']}x")
            self.next_tier_range_label.config(text=f"{next_tier_info['min']}-{next_tier_info['max']} parcels")

            # Estimate earnings at the start of the next tier
            current_avg_base_rent_per_parcel = 0
            if total_parcels > 0:
                current_avg_base_rent_per_parcel = raw_base_earnings_per_second / total_parcels
            else:
                current_avg_base_rent_per_parcel = utils.calculate_average_mixed_parcel_rate_per_second()
            
            est_raw_base_earnings_at_next_tier_min = current_avg_base_rent_per_parcel * next_tier_info['min']

            badge_multiplier = utils.get_passport_boost_multiplier(badge_count)
            next_tier_ad_boost_multiplier = next_tier_info['multiplier']

            est_total_earnings_per_second_at_next_tier_min = \
                est_raw_base_earnings_at_next_tier_min * badge_multiplier * next_tier_ad_boost_multiplier
            
            est_daily_earnings = utils.convert_seconds_to_timeframe(est_total_earnings_per_second_at_next_tier_min, 'day')
            self.est_earnings_next_tier_label.config(text=f"${est_daily_earnings:.8f}")
        else:
            self.parcels_to_next_tier_label.config(text="N/A (Last Tier Reached)")
            self.next_tier_multiplier_label.config(text="N/A")
            self.next_tier_range_label.config(text="N/A")
            self.est_earnings_next_tier_label.config(text="N/A")

    def _clear_labels(self):
        self.current_parcel_count_label.config(text="N/A")
        self.current_ad_boost_label.config(text="N/A")
        self.current_tier_max_label.config(text="N/A")
        self.parcels_to_next_tier_label.config(text="N/A")
        self.next_tier_multiplier_label.config(text="N/A")
        self.next_tier_range_label.config(text="N/A")
        self.est_earnings_next_tier_label.config(text="N/A")
        
    def get_export_data(self):
        """Returns the current and next tier info in a dictionary format for export."""
        data = {
            "current_parcel_count": self.current_parcel_count_label.cget("text"),
            "current_ad_boost_multiplier": self.current_ad_boost_label.cget("text"),
            "current_tier_max_parcels": self.current_tier_max_label.cget("text"),
            "parcels_to_next_tier": self.parcels_to_next_tier_label.cget("text"),
            "next_tier_multiplier": self.next_tier_multiplier_label.cget("text"),
            "next_tier_range": self.next_tier_range_label.cget("text"),
            "est_earnings_next_tier_start": self.est_earnings_next_tier_label.cget("text"),
        }
        return data