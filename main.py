import tkinter as tk
from form_initial import InitialForm
from interface import TemperatureEmulatorApp

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Blood Transport System")

    def start_fridges_form(data):
        root.withdraw()
        open_temperature_emulator_app(data)

    def open_temperature_emulator_app(data):
        temp_root = tk.Toplevel(root)
        temp_root.title("Temperature Emulator")
        app = TemperatureEmulatorApp(temp_root, data)

        def on_close():
            root.quit()

        temp_root.protocol("WM_DELETE_WINDOW", on_close)
        temp_root.mainloop()

    InitialForm(root, on_submit=start_fridges_form)

    root.mainloop()
