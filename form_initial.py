import tkinter as tk
from tkinter import ttk
import configparser


class InitialForm:
    def __init__(self, root, on_submit):
        self.root = root
        self.on_submit = on_submit
        self.frame = ttk.Frame(root, padding="10")
        self.frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(self.frame, text="Blood Transport ID:").grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)
        self.transport_id = tk.Entry(self.frame, width=30)
        self.transport_id.grid(column=1, row=0, padx=5, pady=5)

        # self.style = ttk.Style()
        # self.style.configure("TFrame", background="#b3e0ff")
        # self.style.configure("TButton", background="#008ae6", foreground="black")
        # self.style.map("TButton", background=[("active", "#006bb3")])
        self.fridges = []
        for i in range(1, 4):
            self.add_fridge_fields(i)

        submit_button = ttk.Button(self.frame, text="Submit", command=self.submit_data)
        submit_button.grid(column=0, row=len(self.fridges) * 2 + 1, columnspan=2, pady=10)

    def add_fridge_fields(self, fridge_number):
        ttk.Label(self.frame, text=f"Fridge {fridge_number} ID:").grid(column=0, row=(fridge_number - 1) * 2 + 1, padx=5, pady=5, sticky=tk.W)
        fridge_id = tk.Entry(self.frame, width=30)
        fridge_id.grid(column=1, row=(fridge_number - 1) * 2 + 1, padx=5, pady=5)

        ttk.Label(self.frame, text="Blood Component:").grid(column=0, row=(fridge_number - 1) * 2 + 2, padx=5, pady=5, sticky=tk.W)
        component = ttk.Combobox(self.frame, width=28, values=["Plasma", "Platelets", "Red Blood Cells"])
        component.grid(column=1, row=(fridge_number - 1) * 2 + 2, padx=5, pady=5)
        component.current(0)

        self.fridges.append({
            "fridge_id": fridge_id,
            "component": component
        })

    def submit_data(self):
        data = {
            "transport_id": self.transport_id.get(),
            "fridges": []
        }

        for fridge in self.fridges:
            data["fridges"].append({
                "fridge_id": fridge["fridge_id"].get(),
                "component": fridge["component"].get()
            })

        self.write_to_config(data)

        self.on_submit(data)

    def write_to_config(self, data):
        config = configparser.ConfigParser()

        config["TRANSPORT"] = {
            "transport_id": data["transport_id"]
        }

        for i, fridge in enumerate(data["fridges"], start=1):
            section_name = f"FRIDGE_{i}"
            config[section_name] = {
                "fridge_id": fridge["fridge_id"],
                "component": fridge["component"]
            }

        with open("config.ini", "w") as config_file:
            config.write(config_file)


if __name__ == "__main__":
    def on_submit(data):
        print("Send data:", data)

    root = tk.Tk()
    root.title("Initial Form")
    form = InitialForm(root, on_submit)
    root.mainloop()
