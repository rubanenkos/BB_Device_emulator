import tkinter as tk
from form_initial import InitialForm
from interface import TemperatureEmulatorApp
from utils import center_window

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Blood Transport System")
    root.geometry("340x280")
    center_window(root)

    def start_fridges_form(data):
        root.withdraw()
        open_temperature_emulator_app(data)

    def open_temperature_emulator_app(data):
        temp_root = tk.Toplevel(root)
        temp_root.title("Temperature Emulator")
        app = TemperatureEmulatorApp(temp_root, data, on_back=lambda: show_initial_form(temp_root))
        center_window(temp_root)

        def on_close():
            root.quit()

        temp_root.protocol("WM_DELETE_WINDOW", on_close)
        temp_root.mainloop()

    def show_initial_form(temp_root):
        temp_root.destroy()
        root.deiconify()
        center_window(root)

    InitialForm(root, on_submit=start_fridges_form)

    root.mainloop()
