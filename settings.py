import customtkinter as ctk


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.title_label = ctk.CTkLabel(self, text="Settings", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=20)

        # Dark Mode Switch (Single Switch to Toggle Dark Mode)
        self.dark_mode_switch = ctk.CTkSwitch(self, text="Enable Dark Mode", font=("Arial", 14),
                                              command=self.toggle_theme)
        self.dark_mode_switch.pack(pady=10)

        # Example setting widgets
        setting_1 = ctk.CTkLabel(self, text="Setting 1: Enable Feature", font=("Arial", 14))
        setting_1.pack(pady=10)

        # Example checkbox for additional settings
        enable_feature = ctk.CTkCheckBox(self, text="Enable Feature", font=("Arial", 14))
        enable_feature.pack(pady=10)

    def toggle_theme(self):
        """ Toggle between dark and light mode """
        if self.dark_mode_switch.get():
            ctk.set_appearance_mode("dark")
            print("Dark Mode enabled")
        else:
            ctk.set_appearance_mode("light")
            print("Light Mode enabled")
