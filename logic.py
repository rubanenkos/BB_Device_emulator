import random
import time
import requests
from datetime import datetime
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

BACKEND_URL = 'http://127.0.0.1:5000/create-transport-sensor'

transport_id = int(config["TRANSPORT"]["transport_id"])

BLOOD_COMPONENTS = {
    "Plasma": {"temp_min": -30, "temp_max": -15},
    "Platelets": {"temp_min": 20, "temp_max": 24},
    "Red Blood Cells": {"temp_min": 1, "temp_max": 6},
}

FRIDGES = []
for section in config.sections():
    if section.startswith("FRIDGE_"):
        fridge_id_str = config[section].get("fridge_id", "").strip()
        if not fridge_id_str.isdigit():
            print(f"Skipping section {section} due to missing or invalid fridge_id.")
            continue

        fridge_id = int(fridge_id_str)
        component = config[section].get("component", "Plasma")

        if component not in BLOOD_COMPONENTS:
            print(f"Skipping section {section}: Invalid component '{component}'.")
            continue

        FRIDGES.append({
            "id": fridge_id,
            "temp_min": BLOOD_COMPONENTS[component]["temp_min"],
            "temp_max": BLOOD_COMPONENTS[component]["temp_max"],
            "interval": int(config[section].get("interval", 3)),
        })


def generate_temperature(temp_min, temp_max, anomaly_chance=0):
    normal_range = (temp_max - temp_min)
    new_temp_min = temp_min - normal_range / 2
    new_temp_max = temp_max + normal_range / 2

    if anomaly_chance > 0 and random.randint(1, 100) <= anomaly_chance:
        return round(random.uniform(new_temp_min, new_temp_max), 2)
    return round(random.uniform(temp_min, temp_max), 2)


def send_temperature(running, update_ui, update_indicator, fridge_active, anomaly_chances):
    """Эмулирует отправку данных о температуре и времени для каждого холодильника."""
    while running():
        for fridge, active_var, anomaly_chance_var in zip(FRIDGES, fridge_active, anomaly_chances):
            if not running():
                break

            if not active_var.get():
                update_ui(fridge["id"], "-", "The refrigerator is turned off.")
                continue

            try:
                anomaly_chance = int(anomaly_chance_var.get())
            except ValueError:
                anomaly_chance = 0

            temperature = generate_temperature(
                fridge["temp_min"], fridge["temp_max"], anomaly_chance
            )
            timestamp = datetime.now().isoformat()
            parsed_timestamp = datetime.fromisoformat(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

            status = "good"
            if temperature < fridge["temp_min"]:
                status = "critical low"
            elif temperature > fridge["temp_max"]:
                status = "critical high"

            payload = {
                "blood_transport_id": transport_id,
                "blood_fridge_id": fridge["id"],
                "temperature": temperature,
                "time_stamp": parsed_timestamp,
                "status": status,
            }

            try:
                print("Data send:", payload)
                response = requests.post(BACKEND_URL, json=payload)
                if response.status_code == 201:
                    update_ui(fridge["id"], temperature, "Data send successfully.")
                    update_indicator(fridge["id"], status == "normal")
                else:
                    update_ui(fridge["id"], "-", f"Error {response.status_code}.")
            except Exception as e:
                update_ui(fridge["id"], "-", f"Error: {e}")

            time.sleep(fridge["interval"])
