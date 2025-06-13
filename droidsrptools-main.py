version = "1.0.0"

import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

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

stats = [
    {"Name": "'Medical' A-Base", "HP": 30, "Damage": "1d4", "Movement Points": 7, "Processing Points": 10, "Bonus Instability": 0, "Possible Sentience": False, "Heat Per Day": 10, "Cooling Per Day": 10, "Active Movement Heat": 5, "Secondary Core Heat": 5, "Secondary Core Instability": -20, "id": 0},
    {"Name": "'Surgeon' A-1", "HP": 30, "Damage": "1d4", "Movement Points": 7, "Processing Points": 15, "Bonus Instability": 0, "Possible Sentience": False, "Heat Per Day": 15, "Cooling Per Day": 7, "Active Movement Heat": 5, "Secondary Core Heat": 5, "Secondary Core Instability": -20, "id": 1},
    {"Name": "'Medicine Controller' A-2", "HP": 15, "Damage": "1d4", "Movement Points": 7, "Processing Points": 15, "Bonus Instability": 0, "Possible Sentience": False, "Heat Per Day": 5, "Cooling Per Day": 2, "Active Movement Heat": 2, "Secondary Core Heat": 5, "Secondary Core Instability": -20, "id": 2},
    {"Name": "'Scanner' A-3", "HP": 0, "Damage": "1d4", "Movement Points": 0, "Processing Points": 0, "Bonus Instability": 0, "Possible Sentience": False, "Heat Per Day": 0, "Cooling Per Day": 0, "Active Movement Heat": 0, "Secondary Core Heat": 0, "Secondary Core Instability": -10, "id": 3},
    {"Name": "'Combat' B-Base", "HP": 60, "Damage": "1d10+1d4", "Movement Points": 5, "Processing Points": 10, "Bonus Instability": 20, "Possible Sentience": True, "Heat Per Day": 20, "Cooling Per Day": 15, "Active Movement Heat": 5, "Secondary Core Heat": 10, "Secondary Core Instability": -20, "id": 4},
    {"Name": "'Thrasher' B-1", "HP": 30, "Damage": "1d10+1d6", "Movement Points": 7, "Processing Points": 15, "Bonus Instability": 0, "Possible Sentience": False, "Heat Per Day": 15, "Cooling Per Day": 7, "Active Movement Heat": 5, "Secondary Core Heat": 5, "Secondary Core Instability": -20, "id": 5},
    {"Name": "'DreadNaught' B-2", "HP": 70, "Damage": "1d20", "Movement Points": 4, "Processing Points": 25, "Bonus Instability": 25, "Possible Sentience": False, "Heat Per Day": 20, "Cooling Per Day": 10, "Active Movement Heat": 10, "Secondary Core Heat": 10, "Secondary Core Instability": -20, "Armament Heat Per Turn": 25, "Heat Transfer": -25, "id": 6},
    {"Name": "'Recon' B-3", "HP": 15, "Damage": "1d10+1d6", "Movement Points": 7, "Processing Points": 15, "Bonus Instability": 0, "Possible Sentience": False, "Heat Per Day": 5, "Cooling Per Day": 2, "Active Movement Heat": 2, "Secondary Core Heat": 5, "Secondary Core Instability": -20, "Active Camouflage Heat Per Turn": 4, "id": 7},
    {"Name": "'Industrial' C-Base", "HP": 60, "Damage": "1d10+1d4", "Movement Points": 5, "Processing Points": 10, "Bonus Instability": 20, "Possible Sentience": True, "Heat Per Day": 20, "Cooling Per Day": 15, "Active Movement Heat": 5, "Secondary Core Heat": 10, "Secondary Core Instability": -20, "id": 8},
    {"Name": "'Centaur' C-1", "HP": 30, "Damage": "1d10", "Movement Points": 15, "Processing Points": 10, "Bonus Instability": 0, "Possible Sentience": True, "Heat Per Day": 10, "Cooling Per Day": 10, "Active Movement Heat": 7, "Secondary Core Heat": 10, "Secondary Core Instability": -20, "Heat Transfer": -25, "id": 9},
    {"Name": "'Maker' C-2", "HP": 30, "Damage": "1d10", "Movement Points": 7, "Processing Points": 15, "Bonus Instability": 0, "Possible Sentience": True, "Heat Per Day": 10, "Cooling Per Day": 15, "Active Movement Heat": 5, "Secondary Core Heat": 10, "Secondary Core Instability": -30, "id": 10},
    {"Name": "'MTR' C-3", "HP": 80, "Damage": "1d4", "Movement Points": 5, "Processing Points": 20, "Bonus Instability": 40, "Possible Sentience": False, "Heat Per Day": 5, "Cooling Per Day": 25, "Active Movement Heat": 5, "Secondary Core Heat": 10, "Secondary Core Instability": -20, "Heat Transfer": -25, "id": 11},
    {"Name": "'Civilian' D-Base", "HP": 25, "Damage": "1d4", "Movement Points": 16, "Processing Points": 20, "Bonus Instability": 0, "Possible Sentience": True, "Heat Per Day": 5, "Cooling Per Day": 10, "Active Movement Heat": 0, "Secondary Core Heat": 5, "Secondary Core Instability": -30, "id": 12},
    {"Name": "'Mimic' D-1", "HP": 40, "Damage": "1d10", "Movement Points": 10, "Processing Points": 10, "Bonus Instability": 20, "Possible Sentience": True, "Heat Per Day": 5, "Cooling Per Day": 5, "Active Movement Heat": 5, "Secondary Core Heat": 5, "Secondary Core Instability": -20, "id": 13},
    {"Name": "'Decor' D-2", "HP": 10, "Damage": "1d4", "Movement Points": 5, "Processing Points": 25, "Bonus Instability": 0, "Possible Sentience": True, "Heat Per Day": 20, "Cooling Per Day": 15, "Active Movement Heat": 0, "Secondary Core Heat": 5, "Secondary Core Instability": -40, "id": 14},
    {"Name": "'Servant' D-3", "HP": 50, "Damage": "1d10+1d6", "Movement Points": 5, "Processing Points": 15, "Bonus Instability": 40, "Possible Sentience": True, "Heat Per Day": 5, "Cooling Per Day": 10, "Active Movement Heat": 5, "Secondary Core Heat": 5, "Secondary Core Instability": -40, "id": 15},
    {"Name": "'Parasite' E-Base", "HP": 10, "AHP": 50, "Damage": "1d10+1d4", "Movement Points": 7, "Processing Points": 15, "Bonus Instability": 0, "Possible Sentience": True, "Heat Per Day": 5, "Cooling Per Day": 15, "id": 16},
    {"Name": "'Parasyte' E-1", "HP": 15, "AHP": 50, "Damage": "1d10+1d4", "Movement Points": 7, "Processing Points": 20, "Bonus Instability": 10, "Possible Sentience": True, "Heat Per Day": 7, "Cooling Per Day": 15, "id": 17},
    {"Name": "'Frankenstein' E-2", "HP": 25, "AHP": 50, "Damage": "1d20", "Movement Points": 7, "Processing Points": 25, "Bonus Instability": 30, "Possible Sentience": True, "Heat Per Day": 15, "Cooling Per Day": 15, "id": 18},
    {"Name": "'CyberPsychosis' E-3", "HP": 50, "AHP": 50, "Damage": "1d20+1d4", "Movement Points": 7, "Processing Points": 30, "Bonus Instability": 40, "Possible Sentience": True, "Heat Per Day": 5, "Cooling Per Day": 25, "id": 19},
]
