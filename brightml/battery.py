import os
import platform
import numpy as np


def is_discharging(power_supply_path):
    for supply in os.listdir(power_supply_path):
        if not supply.startswith("BAT"):
            continue
        status_path = os.path.join(power_supply_path, supply, "status")
        with open(status_path) as f:
            status = f.read().strip()
            if status == "Discharging":
                return True
    return False


def get_battery_percentage(power_supply_path):
    available_supply = 0
    max_supply = 0
    for supply in os.listdir(power_supply_path):
        if not supply.startswith("BAT"):
            continue
        # current battery
        charge_now_path = os.path.join(power_supply_path, supply, "charge_now")
        with open(charge_now_path) as f:
            charge_now = int(f.read().strip())
            available_supply += charge_now
        # battery full
        charge_full_path = os.path.join(power_supply_path, supply, "charge_full")
        with open(charge_full_path) as f:
            charge_full = int(f.read().strip())
            max_supply += charge_full
    return available_supply / max_supply * 100


def get_battery_feature(power_supply_path="/sys/class/power_supply/"):
    operating_system = platform.system()
    if operating_system != "Linux":
        return np.nan
    if not is_discharging(power_supply_path):
        return 100
    return get_battery_percentage(power_supply_path)
