import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
from logic import send_temperature
import os


class TemperatureEmulatorApp:
    def __init__(self, root, data):
        self.root = root
        self.data = data
        self.root.title("Temperature Emulator")
        self.root.geometry("415x430")
        self.root.resizable(False, False)

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.panels = []
        self.fridge_active = []

        self.green_icon = self.load_image("green.png")
        self.red_icon = self.load_image("red.png")
        self.grey_icon = self.load_image("grey.png")
        self.app_icon = self.load_image("temperature.png")

        root.iconphoto(False, self.app_icon)


        for i in range(3):
            panel = ttk.LabelFrame(self.main_frame, text=f"Fridge {i + 1}", padding="15")
            panel.grid(column=0, row=i, padx=5, pady=10, sticky=(tk.W, tk.E))

            icon_label = ttk.Label(panel, image=self.grey_icon)
            icon_label.grid(column=0, row=0, padx=5, pady=5)

            label_temp = ttk.Label(panel, text="Temperature: - °C", width=20)
            label_temp.grid(column=1, row=0, padx=10, pady=5)

            active_var = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(
                panel,
                text="Active",
                variable=active_var,
                command=lambda idx=i, var=active_var: self.update_panel_data(idx, var)
            )
            checkbox.grid(column=5, row=0, padx=5, pady=5, sticky=tk.W)

            percentage_var = tk.StringVar(value="20")
            validate_cmd = (self.root.register(self.validate_percentage), "%P")

            ttk.Label(panel, text="Prob.:").grid(column=2, row=0, padx=5, pady=5)

            entry_percentage = ttk.Entry(panel, textvariable=percentage_var, validate="key",
                                         validatecommand=validate_cmd, width=3)
            entry_percentage.grid(column=3, row=0, padx=5, pady=5)

            ttk.Label(panel, text="%").grid(column=4, row=0, padx=5, pady=5)

            self.panels.append({
                "panel": panel,
                "temp_label": label_temp,
                "active_var": active_var,
                "percentage_var": percentage_var,
                "icon_label": icon_label,
            })
            self.fridge_active.append(active_var)

            style = ttk.Style()
            style.configure("Green.TButton", font=("Helvetica", 12, "bold"), foreground="green")
            style.configure("Red.TButton", font=("Helvetica", 12, "bold"), foreground="red")

            self.buttons_frame = ttk.Frame(self.main_frame, padding="10")
            self.buttons_frame.grid(column=0, row=3, pady=10, sticky=(tk.W, tk.E))

            self.buttons_frame.grid_columnconfigure(0, weight=1)
            self.buttons_frame.grid_columnconfigure(1, weight=1)

            self.start_button = ttk.Button(self.buttons_frame, text="START", command=self.start_emulation,
                                           style="Green.TButton")
            self.start_button.grid(column=0, row=0, padx=5, sticky="ew")

            self.stop_button = ttk.Button(self.buttons_frame, text="STOP", command=self.stop_emulation,
                                          style="Red.TButton")
            self.stop_button.grid(column=1, row=0, padx=5, sticky="ew")

        self.status_label = ttk.Label(self.main_frame, text="Information", relief="sunken", anchor=tk.W)
        self.status_label.grid(column=0, row=4, sticky=(tk.W, tk.E), pady=5)

        self.running = False
        self.thread = None


    def update_panel_data(self, idx, active_var):
        panel = self.panels[idx]["panel"]
        icon_label = self.panels[idx]["icon_label"]
        temp_label = self.panels[idx]["temp_label"]

        if active_var.get():
            panel.config(text=f"Fridge {idx + 1}")
            icon_label.config(image=self.green_icon)
            temp_label.config(text=f"Temperature: - °C")
        else:
            panel.config(text="Fridge is inactive")
            icon_label.config(image=self.grey_icon)

    def update_ui_text_data(self, fridge_id, temperature, status):
        temp_label = self.panels[fridge_id - 1]["temp_label"]
        temp_label.config(text=f"Temperature: {temperature} °C")
        self.status_label.config(text=f"Fridge {fridge_id}: {status}")

    def update_fridge_indicator(self, fridge_id, is_temperature_ok: bool):
        icon_label = self.panels[fridge_id - 1]["icon_label"]
        if is_temperature_ok:
            icon_label.config(image=self.green_icon)
        else:
            icon_label.config(image=self.red_icon)

    @staticmethod
    def load_image(image_name):
        image_path = os.path.join("images", image_name)
        image = Image.open(image_path)
        return ImageTk.PhotoImage(image)

    @staticmethod
    def validate_percentage(new_value):
        if not new_value:
            return True
        try:
            value = int(new_value)
            return 0 <= value <= 100
        except ValueError:
            return False

    def start_emulation(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(
                target=send_temperature,
                args=(lambda: self.running, self.update_ui_text_data, self.update_fridge_indicator, self.fridge_active,
                      [panel["percentage_var"] for panel in self.panels]),
                daemon=True
            )
            self.thread.start()
            self.status_label.config(text="Emulation started.")

    def stop_emulation(self):
        if self.running:
            self.running = False
            self.thread.join()
            self.status_label.config(text="Emulation stopped.")
