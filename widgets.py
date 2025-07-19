# widgets.py

import tkinter as tk
from tkinter import ttk

# Custom Entry widget for integer input with robust validation and cleaning
class IntegerEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        # Use a StringVar that we control
        self.var = kwargs.pop('textvariable', tk.StringVar(value="0"))
        super().__init__(master, textvariable=self.var, **kwargs)

        # Register validation command to allow only digits
        vcmd = self.register(self._validate_input)
        self.config(validate="key", validatecommand=(vcmd, '%P')) # %P is the new value of the entry

        # Bind to clean and update on focus out or Return key
        self.bind("<FocusOut>", self._clean_and_update)
        self.bind("<Return>", self._clean_and_update)

        # Initial cleaning in case default value isn't clean (e.g., if it was "00")
        # This calls _clean_and_update, which will then attempt to call update_all_calculations
        self._clean_and_update()

    def _validate_input(self, new_value):
        """Allows only digits and empty string."""
        if new_value == "":
            return True
        return new_value.isdigit()

    def _clean_and_update(self, event=None):
        """
        Cleans the input (removes leading zeros, ensures non-negative integer),
        and then triggers the main application's update_all_calculations.
        """
        current_value = self.var.get()
        
        if current_value.strip() == "":
            cleaned_value = "0"
        else:
            try:
                # Convert to integer to handle leading zeros automatically (e.g., "045" -> 45)
                int_val = int(current_value)
                if int_val < 0: # Ensure non-negative
                    int_val = 0
                cleaned_value = str(int_val) # Convert back to string (e.g., 45 -> "45")
            except ValueError:
                # This should ideally not happen if _validate_input is working,
                # but as a fallback for non-digit input (e.g., paste)
                cleaned_value = "0"
        
        # Only update the StringVar if the value actually changed.
        # This is crucial to prevent unnecessary widget updates.
        if self.var.get() != cleaned_value:
            self.var.set(cleaned_value)
        
        # Trigger the main application's update.
        # IMPORTANT: Check if the app_instance and its calculators are ready
        # before attempting to call update_all_calculations.
        # This prevents the AttributeError during startup.
        app_instance = self.master.winfo_toplevel().app_instance
        if hasattr(app_instance, 'current_earnings_calculator') and \
           hasattr(app_instance, 'goal_calculator') and \
           hasattr(app_instance, 'next_tier_calculator') and \
           hasattr(app_instance, 'custom_tier_calculator'): # Also check for custom_tier_calculator
                app_instance.update_all_calculations()
