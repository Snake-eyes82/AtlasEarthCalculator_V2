# goal_calculator.py

import tkinter as tk
from tkinter import ttk, messagebox

import constants
import utils

class GoalCalculator:
    def __init__(self, parent_frame, get_user_inputs_callback):
        self.parent_frame = parent_frame
        self.get_user_inputs_callback = get_user_inputs_callback

        self.target_amount_var = tk.StringVar(value="1.00")
        self.target_timeframe_var = tk.StringVar(value="day")
        self.assume_boosts_var = tk.BooleanVar(value=False)
        self.assumed_badges_var = tk.StringVar(value="0")
        self.assumed_rent_boost_percent_var = tk.StringVar(value="0")
        self.calc_mode_var = tk.StringVar(value="mixed")
        self.specific_parcel_type_var = tk.StringVar(value="common")

        self._last_target_amount = 0.0
        self._last_target_earnings_per_second = 0.0
        self._last_effective_rate_multiplier = 1.0
        self._last_target_timeframe_str = ""
        self._last_assumed_badges = 0
        self._last_assumed_rent_boost_percentage = 0.0
        self._last_assume_boosts = False
        self._last_total_parcels_needed = 0
        self._last_parcels_breakdown = {}
        self._last_calculation_mode = ""
        self._last_specific_parcel_type = ""

        self._create_widgets()

    def _create_widgets(self):
        row = 0
        ttk.Label(self.parent_frame, text="Target Amount ($):").grid(row=row, column=0, sticky="w", pady=2)
        self.target_amount_entry = ttk.Entry(self.parent_frame, width=10, textvariable=self.target_amount_var)
        self.target_amount_entry.grid(row=row, column=1, sticky="ew", pady=2)

        row += 1
        ttk.Label(self.parent_frame, text="Target Timeframe:").grid(row=row, column=0, sticky="w", pady=2)
        self.timeframe_combo = ttk.Combobox(self.parent_frame, textvariable=self.target_timeframe_var,
                                            values=["second", "minute", "hour", "day", "week", "month", "year"],
                                            state="readonly")
        self.timeframe_combo.grid(row=row, column=1, sticky="ew", pady=2)

        row += 1
        self.assume_boosts_check = ttk.Checkbutton(self.parent_frame, text="Assume Boosts for Goal?",
                                                    variable=self.assume_boosts_var, command=self._toggle_assumed_boosts_entries)
        self.assume_boosts_check.grid(row=row, column=0, sticky="w", pady=2, columnspan=2)

        row += 1
        ttk.Label(self.parent_frame, text="  Assumed Badges:").grid(row=row, column=0, sticky="w", pady=2, padx=(20,0))
        self.assumed_badges_entry = ttk.Entry(self.parent_frame, width=10, textvariable=self.assumed_badges_var)
        self.assumed_badges_entry.grid(row=row, column=1, sticky="ew", pady=2)
        self.assumed_badges_entry.config(state="disabled")

        row += 1
        ttk.Label(self.parent_frame, text="  Assumed Rent Boost %:").grid(row=row, column=0, sticky="w", pady=2, padx=(20,0))
        self.assumed_rent_boost_percent_entry = ttk.Entry(self.parent_frame, width=5, textvariable=self.assumed_rent_boost_percent_var)
        self.assumed_rent_boost_percent_entry.grid(row=row, column=1, sticky="ew", pady=2)
        self.assumed_rent_boost_percent_entry.config(state="disabled")

        row += 1
        ttk.Label(self.parent_frame, text="Calculation Mode:").grid(row=row, column=0, sticky="w", pady=5)
        
        self.mixed_radio = ttk.Radiobutton(self.parent_frame, text="Mixed Parcels (Realistic Avg)", variable=self.calc_mode_var, value="mixed",
                                            command=self._toggle_specific_parcel_combo)
        self.mixed_radio.grid(row=row, column=1, sticky="w", pady=2)

        row += 1
        self.specific_radio = ttk.Radiobutton(self.parent_frame, text="Specific Parcel Type Only:", variable=self.calc_mode_var, value="specific",
                                               command=self._toggle_specific_parcel_combo)
        self.specific_radio.grid(row=row, column=1, sticky="w", pady=2)

        self.specific_parcel_combo = ttk.Combobox(self.parent_frame, textvariable=self.specific_parcel_type_var,
                                                  values=list(constants.PARCEL_RATES_PER_SECOND.keys()),
                                                  state="disabled")
        self.specific_parcel_combo.grid(row=row, column=2, sticky="ew", pady=2)

        row += 1
        self.calculate_goal_button = ttk.Button(self.parent_frame, text="Calculate Parcels Needed", command=self._show_goal_results_window)
        self.calculate_goal_button.grid(row=row, column=0, columnspan=3, pady=10)

        self.goal_info_label = ttk.Label(self.parent_frame, text="Click 'Calculate Parcels Needed' to see results.")
        self.goal_info_label.grid(row=row+1, column=0, columnspan=3, sticky="w", pady=5)
        
        self.parent_frame.grid_columnconfigure(1, weight=1)
        self.parent_frame.grid_columnconfigure(2, weight=1)

    def _toggle_assumed_boosts_entries(self):
        if self.assume_boosts_var.get():
            self.assumed_badges_entry.config(state="normal")
            self.assumed_rent_boost_percent_entry.config(state="normal")
        else:
            self.assumed_badges_entry.config(state="disabled")
            self.assumed_rent_boost_percent_entry.config(state="disabled")
            self.assumed_badges_var.set("0")
            self.assumed_rent_boost_percent_var.set("0")

    def _toggle_specific_parcel_combo(self):
        if self.calc_mode_var.get() == "specific":
            self.specific_parcel_combo.config(state="readonly")
        else:
            self.specific_parcel_combo.config(state="disabled")
            self.specific_parcel_type_var.set("common")

    def _perform_goal_calculation(self):
        try:
            self._last_target_amount = float(self.target_amount_var.get())
            self._last_target_timeframe_str = self.target_timeframe_var.get()
            self._last_calculation_mode = self.calc_mode_var.get()
            self._last_specific_parcel_type = self.specific_parcel_type_var.get()

            self._last_assume_boosts = self.assume_boosts_var.get()
            self._last_assumed_badges = 0
            self._last_assumed_rent_boost_percentage = 0.0

            if self._last_assume_boosts:
                self._last_assumed_badges = int(self.assumed_badges_var.get())
                self._last_assumed_rent_boost_percentage = float(self.assumed_rent_boost_percent_var.get())
                
                if self.assumed_rent_boost_percent_var.get().strip() == "" or self.assumed_rent_boost_percent_var.get().strip() == "0":
                    messagebox.showwarning("Input Warning", "Assumed Rent Boost % is 0 or empty, which means no ad boost will be applied.")

                assumed_passport_multiplier = utils.get_passport_boost_multiplier(self._last_assumed_badges)
                assumed_ad_boost_multiplier = self._last_assumed_rent_boost_percentage 
                
                self._last_effective_rate_multiplier = assumed_ad_boost_multiplier * assumed_passport_multiplier
            else:
                self._last_effective_rate_multiplier = 1.0

            seconds_in_target_timeframe = utils.get_seconds_in_timeframe(self._last_target_timeframe_str)
            if seconds_in_target_timeframe == 0:
                messagebox.showerror("Calculation Error", "Invalid target timeframe selected.")
                return False

            self._last_target_earnings_per_second = self._last_target_amount / seconds_in_target_timeframe
            
            self._last_total_parcels_needed = 0
            self._last_parcels_breakdown = {}

            if self._last_calculation_mode == "mixed":
                avg_parcel_base_rate = utils.calculate_average_mixed_parcel_rate_per_second()
                avg_parcel_boosted_rate = avg_parcel_base_rate * self._last_effective_rate_multiplier

                if avg_parcel_boosted_rate == 0:
                    messagebox.showerror("Calculation Error", "Average boosted parcel rate is zero, cannot calculate. Check inputs or assumed boosts.")
                    return False
                
                self._last_total_parcels_needed = self._last_target_earnings_per_second / avg_parcel_boosted_rate
                
                for parcel_type, prob in constants.PARCEL_PROBABILITIES.items():
                    self._last_parcels_breakdown[parcel_type] = self._last_total_parcels_needed * prob
                
            elif self._last_calculation_mode == "specific":
                parcel_base_rate = constants.PARCEL_RATES_PER_SECOND[self._last_specific_parcel_type]
                parcel_boosted_rate = parcel_base_rate * self._last_effective_rate_multiplier

                if parcel_boosted_rate == 0:
                    messagebox.showerror("Calculation Error", f"Boosted rate for {self._last_specific_parcel_type} parcel is zero, cannot calculate. Check inputs or assumed boosts.")
                    return False
                
                self._last_total_parcels_needed = self._last_target_earnings_per_second / parcel_boosted_rate
                self._last_parcels_breakdown = {}
                
            return True

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for target amount, badges, and percentages.")
            return False
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An unexpected error occurred: {e}")
            return False

    def _show_goal_results_window(self):
        if not self._perform_goal_calculation():
            return

        top = tk.Toplevel(self.parent_frame)
        top.title("Parcels Needed for Goal")
        top.geometry("550x450")
        top.resizable(False, False)
        top.grab_set()
        top.focus_set()

        frame = ttk.Frame(top, padding="15")
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="--- Goal Calculation Results ---", font=("Helvetica", 12, "bold")).pack(pady=(0, 10))

        ttk.Label(frame, text="Goal Summary:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(frame, text=f"  Target: ${self._last_target_amount:.2f} per {self._last_target_timeframe_str}").pack(anchor="w")
        
        if self._last_assume_boosts:
            assumed_passport_multiplier = utils.get_passport_boost_multiplier(self._last_assumed_badges)
            display_assumed_rent_boost = self._last_assumed_rent_boost_percentage
            
            ttk.Label(frame, text=f"  Assumed Badges: {self._last_assumed_badges} (Passport Boost: x{assumed_passport_multiplier:.2f})").pack(anchor="w")
            ttk.Label(frame, text=f"  Assumed Rent Boost: {display_assumed_rent_boost:.0f}x (Effective Multiplier: x{self._last_effective_rate_multiplier:.2f})").pack(anchor="w")
        else:
            ttk.Label(frame, text="  Calculating without assumed boosts.").pack(anchor="w")

        ttk.Label(frame, text="\nParcels Needed:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(5, 5))
        output_font = ("Courier", 10)

        if self._last_calculation_mode == "mixed":
            ttk.Label(frame, text=f"  Total estimated parcels needed: {self._last_total_parcels_needed:,.0f}", font=output_font).pack(anchor="w")
            ttk.Label(frame, text="\nBreakdown based on probabilities:", font=("Helvetica", 10, "bold")).pack(anchor="w")
            for parcel_type, count in self._last_parcels_breakdown.items():
                ttk.Label(frame, text=f"    - {parcel_type.capitalize():<9}: {count:,.0f}", font=output_font).pack(anchor="w")
            
        elif self._last_calculation_mode == "specific":
            ttk.Label(frame, text=f"  Number of {self._last_specific_parcel_type.capitalize()} parcels needed: {self._last_total_parcels_needed:,.0f}", font=output_font).pack(anchor="w")
            
        ttk.Button(frame, text="Show Other Parcel Compositions", command=self._show_alternative_compositions).pack(pady=15)
        ttk.Button(frame, text="Close", command=top.destroy).pack(pady=5)

    def _show_alternative_compositions(self):
        top = tk.Toplevel(self.parent_frame)
        top.title("Alternative Parcel Compositions")
        top.geometry("450x330")
        top.resizable(False, False)
        top.grab_set()
        top.focus_set()

        frame = ttk.Frame(top, padding="15")
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Target Goal Summary:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(frame, text=f"  Target Amount: ${self._last_target_amount:.2f} per {self._last_target_timeframe_str}").pack(anchor="w")
        
        if self._last_assume_boosts:
            assumed_passport_multiplier = utils.get_passport_boost_multiplier(self._last_assumed_badges)
            display_assumed_rent_boost = self._last_assumed_rent_boost_percentage

            ttk.Label(frame, text=f"  Assumed Badges: {self._last_assumed_badges} (Passport Boost: x{assumed_passport_multiplier:.2f})").pack(anchor="w")
            ttk.Label(frame, text=f"  Assumed Rent Boost: {display_assumed_rent_boost:.0f}x (Effective Multiplier: x{self._last_effective_rate_multiplier:.2f})").pack(anchor="w")
        else:
            ttk.Label(frame, text="  No boosts assumed for this goal.").pack(anchor="w")

        ttk.Label(frame, text="\nRequired Parcels if acquiring ONLY one type:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10, 5))

        output_font = ("Courier", 10)

        for parcel_type, base_rate in constants.PARCEL_RATES_PER_SECOND.items():
            boosted_rate = base_rate * self._last_effective_rate_multiplier
            
            if boosted_rate == 0:
                needed_parcels = "N/A (Rate is Zero)"
            else:
                needed_parcels = self._last_target_earnings_per_second / boosted_rate
                needed_parcels = f"{needed_parcels:,.0f}"

            text = f"  - {parcel_type.capitalize():<9}: {needed_parcels:>10} parcels"
            ttk.Label(frame, text=text, font=output_font).pack(anchor="w")

        ttk.Button(frame, text="Close", command=top.destroy).pack(pady=20)
        
    def get_export_data(self):
        """Returns the last calculated goal data in a dictionary format for export."""
        data = {
            "target_amount": f"${self._last_target_amount:.2f}",
            "target_timeframe": self._last_target_timeframe_str,
            "assume_boosts_for_goal": self._last_assume_boosts,
            "assumed_badges": self._last_assumed_badges,
            "assumed_rent_boost_multiplier": f"{self._last_assumed_rent_boost_percentage:.0f}x",
            "calculation_mode": self._last_calculation_mode,
            "specific_parcel_type": self._last_specific_parcel_type,
            "total_parcels_needed": f"{self._last_total_parcels_needed:,.0f}",
        }
        if self._last_calculation_mode == "mixed" and self._last_parcels_breakdown:
            breakdown_data = {k: f"{v:,.0f}" for k, v in self._last_parcels_breakdown.items()}
            data["parcels_breakdown"] = breakdown_data
        return data