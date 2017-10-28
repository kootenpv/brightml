import os
import platform
import numpy as np


def on_power(power_supply_path):
    for supply in os.listdir(power_supply_path):
        # check if supply other than BATTERY is "online"
        if supply.startswith("BAT"):
            continue
        online_path = os.path.join(power_supply_path, supply, "online")
        with open(online_path) as f:
            online = f.read().strip()
            if online == "1":
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
    # missing value if not on linux
    if operating_system != "Linux":
        return np.nan
    # if on_power, return highest score (100%)
    if on_power(power_supply_path):
        return 100
    # get aggregated battery percentage
    return get_battery_percentage(power_supply_path)
