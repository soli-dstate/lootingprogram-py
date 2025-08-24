import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from datetime import datetime
import logging
import time
import sys
import platform
import threading
import warnings
import json
import pygame
import random
import zipfile
import base64
import pickle
import uuid
import calendar
import uuid
import psutil
import ctypes
import os
import tkinter as tk

# don't add anything new, all of these need to be run pre-setup

version = "4.0.0"

ctypes.windll.kernel32.SetConsoleTitleW(f"Loot {version}")

ide_envs = [
    ("TERM_PROGRAM", ["vscode", "vscode-insiders", "vscodium"]),
    ("PYCHARM_HOSTED", ["1"]),
    ("SPYDER_PID", [""]),
    ("JUPYTER_PLATFORM", [""]),
    ("ATOM_HOME", [""]),
    ("SUBLIME_TEXT", [""]),
    ("VSCODE_PID", [""]),
    ("VSCODE_CWD", [""]),
    ("VSCODE_IPC_HOOK", [""]),
]

devmode = False
for env_var, values in ide_envs:
    env_val = os.environ.get(env_var, "").lower()
    for v in values:
        if v and v in env_val:
            devmode = True
            break
        elif v == "" and env_val:
            devmode = True
            break
    if devmode:
        break
if "-dev" in sys.argv:
    devmode = True

if not os.path.exists("log"):
    os.makedirs("log")

log_dir = "./log"
existing_logs = [f for f in os.listdir(log_dir) if f.startswith("log") and f.endswith(".log")]
log_numbers = []
for fname in existing_logs:
    parts = fname.split('-')
    if parts[0].startswith("log") and parts[0][3:].isdigit():
        log_numbers.append(int(parts[0][3:]))
if len(log_numbers) >= 50:
    archive_index = len([f for f in os.listdir(log_dir) if f.startswith("archive") and f.endswith(".zip")]) + 1
    archive_name = f"archive{archive_index}.zip"
    archive_path = os.path.join(log_dir, archive_name)
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for fname in existing_logs:
            archive.write(os.path.join(log_dir, fname), fname)
            os.remove(os.path.join(log_dir, fname))
    log_number = 1
else:
    log_number = max(log_numbers, default=0) + 1

log_filename = f"./log/log{log_number}-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_filename)
    ]
)

if devmode:
    def show_log_window():
        def update_log_content():
            try:
                with open(log_filename, "r", encoding="utf-8") as f:
                    log_content = f.read()
            except Exception as e:
                log_content = f"Failed to read log file: {e}"
            text.config(state="normal")
            text.delete("1.0", tk.END)
            text.insert("1.0", log_content)
            text.config(state="disabled")
            root.after(1000, update_log_content)

        root = tk.Tk()
        root.title("Log")
        text = tk.Text(root, wrap="none", width=120, height=40)
        text.config(state="disabled")
        text.pack(expand=True, fill="both")
        scrollbar_y = tk.Scrollbar(root, orient="vertical", command=text.yview)
        scrollbar_y.pack(side="right", fill="y")
        text.config(yscrollcommand=scrollbar_y.set)
        scrollbar_x = tk.Scrollbar(root, orient="horizontal", command=text.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        text.config(xscrollcommand=scrollbar_x.set)
        root.after(1000, update_log_content)
        root.mainloop()
    threading.Thread(target=show_log_window, daemon=True).start()

logging.info(f"Log initialized @ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} {time.tzname[0]}, version {version}")
logging.info(f"Python version: {sys.version}")
logging.info(f"OS: {os.name}, System: {platform.system()}, Release: {platform.release()}, Version: {platform.version()}, Machine: {platform.machine()}, Processor: {platform.processor()}, Cores: {os.cpu_count()}")

if devmode:
    logging.info("Running in development mode.")
elif not devmode:
    logging.info("Running in production mode.")

# get system information for debugging later on

def log_exceptions_and_warnings():
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    def handle_warning(message, category, filename, lineno, file=None, line=None):
        logging.warning(f"{category.__name__}: {message} ({filename}:{lineno})")
    sys.excepthook = handle_exception
    warnings.showwarning = handle_warning
threading.Thread(target=log_exceptions_and_warnings, daemon=True).start()
logging.info("Exception and warning logging thread started successfully.")

logging.info("Loaded the following modules: %s", ", ".join(sys.modules.keys()))

def print_menu(options):
    for i, option in enumerate(options, start=1):
        print(f"[{i}] {option}")

def get_user_choice(max_option):
    choice = None
    while choice is None or choice < 1 or choice > max_option:
        try:
            choice = int(input(f"Enter your choice (1-{max_option}): "))
        except ValueError:
            pass
    return choice

def find_first_instance(iterable, key):
    for item in iterable:
        if isinstance(item, dict) and key in item:
            return item[key]
    raise ValueError(f"{key} not found in iterable")

def update_check():
    logging.info("Checking for updates...")
    print("This is a placeholder for the update checker. Pretend it checked for updates reaaal good.")

def anticheat_abort(detected):
    logging.critical(f"Anticheat initialized abort function due to {detected}")
    if os.name == "nt":
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Anticheat initialized abort function due to {detected}, Loot {version}",
            "Anticheat Alert",
            0x10
        )
    else:
        print(f"ANTICHEAT ALERT: {detected}")
    os.abort()

def anticheat():
    if not devmode:
        logging.info("Anticheat started successfully.")
        while True:
            suspicious_processes = ["cheatengine", "cheatengine-x86_64", "cheatengine-x86", "cheatengine.exe"]
            try:
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] and any(susp in proc.info['name'].lower() for susp in suspicious_processes):
                        logging.warning("Suspicious process detected: %s", proc.info['name'])
                        anticheat_abort(f"Suspicious process detected: {proc.info['name']}")
            except ImportError:
                logging.warning("psutil not installed, process check skipped.")
            try:
                pid = os.getpid()
                suspicious_dlls = ["cheatengine-i386.dll", "cheatengine-x86_64.dll", "cheatengine-x86.dll", "cheatengine.dll"]
                if os.name == "nt":
                    proc = psutil.Process(pid)
                    for dll in proc.memory_maps():
                        dll_name = os.path.basename(dll.path).lower()
                        if any(susp in dll_name for susp in suspicious_dlls):
                            logging.warning("Suspicious DLL detected: %s", dll_name)
                            anticheat_abort(f"Suspicious DLL detected: {dll_name}")
            except Exception as e:
                logging.warning(f"Failed to check for DLL hooks: {e}")
            suspicious_changes = False
            try:
                money = find_first_instance(data, "money")
                freeslots = find_first_instance(data, "freeslots")
                usedslots = find_first_instance(data, "usedslots")
                prev_money = persistent_data[3].get("previous_money") if len(persistent_data) > 3 else None
                prev_freeslots = persistent_data[1].get("previous_inventory") if len(persistent_data) > 1 else None
                prev_usedslots = persistent_data[2].get("previous_uuid") if len(persistent_data) > 2 else None
                if prev_money is not None and abs(money - prev_money) > 100_000:
                    suspicious_changes = True
                    logging.critical(f"Possible memory editing detected: money changed from {prev_money} to {money}")
                    anticheat_abort(f"Possible memory editing detected: money changed from {prev_money} to {money}")
                if prev_freeslots is not None and abs(freeslots - prev_freeslots) > 50:
                    suspicious_changes = True
                    logging.critical(f"Possible memory editing detected: freeslots changed from {prev_freeslots} to {freeslots}")
                    anticheat_abort(f"Possible memory editing detected: freeslots changed from {prev_freeslots} to {freeslots}")
                if prev_usedslots is not None and abs(usedslots - prev_usedslots) > 50:
                    suspicious_changes = True
                    logging.critical(f"Possible memory editing detected: usedslots changed from {prev_usedslots} to {usedslots}")
                    anticheat_abort(f"Possible memory editing detected: usedslots changed from {prev_usedslots} to {usedslots}")
            except Exception as e:
                logging.warning(f"Anticheat data check failed: {e}")
            time.sleep(1)
    else:
        logging.info("Anticheat disabled due to development mode.")

threading.Thread(target=anticheat, daemon=True).start()
logging.info("Anticheat thread started successfully.")

folders = ["transfer", "modules"]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        logging.info(f"Created folder: {folder}")
    else:
        logging.info(f"Folder already exists: {folder}")

module_files = [f for f in os.listdir("./modules") if f.endswith(".py")]
modules_info = []
for fname in module_files:
    mod_path = os.path.join("./modules", fname)
    mod_name = fname[:-3]
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(mod_name, mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        displayname = getattr(mod, "displayname", mod_name)
        modules_info.append({"filename": fname, "displayname": displayname})
    except Exception as e:
        modules_info.append({"filename": fname, "displayname": f"Error loading: {e}"})
logging.info("Modules found in ./modules/: " + ", ".join([f"{info['filename']} ({info['displayname']})" for info in modules_info]))

if devmode:
    saves_folder = "./saves"
else:
    appdata = os.getenv("APPDATA") or os.path.expanduser("~/.local/share")
    saves_folder = os.path.join(appdata, "soli_dstate", "looting", "saves")

if not os.path.exists(saves_folder):
    os.makedirs(saves_folder)
    logging.info(f"Created folder: saves")
else:
    logging.info("Folder already exists: saves")

soundsinstalled = None

if not os.path.exists("sounds"):
    logging.info("Optional SFX folder is missing. Sounds will not be played.")
    soundsinstalled = False
else:
    logging.info("Optional SFX folder is installed. Sounds will be played.")
    soundsinstalled = True

# setup complete after this point, tables next. any tables added after this point and before the next
# will break things. so like, don't do it

rarity_weights = {
    "common": 60,
    "uncommon": 25,
    "rare": 10,
    "legendary": 4,
    "mythic": 1
}

rifles = [
    {
        "name": "Colt AR-15 Sporter",
        "value": 1200,
        "description": "Gas-operated polymer framed semi-automatic assault rifle. Staple of American schools!",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 0,
        "firearm": True,
        "type": "Rifle",
        "caliber": [".223 Remington", "5.56x45mm NATO"],
        "action": "Semi",
        "cyclic": 700,
        "magazinetype": "Detachable Box",
        "magazinesystem": "STANAG"
    },
    {
        "name": "Remington 700",
        "value": 750,
        "description": "Bolt-action .308 hunting rifle. If you like hunting, this one is for you!",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 1,
        "firearm": True,
        "type": "Rifle",
        "caliber": [".308 Winchester", "7.62x51mm NATO"],
        "action": "Bolt",
        "magazinetype": "Internal",
        "internaltype": "Box",
        "magazinecapacity": 5,
    },
    {
        "name": "Winchester Model 70",
        "value": 900,
        "description": "Bolt-action .308 hunting rifle. It's uh... it's a rifle!",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 2,
        "firearm": True,
        "type": "Rifle",
        "caliber": [".308 Winchester", "7.62x51mm NATO"],
        "action": "Bolt",
        "magazinetype": "Internal",
        "internaltype": "Box",
        "magazinecapacity": 5
    },
    {
        "name": "Marlin Model 336",
        "value": 800,
        "description": "Lever-action .30-30 rifle. For your cowboy larping.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 3,
        "firearm": True,
        "type": "Rifle",
        "caliber": ".30-30 Winchester",
        "action": "Lever",
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 6
    },
    {
        "name": "Ruger Mini-14",
        "value": 900,
        "description": "Gas-operated .223 Remington rifle. Perfect for... uhm... uh... I dunno.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 4,
        "firearm": True,
        "type": "Rifle",
        "caliber": [".223 Remington", "5.56x45mm NATO"],
        "action": "Semi",
        "cyclic": 600,
        "magazinetype": "Detachable Box",
        "magazinesystem": "Mini-14"
    },
    {
        "name": "SKS",
        "value": 700,
        "description": "Gas-operated, magazine-fed 7.62x39mm semi-automatic rifle. Cheap Soviet slop.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 5,
        "firearm": True,
        "type": "Rifle",
        "caliber": "7.62x39mm",
        "action": "Semi",
        "cyclic": 600,
        "magazinetype": "Detachable Box",
        "magazinesystem": "SKS"
    },
    {
        "name": "Mosin-Nagant",
        "value": 600,
        "description": "Bolt-action 7.62x54mmR rifle. Cheaper Soviet slop. You can probably buy hundreds of these for a pennies on the dollar.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 6,
        "firearm": True,
        "type": "Rifle",
        "caliber": "7.62x54mmR",
        "action": "Bolt",
        "magazinetype": "Internal",
        "internaltype": "Box",
        "magazinesystem": "Mosin-Nagant"
    },
    {
        "name": "Polytech AK-74",
        "value": 800,
        "description": "Gas-operated, magazine-fed 5.45x39mm rifle. Chinese garbage.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 7,
        "firearm": True,
        "type": "Rifle",
        "caliber": "5.45x39mm",
        "action": "Semi",
        "cyclic": 650,
        "magazinetype": "Detachable Box",
        "magazinesystem": "AK-74"
    },
    {
        "name": "Lee-Enfield No. 4",
        "value": 600,
        "description": "Bolt-action .303 British rifle. It's fucking British. Disgusting.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 8,
        "firearm": True,
        "type": "Rifle",
        "caliber": ".303 British",
        "action": "Bolt",
        "magazinetype": "Internal",
        "internaltype": "Box",
        "magazinecapacity": 10
    },
    {
        "name": "Springfield M1903",
        "value": 800,
        "description": "Bolt-action .30-06 Springfield rifle. Good 'ol American stopping power.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 9,
        "firearm": True,
        "type": "Rifle",
        "caliber": ".30-06 Springfield",
        "action": "Bolt",
        "magazinetype": "Internal",
        "internaltype": "Box",
        "magazinecapacity": 5
    },
    {
        "name": "FN FAL",
        "value": 2500,
        "description": "Gas-operated, semi-automatic magazine-fed .308 rifle. The right arm of the free world.",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 10,
        "firearm": True,
        "type": "Rifle",
        "caliber": [".308 Winchester", "7.62x51mm NATO"],
        "action": "Semi",
        "cyclic": 650,
        "magazinetype": "Detachable Box",
        "magazinesystem": "FAL"
    },
    {
        "name": "HK91",
        "value": 5000,
        "description": "Gas-operated, semi-automatic magazine-fed .308 rifle. Look at you. Fancy pants. With your fucking HK.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 11,
        "firearm": True,
        "type": "Rifle",
        "caliber": [".308 Winchester", "7.62x51mm NATO"],
        "action": "Semi",
        "hk": True,
        "cyclic": 500,
        "magazinetype": "Detachable Box",
        "magazinesystem": "G3"
    },
    {
        "name": "Colt M16A1",
        "value": 10500,
        "description": "Gas-operated, fully-automatic magazine-fed .223 rifle. Pre-86 transferable machine gun, very sought after.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 12,
        "firearm": True,
        "type": "Rifle",
        "caliber": [".223 Remington", "5.56x45mm NATO"],
        "action": "Automatic",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "STANAG"
    }
]
shotguns = [
    {
        "name": "Remington 870",
        "value": 400,
        "description": "Pump-action tube-fed 12 gauge shotgun. The choice shotgun by cops and home defenders.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 13,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Pump",
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 5
    },
    {
        "name": "Mossberg 500",
        "value": 350,
        "description": "Pump-action tube-fed 12 gauge shotgun. Most well known for being used by a blonde dog girl.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 14,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Pump",
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 5
    },
    {
        "name": "Winchester Model 1300",
        "value": 300,
        "description": "Pump-action tube-fed 12 gauge shotgun. Incase you can't afford an 870 or M500.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 15,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Pump",
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 5
    },
    {
        "name": "Ithaca Model 37",
        "value": 350,
        "description": "Pump-action tube-fed 12 gauge shotgun. Basic bitch.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 16,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Pump",
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 5
    },
    {
        "name": "Remington 1100",
        "value": 700,
        "description": "Semi-automatic tube-fed 12 gauge shotgun. Incase your arms are too weak for the pump-action. Pansy.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 17,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Semi",
        "cyclic": 300,
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 4
    },
    {
        "name": "Remington 11-87",
        "value": 800,
        "description": "Semi-automatic tube-fed 12 gauge shotgun. Do you really need a semi automatic shotgun?",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 18,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Semi",
        "cyclic": 300,
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 4
    },
    {
        "name": "Browning Auto-5",
        "value": 900,
        "description": "Semi-automatic tube-fed 12 gauge shotgun. Thanks John Moses Browning!",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 19,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Semi",
        "cyclic": 700,
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 5
    },
    {
        "name": "Beretta 303",
        "value": 950,
        "description": "Semi-automatic tube-fed 12 gauge shotgun. Italian... uh... craftsmanship I guess.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 20,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Semi",
        "cyclic": 700,
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 5
    },
    {
        "name": "Browning Citori",
        "value": 700,
        "description": "Over-under double barrel 12 gauge shotgun. For the duck hunter that wear suits by day.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 21,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Semi",
        "cyclic": 700,
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 2,
        "can_chamber_extra": False
    },
    {
        "name": "Ruger Red Label",
        "value": 500,
        "description": "Over-under double barrel 12 gauge shotgun. For the duck hunter that works in the trades.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 22,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Semi",
        "cyclic": 700,
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 2,
        "can_chamber_extra": False
    },
    {
        "name": "Stevens Model 311",
        "value": 200,
        "description": "Side-by-side double barrel 12 gauge shotgun. For the duck hunter that uh... fucks their cousin.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 23,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Simultaneous",
        "magazinetype": "Internal",
        "internaltype": "Box",
        "magazinecapacity": 2,
        "can_chamber_extra": False
    },
    {
        "name": "Mossberg 590A1",
        "value": 2500,
        "description": "Pump-action 12 gauge shotgun. Favorite of the US military.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 24,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Pump",
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 8
    },
    {
        "name": "SPAS-12",
        "value": 4500,
        "description": "Semi-automatic 12 gauge shotgun. Favorite of uh... cops I guess.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 25,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Semi",
        "cyclic": 300,
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 8
    },
    {
        "name": "Benelli M1 Super 90",
        "value": 3500,
        "description": "Semi-automatic 12 gauge shotgun. Incase you're afraid of American things.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 26,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "12 gauge",
        "action": "Semi",
        "cyclic": 300,
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 8
    },
    {
        "name": "Remington Model 11",
        "value": 600,
        "description": "And I swear that I don't have a gun... No, I don't have a gun...",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 27,
        "firearm": True,
        "type": "Shotgun",
        "caliber": "20 gauge",
        "action": "Semi",
        "cyclic": 300,
        "magazinetype": "Internal",
        "internaltype": "Tube",
        "magazinecapacity": 5
    }
]
pistols = [
    {
        "name": "Beretta 92FS",
        "value": 500,
        "description": "Semi-automatic 9x19mm Parabellum pistol. Guess the military wants to get rid of American manufacturing.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 28,
        "firearm": True,
        "type": "Pistol",
        "caliber": "9x19mm Parabellum",
        "action": "Semi",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "M9"
    },
    {
        "name": "Glock 17 Gen 1",
        "value": 1000,
        "description": "Semi-automatic 9x19mm Parabellum pistol. Glock 7, porcelain gun made in Germany. It doesn't show up on your airport x-ray machines here and it costs more than what you make in a month!",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 29,
        "firearm": True,
        "type": "Pistol",
        "caliber": "9x19mm Parabellum",
        "action": "Semi",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "Glock"
    },
    {
        "name": "SIG Sauer P226",
        "value": 1200,
        "description": "Semi-automatic 9x19mm Parabellum pistol. At least it's not a P320!",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 30,
        "firearm": True,
        "type": "Pistol",
        "caliber": "9x19mm Parabellum",
        "action": "Semi",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "P226"
    },
    {
        "name": "Smith & Wesson 5906",
        "value": 700,
        "description": "Semi-automatic 9x19mm Parabellum pistol. Quality American stainless steel.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 31,
        "firearm": True,
        "type": "Pistol",
        "caliber": "9x19mm Parabellum",
        "action": "Semi",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "5906"
    },
    {
        "name": "CZ-75",
        "value": 1500,
        "description": "Semi-automatic 9x19mm Parabellum pistol. Czechoslovakia? What is that, some kind of Soviet meal?",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 32,
        "firearm": True,
        "type": "Pistol",
        "caliber": "9x19mm Parabellum",
        "action": "Semi",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "CZ-75"
    },
    {
        "name": "Colt M1911A1",
        "value": 350,
        "description": "Semi-automatic .45 ACP pistol. Muh two world wars.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 33,
        "firearm": True,
        "type": "Pistol",
        "caliber": ".45 ACP",
        "action": "Semi",
        "cyclic": 600,
        "magazinetype": "Detachable Box",
        "magazinesystem": "M1911"
    },
    {
        "name": "Browning Hi-Power",
        "value": 500,
        "description": "Semi-automatic 9x19mm Parabellum pistol. John Moses Browning's last design, kinda.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 34,
        "firearm": True,
        "type": "Pistol",
        "caliber": "9x19mm Parabellum",
        "action": "Semi",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "Hi-Power"
    },
    {
        "name": "Walther P38",
        "value": 600,
        "description": "Semi-automatic 9x19mm Parabellum pistol. What can I say without making a Nazi joke...",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 35,
        "firearm": True,
        "type": "Pistol",
        "caliber": "9x19mm Parabellum",
        "action": "Semi",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "P38"
    },
    {
        "name": "Walther PPK",
        "value": 400,
        "description": "Semi-automatic .380 ACP pistol. This is the gun that killed Hitler!",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 36,
        "firearm": True,
        "type": "Pistol",
        "caliber": ".380 ACP",
        "action": "Semi",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "PPK"
    },
    {
        "name": "Beretta 84",
        "value": 450,
        "description": "Semi-automatic .380 ACP pistol. Suitable for hiding in your waistband.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 37,
        "firearm": True,
        "type": "Pistol",
        "caliber": ".380 ACP",
        "action": "Semi",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "84"
    },
    {
        "name": "AMT Backup",
        "value": 300,
        "description": "Semi-automatic .380 ACP pistol. I hate .380 ACP so much.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 38,
        "firearm": True,
        "type": "Pistol",
        "caliber": ".380 ACP",
        "action": "Semi",
        "cyclic": 300,
        "magazinetype": "Detachable Box",
        "magazinesystem": "Backup"
    },
    {
        "name": "Smith & Wesson Model 10",
        "value": 350,
        "description": "Revolver chambered in .38 Special. Tiny revolver.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 39,
        "firearm": True,
        "type": "Revolver",
        "caliber": ".38 Special",
        "action": "Double",
        "cyclic": 180,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 6,
        "can_chamber_extra": False
    },
    {
        "name": "Smith & Wesson Model 19",
        "value": 500,
        "description": "Revolver chambered in .357 Magnum. That's some stopping power right there.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 40,
        "firearm": True,
        "type": "Revolver",
        "caliber": [".357 Magnum", ".38 Special"],
        "action": "Double",
        "cyclic": 180,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 6,
        "can_chamber_extra": False
    },
    {
        "name": "Smith & Wesson Model 66",
        "value": 700,
        "description": "Revolver chambered in .357 Magnum. Stainless steel and ready to stop bandits.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 41,
        "firearm": True,
        "type": "Revolver",
        "caliber": [".357 Magnum", ".38 Special"],
        "action": "Double",
        "cyclic": 180,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 6,
        "can_chamber_extra": False
    },
    {
        "name": "Colt Python",
        "value": 800,
        "description": "Revolver chambered in .357 Magnum. The king of revolvers.",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 42,
        "firearm": True,
        "type": "Revolver",
        "caliber": [".357 Magnum", ".38 Special"],
        "action": "Double",
        "cyclic": 180,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 6,
        "can_chamber_extra": False
    },
    {
        "name": "Ruger GP100",
        "value": 750,
        "description": "Revolver chambered in .357 Magnum. Incase you can't afford a Python, but don't want a Model 66.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 43,
        "firearm": True,
        "type": "Revolver",
        "caliber": [".357 Magnum", ".38 Special"],
        "action": "Double",
        "cyclic": 180,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 6,
        "can_chamber_extra": False
    },
    {
        "name": "Colt Anaconda",
        "value": 900,
        "description": "Revolver chambered in .44 Magnum. THE KING GOT BETTER?!",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 44,
        "firearm": True,
        "type": "Revolver",
        "caliber": ".44 Magnum",
        "action": "Double",
        "cyclic": 180,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 6,
        "can_chamber_extra": False
    },
    {
        "name": "Smith & Wesson Model 36",
        "value": 400,
        "description": "Revolver chambered in .38 Special. Tiny revolver for tiny men.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 45,
        "firearm": True,
        "type": "Revolver",
        "caliber": ".38 Special",
        "action": "Double",
        "cyclic": 180,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 6,
        "can_chamber_extra": False
    },
    {
        "name": "Smith & Wesson Model 60",
        "value": 450,
        "description": "Revolver chambered in .38 Special. I'm so tired of these .38 specials.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 46,
        "firearm": True,
        "type": "Revolver",
        "caliber": ".38 Special",
        "action": "Double",
        "cyclic": 180,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 6,
        "can_chamber_extra": False
    },
    {
        "name": "Smith & Wesson Model 29",
        "value": 750,
        "description": "Revolver chambered in .44 Magnum. Dirty Harry's trusty 6 shooter.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 173,
        "firearm": True,
        "type": "Revolver",
        "caliber": ".44 Magnum",
        "action": "Double",
        "cyclic": 180,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 6,
        "can_chamber_extra": False
    },
    {
        "name": "Ruger Super Blackhawk",
        "value": 550,
        "description": "Revolver chambered in .44 Magnum. Incase the deer challenge you to a duel.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 174,
        "firearm": True,
        "type": "Revolver",
        "caliber": ".44 Magnum",
        "action": "Single",
        "cyclic": 180,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 6,
        "can_chamber_extra": False
    },
    {
        "name": "H&K MP5A2",
        "value": 7500,
        "description": "Submachine gun chambered in 9x19mm Parabellum. Incase you want to larp as a SWAT officer.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 47,
        "firearm": True,
        "type": "Submachine Gun",
        "caliber": "9x19mm Parabellum",
        "action": "Automatic",
        "hk": True,
        "cyclic": 800,
        "magazinetype": "Detachable Box",
        "magazinesystem": "MP5",
        "include_in_character_creator": False
    },
    {
        "name": "MAC-10",
        "value": 4000,
        "description": "Submachine gun chambered in .45 ACP. Incase you want to larp as a gangster.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 48,
        "firearm": True,
        "type": "Submachine Gun",
        "caliber": ".45 ACP",
        "action": "Automatic",
        "cyclic": 1200,
        "magazinetype": "Detachable Box",
        "magazinesystem": "MAC-10",
        "include_in_character_creator": False
    },
]
ammunition = [
    {
        "name": "9x19mm Parabellum",
        "description": "A pretty popular pistol cartridge, .38 and .45 overshadow it still though.",
        "value": 1,
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 150,
        "inventoryslots": False,
        "id": 49,
        "caliber": "9x19mm Parabellum",
        "roundtype": ["Pistol", "Submachine Gun"],
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "FMJ +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "HP +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": "9x18mm Makarov",
        "description": "A Soviet handgun cartridge, known for its use in the Makarov pistol.",
        "value": 1,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 150,
        "inventoryslots": False,
        "id": 183,
        "caliber": "9x19mm Parabellum",
        "roundtype": ["Pistol", "Submachine Gun"],
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "FMJ +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "HP +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": ".223 Remington",
        "value": 2,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 120,
        "inventoryslots": False,
        "id": 50,
        "caliber": ".223 Remington",
        "roundtype": "Rifle",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "Armor Piercing",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2,
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": ".308 Winchester",
        "value": 3,
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 80,
        "inventoryslots": False,
        "id": 51,
        "caliber": ".308 Winchester",
        "roundtype": "Rifle",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "Armor Piercing",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2,
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": "5.56x45mm NATO",
        "value": 10,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 100,
        "inventoryslots": False,
        "id": 52,
        "caliber": "5.56x45mm NATO",
        "roundtype": "Rifle",
        "variants": [
            {
                "name": "M855 Ball",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1
            },
            {
                "name": "M856 Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Legendary",
                "costmult": 2
            },
            {
                "name": "M995 Armor Piercing",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Legendary",
                "costmult": 3
            },
            {
                "name": "M193 Ball",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 0.7
            },
            {
                "name": "M196 Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 1.25
            }
        ]
    },
    {
        "name": "7.62x51mm NATO",
        "value": 15,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 100,
        "inventoryslots": False,
        "id": 53,
        "caliber": "7.62x51mm NATO",
        "roundtype": "Rifle",
        "variants": [
            {
                "name": "M80 Ball",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 0.8
            },
            {
                "name": "M61 Armor Piercing",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 1.5
            },
            {
                "name": "M62 Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 1.25
            },
            {
                "name": "M993 Armor Piercing",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Legendary",
                "costmult": 2
            },
            {
                "name": "M948 Saboted Light Armor Penetrator",
                "wearmult": 2,
                "statchanges": None,
                "rarity": "Legendary",
                "costmult": 5
            },
            {
                "name": "M959 Saboted Light Armor Penetrator Tracer",
                "wearmult": 2.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Mythic",
                "costmult": 5.5
            }
        ]
    },
    {
        "name": "7.62x39mm",
        "value": 2,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 100,
        "inventoryslots": False,
        "id": 54,
        "caliber": "7.62x39mm",
        "roundtype": "Rifle",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "Armor Piercing",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2,
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": "7.62x54mmR",
        "value": 2,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 60,
        "inventoryslots": False,
        "id": 55,
        "caliber": "7.62x54mmR",
        "roundtype": "Rifle",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "Armor Piercing",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2,
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": "5.45x39mm",
        "value": 2,
        "rarity": "Legendary",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 60,
        "inventoryslots": False,
        "id": 56,
        "caliber": "5.45x39mm",
        "roundtype": "Rifle",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "Armor Piercing",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2,
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": ".303 British",
        "value": 2,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 50,
        "inventoryslots": False,
        "id": 57,
        "caliber": ".303 British",
        "roundtype": "Rifle",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "Armor Piercing",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2,
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": ".30-06 Springfield",
        "value": 3,
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 60,
        "inventoryslots": False,
        "id": 58,
        "caliber": ".30-06 Springfield",
        "roundtype": "Rifle",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "M2 Ball",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.25
            },
            {
                "name": "M25 Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "M2 Armor Piercing",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 3
            }
        ]
    },
    {
        "name": ".30-30 Winchester",
        "value": 2,
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 60,
        "inventoryslots": False,
        "id": 59,
        "caliber": ".30-30 Winchester",
        "roundtype": "Rifle",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Armor Piercing",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2,
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": "12 gauge",
        "value": 1,
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 50,
        "inventoryslots": False,
        "id": 60,
        "caliber": "12 gauge",
        "roundtype": "Shotgun",
        "variants": [
            {
                "name": "Birdshot",
                "wearmult": 0.8,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 0.75
            },
            {
                "name": "00 buckshot",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "Slug",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1.25
            },
            {
                "name": "Flechette",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "Duckshot",
                "wearmult": 0,
                "statchanges": None,
                "rarity": "Mythic",
                "costmult": 10
            },
            {
                "name": "Dragon's breath",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Mythic",
                "costmult": 10
            }
        ]
    },
    {
        "name": "20 gauge",
        "value": 1,
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 40,
        "inventoryslots": False,
        "id": 61,
        "caliber": "20 gauge",
        "roundtype": "Shotgun",
        "variants": [
            {
                "name": "Birdshot",
                "wearmult": 0.8,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 0.75
            },
            {
                "name": "#4 buckshot",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "Slug",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1.25
            },
            {
                "name": "Flechette",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "Duckshot",
                "wearmult": 0,
                "statchanges": None,
                "rarity": "Mythic",
                "costmult": 10
            },
            {
                "name": "Dragon's breath",
                "wearmult": 1.2,
                "statchanges": None,
                "rarity": "Mythic",
                "costmult": 10
            }
        ]
    },
    {
        "name": ".45 ACP",
        "value": 1,
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 100,
        "inventoryslots": False,
        "id": 62,
        "caliber": ".45 ACP",
        "roundtype": ["Pistol", "Submachine Gun"],
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "FMJ +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "HP +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": ".380 ACP",
        "value": 1,
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 80,
        "inventoryslots": False,
        "id": 63,
        "caliber": ".380 ACP",
        "roundtype": "Pistol",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "FMJ +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "HP +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": ".38 Special",
        "value": 1,
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 80,
        "inventoryslots": False,
        "id": 64,
        "caliber": ".38 Special",
        "roundtype": "Revolver",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "FMJ +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "HP +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": ".357 Magnum",
        "value": 2,
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 60,
        "inventoryslots": False,
        "id": 65,
        "caliber": ".357 Magnum",
        "roundtype": "Revolver",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "FMJ +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "HP +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    },
    {
        "name": ".44 Magnum",
        "value": 3,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 10,
        "max_quantity": 60,
        "inventoryslots": False,
        "id": 66,
        "caliber": ".44 Magnum",
        "roundtype": "Revolver",
        "variants": [
            {
                "name": "FMJ",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Common",
                "costmult": 1
            },
            {
                "name": "HP",
                "wearmult": 1,
                "statchanges": None,
                "rarity": "Uncommon",
                "costmult": 1.01
            },
            {
                "name": "Subsonic",
                "wearmult": 0.9,
                "statchanges": {
                    "Stealth": 1
                },
                "rarity": "Uncommon",
                "costmult": 1.1
            },
            {
                "name": "FMJ +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "HP +P",
                "wearmult": 1.5,
                "statchanges": None,
                "rarity": "Rare",
                "costmult": 2
            },
            {
                "name": "Tracer",
                "wearmult": 1.2,
                "statchanges": {
                    "Stealth": -1,
                    "Aim": 1
                },
                "rarity": "Rare",
                "costmult": 2
            }
        ]
    }
]
magazines = [
    {
        "name": "20 round STANAG magazine",
        "value": 10,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 3,
        "inventoryslots": False,
        "id": 67,
        "caliber": [".223 Remington", "5.56x45mm NATO"],
        "roundtype": "Rifle",
        "capacity": 20,
        "compatible_system": "STANAG"
    },
    {
        "name": "30 round STANAG magazine",
        "value": 25,
        "rarity": "Legendary",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": False,
        "id": 68,
        "caliber": [".223 Remington", "5.56x45mm NATO"],
        "roundtype": "Rifle",
        "capacity": 30,
        "compatible_system": "STANAG"
    },
    {
        "name": "5 round Mini-14 magazine",
        "value": 5,
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 4,
        "inventoryslots": False,
        "id": 69,
        "caliber": [".223 Remington", "5.56x45mm NATO"],
        "roundtype": "Rifle",
        "capacity": 5,
        "compatible_system": "Mini-14"
    },
    {
        "name": "20 round Mini-14 magazine",
        "value": 12,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": False,
        "id": 70,
        "caliber": [".223 Remington", "5.56x45mm NATO"],
        "roundtype": "Rifle",
        "capacity": 20,
        "compatible_system": "Mini-14"
    },
    {
        "name": "10 round SKS magazine",
        "value": 3,
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 5,
        "inventoryslots": False,
        "id": 71,
        "caliber": "7.62x39mm",
        "roundtype": "Rifle",
        "capacity": 10,
        "compatible_system": "SKS"
    },
    {
        "name": "30 round AK-74 magazine",
        "value": 12,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": False,
        "id": 72,
        "caliber": "5.45x39mm",
        "roundtype": "Rifle",
        "capacity": 30,
        "compatible_system": "AK-74"
    },
    {
        "name": "20 round FAL magazine",
        "value": 20,
        "rarity": "Legendary",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": False,
        "id": 73,
        "caliber": [".308 Winchester", "7.62x51mm NATO"],
        "roundtype": "Rifle",
        "capacity": 20,
        "compatible_system": "FAL"
    },
    {
        "name": "20 round G3/HK91 magazine",
        "value": 40,
        "rarity": "Mythic",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 1,
        "inventoryslots": False,
        "id": 74,
        "caliber": [".308 Winchester", "7.62x51mm NATO"],
        "roundtype": "Rifle",
        "capacity": 20,
        "compatible_system": "G3"
    },
    {
        "name": "30 round MP5 magazine",
        "value": 45,
        "rarity": "Mythic",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 1,
        "inventoryslots": False,
        "id": 75,
        "caliber": "9x19mm Parabellum",
        "roundtype": "Submachine Gun",
        "capacity": 30,
        "compatible_system": "MP5"
    },
    {
        "name": "30 round MAC-10 magazine",
        "value": 40,
        "rarity": "Mythic",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 1,
        "inventoryslots": False,
        "id": 76,
        "caliber": ".45 ACP",
        "roundtype": "Submachine Gun",
        "capacity": 30,
        "compatible_system": "MAC-10"
    },
    {
        "name": "15 round M9/Beretta 92FS magazine",
        "value": 10,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 3,
        "inventoryslots": False,
        "id": 77,
        "caliber": "9x19mm Parabellum",
        "roundtype": "Pistol",
        "capacity": 15,
        "compatible_system": "M9"
    },
    {
        "name": "17 round Glock magazine",
        "value": 20,
        "rarity": "Mythic",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": False,
        "id": 78,
        "caliber": "9x19mm Parabellum",
        "roundtype": "Pistol",
        "capacity": 17,
        "compatible_system": "Glock"
    },
    {
        "name": "15 round SIG P226 magazine",
        "value": 20,
        "rarity": "Mythic",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": False,
        "id": 79,
        "caliber": "9x19mm Parabellum",
        "roundtype": "Pistol",
        "capacity": 15,
        "compatible_system": "P226"
    },
    {
        "name": "16 round CZ-75 magazine",
        "value": 22,
        "rarity": "Mythic",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": False,
        "id": 80,
        "caliber": "9x19mm Parabellum",
        "roundtype": "Pistol",
        "capacity": 16,
        "compatible_system": "CZ-75"
    },
    {
        "name": "7 round M1911 magazine",
        "value": 3,
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 4,
        "inventoryslots": False,
        "id": 81,
        "caliber": ".45 ACP",
        "roundtype": "Pistol",
        "capacity": 7,
        "compatible_system": "M1911"
    },
    {
        "name": "13 round Hi-Power magazine",
        "value": 7,
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 3,
        "inventoryslots": False,
        "id": 82,
        "caliber": "9x19mm Parabellum",
        "roundtype": "Pistol",
        "capacity": 13,
        "compatible_system": "Hi-Power"
    },
    {
        "name": "8 round P38 magazine",
        "value": 6,
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 3,
        "inventoryslots": False,
        "id": 83,
        "caliber": "9x19mm Parabellum",
        "roundtype": "Pistol",
        "capacity": 8,
        "compatible_system": "P38"
    },
    {
        "name": "7 round PPK magazine",
        "value": 3,
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 4,
        "inventoryslots": False,
        "id": 84,
        "caliber": ".380 ACP",
        "roundtype": "Pistol",
        "capacity": 7,
        "compatible_system": "PPK"
    },
    {
        "name": "13 round Beretta 84 magazine",
        "value": 4,
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 4,
        "inventoryslots": False,
        "id": 85,
        "caliber": ".380 ACP",
        "roundtype": "Pistol",
        "capacity": 13,
        "compatible_system": "84"
    },
    {
        "name": "6 round Backup magazine",
        "value": 2,
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 4,
        "inventoryslots": False,
        "id": 86,
        "caliber": ".380 ACP",
        "roundtype": "Pistol",
        "capacity": 6,
        "compatible_system": "Backup"
    },
    {
        "name": "8 round Makarov magazine",
        "value": 2,
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 4,
        "inventoryslots": False,
        "id": 184,
        "caliber": "9x18mm Makarov",
        "roundtype": "Pistol",
        "capacity": 8,
        "compatible_system": "Makarov"
    },
    {
        "name": "10 round Dragunov magazine",
        "value": 2,
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 4,
        "inventoryslots": False,
        "id": 186,
        "caliber": "7.62x54mmR",
        "roundtype": "Rifle",
        "capacity": 10,
        "compatible_system": "Dragunov"
    },
    {
        "name": "45 round RPK-74 magazine",
        "value": 12,
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": False,
        "id": 188,
        "caliber": "5.45x39mm",
        "roundtype": "Rifle",
        "capacity": 45,
        "compatible_system": "AK-74"
    },
]
junk = [
    {
        "name": "Wood board",
        "value": 5,
        "description": "A cut board made from pine.",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 5,
        "inventoryslots": 2,
        "id": 87
    },
    {
        "name": "Steel tube",
        "value": 15,
        "description": "A rusted out chunk of steel tubing.",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 3,
        "inventoryslots": 2,
        "id": 88
    },
    {
        "name": "PVC pipe",
        "value": 2,
        "description": "A length of plastic tubing.",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 3,
        "inventoryslots": 1,
        "id": 89
    },
    {
        "name": "Sheet metal",
        "value": 25,
        "description": "A rusty piece of sheet metal, probably steel.",
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": 5,
        "id": 90
    },
    {
        "name": "Welding wire",
        "value": 50,
        "description": "A spindle of MIG welding wire.",
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": 1,
        "id": 91
    },
    {
        "name": "Welding wire",
        "value": 165,
        "description": "A length of TIG welding wire.",
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": 1,
        "id": 92
    },
    {
        "name": "Sling",
        "value": 15,
        "description": "A simple sling for weapons.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 93,
        "slot": "shoulder",
        "addedslots": 2
    },
    {
        "name": "Welding wire",
        "value": 50,
        "description": "A spindle of welding wire.",
        "rarity": "Rare",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": 1,
        "id": 94
    },
    {
        "name": "Empty can",
        "value": 1,
        "description": "An empty can, appears to be made of tin, was probably food at some point.",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 7,
        "inventoryslots": 1,
        "id": 95
    },
    {
        "name": "Empty can",
        "value": 2,
        "description": "An empty can, appears to be made of aluminum, probably was a drink of sorts.",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 12,
        "inventoryslots": 1,
        "id": 96
    },
    {
        "name": "Empty plastic bag",
        "value": 0,
        "description": "A plastic bag that's weak and falling apart, no good for carrying items.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 0,
        "id": 97
    },
    {
        "name": "Candy bar",
        "value": 5,
        "description": "It's your favorite candy bar! Aw shucks, it's expired though. Probably tastes like the souls of the damned.",
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 3,
        "inventoryslots": 1,
        "id": 98
    },
    {
        "name": "Soda",
        "value": 7,
        "description": "It's your favorite soda! Aw shucks, it's expired though. Probably tastes like the blood of the damned. Flat too, flatter than your mom!",
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 3,
        "inventoryslots": 1,
        "id": 99
    },
    {
        "name": "Motor oil",
        "value": 15,
        "description": "A quart bottle of motor oil. It's horrible and has metal chunks all up in it, it's probably used...",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 3,
        "inventoryslots": 1,
        "id": 100
    },
    {
        "name": "Glass bottle",
        "value": 2,
        "description": "An empty glass bottle that still has the stench of beer. You should smash it against a legion footsoldier's skull! Or your friends, I don't really care.",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 24,
        "inventoryslots": 2,
        "id": 101
    },
    {
        "name": "Screwdriver",
        "value": 15,
        "description": "A simple handheld screwdriver. Good for screwing and/or stabbing!",
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 5,
        "inventoryslots": 1,
        "id": 102
    },
    {
        "name": "Pry bar",
        "value": 15,
        "description": "A crowbar but it has a handle. Good for... uh... prying...?",
        "rarity": "Uncommon",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": 1,
        "id": 103
    },
    {
        "name": "Drill",
        "value": 75,
        "description": "A battery operated drill. It's uh... a drill.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 104
    },
    {
        "name": "Handsaw",
        "value": 10,
        "description": "A saw. But hand operated. Good for dismemberment if you try hard enough!",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 105
    },
    {
        "name": "Circular saw",
        "value": 10,
        "description": "A saw. But electric. This one is really good for dismemberment!",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 106
    },
    {
        "name": "Grinder",
        "value": 35,
        "description": "A grinder. You use it to grind. Better get on that grind real quick! HAAAAH, I'm so funny.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 107
    },
    {
        "name": "Match",
        "value": 1,
        "description": "Aw yep, that's a match right there.",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 50,
        "inventoryslots": 1,
        "id": 108
    },
    {
        "name": "Wristwatch",
        "value": 10,
        "description": "A watch, but for your wrist? What a novel idea!",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 109,
        "slot": "wrist"
    },
    {
        "name": "Literally garbage",
        "value": 0,
        "description": "Yeah... that's literally garbage...",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 15,
        "inventoryslots": 1,
        "id": 110
    },
    {
        "name": "Car battery",
        "value": 125,
        "description": "A 12 volt lead acid car battery. It's kinda hefty.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 111
    },
    {
        "name": "Gasoline",
        "value": 50,
        "description": "A jerry can full of gasoline that somehow hasn't evaporated or gone bad.",
        "rarity": "Mythic",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 2,
        "inventoryslots": 3,
        "id": 112
    },
    {
        "name": "Pocket sand",
        "value": 1,
        "description": "It's a ziploc bag full of sand with 'Pocket Sand' labelled on it in sharpie. [Blinds enemies for 1 turn]",
        "rarity": "Mythic",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 1,
        "inventoryslots": 1,
        "id": 113
    },
    {
        "name": "Cloth scrap",
        "value": 5,
        "description": "A scrap of cloth. It's not worth much, but it could be useful.",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 10,
        "inventoryslots": 1,
        "id": 114
    },
    {
        "name": "Stick",
        "value": 0,
        "description": "A simple stick. Not very useful on its own.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 115
    },
    {
        "name": "String",
        "value": 1,
        "description": "A length of string. Useful for tying things up.",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 5,
        "inventoryslots": 1,
        "id": 116
    }
]
consumables = [
    {
        "name": "Bandage",
        "value": 5,
        "description": "A wrap used to hold dressing in place. If tied tight enough, can stop bleeding on its own.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 117
    },
    {
        "name": "Dressing",
        "value": 10,
        "description": "A sterile pad used to cover and protect wounds.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 118
    },
    {
        "name": "Antiseptic",
        "value": 15,
        "description": "A solution used to kill bacteria and prevent infection.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 119
    },
    {
        "name": "Tourniquet",
        "value": 20,
        "description": "A device used to stop bleeding by applying pressure to a limb.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 120
    },
    {
        "name": "Can of beer",
        "value": 5,
        "description": "A can of beer. Nice, refreshing, American pisswater.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 121
    },
    {
        "name": "Bottle of beer",
        "value": 6,
        "description": "A bottle of beer. Nice, refreshing, American pisswater. Useful as a weapon when you're done!",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 122
    },
    {
        "name": "Can of soda",
        "value": 2,
        "description": "A can of soda. I love the taste of high fructose corn syrup!",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 123
    },
    {
        "name": "Pack of cigarettes",
        "value": 20,
        "description": "A pack of cigarettes. If you're gonna die anyways, what's the harm in a little smoke?",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 124
    },
    {
        "name": "Cigarette",
        "value": 1,
        "description": "A single cigarette. If you're gonna die anyways, what's the harm in a little smoke?",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 20,
        "inventoryslots": 1,
        "id": 125
    },
    {
        "name": "Painkillers",
        "value": 10,
        "description": "A small packet of painkillers. Useful for uh... killing pain what the fuck do you want me to tell you?",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 126
    },
    {
        "name": "Energy drink",
        "value": 5,
        "description": "A can of unhealthy carbonated sugar water that tastes like battery acid, but has 300mg of caffeine.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 127
    },
    {
        "name": "Instant coffee",
        "value": 5,
        "description": "A packet of instant coffee. Just add hot water, and you too can have a mediocre at best cup of coffee.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 128
    },
    {
        "name": "Type 1 Rapid Expanding Stabilizer",
        "value": 950,
        "description": "A needle with contents that expand rapidly upon injection, instantly stopping bleeding.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 129
    },
    {
        "name": "Type 2 Rapid Expanding Replacement",
        "value": 1500,
        "description": "A needle with contents that expand rapidly upon injection, meshing together with flesh and providing proper replacements to anything removed or displaced from open wounds. Unusable for limbs.",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 130
    },
    {
        "name": "Type 3 Rapid Expanding Repair",
        "value": 2500,
        "description": "A needle with contents that enter the bloodstream and rapidly repair and replace anything missing or wounded on the body. Can fix limbs, organs, and other vital structures.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 131
    },
    {
        "name": "Mechanical arm",
        "value": 1500,
        "description": "A mechanical replacement for a missing arm. Powered by movements in the shoulder to open and close the hand.",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 132
    },
    {
        "name": "Passive leg",
        "value": 1000,
        "description": "A passive replacement for a missing leg. Useful for stability and basic movement.",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 133
    },
    {
        "name": "Running blade",
        "value": 1500,
        "description": "A passive replacement for a missing leg. Useful for stability and sprinting fast on solid ground.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 134
    },
    {
        "name": "Can of beans",
        "value": 1,
        "description": "A can of beans. It's not much, but it's better than nothing.",
        "rarity": "Common",
        "random_quantity": True,
        "min_quantity": 1,
        "max_quantity": 10,
        "inventoryslots": 1,
        "id": 135
    },
    {
        "name": "MRE",
        "value": 25,
        "description": "A US military meal-ready-to-eat. Contains everything you need to have a hot meal on the go.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 136
    },
    {
        "name": "MRE",
        "value": 15,
        "description": "A Soviet meal-ready-to-eat. Contains everything you need to have hot Soviet slop on the go.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 137
    }
]
special = [
    {
        "name": "Triple Regret",
        "value": 10500,
        "description": "A deadly revolver for both the user and their target. Holds 3 .50 BMG rounds, the ones loaded are 3 M962 SLAPT rounds. Use them wisely.",
        "rarity": "Mythic",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 138,
        "firearm": True,
        "type": "Revolver",
        "caliber": "12.7x99mm NATO",
        "action": "Double",
        "cyclic": 300,
        "magazinetype": "Internal",
        "internaltype": "Cylinder",
        "magazinecapacity": 3,
        "can_chamber_extra": False
    },
    {
        "name": "Sony Walkman WM-AF59",
        "value": 500,
        "description": "A red Walkman. There's a pair of cheap earbuds hanging off of it and inside the Walkman lies a bright orange cassette labeled 'And One - Bodypop'.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 139
    },
    {
        "name": "Flash Goggles",
        "value": 250,
        "description": "A pair of flashbang-proof goggles. They're covered in... blonde dog hair? Must've been a golden retriever.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 140
    },
    {
        "name": "ALVMS MKIV",
        "value": 250,
        "description": "A well known toy gun. Shoots a little flag that says 'BANG!' out of the barrel. Made to look like some sort of futuristic railgun.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 141
    },
    {
        "name": "Colt M16A1",
        "value": 10500,
        "description": "Something's different about this M16... There's a yellow sticker on the magwell and the fire selector is yellow. (+2 aim while firing)",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 142,
        "firearm": True,
        "type": "Rifle",
        "caliber": [".223 Remington", "5.56x45mm NATO"],
        "action": "Automatic",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "STANAG"
    },
    {
        "name": "Can of Dr. Thunder",
        "value": 5,
        "description": "A can of Dr. Thunder. Rumor has it that consuming this beverage summons someone named Sam.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 143
    },
    {
        "name": "Can of Water",
        "value": 1,
        "description": "A regular old aluminum can of water. Rumor has it though, that consuming this summons someone named Mary.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 144
    },
    {
        "name": "Skeleton Key",
        "value": 15000,
        "description": "A key that can open any locked door.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 145
    }
]
craftables = [
    {
        "name": "Molotov cocktail",
        "value": 15,
        "description": "A crude mixture of gasoline and oil in a glass bottle with a wick, effective at lighting things on fire.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 146
    },
    {
        "name": "Gunpowder",
        "value": 5,
        "description": "A basic component for crafting ammunition and explosives.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 147
    },
    {
        "name": "Bullet casing",
        "value": 0.5,
        "description": "An empty bullet casing. Can be used to craft ammunition.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 148
    },
    {
        "name": "Improvised Explosive",
        "value": 25,
        "description": "Appears to be an ordinary can of food, until you notice the crude pin up top.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 149
    },
    {
        "name": "Improvised explosive charge",
        "value": 25,
        "description": "A crude explosive device in a plastic bag, meant to be put onto doors to blow them open.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 150
    },
    {
        "name": "Pipe bomb",
        "value": 50,
        "description": "A makeshift explosive device made from a PVC pipe filled with explosive material.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 151
    },
    {
        "name": "Makeshift bandage",
        "value": 5,
        "description": "A crude bandage made from torn clothing.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 152
    },
    {
        "name": "Spear",
        "value": 5,
        "description": "A simple spear made from a sharpened stick.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 153
    },
    {
        "name": "Advanced spear",
        "value": 10,
        "description": "An 'advanced' spear made from a sharpened stick and a screwdriver.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 154
    },
    {
        "name": "Makeshift tourniquet",
        "value": 5,
        "description": "A crude tourniquet made from string and a stick.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 155
    },
    {
        "name": "Small bullet",
        "value": 1,
        "description": "A small bullet, suitable for use in handguns.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 156
    },
    {
        "name": "Medium bullet",
        "value": 2,
        "description": "A medium bullet, suitable for use in rifles.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 157
    },
    {
        "name": "Large bullet",
        "value": 3,
        "description": "A large bullet, suitable for use in rifles.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 158
    },
    {
        "name": "Luty",
        "value": 250,
        "description": "A 9x19mm submachine gun crafted from common materials.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 159,
        "firearm": True,
        "type": "Submachine Gun",
        "caliber": "9x19mm Parabellum",
        "action": "Automatic",
        "cyclic": 600,
        "magazinetype": "Detachable Box",
        "magazinesystem": "Luty",
    },
    {
        "name": "Luty magazine",
        "value": 15,
        "description": "A magazine for the Luty submachine gun.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 160,
        "caliber": "9x19mm Parabellum",
        "roundtype": "Submachine Gun",
        "capacity": 30,
        "compatible_system": "Luty"
    },
    {
        "name": "Satchel",
        "value": 15,
        "description": "A satchel made out of cloth scraps.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 172,
        "slot": "Shoulder",
        "addedslots": 5
    }
]
armor = [
    {
        "name": "HRM tactical vest",
        "value": 250,
        "description": "A soft kevlar vest used by law enforcement.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 161,
        "slot": "Torso",
        "armorrating": "IIIa"
    },
    {
        "name": "PASGT vest",
        "value": 750,
        "description": "A standard issue soft kevlar vest used by the US military.",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 162,
        "slot": "Torso",
        "armorrating": "IIIa"
    },
    {
        "name": "RBA plate carrier",
        "value": 750,
        "description": "A modular plate carrier used by special forces.",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 189,
        "slot": "Torso",
        "subslots": ["Front plate", "Back plate"],
        "armorrating": "IIIa"
    },
    {
        "name": "6B3 vest",
        "value": 500,
        "description": "A standard issue plate carrier issued by the USSR.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 163,
        "slot": "Torso",
        "subslots": ["Front plate", "Back plate"]
    },
    {
        "name": "Kevlar vest",
        "value": 150,
        "description": "A simple soft kevlar vest, designed to stop handgun rounds.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 164,
        "slot": "Torso",
        "armorrating": "II"
    },
    {
        "name": "Kevlar vest",
        "value": 200,
        "description": "A simple soft kevlar vest, designed to stop more powerful handgun rounds, and even shotguns.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 165,
        "slot": "Torso",
        "armorrating": "IIIa"
    },
    {
        "name": "Plate carrier",
        "value": 250,
        "description": "A simple plate carrier. Has in-built soft protection against small arms, and slots for plates.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 166,
        "slot": "Torso",
        "subslots": ["Front plate", "Back plate"],
        "armorrating": "II",
    },
    {
        "name": "PASGT helmet",
        "value": 300,
        "description": "A standard issue helmet used by the US military.",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 167,
        "slot": "Head",
        "armorrating": "IIIa"
    },
    {
        "name": "SSh-68 helmet",
        "value": 250,
        "description": "A standard issue helmet used by the USSR.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 168,
        "slot": "Head",
        "armorrating": "IIIa"
    },
    {
        "name": "ALICE pack",
        "value": 150,
        "description": "A standard issue rucksack by the US military.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 169,
        "slot": "Back",
        "addedslots": 20
    },
    {
        "name": "RD-54 Airborne Assault Backpack",
        "value": 200,
        "description": "A standard issue airborne assault backpack used by the USSR.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 170,
        "slot": "Back",
        "addedslots": 15
    },
    {
        "name": "Backpack",
        "value": 50,
        "description": "A backpack, commonly used by children to go to school.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 171,
        "slot": "Back",
        "addedslots": 10
    }
]

non_lootables = [
    {
        "name": "Handcuffs",
        "value": 15,
        "description": "A crude mixture of gasoline and oil in a glass bottle with a wick, effective at lighting things on fire.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 175
    },
    {
        "name": "Expandable baton",
        "value": 25,
        "description": "A collapsible baton that can be easily carried and deployed.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 176
    },
    {
        "name": "Radio",
        "value": 50,
        "description": "A simple handheld radio.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 177
    },
    {
        "name": "Flashlight",
        "value": 30,
        "description": "A simple handheld flashlight.",
        "rarity": "Common",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 178
    },
    {
        "name": "Pepper spray",
        "value": 20,
        "description": "A canister of pepper spray, effective for self-defense.",
        "rarity": "Uncommon",
        "random_quantity": False,
        "inventoryslots": 1,
        "id": 179
    },
    {
        "name": "AKS-74",
        "value": 9500,
        "description": "Gas-operated assault rifle with a side-folding wire stock, designed for paratrooper use. Great for fighting off neo-nazis!",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 180,
        "firearm": True,
        "type": "Rifle",
        "caliber": "5.45x39mm",
        "action": "Automatic",
        "cyclic": 650,
        "magazinetype": "Detachable Box",
        "magazinesystem": "AK-74"
    },
    {
        "name": "AKS-74U",
        "value": 12500,
        "description": "Gas-operated assault rifle with a side-folding wire stock, shorter for special operations use. Great for fighting off neo-nazis!",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 181,
        "firearm": True,
        "type": "Rifle",
        "caliber": "5.45x39mm",
        "action": "Automatic",
        "cyclic": 650,
        "magazinetype": "Detachable Box",
        "magazinesystem": "AK-74"
    },
    {
        "name": "Makarov",
        "value": 250,
        "description": "Semi-automatic 9x19mm Parabellum pistol. Guess the military wants to get rid of American manufacturing.",
        "rarity": "Rare",
        "random_quantity": False,
        "inventoryslots": 2,
        "id": 182,
        "firearm": True,
        "type": "Pistol",
        "caliber": "9x18mm Makarov",
        "action": "Semi",
        "cyclic": 900,
        "magazinetype": "Detachable Box",
        "magazinesystem": "Makarov"
    },
    {
        "name": "Dragunov SVD",
        "value": 3000,
        "description": "A semi-automatic sniper rifle, known for its accuracy and power.",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 185,
        "firearm": True,
        "type": "Rifle",
        "caliber": "7.62x54mmR",
        "action": "Semi",
        "cyclic": 30,
        "magazinetype": "Detachable Box",
        "magazinesystem": "Dragunov"
    },
    {
        "name": "RPKS-74",
        "value": 15000,
        "description": "Gas-operated light machine gun with a side-folding wood stock, designed for paratrooper use. I know it's called a light machine gun, but is it really?",
        "rarity": "Legendary",
        "random_quantity": False,
        "inventoryslots": 3,
        "id": 187,
        "firearm": True,
        "type": "Rifle",
        "caliber": "5.45x39mm",
        "action": "Automatic",
        "cyclic": 650,
        "magazinetype": "Detachable Box",
        "magazinesystem": "AK-74"
    },
]

all_tables = []
seen_lists = set()
current_module = sys.modules[__name__]
for var_name in dir(current_module):
    if not var_name.startswith("__"):
        value = getattr(current_module, var_name)
        if isinstance(value, list) and id(value) not in seen_lists:
            all_tables.append(value)
            seen_lists.add(id(value))
seen_ids = {}
all_ids = []
for table in all_tables:
    for item in table:
        if isinstance(item, dict):
            item_id = item.get("id")
            if item_id is not None:
                if item_id in seen_ids:
                    raise Exception(
                        f"Conflicting item id detected: {item_id} "
                        f"('{seen_ids[item_id]['name']}' and '{item['name']}')"
                    )
                seen_ids[item_id] = item
                all_ids.append(item_id)
positive_ids = sorted([i for i in all_ids if i >= 0])
for idx in range(1, len(positive_ids)):
    if positive_ids[idx] != positive_ids[idx - 1] + 1:
        raise Exception(
            f"Non-consecutive item id detected: {positive_ids[idx-1]} -> {positive_ids[idx]}"
        )
    
if devmode == True:
    logging.info(f"Last item id: {positive_ids[-1]}")
    logging.info(f"Next item id: {positive_ids[-1]+1}")

# non looting tables can be added from this point forward, no more restrictions

data = [
    {"inventory": []},
    {"freeslots": 10},
    {"usedslots": 0},
    {"addedslots": 0},
    {"money": 0},
    {"charname": None},
    {"options": [
        {"difficulty": None},
        {"hardcore": False},
        {"statprog": False},
        {"gamemode": False}
    ]},
    {"stats": [
        {"name": "aim", "level": 0, "exp": 0, "mod": 0},
    ]},
    {"storage": {}},
    {"equipment": {
        "torso": None,
        "head": None,
        "back": None,
        "shoulder": None,
        "waist": None,
        "face": None,
        "undertorso": None,
        "shoes": None,
        "special": None,
        "wrist": None
    }},
    {"uuid": None}
]

empty_data = [
    {"inventory": []},
    {"freeslots": 10},
    {"usedslots": 0},
    {"addedslots": 0},
    {"money": 0},
    {"charname": None},
    {"options": [
        {"difficulty": None},
        {"hardcore": False},
        {"statprog": False},
        {"gamemode": False}
    ]},
    {"stats": [
        {"name": "aim", "level": 0, "exp": 0, "mod": 0},
    ]},
    {"storage": {}},
    {"equipment": {
        "torso": None,
        "head": None,
        "back": None,
        "shoulder": None,
        "waist": None,
        "face": None,
        "undertorso": None,
        "shoes": None,
        "special": None,
        "wrist": None
    }},
    {"uuid": None}
]

persistent_data = [
    {"previously_loaded": None},
    {"previous_inventory": None},
    {"previous_uuid": None},
    {"previous_money": None},
    {"previous_equipment": None},
    {"previous_storage": None},
    {"database": None}
]

persistent_save_path = os.path.join(saves_folder, "persistent_data.sldsv")
if os.path.exists(persistent_save_path):
    with open(persistent_save_path, "rb") as f:
        try:
            persistent_data = pickle.loads(base64.a85decode(f.read()))
            logging.info("Loaded persistent_data from persistent_data.sldsv")
        except Exception as e:
            logging.error(f"Failed to load persistent_data: {e}")

def save_current_data():
    global persistent_data, data
    charname = find_first_instance(data, "charname")
    logging.info(f"Saving currently loaded file: {charname}")
    persistent_data[0]["previously_loaded"] = charname
    save_path = os.path.join(saves_folder, f"{charname}.sldsv")
    if data[11].get("uuid") is None:
        new_uuid = str(uuid.uuid4())
        data[11]["uuid"] = new_uuid
        filename = f"{charname}.sldsv"
        entry = {"filename": filename, "uuid": new_uuid, "charname": charname}
        if persistent_data[6]["database"] is None:
            persistent_data[6]["database"] = []
        persistent_data[6]["database"].append(entry)
        logging.info(f"Generated new uuid for save: {new_uuid}")
    persistent_data[0]["previously_loaded"] = find_first_instance(data, "charname")
    persistent_data[1]["previous_inventory"] = find_first_instance(data, "inventory")
    persistent_data[2]["previous_uuid"] = find_first_instance(data, "uuid")
    persistent_data[3]["previous_money"] = find_first_instance(data, "money")
    persistent_data[4]["previous_equipment"] = find_first_instance(data, "equipment")
    persistent_data[5]["previous_storage"] = find_first_instance(data, "storage")
    with open(save_path, "wb") as f:
        encoded = base64.a85encode(pickle.dumps(data))
        f.write(encoded)
    persistent_save_path = os.path.join(saves_folder, "persistent_data.sldsv")
    with open(persistent_save_path, "wb") as f:
        encoded_persistent = base64.a85encode(pickle.dumps(persistent_data))
        f.write(encoded_persistent)

def load_data(savetoload):
    global persistent_data, data
    logging.info(f"Loading data from: {savetoload}")
    with open(savetoload, "rb") as f:
        try:
            data = pickle.loads(base64.a85decode(f.read()))
            logging.info("Loaded data from saved file")
        except Exception as e:
            logging.error(f"Failed to load data: {e}")

def loot():
    logging.info("Loot function started")

def craft():
    logging.info("Craft function started")

def stores():
    logging.info("Stores function started")

def create_character():
    logging.info("Create Character function started")
    if find_first_instance(data, "charname") is not None:
        save_current_data()
    data = empty_data.copy()
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("Character Creation Menu")
        print(f"Current name: {find_first_instance(data, 'charname')}")

def manage_character():
    logging.info("Manage Character function started")

def combat_mode():
    logging.info("Combat Mode function started")

def dev_opts():
    logging.info("Developer Options function started")

def main():
    module_files = [f for f in os.listdir("./modules") if f.endswith(".py")]
    module_displaynames = []
    module_map = {}
    for fname in module_files:
        mod_path = os.path.join("./modules", fname)
        mod_name = fname[:-3]
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(mod_name, mod_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            displayname = getattr(mod, "displayname", mod_name)
            module_displaynames.append(displayname)
            module_map[displayname] = mod
        except Exception as e:
            logging.error(f"Failed to load module {mod_name}: {e}")
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        logging.info("Main function started")
        print(f"Loot {version}")
        update_check()
        zip_files = [f for f in os.listdir(log_dir) if f.endswith(".zip")]
        if zip_files:
            print(f"You have {len(zip_files)} archived log files! Each zip contains 50 logs, consider deleting some logs!")
            logging.info(f"Archived log files detected: {', '.join(zip_files)}")
        opts = ["Loot", "Craft", "Stores", "Manage Character", "Enter Combat Mode"]
        if devmode:
            opts.append("Developer Options")
        opts += module_displaynames
        opts.append("Exit")
        print_menu(opts)
        choice = get_user_choice(len(opts))
        logging.info(f"User selected option: {opts[choice - 1]}")
        if choice == 1:
            loot()
        elif choice == 2:
            craft()
        elif choice == 3:
            stores()
        elif choice == 4:
            manage_character()
            create_character()
        elif choice == 5:
            combat_mode()
        elif choice == 6 and devmode:
            dev_opts()
        elif (6 if devmode else 5) <= choice < len(opts):
            selected_module_name = opts[choice - 1]
            mod = module_map.get(selected_module_name)
            if mod and hasattr(mod, "primary"):
                try:
                    mod.primary()
                except Exception as e:
                    logging.error(f"Error running primary() in module {selected_module_name}: {e}")
            else:
                print(f"Module '{selected_module_name}' does not have a 'primary' function.")
        elif choice == len(opts):
            logging.info("Exiting the program safely")
            exit()

main()