import os
import random
import json
import base64
import requests
from packaging import version as ver
import time
import uuid
import zipfile
import shutil
import glob

version = "3.0.4"

developmentcopy = False

freeslots = 10
current_inventory = []
current_inventory_name = None
storage = []
tradershop = []
questitems = []
gold = 0
saves_folder = "./saves"
equipped_items = {
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
}

incompatible_saves = [
    "3.0.0developmentcopy",
    "3.0.0developmentcopy2",
    "3.0.0",
]

os.makedirs(saves_folder, exist_ok=True)

def save_inventory_to_file(inventory, file_name):
    file_path = os.path.join(saves_folder, file_name)
    try:
        data_to_save = {
            "version": version,
            "inventory": inventory,
            "freeslots": freeslots,
            "storage": storage,
            "gold": gold,
            "equipped_items": equipped_items
        }
        encoded_data = base64.b64encode(json.dumps(data_to_save).encode("utf-8")).decode("utf-8")
        with open(file_path, "w") as file:
            file.write(encoded_data)
        print(f"Inventory saved to {file_path}")
    except Exception as e:
        print(f"Error saving inventory: {e}")

def load_inventory_from_file(file_name):
    global freeslots, storage, gold, equipped_items
    file_path = os.path.join(saves_folder, file_name)
    try:
        with open(file_path, "r") as file:
            encoded_data = file.read()
            data_loaded = json.loads(base64.b64decode(encoded_data).decode("utf-8"))
            freeslots = data_loaded.get("freeslots", 10)
            storage = data_loaded.get("storage", [])
            gold = data_loaded.get("gold", 0)
            equipped_items = data_loaded.get("equipped_items", {})
            return data_loaded.get("inventory", [])
    except FileNotFoundError:
        print(f"Error: File {file_path} does not exist.")
    except Exception as e:
        print(f"Error loading inventory: {e}")
    return None

previous_inventory_file = os.path.join(saves_folder, "previousinventory.save")
if os.path.exists(previous_inventory_file):
    try:
        with open(previous_inventory_file, "r") as file:
            encoded_data = file.read()
            save_name = base64.b64decode(encoded_data).decode("utf-8").strip()
            if save_name:
                save_path = os.path.join(saves_folder, save_name)
                if os.path.exists(save_path):
                    current_inventory_name = save_name
                    current_inventory = load_inventory_from_file(current_inventory_name) or []
                    print(f"Loaded previous inventory: {current_inventory_name}")
                else:
                    print(f"Save file '{save_name}' not found in the saves folder.")
    except Exception as e:
        print(f"Error reading previous inventory file: {e}")

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

test_table = [
    {"name": "Methamphetamine", "value": 10, "description": "Walter's blue stuff for realsies", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": -5},
    {"name": "Walter Hartwell White", "value": 10, "description": "Waltuh", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": -4},
    {"name": "Hank Schrader", "value": 10, "description": "FACKIN ANDROIDS", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": -3},
    {"name": "SKYLAR WHITE YO", "value": 10, "description": "my name is skylar white yo", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": -2},
    {"name": "JESSE PINKDUDE", "value": 10, "description": "what's up bitch", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": -1},
]

melee_weapons = [
    {"name": "Dagger", "value": 30, "description": "A british staple of gang related disputes.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 0},
    {"name": "Bowie Knife", "value": 40, "description": "Thats not a knife…", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 1},
    {"name": "Military Grade Combat Knife", "value": 50, "description": "Nice, your fruit killin’ skills are remarkable.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 2},
    {"name": "Short Sword", "value": 60, "description": "A finely crafted and well edged sword from an unknown blacksmith.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 3},
    {"name": "Machete", "value": 60, "description": "A single edged blade used for forest environments or survival situations… but mostly used for killing teenagers at lakes", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 4},
    {"name": "Katana", "value": 80, "description": "To master your blade… you must first control your emotions.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 5},
    {"name": "Longsword", "value": 95, "description": "A longer blade for more reach, though it requires two hands to effectively use.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 3, "id": 6},
    {"name": "Claymore", "value": 130, "description": "A Highland Claymore of Northern Thedoria origin, its long blade and interesting design gives you a sense of gaelic pride.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 3, "id": 7},
    {"name": "Greatsword", "value": 150, "description": "A very big sword that crushes anything in its path… including your own arm muscles.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 3, "id": 8},
    {"name": "Spear", "value": 60, "description": "A very pointy stick that makes your primal urges for violence surge.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 9},
    {"name": "Glaive", "value": 90, "description": "in case single edged weapons that make you bleed wasn’t annoying enough, now you have it on a stick!", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 3, "id": 10},
    {"name": "Wood Axe", "value": 60, "description": "A wood handled axe made for handling wood", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 11},
    {"name": "Fire Axe", "value": 80, "description": "An axe designed to break doors and clear house fires, a life saving tool that you are now using to decapitate people.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 12},
]

ranged_weapons = [
    {"name": "Wooden Bow", "value": 10, "description": "A very simple wooden bow, something that you could easily make… but you’re lazy aren’t you?", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 13},
    {"name": "Compound Bow", "value": 80, "description": "A more modern take on the simple bow, quiet and hits like a truck.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 14},
    {"name": "Wooden Crossbow", "value": 50, "description": "Used by an ancient race of marauders with comically large noses and gray skin, it now belongs to you.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 15},
    {"name": "Compound Crossbow", "value": 80, "description": "Crossbows for pretentious rich kids", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 16},
    {"name": "Pistol of your choosing", "value": 80, "description": "guns for poor people.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 17},
    {"name": "Revolver of your choosing", "value": 80, "description": "you feel the urge to smoke 5 cigarettes and down snake oil while using it", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 18},
    {"name": "SMG of your choosing", "value": 80, "description": "Attack of the killer bees!", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 19},
    {"name": "5.56 Rifle of your choosing", "value": 120, "description": "Freedom at its finest.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 20},
    {"name": "7.62 Rifle of your choosing", "value": 130, "description": "You’re either a communist or really hate keeping things alive… or both.", "rarity": "Legendary", "minrand": 1, "maxrand": 2, "inventoryslots": 1, "id": 21},
    {"name": "308.Sniper Rifle of your choosing", "value": 150, "description": "Sniping's a good job, mate", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 22},
    {"name": "338.Lupua Sniper Rifle of your choosing", "value": 300, "description": "Säkkijärven polkka.", "rarity": "Mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 3, "id": 23},
    {"name": "Empty 50 Caliber. Sniper Rifle of your choosing", "value": 500, "description": "Jokes on you it's empty!", "rarity": "Mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 4, "id": 24},
]


ammo = [
    {"name": ".22 Long Rifle", "value": 1, "description": "A small caliber round, great for plinking and small game.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0, "id": 25},
    {"name": "9x19mm Parabellum", "value": 2, "description": "A widely used pistol round, reliable and effective.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0, "id": 26},
    {"name": ".45 ACP", "value": 3, "description": "A classic American round, known for its stopping power, and the natural subsonic nature.", "rarity": "uncommon", "minrand": 10, "maxrand": 40, "inventoryslots": 0, "id": 27},
    {"name": ".38 Special", "value": 2, "description": "A revolver round, popular for self-defense.", "rarity": "common", "minrand": 10, "maxrand": 40, "inventoryslots": 0, "id": 28},
    {"name": ".357 Magnum", "value": 4, "description": "A powerful revolver round with excellent penetration.", "rarity": "uncommon", "minrand": 10, "maxrand": 30, "inventoryslots": 0, "id": 29},
    {"name": ".44 Magnum", "value": 5, "description": "A very powerful handgun round, for when you need serious firepower.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0, "id": 30},
    {"name": "10mm Auto", "value": 4, "description": "A versatile round, great for both self-defense and hunting.", "rarity": "uncommon", "minrand": 10, "maxrand": 30, "inventoryslots": 0, "id": 31},
    {"name": ".223 Remington", "value": 3, "description": "A popular rifle round, great for varmint hunting.", "rarity": "common", "minrand": 10, "maxrand": 40, "inventoryslots": 0, "id": 32},
    {"name": ".308 Winchester", "value": 6, "description": "A powerful rifle round, excellent for hunting and long-range shooting.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0, "id": 33},
    {"name": "5.45x39mm Soviet", "value": 3, "description": "A standard round for Soviet-era rifles, lightweight and effective.", "rarity": "common", "minrand": 10, "maxrand": 40, "inventoryslots": 0, "id": 34},
    {"name": "5.56x45mm NATO", "value": 4, "description": "A standard NATO round, widely used in modern rifles.", "rarity": "uncommon", "minrand": 10, "maxrand": 30, "inventoryslots": 0, "id": 35},
    {"name": "7.62x51mm NATO", "value": 6, "description": "A powerful NATO round, used in battle rifles and machine guns.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0, "id": 36},
    {"name": ".300 AAC Blackout", "value": 5, "description": "A versatile round, great for suppressed rifles.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0, "id": 37},
    {"name": ".30-06 Springfield", "value": 6, "description": "A classic American hunting round, known for its power.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0, "id": 38},
    {"name": "7.62x39mm Soviet", "value": 4, "description": "A standard round for AK-pattern rifles, reliable and effective.", "rarity": "uncommon", "minrand": 10, "maxrand": 30, "inventoryslots": 0, "id": 39},
    {"name": ".45-70 Government", "value": 7, "description": "A heavy round, great for big game hunting... or hunting humans.", "rarity": "rare", "minrand": 5, "maxrand": 15, "inventoryslots": 0, "id": 40},
    {"name": "12 Gauge", "value": 2, "description": "A versatile shotgun shell, great for hunting and self-defense.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0, "id": 41},
    {"name": "20 Gauge", "value": 2, "description": "A light shotgun shell, great for smaller game.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0, "id": 42},
    {"name": "10 Gauge", "value": 3, "description": "A heavy shotgun shell, great for large game and defense.", "rarity": "uncommon", "minrand": 5, "maxrand": 30, "inventoryslots": 0, "id": 43},
    {"name": ".410 Bore", "value": 1, "description": "A small shotgun shell, great for beginners and small game.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0, "id": 44},
    {"name": "8 Gauge", "value": 4, "description": "A very large shotgun shell, used for real big game.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0, "id": 45},
    {"name": "4 Gauge", "value": 5, "description": "An extremely large shotgun shell, rarely used today.", "rarity": "rare", "minrand": 5, "maxrand": 15, "inventoryslots": 0, "id": 46},
    {"name": ".338 Lapua Magnum", "value": 8, "description": "A high-powered sniper round, excellent for long-range precision.", "rarity": "mythic", "minrand": 1, "maxrand": 10, "inventoryslots": 0, "id": 47},
    {"name": ".500 S&W Magnum", "value": 7, "description": "A massive revolver round, known for its incredible power.", "rarity": "rare", "minrand": 5, "maxrand": 15, "inventoryslots": 0, "id": 48},
    {"name": ".500 Nitro Express", "value": 9, "description": "A heavy round, used for hunting dangerous game.", "rarity": "mythic", "minrand": 1, "maxrand": 10, "inventoryslots": 0, "id": 49},
    {"name": ".50 Beowulf", "value": 8, "description": "A powerful round, designed for AR-pattern rifles.", "rarity": "legendary", "minrand": 1, "maxrand": 10, "inventoryslots": 0, "id": 50},
    {"name": ".50 BMG", "value": 10, "description": "A massive round, used in anti-materiel rifles.", "rarity": "mythic", "minrand": 1, "maxrand": 5, "inventoryslots": 0, "id": 51},
    {"name": "Railgun Rail", "value": 15, "description": "A futuristic projectile, used in experimental railguns.", "rarity": "mythic", "minrand": 1, "maxrand": 3, "inventoryslots": 0, "id": 52},
    {"name": "Pepperball", "value": 1, "description": "A non-lethal round, used for crowd control.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0, "id": 53},
]

armor_and_defense = [
    {"name": "Plate carrier", "value": 95, "description": "An adjustable vest with sleeves for armor plates. The material of the vest appears to be kevlar.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 54, "slot": "torso"},
    {"name": "NIJ Level IIIa soft plate", "value": 50, "description": "A lightweight soft plate offering protection against most handgun rounds.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 55, "slot": "armorplate", "armorrating": "IIIa"},
    {"name": "NIJ Level III ceramic plate", "value": 120, "description": "A ceramic plate capable of stopping rifle rounds.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 56, "slot": "armorplate", "armorrating": "III"},
    {"name": "NIJ Level III steel plate", "value": 100, "description": "A durable steel plate offering protection against rifle rounds.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 57, "slot": "armorplate", "armorrating": "III"},
    {"name": "NIJ Level IV ceramic plate", "value": 200, "description": "A high-grade ceramic plate capable of stopping armor-piercing rounds.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 58, "slot": "armorplate", "armorrating": "IV"},
    {"name": "NIJ Level IV steel plate", "value": 180, "description": "A steel plate offering protection against armor-piercing rounds.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 59, "slot": "armorplate", "armorrating": "IV"},
    {"name": "NIJ Level IV+ ceramic plate", "value": 250, "description": "An advanced ceramic plate with enhanced durability and protection.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 60, "slot": "armorplate", "armorrating": "IV+"},
    {"name": "NIJ Level IV+ steel plate", "value": 230, "description": "An advanced steel plate with enhanced durability and protection.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 61, "slot": "armorplate", "armorrating": "IV+"},
    {"name": "Great helmet", "value": 150, "description": "A large, fully enclosed helmet offering excellent protection.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 62, "slot": "head", "armorrating": "II"},
    {"name": "Bascinet", "value": 120, "description": "A medieval helmet with a pointed top, offering good protection.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 63, "slot": "head", "armorrating": "II"},
    {"name": "Sallet", "value": 130, "description": "A rounded helmet with a visor, popular in the late medieval period.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 64, "slot": "head", "armorrating": "II"},
    {"name": "Barbute", "value": 140, "description": "An open-faced helmet inspired by ancient Greek designs.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 65, "slot": "head", "armorrating": "II"},
    {"name": "Sugarloaf helmet", "value": 160, "description": "A conical helmet offering excellent deflection against strikes.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 66, "slot": "head", "armorrating": "II"},
    {"name": "Nasal helmet", "value": 90, "description": "A simple helmet with a nose guard, popular in the early medieval period.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 67, "slot": "head", "armorrating": "II"},
    {"name": "Full plate chestplate", "value": 300, "description": "A full chestplate offering maximum protection.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 3, "id": 68, "slot": "torso", "armorrating": "II"},
    {"name": "Half plate chestplate", "value": 200, "description": "A partial chestplate offering good protection with more mobility.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 69, "slot": "torso", "armorrating": "II"},
    {"name": "Leather armor", "value": 50, "description": "A lightweight leather armor offering basic protection.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 70, "slot": "undertorso", "armorrating": "I"},
    {"name": "Chainmail armor", "value": 150, "description": "A chainmail shirt offering good protection against slashes.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 71, "slot": "torso", "armorrating": "I"},
    {"name": "Gambeson chestplate", "value": 80, "description": "A padded armor offering decent protection and comfort.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 72, "slot": "torso", "armorrating": "II"},
    {"name": "Brigandine chestplate", "value": 180, "description": "A reinforced chestplate with metal plates sewn into fabric.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 73, "slot": "torso", "armorrating": "II"},
    {"name": "Small backpack", "value": 5, "description": "A small bag for carrying items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 74, "slot": "back", "addedslots": 5},
    {"name": "Day pack", "value": 10, "description": "A small backpack for carrying items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 75, "slot": "back", "addedslots": 10},
    {"name": "Bookbag", "value": 12, "description": "A medium-sized backpack for carrying items.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": -12, "id": 76, "slot": "back", "addedslots": 12},
    {"name": "Rucksack", "value": 15, "description": "A large backpack for carrying items.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 77, "slot": "back", "addedslots": 15},
    {"name": "Hiking bag", "value": 20, "description": "A durable backpack for carrying items.", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 78, "slot": "back", "addedslots": 20},
    {"name": "Duffel bag", "value": 25, "description": "A duffel bag for carrying a moderate amount of items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 79, "slot": "back", "addedslots": 10},
    {"name": "Tactical backpack", "value": 30, "description": "A tactical backpack for carrying a large amount of items. Has an insert for a plate in the back.", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 80, "slot": "back", "addedslots": 15},
    {"name": "Purse", "value": 5, "description": "A small bag for carrying personal items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 81, "slot": "shoulder", "addedslots": 2},
    {"name": "Vest pouch", "value": 10, "description": "A small pouch for carrying items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 82, "slot": "platecarrier", "addedslots": 3},
    {"name": "Fanny pack", "value": 8, "description": "A small bag for carrying items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 83, "slot": "waist", "addedslots": 3},
    {"name": "Shoulder bag", "value": 12, "description": "A small bag for carrying items.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 84, "slot": "shoulder", "addedslots": 5},
    {"name": "Messenger bag", "value": 15, "description": "A small bag for carrying items.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 85, "slot": "shoulder", "addedslots": 10},
]

healing_and_magic = [
    {"name": "Bandage", "value": 5, "description": "A simple bandage to stop bleeding.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0, "id": 86},
    {"name": "First Aid Kit", "value": 20, "description": "A comprehensive kit for treating injuries.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 87},
    {"name": "Antidote", "value": 10, "description": "A potion that cures poison.", "rarity": "uncommon", "minrand": 1, "maxrand": 3, "inventoryslots": 0, "id": 88},
    {"name": "Panacea", "value": 25, "description": "A potion that cures all ailments.", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 89},
    {"name": "Mana Potion", "value": 20, "description": "A potion that restores magical energy.", "rarity": "rare", "minrand": 1, "maxrand": 3, "inventoryslots": 0, "id": 90},
    {"name": "Apple", "value": 2, "description": "A simple fruit that restores a small amount of health.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0, "id": 91},
    {"name": "Bread", "value": 3, "description": "A loaf of bread that restores a small amount of health.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0, "id": 92},
    {"name": "Cheese Wheel", "value": 15, "description": "A wheel of cheese that restores a medium amount of health.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 93},
    {"name": "Steak", "value": 10, "description": "A cooked steak that restores a medium amount of health.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 94},
    {"name": "Hardtack", "value": 1, "description": "A hard biscuit that restores a small amount of health.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0, "id": 95},
    {"name": "Honey", "value": 5, "description": "A jar of honey that restores a small amount of health.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 96},
    {"name": "Sandwich", "value": 8, "description": "A sandwich that restores a medium amount of health.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 97},
    {"name": "Chips", "value": 2, "description": "A bag of chips that restores a small amount of health.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0, "id": 98},
    {"name": "Energy Drink", "value": 5, "description": "A can of Red Bull that restores a small amount of health. (does not give you wings)", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0, "id": 99},
    {"name": "Health Cure", "value": 30, "description": "A potion that restores a large amount of health.", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 100},
    {"name": "Moonshine", "value": 10, "description": "A strong alcoholic beverage that restores a large amount of health.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 101},
    {"name": "Bitters", "value": 15, "description": "A strong alcoholic beverage that restores a medium amount of health.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 102},
    {"name": "Snake Oil", "value": 20, "description": "A magical potion that restores a large amount of health.", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 103},
    {"name": "Miracle Tonic", "value": 25, "description": "A magical potion that restores a large amount of health and cures all ailments.", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 104},
    {"name": "Small ornate locket", "value": 5, "description": "A small spherical ornate silver locket on a chain that when opened provides a soft blue glow and provides a constant healing effect. Prolonged exposure may result in death. (SCP-427)", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 105},
    {"name": "Red unmarked pill", "value": 25, "description": "A small red pill that when consumed heals all ailments and injuries. (SCP-500)", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 106},
    {"name": "Phoenix Feather", "value": 50, "description": "A magical feather that can revive the dead.", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 107},
    {"name": "Compound Red", "value": 150, "description": "A rather... unclean needle with a red liquid inside. Used to stave off eldritchification.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 166},
    {"name": "Compound Blue", "value": 250, "description": "A needle enclosed in a sterile bag with a handwritten label denoting that it is compound blue. The handwriting is overtly girly and signed Erin Baker.", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 167}
]

cursed_and_blessed_items = [
    {"name": "Charlotte’s MP3 Player", "value": 1000, "description": "An MP3 player filled with various songs under the artist ‘And One’... can I have it back please?", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 108},
    {"name": "Mysterious Dagger", "value": 3000, "description": "Allows you to summon Undertaker for a short period of time when used to sacrifice something.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 109},
    {"name": "Model M500 Flash Goggles", "value": 200, "description": "Some sturdy looking goggles that appear flashbang proof… why is it covered in dog hair?", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 110, "slot": "face"},
    {"name": "M4’s Boots", "value":500, "description": "Made out of an almost ethereal leather, its completely indestructible.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 111, "slot": "shoes"},
    {"name": "Comedy Wrench", "value": 200, "description": "A basic utility wrench used by past survivors for comedic effect, its unbelievable luck is now in your hands. (+2 to whatever you’re using it for)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 112},
    {"name": "Strange Sweater", "value": 200, "description": "A sweater made out of a strange yarn. Prevents bleeding. (+2 resistance)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 113, "slot": "undertorso"},
    {"name": "Strange Shovel", "value": 200, "description": "It's heavy, but it has a good reach! (+1 to attack & parry rolls when using shovel)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 114},
    {"name": "Red Headset", "value": 200, "description": "Not again! You should know better!", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 115},
    {"name": "Panzerfaust", "value": 500, "description": "The box had some severed fingers inside too, strange…", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 116},
    {"name": "Unusual Pink Potion", "value": 350, "description": "I wouldn’t recommend drinking it.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 117},
    {"name": "Brazilian made plate carrier", "value": 500, "description": "Its high great materials makes you feel invincible, or at least until someone cuts you in half with swords. (+1 to all stats)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 118, "slot": "torso"},
    {"name": "MEB Biofoam", "value": 200, "description": "Who the hell put this here?! (instantly heals all damage, no matter its severity)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 119},
    {"name": "Clown Mask", "value": 200, "description": "AAAAAAAAUGH I NEED A MEDIC BAG! (Gives a 50% price cut to any items bought from traders)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 120, "slot": "face"},
    {"name": "Drill", "value": 200, "description": "This drill is fucking worthless! (unlocks any locked item no matter the difficulty)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 3, "id": 121},
    {"name": "Persica Water", "value": 1, "description": "I found it in a vending machine at the police station. (Instantly heals all damage… but tastes awful)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 122},
    {"name": "M16A1", "value": 300, "description": "Comes with a complimentary eyepatch! (+1 aim & agility when using item)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 123},
    {"name": "Cardboard Box", "value": 5, "description": "Huh… just a box. (makes you unable to be spotted, however you cannot do any actions)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 124},
    {"name": "Locked Case", "value": 1000, "description": "A locked gun case with green ribbons wrapped around its exterior. There is a 4 number combination lock with a griffin carved into the metal holding it shut.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 3, "id": 125},
    {"name": "Lost Code", "value": 10, "description": "A lost 4 combination code with a griffin engraved on the back of the card", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 126},
    {"name": "Explosion Staff", "value": 10, "description": "A wooden staff wrapped in cloth around the handle with a red orb floating inside. (Allows the usage of the ‘Explosion’ spell)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 127},
    {"name": "Chunchunmaru", "value": 10, "description": "A short katana once wielded by a long lost hero. (+1 to all combat stats when using this item)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 128},
    {"name": "Stratagem", "value": 10, "description": "Unleashing Democracy! (calls in a free A-10 500kg strike on site that the item is thrown)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 129},
    {"name": "Space Stimulant", "value": 10, "description": "A little shot of liberty. (instantly heals all damage & grants +2 to all stats for the next turn)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 130},
    {"name": "Weldless Metal Quickrepair", "value": 250, "description": "A small box with a handwritten label slapped on. The label reads ‘Weldless Metal Quickrepair. Simply apply the provided paste and pour the powder on and watch as the metal is instantly bonded, stronger than steel!’ The handwriting is overtly girly and signed Erin Baker on the bottom.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 131},
    {"name": "Gatorade Zero", "value": 10, "description": "Is it in you?", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 132},
    {"name": "Percy’s Hat", "value": 100, "description": "the letters ‘HK’ are carved on the interior. (turns you into a complete asshole. -5 charisma with a +2 combat roll bonus)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 133, "slot": "head"},
    {"name": "HK’s Beret", "value": 100, "description": "Commander, I am all you need. (+5 charisma when worn)", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 134, "slot": "head"},
    {"name": "Everclear", "value": 50, "description": "I just need to try a little harder. (immune to all damage for 1 turn)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 135},
    {"name": "ALVMS MKII", "value": 1000, "description": "’Dispose of immediately’ is written on the side in red marker", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 136},
    {"name": "James’ Beanie", "value": 25, "description": "A pretty cool beanie. (+5 charisma when worn, gives you the urge to rizz up Edytha)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 137, "slot": "head"},
    {"name": "Carhartt Jacket", "value": 75, "description": "A rugged and durable jacket, seems like it's covered in black cat hairs. (+3 strength, +2 charisma when worn)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 138, "slot": "undertorso"},
    {"name": "Dreamcatcher", "value": 50, "description": "A fairly high quality Native American style dreamcatcher. (When hung up at a home base, all enemies are warded away no matter what)", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 139},
    {"name": "Mossberg 500", "value": 1000, "description": "A fairly high quality American made shotgun. The shotgun looks like it’s covered in like… blonde dog hair. (+2 aim when used, you feel patriotism coursing through your veins when you use it)", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 140},
    {"name": "Void Pocket", "value": 2147483647, "description": "A mysterious infinite black pit you can put stuff in.", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 141, "slot": "special", "addedslots": 2147483647},
    {"name": "Glowing Red Vial", "value": 75, "description": "All the labels are written in german, too bad im not reading it for you. (turns you into a Lesser Hexen when consumed)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 142},
    {"name": "The Maid Outfit", "value": 500, "description": "Go ahead. Put it on. (curse of binding)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 143, "slot": "special", "curseofbinding": True},
    {"name": "Helmet Chan’s Helmet", "value": 150, "description": "A green WW2 era tanker helmet with a large chunk of shrapnel buried inside. I think someone wants it back. (+2 Resistance, +1 Aim when worn)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 144, "slot": "head"},
    {"name": "Beaten M1911", "value": 300, "description": "Can take out a tiger! (+2 aim bonus)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 145},
    {"name": "Strange MP3 Player", "value": 300, "description": "looks like a normal MP3 player… dunno what else to tell you.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 146},
    {"name": "The Famas", "value": 500, "description": "EUGH UGH- GAH- FRENCH!", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2, "id": 147},
    {"name": "Roon’s Cross", "value": 1000, "description": "when you inch your hand closer, you hear ‘The March of Domination’ playing faintly in the background (turns you into a nazi temporarily and gives you the urge to min max in HOI4)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 148, "slot": "special"},
    {"name": "American Flag", "value": 1000, "description": "WHAT THE FUCK IS A KILOMETER! (turns you into a hardcore american patriot temporarily)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 149, "slot": "special"},
    {"name": "USSR Ushanka", "value":1000, "description": "A ring of steel surrounds your rotten city! We will crush all who dare to resist the will of the Red army! Abandon your posts! Abandon your homes! Abandon all hope! URA! (Turns you into a communist temporarily)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 150, "slot": "head"},
    {"name": "GDR Cap", "value": 1000, "description": "EINS-ZWEI-DREI DIE BESTE PARTEI UND VIER FÜNF SECHS- (turns you into a Socialist and allows you to translate german temporarily)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 151, "slot": "head"},
    {"name": "Cat Ears Headband", "value": 1000, "description": "Hey pal, it's the wrong story. (curse of binding)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 152, "slot": "head", "curseofbinding": True},
    {"name": "Persica’s Cat Headband", "value": 1000, "description": "”Hey there ho there.” (+2 intelligence & perception when worn)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 153, "slot": "head"},
    {"name": "Ornate Knife", "value": 25, "description": "A very ornate silver knife with lots of complicated etchings in the blade. (when picked up, you feel the urge to cut yourself on your wrists)", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 154},
    {"name": "ANNA Watch", "value": 5000, "description": "A watch from an unknown company, strangely enough there is an anglerfish carved into the underside of the watch’s frame… (grants the user the ANNA Personal Assistant)", "rarity": "Mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 155, "slot": "wrist"},
    {"name": "Yukari’s Bag", "value": 5000, "description": "A lost bag belonging to a brilliant mechanical engineer from Oarai. (allows the usage of 2 special tech items when combined with the ‘ANNA Watch’.", "rarity": "Mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 156, "slot": "wrist", "addedslots": 15},
]

junk = [
    {"name": "Wood board", "value": 5, "description": "A cut board made from pine.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 2, "id": 169},
    {"name": "Steel tube", "value": 15, "description": "A rusted out chunk of steel tubing.", "rarity": "common", "minrand": 1, "maxrand": 3, "inventoryslots": 2, "id": 170},
    {"name": "PVC pipe", "value": 2, "description": "A length of plastic tubing.", "rarity": "common", "minrand": 1, "maxrand": 3, "inventoryslots": 1, "id": 171},
    {"name": "Sheet metal", "value": 25, "description": "A rusty piece of sheet metal, probably steel.", "rarity": "uncommon", "minrand": 1, "maxrand": 2, "inventoryslots": 5, "id": 172},
    {"name": "Welding wire", "value": 50, "description": "A spindle of MIG welding wire.", "rarity": "rare", "minrand": 1, "maxrand": 2, "inventoryslots": 1, "id": 173},
    {"name": "Welding wire", "value": 165, "description": "A length of TIG welding wire.", "rarity": "rare", "minrand": 1, "maxrand": 2, "inventoryslots": 1, "id": 174},
    {"name": "Sling", "value": 15, "description": "A simple sling for weapons.", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 175, "slot": "shoulder", "addedslots": 2},
    {"name": "Welding wire", "value": 50, "description": "A spindle of welding wire.", "rarity": "rare", "minrand": 1, "maxrand": 2, "inventoryslots": 1, "id": 176},
    {"name": "Empty can", "value": 1, "description": "An empty can, appears to be made of tin, was probably food at some point.", "rarity": "common", "minrand": 1, "maxrand": 7, "inventoryslots": 1, "id": 177},
    {"name": "Empty can", "value": 2, "description": "An empty can, appears to be made of aluminum, probably was a drink of sorts.", "rarity": "common", "minrand": 1, "maxrand": 12, "inventoryslots": 1, "id": 178},
    {"name": "Empty plastic bag", "value": 0, "description": "A plastic bag that's weak and falling apart, no good for carrying items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0, "id": 179},
    {"name": "Candy bar", "value": 5, "description": "It's your favorite candy bar! Aw shucks, it's expired though. Probably tastes like the souls of the damned.", "rarity": "uncommon", "minrand": 1, "maxrand": 3, "inventoryslots": 1, "id": 180},
    {"name": "Soda", "value": 7, "description": "It's your favorite soda! Aw shucks, it's expired though. Probably tastes like the blood of the damned. Flat too, flatter than your mom!", "rarity": "uncommon", "minrand": 1, "maxrand": 3, "inventoryslots": 1, "id": 181},
    {"name": "Motor oil", "value": 15, "description": "A quart bottle of motor oil. It smells horrible and has metal chunks all up in it, it's probably used...", "rarity": "common", "minrand": 1, "maxrand": 3, "inventoryslots": 1, "id": 182},
    {"name": "Glass bottle", "value": 2, "description": "An empty glass bottle that still has the stench of beer. You should smash it against a legion footsoldier's skull! Or your friends, I don't really care.", "rarity": "common", "minrand": 1, "maxrand": 24, "inventoryslots": 2, "id": 183},
    {"name": "Screwdriver", "value": 15, "description": "A simple handheld screwdriver. Good for screwing and/or stabbing!", "rarity": "uncommon", "minrand": 1, "maxrand": 5, "inventoryslots": 1, "id": 184},
    {"name": "Pry bar", "value": 15, "description": "A crowbar but it has a handle. Good for... uh... prying...?", "rarity": "uncommon", "minrand": 1, "maxrand": 2, "inventoryslots": 1, "id": 185},
    {"name": "Drill", "value": 75, "description": "A battery operated drill. It's uh... a drill.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 186},
    {"name": "Handsaw", "value": 10, "description": "A saw. But hand operated. Good for dismemberment if you try hard enough!", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 187},
    {"name": "Circular saw", "value": 10, "description": "A saw. But electric. This one is really good for dismemberment!", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 188},
    {"name": "Grinder", "value": 35, "description": "A grinder. You use it to grind. Better get on that grind real quick! HAAAAH, I'm so funny.", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 189},
    {"name": "Match", "value": 1, "description": "Aw yep, that's a match right there.", "rarity": "common", "minrand": 1, "maxrand": 50, "inventoryslots": 1, "id": 190},
    {"name": "Wristwatch", "value": 10, "description": "A watch, but for your wrist? What a novel idea!", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 191, "slot": "wrist"},
    {"name": "Literally garbage", "value": 0, "description": "Yeah... that's literally garbage...", "rarity": "common", "minrand": 1, "maxrand": 15, "inventoryslots": 1, "id": 192},
    {"name": "Car battery", "value": 125, "description": "A 12 volt lead acid car battery. It's kinda hefty.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 3, "id": 193},
    {"name": "Fusion cell", "value": 25000, "description": "A small, enclosed, controlled nuclear fusion in a tube providing a steady warmth and power output of well over 15 KW. Don't drop it!", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 7, "id": 194},
    {"name": "Fusion battery", "value": 500, "description": "A tiny, enclosed, controlled nuclear fusion in a AA battery-sized tube, providing warmth and a power output of 500 W. Don't drop it!", "rarity": "rare", "minrand": 1, "maxrand": 5, "inventoryslots": 7, "id": 195},
    {"name": "Gasoline", "value": 50, "description": "A jerry can full of gasoline that somehow hasn't evaporated or gone bad.", "rarity": "mythic", "minrand": 1, "maxrand": 2, "inventoryslots": 3, "id": 196},
    {"name": "Rock", "value": 500, "description": "I call it big rock. Rhymes with Grug.", "rarity": "rare", "minrand": 1, "maxrand": 4, "inventoryslots": 15, "id": 197},
    {"name": "Pebble", "value": 0.01, "description": "I call it pebble. Rhymes with Grug.", "rarity": "common", "minrand": 1, "maxrand": 1000000, "inventoryslots": 1, "id": 198},
    {"name": "Pocket sand", "value": 1, "description": "It's a ziploc bag full of sand with 'Pocket Sand' labelled on it in sharpie. [Blinds enemies for 1 turn]", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 199},
]

traderspecificitems = [
    {"name": "Cheese", "value": 30, "description": "Cheesed to meet you :3 (Heals on consumption)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 157},
    {"name": "Sake", "value": 30, "description": "Made by yours truely!", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 158},
    {"name": "S. POTION", "value": 150, "description": "the Super Potion! (heals all wounds, before promptly unhealing them after battle)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 159},
    {"name": "B. Shot Bowtie", "value": 150, "description": "Gives you +50 defence! (Gives +1 strength, +1 resistance, & +1 magic when equipped)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 160},
    {"name": "Multi Colored Glasses", "value": 500, "description": "Now’s your chance. (Sells items with a 2x bonus & given +2 charisma when worn)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 161},
    {"name": "Gilded Samurai Armor", "value": 1000, "description": "Some old armor I used to wear, still very useful. (Grants +1 agility & gives entire body tier III armor)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 162},
    {"name": "Imperial Blade", "value": 500, "description": "Some surplus weaponry from my home! Still sharp. (+1 agility when used)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 163},
    {"name": "Broken Sword", "value": 100000, "description": "A legendary sword wielded by a fierce warrior from legends, it smites anything struck with it!", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 164},
    {"name": "Golden Key", "value": 1000, "description": "Not sure where I got it from, but it's cool!", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1, "id": 165},
]

all_tables = [
    test_table, melee_weapons, ranged_weapons, ammo, armor_and_defense,
    healing_and_magic, cursed_and_blessed_items, junk, traderspecificitems
]
seen_ids = {}
for table in all_tables:
    for item in table:
        item_id = item.get("id")
        if item_id is not None:
            if item_id in seen_ids:
                raise Exception(
                    f"Conflicting item id detected: {item_id} "
                    f"('{seen_ids[item_id]['name']}' and '{item['name']}')"
                )
            seen_ids[item_id] = item

traderitemdescriptions = [
    {"id": 0, "traderdesc": "A favorite among the unsavory… or those with horrible dental hygiene."},
    {"id": 1, "traderdesc": "Popular in the southern Union territories for hunting."},
    {"id": 2, "traderdesc": "I'm not sure where this originated from, but it's sharp and therefore valuable!"},
    {"id": 3, "traderdesc": "A common weapon among adventurers and knights alike!"},
    {"id": 4, "traderdesc": "Where is its handguard?!"},
    {"id": 5, "traderdesc": "A well edged blade I have used extensively in the past, though my Warrior days are long over."},
    {"id": 6, "traderdesc": "A far larger blade then your standard shortsword, this weapon type requires two hands to utilize."},
    {"id": 7, "traderdesc": "A very rare blade type originating from the north, their time in warfare has long passed."},
    {"id": 8, "traderdesc": "A large and heavy sword used by Gilded Knights of the Legion, it has proved its effectiveness in battle through countless wars."},
    {"id": 9, "traderdesc": "Extremely popular among the Legion, these very pointy sticks have been in circulation since the dawn of time!"},
    {"id": 10, "traderdesc": "I have seen countless soldiers from my homeland use weapons such as these."},
    {"id": 11, "traderdesc": "A axe for chopping wood, you can find these pretty much anywhere…"},
    {"id": 12, "traderdesc": "A highly unusual Axe that I don’t really know the source to, but its red paint has to mean it comes from somewhere cool!"},
    {"id": 13, "traderdesc": "A common bow with a very good drawstring, fine craftsmanship indeed!"},
    {"id": 14, "traderdesc": "This strange bow is made from very unusual materials…"},
    {"id": 15, "traderdesc": "I think I remember a clan of Pillagers used to use these…"},
    {"id": 16, "traderdesc": "A magical crossbow that has very high power, militaries from all over wish they could have these."},
    {"id": 17, "traderdesc": "Why is it so small…"},
    {"id": 18, "traderdesc": "These are eerily similar to those Kyntarian prototypes I’ve been seeing around…"},
    {"id": 19, "traderdesc": "It's a small weapon but it has a long barrel!"},
    {"id": 20, "traderdesc": "I have… no idea what this is."},
    {"id": 21, "traderdesc": "I have… no idea what this is."},
    {"id": 22, "traderdesc": "A very fast firing musket!"},
    {"id": 23, "traderdesc": "Its like a cannon, but smaller."},
    {"id": 24, "traderdesc": "I once heard that these things shoot tiny dragons, is that true?"},
    {"id": 25, "traderdesc": "I'm not sure what these are…"},
    {"id": 26, "traderdesc": "I'm not sure what these are…"},
    {"id": 27, "traderdesc": "I'm not sure what these are…"},
    {"id": 28, "traderdesc": "I'm not sure what these are…"},
    {"id": 29, "traderdesc": "I'm not sure what these are…"},
    {"id": 30, "traderdesc": "I'm not sure what these are…"},
    {"id": 31, "traderdesc": "I'm not sure what these are…"},
    {"id": 32, "traderdesc": "I'm not sure what these are…"},
    {"id": 33, "traderdesc": "I'm not sure what these are…"},
    {"id": 34, "traderdesc": "I'm not sure what these are…"},
    {"id": 35, "traderdesc": "I'm not sure what these are…"},
    {"id": 36, "traderdesc": "I'm not sure what these are…"},
    {"id": 37, "traderdesc": "I'm not sure what these are…"},
    {"id": 38, "traderdesc": "I'm not sure what these are…"},
    {"id": 39, "traderdesc": "I'm not sure what these are…"},
    {"id": 40, "traderdesc": "I'm not sure what these are…"},
    {"id": 41, "traderdesc": "I'm not sure what these are…"},
    {"id": 42, "traderdesc": "I'm not sure what these are…"},
    {"id": 43, "traderdesc": "I'm not sure what these are…"},
    {"id": 44, "traderdesc": "I'm not sure what these are…"},
    {"id": 45, "traderdesc": "I'm not sure what these are…"},
    {"id": 46, "traderdesc": "I'm not sure what these are…"},
    {"id": 47, "traderdesc": "I'm not sure what these are…"},
    {"id": 48, "traderdesc": "I'm not sure what these are…"},
    {"id": 49, "traderdesc": "I'm not sure what these are…"},
    {"id": 50, "traderdesc": "I'm not sure what these are…"},
    {"id": 51, "traderdesc": "Behold! The artifact that the dragon spitter takes!"},
    {"id": 52, "traderdesc": "What the hell even is this?"},
    {"id": 53, "traderdesc": "A spicy berry, I do not recommend eating them…"},
    {"id": 54, "traderdesc": "I'm not sure what these do, but your military seems to like wearing them."},
    {"id": 55, "traderdesc": "It's almost like chainmail, but strangely its fabric…"},
    {"id": 56, "traderdesc": "A surprisingly lightweight armor plate, I'm not sure how your people made it…"},
    {"id": 57, "traderdesc": "A durable steel plate offering protection against rifle rounds."},
    {"id": 58, "traderdesc": "A surprisingly lightweight armor plate, that stops a lot more things!"},
    {"id": 59, "traderdesc": "A thick plate of steel, its craftsmanship is nothing I’ve ever seen before…"},
    {"id": 60, "traderdesc": "A lightweight plate that's somehow even more powerful than our own armor… Is it magic?"},
    {"id": 61, "traderdesc": "How could such a thick plate of steel be bent so well?"},
    {"id": 62, "traderdesc": "Helmet of the Legion, the great helm offers great protection against bladed weaponry."},
    {"id": 63, "traderdesc": "A very popular helmet from around the world, it accepts many faceplate attachments for various needs!"},
    {"id": 64, "traderdesc": "A more rounded helmet with better neck protection, includes a faceplate to protect from bladed weapons."},
    {"id": 65, "traderdesc": "Very popular with knights of the Legion, mostly due it its comfort and easy to remove faceplate."},
    {"id": 66, "traderdesc": "A later model of the Great Helms used by the Legion, the sugarloaf helmets have better angling to help deflect blows done by enemies."},
    {"id": 67, "traderdesc": "An early Nasal helmet dawned originally by the Kyntarians, however due to their doctrine changes, they no longer use them in service."},
    {"id": 68, "traderdesc": "A fully covered plate of armor, offers great protection from bladed weaponry and arrows! Er… watch out for maces though."},
    {"id": 69, "traderdesc": "In case you wish for more maneuverability in combat rather than protection."},
    {"id": 70, "traderdesc": "A very lightweight armor that helps soften the blows done by edged weapons, though it isn’t the greatest against high powered arrows…"},
    {"id": 71, "traderdesc": "A light weight blanket of metal rings, chainmail offers a great balance of both maneuverability and protection."},
    {"id": 72, "traderdesc": "Similar in thought process to chainmail, this thick coat is made of dense fabrics and cloth to help soften the blows of enemy attacks."},
    {"id": 73, "traderdesc": "Plated armor blanketed in thick cloth and leather, it offers great protection, as well as style."},
    {"id": 74, "traderdesc": "It's a pretty small bag with straps on it so you can wear it. Pretty handy!"},
    {"id": 75, "traderdesc": "It's a pretty small bag with straps on it, it's bigger than the other small bag but it's still pretty small."},
    {"id": 76, "traderdesc": "It's not too big, it's not small either, it's a pretty all-round decent bag."},
    {"id": 77, "traderdesc": "This is a really big bag. You sure can fit a lot in here, but it seems kinda inconvenient."},
    {"id": 78, "traderdesc": "This bag is massive! You can fit a lot of stuff in here, but it's really heavy and hard to carry."},
    {"id": 79, "traderdesc": "Pretty small and convenient! I like this bag."},
    {"id": 80, "traderdesc": "Your military loves this bag, I don't really know why."},
    {"id": 81, "traderdesc": "What is this, a bag for ants?"},
    {"id": 82, "traderdesc": "I don't really know what this is or what to do with this, your military seems to like these though."},
    {"id": 83, "traderdesc": "What is this, a bag for ants?"},
    {"id": 84, "traderdesc": "I love this bag! It's so convenient yet spacious!"},
    {"id": 85, "traderdesc": "This bag has to be one of my favorites, it's so convenient and comfortable!"},
    {"id": 86, "traderdesc": "A cloth bandage wrap for preventing bleeding."},
    {"id": 87, "traderdesc": "Although I'm not sure what the need for the cross on the front of it is for, it's full of medical supplies and therefore useful!"},
    {"id": 88, "traderdesc": "No, no! It's not snake oil I swear!"},
    {"id": 89, "traderdesc": "I already told you, it is NOT snake oil!"},
    {"id": 90, "traderdesc": "A potion used by magic users to restore their mana, I get sold out of these a lot."},
    {"id": 91, "traderdesc": "Its… an apple, why do you need me to describe this to you?"},
    {"id": 92, "traderdesc": "Bread."},
    {"id": 93, "traderdesc": "I don't need it... I don't need it... IIII NEEEEEDDD IIIITTTT!!"},
    {"id": 94, "traderdesc": "A cooked steak. I don't know why it's still hot, must be magic or something."},
    {"id": 95, "traderdesc": "A hard biscuit often given to soldiers on long patrols."},
    {"id": 96, "traderdesc": "The amount of bears I’ve had to fend off from my cart to keep this stuff is astounding."},
    {"id": 97, "traderdesc": "Sandwich makes me strong!"},
    {"id": 98, "traderdesc": "It's not fries."},
    {"id": 99, "traderdesc": "I’ve never seen these in our world, but they make me feel awake when I drink them."},
    {"id": 100, "traderdesc": "No, I'm not a snake oiler."},
    {"id": 101, "traderdesc": "I hope you know it's illegal for me to have this."},
    {"id": 102, "traderdesc": "You're supposed to mix this with other alcohol, you know that right?"},
    {"id": 103, "traderdesc": "It cures all. I swear!"},
    {"id": 104, "traderdesc": "This magical potion was created by the great wizards of… uhm… its… its just snake oil again."},
    {"id": 105, "traderdesc": "I'm not sure where this originates from, however it appears to heal injuries over time when opened… I… wouldn’t trust it though."},
    {"id": 106, "traderdesc": "I don’t know what this is and I'm too scared to find out."},
    {"id": 107, "traderdesc": "They say the feather of the phoenix can restore the dead to the living… but that's just a legend."},
    {"id": 108, "traderdesc": "When I hold it, it feels like something is watching me…"},
    {"id": 109, "traderdesc": "A sacrificial dagger of demonic origin, I believe i’ve seen those cultists use these a lot."},
    {"id": 110, "traderdesc": "It smells like a dog."},
    {"id": 111, "traderdesc": "These boots are of excellent craftsmanship… they are almost impossible to destroy!"},
    {"id": 112, "traderdesc": "It makes a funny noise when I hit things with it."},
    {"id": 113, "traderdesc": "A sweater that's made out of an unknown yarn like substance, it reminds me of my grandmother."},
    {"id": 114, "traderdesc": "A very sturdy shovel, the blood on it makes it apparent it's already been used."},
    {"id": 115, "traderdesc": "I hear a funny voice when I put it on."},
    {"id": 116, "traderdesc": "It looks almost like a wizard staff… but its too short."},
    {"id": 117, "traderdesc": "You don’t wanna drink this."},
    {"id": 118, "traderdesc": "I have no idea what this really is, but it has a cool flag on it!"},
    {"id": 119, "traderdesc": "I don’t recommend trying to eat it… trust me."},
    {"id": 120, "traderdesc": "I think i’ve seen this before."},
    {"id": 121, "traderdesc": "It keeps breaking!"},
    {"id": 122, "traderdesc": "It smells... fishy."},
    {"id": 123, "traderdesc": "Hey, it has a cool eyepatch with it too!"},
    {"id": 124, "traderdesc": "It's... literally just a box."},
    {"id": 125, "traderdesc": "A treasure chest covered in green stuff. There is a 4 number combination lock with a griffin carved into the metal holding it shut."},
    {"id": 126, "traderdesc": "A lost 4 combination code with a griffin engraved on the back of the card."},
    {"id": 127, "traderdesc": "I believe this staff originates from the Crimson Demon Clan… I’d be careful with it if I were you."},
    {"id": 128, "traderdesc": "It looks almost like my sword but… smaller."},
    {"id": 129, "traderdesc": "I don't know how it works."},
    {"id": 130, "traderdesc": "It makes me feel like I'm about to have a heart attack!"},
    {'id': 131, "traderdesc": "This thing looks pretty makeshift… It has a label on the back too."},
    {"id": 132, "traderdesc": "Why is it asking me if its in me?"},
    {"id": 133, "traderdesc": "It's a cowboy hat covered in blood! Neat!"},
    {"id": 134, "traderdesc": "A strange hat that I’ve never seen before… strange."},
    {"id": 135, "traderdesc": "This WILL fuck you up."},
    {"id": 136, "traderdesc": "This thing looks almost alien... it's so strange."},
    {"id": 137, "traderdesc": "A neat hat!"},
    {"id": 138, "traderdesc": "A neat jacket!"},
    {"id": 139, "traderdesc": "I heard these ward off danger, only a rumor though."},
    {"id": 140, "traderdesc": "A weapon from your world.. It has dog hair on it."},
    {"id": 141, "traderdesc": "It seems to hold anything I put into it."},
    {"id": 142, "traderdesc": "It's written in a strange language."},
    {"id": 143, "traderdesc": "Stylish but also humiliating."},
    {"id": 144, "traderdesc": "A helmet I don’t know the origin of, it's pretty damaged."},
    {"id": 145, "traderdesc": "I'm not familiar with the weapons of your world, but this one seems pretty broken."},
    {"id": 146, "traderdesc": "I have no idea what this is."},
    {"id": 147, "traderdesc": "I feel gross holding this."},
    {"id": 148, "traderdesc": "Gentlemen, vwei are nazis, und vwei, will have war…"},
    {"id": 149, "traderdesc": "Are you some kinda fuckin’ commie?"},
    {"id": 150, "traderdesc": "BLYAAAAAAAAAAAAT TRAKTORRRR BLYAAAAT!"},
    {"id": 151, "traderdesc": "DA SIND WIR ABER IMMER NOCH-"},
    {"id": 152, "traderdesc": "They look like cat ears… why would you wear this?"},
    {"id": 153, "traderdesc": "Ew… smells like coffee."},
    {"id": 154, "traderdesc": "..."},
    {"id": 155, "traderdesc": "I dunno what it is but it keeps making fun of me when I talk to it."},
    {"id": 156, "traderdesc": "A bag with an anglerfish emblem on the back of it."},
    {"id": 166, "traderdesc": "I'm not sure what this is..."},
    {"id": 167, "traderdesc": "I'm not sure what this is..."},
]

caliberinfo = [
    {"caliber": ".22 Long Rifle", "penlevel": "none"},
    {"caliber": "9x19mm Parabellum", "penlevel": "I"},
    {"caliber": ".45 ACP", "penlevel": "I"},
    {"caliber": ".38 Special", "penlevel": "I"},
    {"caliber": ".357 Magnum", "penlevel": ["I", "IIa"]},
    {"caliber": ".44 Magnum", "penlevel": ["I", "IIa", "II"]},
    {"caliber": "10mm auto", "penlevel": ["I"]},
    {"caliber": ".223 Remington", "penlevel": ["I", "IIa", "II", "IIIa"]},
    {"caliber": ".308 Winchester", "penlevel": ["I", "IIa", "II", "IIIa"]},
    {"caliber": "5.45x39mm Soviet", "penlevel": ["I", "IIa", "II", "IIIa"]},
    {"caliber": "5.56x45mm NATO", "penlevel": ["I", "IIa", "II", "IIIa"]},
    {"caliber": "7.62x51mm NATO", "penlevel": ["I", "IIa", "II", "IIIa"]},
    {"caliber": ".300 AAC BLK", "penlevel": ["I", "IIa", "II", "IIIa"]},
    {"caliber": ".30-06 Springfield", "penlevel": ["I", "IIa", "II", "IIIa"]},
    {"caliber": "7.62x39mm Soviet", "penlevel": ["I", "IIa", "II", "IIIa"]},
    {"caliber": ".45-70 Government", "penlevel": ["I", "IIa", "II", "IIIa", "III"]},
    {"caliber": ".338 Lapua Magnum", "penlevel": ["I", "IIa", "II", "IIIa", "III", "IV", "IV+"]},
    {"caliber": ".500 S&W Magnum", "penlevel": ["I", "IIa", "II", "IIIa", "III", "IV"]},
    {"caliber": ".500 Nitro Express", "penlevel": ["I", "IIa", "II", "IIIa", "III", "IV", "IV+"]},
    {"caliber": ".50 Beowulf", "penlevel": ["I", "IIa", "II", "IIIa", "III", "IV", "IV+"]},
    {"caliber": ".50 BMG", "penlevel": ["I", "IIa", "II", "IIIa", "III", "IV", "IV+"]}
]

card_deck = [
    {"name": "Ace of Spades", "cardface": "🂡", "internalname": "A-S"},
    {"name": "Ace of Hearts", "cardface": "🂱", "internalname": "A-H"},
    {"name": "Ace of Diamonds", "cardface": "🃁", "internalname": "A-D"},
    {"name": "Ace of Clubs", "cardface": "🃑", "internalname": "A-C"},
    {"name": "2 of Spades", "cardface": "🂢", "internalname": "2-S"},
    {"name": "2 of Hearts", "cardface": "🂲", "internalname": "2-H"},
    {"name": "2 of Diamonds", "cardface": "🃂", "internalname": "2-D"},
    {"name": "2 of Clubs", "cardface": "🃒", "internalname": "2-C"},
    {"name": "3 of Spades", "cardface": "🂣", "internalname": "3-S"},
    {"name": "3 of Hearts", "cardface": "🂳", "internalname": "3-H"},
    {"name": "3 of Diamonds", "cardface": "🃃", "internalname": "3-D"},
    {"name": "3 of Clubs", "cardface": "🃓", "internalname": "3-C"},
    {"name": "4 of Spades", "cardface": "🂤", "internalname": "4-S"},
    {"name": "4 of Hearts", "cardface": "🂴", "internalname": "4-H"},
    {"name": "4 of Diamonds", "cardface": "🃄", "internalname": "4-D"},
    {"name": "4 of Clubs", "cardface": "🃔", "internalname": "4-C"},
    {"name": "5 of Spades", "cardface": "🂥", "internalname": "5-S"},
    {"name": "5 of Hearts", "cardface": "🂵", "internalname": "5-H"},
    {"name": "5 of Diamonds", "cardface": "🃅", "internalname": "5-D"},
    {"name": "5 of Clubs", "cardface": "🃕", "internalname": "5-C"},
    {"name": "6 of Spades", "cardface": "🂦", "internalname": "6-S"},
    {"name": "6 of Hearts", "cardface": "🂶", "internalname": "6-H"},
    {"name": "6 of Diamonds", "cardface": "🃆", "internalname": "6-D"},
    {"name": "6 of Clubs", "cardface": "🃖", "internalname": "6-C"},
    {"name": "7 of Spades", "cardface": "🂧", "internalname": "7-S"},
    {"name": "7 of Hearts", "cardface": "🂷", "internalname": "7-H"},
    {"name": "7 of Diamonds", "cardface": "🃇", "internalname": "7-D"},
    {"name": "7 of Clubs", "cardface": "🃗", "internalname": "7-C"},
    {"name": "8 of Spades", "cardface": "🂨", "internalname": "8-S"},
    {"name": "8 of Hearts", "cardface": "🂸", "internalname": "8-H"},
    {"name": "8 of Diamonds", "cardface": "🃈", "internalname": "8-D"},
    {"name": "8 of Clubs", "cardface": "🃘", "internalname": "8-C"},
    {"name": "9 of Spades", "cardface": "🂩", "internalname": "9-S"},
    {"name": "9 of Hearts", "cardface": "🂹", "internalname": "9-H"},
    {"name": "9 of Diamonds", "cardface": "🃉", "internalname": "9-D"},
    {"name": "9 of Clubs", "cardface": "🃙", "internalname": "9-C"},
    {"name": "10 of Spades", "cardface": "🂪", "internalname": "10-S"},
    {"name": "10 of Hearts", "cardface": "🂺", "internalname": "10-H"},
    {"name": "10 of Diamonds", "cardface": "🃊", "internalname": "10-D"},
    {"name": "10 of Clubs", "cardface": "🃚", "internalname": "10-C"},
    {"name": "Jack of Spades", "cardface": "🂫", "internalname": "J-S"},
    {"name": "Jack of Hearts", "cardface": "🂻", "internalname": "J-H"},
    {"name": "Jack of Diamonds", "cardface": "🃋", "internalname": "J-D"},
    {"name": "Jack of Clubs", "cardface": "🃛", "internalname": "J-C"},
    {"name": "Queen of Spades", "cardface": "🂭", "internalname": "Q-S"},
    {"name": "Queen of Hearts", "cardface": "🂽", "internalname": "Q-H"},
    {"name": "Queen of Diamonds", "cardface": "🃍", "internalname": "Q-D"},
    {"name": "Queen of Clubs", "cardface": "🃝", "internalname": "Q-C"},
    {"name": "King of Spades", "cardface": "🂮", "internalname": "K-S"},
    {"name": "King of Hearts", "cardface": "🂾", "internalname": "K-H"},
    {"name": "King of Diamonds", "cardface": "🃎", "internalname": "K-D"},
    {"name": "King of Clubs", "cardface": "🃞", "internalname": "K-C"},
    {"name": "Joker", "cardface": "🃏︎", "internalname": "Joker"},
]

firstnames = [
    {"name": "Oliver", "sex": "Masculine", "popularity": 1},
    {"name": "Charlotte", "sex": "Feminine", "popularity": 1},
    {"name": "Theodore", "sex": "Masculine", "popularity": 2},
    {"name": "Amelia", "sex": "Feminine", "popularity": 2},
    {"name": "Liam", "sex": "Masculine", "popularity": 3},
    {"name": "Olivia", "sex": "Feminine", "popularity": 3},
    {"name": "Noah", "sex": "Masculine", "popularity": 4},
    {"name": "Sophia", "sex": "Feminine", "popularity": 4},
    {"name": "Henry", "sex": "Masculine", "popularity": 5},
    {"name": "Evelyn", "sex": "Feminine", "popularity": 5},
    {"name": "Elijah", "sex": "Masculine", "popularity": 6},
    {"name": "Emma", "sex": "Feminine", "popularity": 6},
    {"name": "Hudson", "sex": "Masculine", "popularity": 7},
    {"name": "Ava", "sex": "Feminine", "popularity": 7},
    {"name": "William", "sex": "Masculine", "popularity": 8},
    {"name": "Harper", "sex": "Feminine", "popularity": 8},
    {"name": "Owen", "sex": "Masculine", "popularity": 9},
    {"name": "Eleanor", "sex": "Feminine", "popularity": 9},
    {"name": "Jackson", "sex": "Masculine", "popularity": 10},
    {"name": "Nora", "sex": "Feminine", "popularity": 10},
    {"name": "James", "sex": "Masculine", "popularity": 11},
    {"name": "Willow", "sex": "Feminine", "popularity": 11},
    {"name": "Benjamin", "sex": "Masculine", "popularity": 12},
    {"name": "Mia", "sex": "Feminine", "popularity": 12},
    {"name": "Lucas", "sex": "Masculine", "popularity": 13},
    {"name": "Ellie", "sex": "Feminine", "popularity": 13},
    {"name": "Lincoln", "sex": "Masculine", "popularity": 14},
    {"name": "Hazel", "sex": "Feminine", "popularity": 14},
    {"name": "Asher", "sex": "Masculine", "popularity": 15},
    {"name": "Violet", "sex": "Feminine", "popularity": 15},
    {"name": "Jack", "sex": "Masculine", "popularity": 16},
    {"name": "Scarlett", "sex": "Feminine", "popularity": 16},
    {"name": "Grayson", "sex": "Masculine", "popularity": 17},
    {"name": "Isabella", "sex": "Feminine", "popularity": 17},
    {"name": "Maverick", "sex": "Masculine", "popularity": 18},
    {"name": "Isla", "sex": "Feminine", "popularity": 18},
    {"name": "Levi", "sex": "Masculine", "popularity": 19},
    {"name": "Aurora", "sex": "Feminine", "popularity": 19},
    {"name": "Michael", "sex": "Masculine", "popularity": 20},
    {"name": "Layla", "sex": "Feminine", "popularity": 20},
    {"name": "Cooper", "sex": "Masculine", "popularity": 21},
    {"name": "Avery", "sex": "Feminine", "popularity": 21},
    {"name": "Samuel", "sex": "Masculine", "popularity": 22},
    {"name": "Luna", "sex": "Feminine", "popularity": 22},
    {"name": "Leo", "sex": "Masculine", "popularity": 23},
    {"name": "Nova", "sex": "Feminine", "popularity": 23},
    {"name": "Ezra", "sex": "Masculine", "popularity": 24},
    {"name": "Ivy", "sex": "Feminine", "popularity": 24},
    {"name": "Joseph", "sex": "Masculine", "popularity": 25},
    {"name": "Lainey", "sex": "Feminine", "popularity": 25},
    {"name": "Wyatt", "sex": "Masculine", "popularity": 26},
    {"name": "Lucy", "sex": "Feminine", "popularity": 26},
    {"name": "Luke", "sex": "Masculine", "popularity": 27},
    {"name": "Aria", "sex": "Feminine", "popularity": 27},
    {"name": "Mason", "sex": "Masculine", "popularity": 28},
    {"name": "Paisley", "sex": "Feminine", "popularity": 28},
    {"name": "Waylon", "sex": "Masculine", "popularity": 29},
    {"name": "Lillian", "sex": "Feminine", "popularity": 29},
    {"name": "Carter", "sex": "Masculine", "popularity": 30},
    {"name": "Penelope", "sex": "Feminine", "popularity": 30},
    {"name": "Thomas", "sex": "Masculine", "popularity": 31},
    {"name": "Ella", "sex": "Feminine", "popularity": 31},
    {"name": "Cameron", "sex": "Masculine", "popularity": 32},
    {"name": "Lily", "sex": "Feminine", "popularity": 32},
    {"name": "Luca", "sex": "Masculine", "popularity": 33},
    {"name": "Chloe", "sex": "Feminine", "popularity": 33},
    {"name": "Myles", "sex": "Masculine", "popularity": 34},
    {"name": "Riley", "sex": "Feminine", "popularity": 34},
    {"name": "Miles", "sex": "Masculine", "popularity": 35},
    {"name": "Elizabeth", "sex": "Feminine", "popularity": 35},
    {"name": "Nolan", "sex": "Masculine", "popularity": 36},
    {"name": "Gianna", "sex": "Feminine", "popularity": 36},
    {"name": "John", "sex": "Masculine", "popularity": 37},
    {"name": "Josephine", "sex": "Feminine", "popularity": 37},
    {"name": "Alexander", "sex": "Masculine", "popularity": 38},
    {"name": "Kinsley", "sex": "Feminine", "popularity": 38},
    {"name": "Ethan", "sex": "Masculine", "popularity": 39},
    {"name": "Stella", "sex": "Feminine", "popularity": 39},
    {"name": "Everett", "sex": "Masculine", "popularity": 40},
    {"name": "Mila", "sex": "Feminine", "popularity": 40},
    {"name": "Brooks", "sex": "Masculine", "popularity": 41},
    {"name": "Naomi", "sex": "Feminine", "popularity": 41},
    {"name": "Charles", "sex": "Masculine", "popularity": 42},
    {"name": "Abigail", "sex": "Feminine", "popularity": 42},
    {"name": "Weston", "sex": "Masculine", "popularity": 43},
    {"name": "Grace", "sex": "Feminine", "popularity": 43},
    {"name": "Beau", "sex": "Masculine", "popularity": 44},
    {"name": "Madison", "sex": "Feminine", "popularity": 44},
    {"name": "Jacob", "sex": "Masculine", "popularity": 45},
    {"name": "Vivian", "sex": "Feminine", "popularity": 45},
    {"name": "Logan", "sex": "Masculine", "popularity": 46},
    {"name": "Addison", "sex": "Feminine", "popularity": 46},
    {"name": "Andrew", "sex": "Masculine", "popularity": 47},
    {"name": "Cora", "sex": "Feminine", "popularity": 47},
    {"name": "Daniel", "sex": "Masculine", "popularity": 48},
    {"name": "Delilah", "sex": "Feminine", "popularity": 48},
    {"name": "Aiden", "sex": "Masculine", "popularity": 49},
    {"name": "Zoey", "sex": "Feminine", "popularity": 49},
    {"name": "Gabriel", "sex": "Masculine", "popularity": 50},
    {"name": "Sofia", "sex": "Feminine", "popularity": 50},
    {"name": "Colton", "sex": "Masculine", "popularity": 51},
    {"name": "Quinn", "sex": "Feminine", "popularity": 51},
    {"name": "Silas", "sex": "Masculine", "popularity": 52},
    {"name": "Ruby", "sex": "Feminine", "popularity": 52},
    {"name": "David", "sex": "Masculine", "popularity": 53},
    {"name": "Sadie", "sex": "Feminine", "popularity": 53},
    {"name": "Matthew", "sex": "Masculine", "popularity": 54},
    {"name": "Madelyn", "sex": "Feminine", "popularity": 54},
    {"name": "Rowan", "sex": "Masculine", "popularity": 55},
    {"name": "Iris", "sex": "Feminine", "popularity": 55},
    {"name": "Anthony", "sex": "Masculine", "popularity": 56},
    {"name": "Kennedy", "sex": "Feminine", "popularity": 56},
    {"name": "Bennett", "sex": "Masculine", "popularity": 57},
    {"name": "Emery", "sex": "Feminine", "popularity": 57},
    {"name": "Roman", "sex": "Masculine", "popularity": 58},
    {"name": "Maeve", "sex": "Feminine", "popularity": 58},
    {"name": "Isaac", "sex": "Masculine", "popularity": 59},
    {"name": "Emilia", "sex": "Feminine", "popularity": 59},
    {"name": "Wesley", "sex": "Masculine", "popularity": 60},
    {"name": "Josie", "sex": "Feminine", "popularity": 60},
    {"name": "Jameson", "sex": "Masculine", "popularity": 61},
    {"name": "Oaklynn", "sex": "Feminine", "popularity": 61},
    {"name": "Parker", "sex": "Masculine", "popularity": 62},
    {"name": "Claire", "sex": "Feminine", "popularity": 62},
    {"name": "Elias", "sex": "Masculine", "popularity": 63},
    {"name": "Lydia", "sex": "Feminine", "popularity": 63},
    {"name": "Mateo", "sex": "Masculine", "popularity": 64},
    {"name": "Eloise", "sex": "Feminine", "popularity": 64},
    {"name": "Carson", "sex": "Masculine", "popularity": 65},
    {"name": "Clara", "sex": "Feminine", "popularity": 65},
    {"name": "Jaxon", "sex": "Masculine", "popularity": 66},
    {"name": "Eden", "sex": "Feminine", "popularity": 66},
    {"name": "Braxton", "sex": "Masculine", "popularity": 67},
    {"name": "Emily", "sex": "Feminine", "popularity": 67},
    {"name": "Josiah", "sex": "Masculine", "popularity": 68},
    {"name": "Sophie", "sex": "Feminine", "popularity": 68},
    {"name": "Theo", "sex": "Masculine", "popularity": 69},
    {"name": "Athena", "sex": "Feminine", "popularity": 69},
    {"name": "Caleb", "sex": "Masculine", "popularity": 70},
    {"name": "Eliana", "sex": "Feminine", "popularity": 70},
    {"name": "Isaiah", "sex": "Masculine", "popularity": 71},
    {"name": "Juniper", "sex": "Feminine", "popularity": 71},
    {"name": "Walker", "sex": "Masculine", "popularity": 72},
    {"name": "Audrey", "sex": "Feminine", "popularity": 72},
    {"name": "Joshua", "sex": "Masculine", "popularity": 73},
    {"name": "Hadley", "sex": "Feminine", "popularity": 73},
    {"name": "Landon", "sex": "Masculine", "popularity": 74},
    {"name": "Adalynn", "sex": "Feminine", "popularity": 74},
    {"name": "Easton", "sex": "Masculine", "popularity": 75},
    {"name": "Oakley", "sex": "Feminine", "popularity": 75},
    {"name": "Robert", "sex": "Masculine", "popularity": 76},
    {"name": "Aubrey", "sex": "Feminine", "popularity": 76},
    {"name": "Emmett", "sex": "Masculine", "popularity": 77},
    {"name": "Everly", "sex": "Feminine", "popularity": 77},
    {"name": "Dylan", "sex": "Masculine", "popularity": 78},
    {"name": "Raelynn", "sex": "Feminine", "popularity": 78},
    {"name": "Dominic", "sex": "Masculine", "popularity": 79},
    {"name": "Natalie", "sex": "Feminine", "popularity": 79},
    {"name": "Kai", "sex": "Masculine", "popularity": 80},
    {"name": "Rylee", "sex": "Feminine", "popularity": 80},
    {"name": "Greyson", "sex": "Masculine", "popularity": 81},
    {"name": "Millie", "sex": "Feminine", "popularity": 81},
    {"name": "Calvin", "sex": "Masculine", "popularity": 82},
    {"name": "Savannah", "sex": "Feminine", "popularity": 82},
    {"name": "Xavier", "sex": "Masculine", "popularity": 83},
    {"name": "Brooklyn", "sex": "Feminine", "popularity": 83},
    {"name": "Christopher", "sex": "Masculine", "popularity": 84},
    {"name": "Autumn", "sex": "Feminine", "popularity": 84},
    {"name": "Micah", "sex": "Masculine", "popularity": 85},
    {"name": "Elliana", "sex": "Feminine", "popularity": 85},
    {"name": "August", "sex": "Masculine", "popularity": 86},
    {"name": "Gabriella", "sex": "Feminine", "popularity": 86},
    {"name": "Nathan", "sex": "Masculine", "popularity": 87},
    {"name": "Rose", "sex": "Feminine", "popularity": 87},
    {"name": "Julian", "sex": "Masculine", "popularity": 88},
    {"name": "Lyla", "sex": "Feminine", "popularity": 88},
    {"name": "Atlas", "sex": "Masculine", "popularity": 89},
    {"name": "Anna", "sex": "Feminine", "popularity": 89},
    {"name": "Graham", "sex": "Masculine", "popularity": 90},
    {"name": "Everleigh", "sex": "Feminine", "popularity": 90},
    {"name": "Jaxson", "sex": "Masculine", "popularity": 91},
    {"name": "Hannah", "sex": "Feminine", "popularity": 91},
    {"name": "Archer", "sex": "Masculine", "popularity": 92},
    {"name": "Remi", "sex": "Feminine", "popularity": 92},
    {"name": "Jonah", "sex": "Masculine", "popularity": 93},
    {"name": "Leah", "sex": "Feminine", "popularity": 93},
    {"name": "Ezekiel", "sex": "Masculine", "popularity": 94},
    {"name": "Caroline", "sex": "Feminine", "popularity": 94},
    {"name": "Milo", "sex": "Masculine", "popularity": 95},
    {"name": "Daisy", "sex": "Feminine", "popularity": 95},
    {"name": "River", "sex": "Masculine", "popularity": 96},
    {"name": "Eliza", "sex": "Feminine", "popularity": 96},
    {"name": "Vincent", "sex": "Masculine", "popularity": 97},
    {"name": "Wrenley", "sex": "Feminine", "popularity": 97},
    {"name": "Legend", "sex": "Masculine", "popularity": 98},
    {"name": "Peyton", "sex": "Feminine", "popularity": 98},
    {"name": "Jasper", "sex": "Masculine", "popularity": 99},
    {"name": "Victoria", "sex": "Feminine", "popularity": 99},
    {"name": "Adam", "sex": "Masculine", "popularity": 100},
    {"name": "Emersyn", "sex": "Feminine", "popularity": 100}
]

lastnames = [
    {"name": "Smith", "popularity": 1},
    {"name": "Miller", "popularity": 2},
    {"name": "Johnson", "popularity": 3},
    {"name": "Brown", "popularity": 4},
    {"name": "Williams", "popularity": 5},
    {"name": "Jones", "popularity": 6},
    {"name": "Davis", "popularity": 7},
    {"name": "Wilson", "popularity": 8},
    {"name": "Moore", "popularity": 9},
    {"name": "Thomas", "popularity": 10},
    {"name": "Taylor", "popularity": 11},
    {"name": "Thompson", "popularity": 12},
    {"name": "Clark", "popularity": 13},
    {"name": "Jackson", "popularity": 14},
    {"name": "Martin", "popularity": 15},
    {"name": "White", "popularity": 16},
    {"name": "Baker", "popularity": 17},
    {"name": "Hall", "popularity": 18},
    {"name": "Anderson", "popularity": 19},
    {"name": "Harris", "popularity": 20},
    {"name": "Lewis", "popularity": 21},
    {"name": "Robinson", "popularity": 22},
    {"name": "Young", "popularity": 23},
    {"name": "King", "popularity": 24},
    {"name": "Adams", "popularity": 25},
    {"name": "Hill", "popularity": 26},
    {"name": "Allen", "popularity": 27},
    {"name": "Evans", "popularity": 28},
    {"name": "Scott", "popularity": 29},
    {"name": "Wright", "popularity": 30},
    {"name": "Campbell", "popularity": 31},
    {"name": "Myers", "popularity": 32},
    {"name": "Walker", "popularity": 33},
    {"name": "Phillips", "popularity": 34},
    {"name": "Roberts", "popularity": 35},
    {"name": "Green", "popularity": 36},
    {"name": "Reed", "popularity": 37},
    {"name": "Lee", "popularity": 38},
    {"name": "Morris", "popularity": 39},
    {"name": "Mitchell", "popularity": 40},
    {"name": "Snyder", "popularity": 41},
    {"name": "Carter", "popularity": 42},
    {"name": "Stewart", "popularity": 43},
    {"name": "Turner", "popularity": 44},
    {"name": "Howard", "popularity": 45},
    {"name": "Bailey", "popularity": 46},
    {"name": "Fisher", "popularity": 47},
    {"name": "Cox", "popularity": 48},
    {"name": "Long", "popularity": 49},
    {"name": "Ross", "popularity": 50},
    {"name": "Morgan", "popularity": 51},
    {"name": "Edwards", "popularity": 52},
    {"name": "Ward", "popularity": 53},
    {"name": "Murphy", "popularity": 54},
    {"name": "Parker", "popularity": 55},
    {"name": "Hughes", "popularity": 56},
    {"name": "Wagner", "popularity": 57},
    {"name": "Bell", "popularity": 58},
    {"name": "Gray", "popularity": 59},
    {"name": "Price", "popularity": 60},
    {"name": "Rogers", "popularity": 61},
    {"name": "Bennett", "popularity": 62},
    {"name": "Gibson", "popularity": 63},
    {"name": "Jenkins", "popularity": 64},
    {"name": "Hamilton", "popularity": 65},
    {"name": "Russell", "popularity": 66},
    {"name": "Nelson", "popularity": 67},
    {"name": "Weaver", "popularity": 68},
    {"name": "Perry", "popularity": 69},
    {"name": "Adkins", "popularity": 70},
    {"name": "Patterson", "popularity": 71},
    {"name": "Wood", "popularity": 72},
    {"name": "Stevens", "popularity": 73},
    {"name": "Brooks", "popularity": 74},
    {"name": "Fox", "popularity": 75},
    {"name": "Rose", "popularity": 76},
    {"name": "Carpenter", "popularity": 77},
    {"name": "Foster", "popularity": 78},
    {"name": "West", "popularity": 79},
    {"name": "Watson", "popularity": 80},
    {"name": "Wells", "popularity": 81},
    {"name": "Jordan", "popularity": 82},
    {"name": "Cole", "popularity": 83},
    {"name": "James", "popularity": 84},
    {"name": "Henderson", "popularity": 85},
    {"name": "Burns", "popularity": 86},
    {"name": "Powell", "popularity": 87},
    {"name": "Coleman", "popularity": 88},
    {"name": "Wallace", "popularity": 89},
    {"name": "Kelly", "popularity": 90},
    {"name": "Reynolds", "popularity": 91},
    {"name": "Crawford", "popularity": 92},
    {"name": "Webb", "popularity": 93},
    {"name": "Alexander", "popularity": 94},
    {"name": "Woods", "popularity": 95},
    {"name": "Butler", "popularity": 96},
    {"name": "Graham", "popularity": 97},
    {"name": "Porter", "popularity": 98},
    {"name": "Hayes", "popularity": 99},
    {"name": "Black", "popularity": 100}
]

parent1 = "XY"
parent2 = "XX"

def generate_child_name(parent1, parent2):
    child_chromosomes = random.choice(parent1) + random.choice(parent2)
    if child_chromosomes == "XX":
        filtered_names = [name for name in firstnames if name["sex"] == "Feminine"]
    else:
        filtered_names = [name for name in firstnames if name["sex"] == "Masculine"]
    total_weight = sum(name["popularity"] for name in filtered_names)
    random_choice = random.uniform(0, total_weight)
    cumulative_weight = 0
    for name in filtered_names:
        cumulative_weight += name["popularity"]
        if random_choice <= cumulative_weight:
            return name["name"]
    total_lastname_weight = sum(lastname["popularity"] for lastname in lastnames)
    random_lastname_choice = random.uniform(0, total_lastname_weight)
    cumulative_lastname_weight = 0
    for lastname in lastnames:
        cumulative_lastname_weight += lastname["popularity"]
        if random_lastname_choice <= cumulative_lastname_weight:
            return f"{name['name']} {lastname['name']}"
        
def traderitems():
    global tradershop, questitems
    trader_save_file = os.path.join(saves_folder, "trader.save")
    all_tables = [ammo, healing_and_magic, melee_weapons, armor_and_defense, ranged_weapons, cursed_and_blessed_items, traderspecificitems]
    if os.path.exists(trader_save_file):
        try:
            with open(trader_save_file, "r") as file:
                encoded_data = file.read()
                trader_data = json.loads(base64.b64decode(encoded_data).decode("utf-8"))
                last_refresh_time = trader_data.get("last_refresh_time")
                if last_refresh_time:
                    last_refresh_time = time.strptime(last_refresh_time, "%Y-%m-%d %H:%M:%S")
                    current_time = time.gmtime()
                    time_difference = time.mktime(current_time) - time.mktime(last_refresh_time)
                    if time_difference < 12 * 3600:
                        tradershop = trader_data.get("items", [])
                        questitems = trader_data.get("questitems", [])
                        return
                trader_data["items"] = []
                for _ in range(20):
                    selected_table = random.choice(all_tables)
                    item = get_random_item(selected_table)
                    trader_data["items"].append(item)
                tradershop = trader_data["items"]
                questitems = []
                for _ in range(5):
                    selected_table = random.choice(all_tables)
                    item = get_random_item(selected_table)
                    questitems.append(item)
                trader_data["questitems"] = questitems
                trader_data["last_refresh_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                encoded_data = base64.b64encode(json.dumps(trader_data).encode("utf-8")).decode("utf-8")
                with open(trader_save_file, "w") as file:
                    file.write(encoded_data)
                print("Items have been refreshed since last time you've visited!")
                return
        except Exception as e:
            print(f"Error reading trader save file: {e}")
    else:
        try:
            items = []
            for _ in range(20):
                selected_table = random.choice(all_tables)
                item = get_random_item(selected_table)
                items.append(item)
            questitems = []
            for _ in range(5):
                selected_table = random.choice(all_tables)
                item = get_random_item(selected_table)
                questitems.append(item)
            trader_data = {
                "last_refresh_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                "items": items,
                "questitems": questitems
            }
            tradershop = items
            encoded_data = base64.b64encode(json.dumps(trader_data).encode("utf-8")).decode("utf-8")
            with open(trader_save_file, "w") as file:
                file.write(encoded_data)
            print("Trader save file created.")
        except Exception as e:
            print(f"Error creating trader save file: {e}")

def get_random_item(table):
    rarity_weights = {
        "common": 60,
        "uncommon": 25,
        "rare": 10,
        "legendary": 4,
        "mythic": 1
    }

    total_weight = sum(rarity_weights[item["rarity"].lower()] for item in table)
    random_weight = random.randint(1, total_weight)
    cumulative_weight = 0

    for item in table:
        cumulative_weight += rarity_weights[item["rarity"].lower()]
        if random_weight <= cumulative_weight:
            quantity = random.randint(item["minrand"], item["maxrand"])
            item_copy = item.copy()
            item_copy["quantity"] = quantity
            return item_copy

def main_logic(table):
    global freeslots, current_inventory, current_inventory_name
    item = get_random_item(table)
    print(f"Found: {item['name']}")
    print(item["description"])
    print("")
    print(f"Rarity: {item['rarity']}")
    print(f"Value: ${item['value']*item['quantity']}")
    print(f"Quantity: {item['quantity']}")
    print("")
    print(f"You have {freeslots} free slots in your inventory.")
    print(f"This item takes up {item['inventoryslots']} slots per unit.")
    print(f"Total slots required: {item['inventoryslots'] * item['quantity']}")
    print("")
    choice = input("Do you want to pick it up? (y/n): ").strip().lower()
    if choice == "y":
        total_slots_required = item["inventoryslots"] * item["quantity"]
        if freeslots >= total_slots_required:
            print(f"You picked up {item['quantity']}x {item['name']}!")
            freeslots -= total_slots_required
            if freeslots < 0:
                freeslots = abs(freeslots)
            current_inventory.append(item)
            if current_inventory_name:
                save_inventory_to_file(current_inventory, current_inventory_name)
        else:
            print("Not enough free slots in your inventory.")
            print("Would you like to drop an item to make space? (y/n): ", end="")
            drop_choice = input().strip().lower()
            if drop_choice == "y":
                if current_inventory:
                    print("Select an item to drop:")
                    for i, inv_item in enumerate(current_inventory, start=1):
                        print(f"[{i}] {inv_item['name']} (Quantity: {inv_item['quantity']}, Slots: {inv_item['inventoryslots']})")
                    item_choice = get_user_choice(len(current_inventory))
                    selected_item = current_inventory[item_choice - 1]
                    print(f"How many '{selected_item['name']}' would you like to drop? (1-{selected_item['quantity']}):")
                    quantity_to_drop = get_user_choice(selected_item['quantity'])
                    freed_slots = selected_item["inventoryslots"] * quantity_to_drop
                    selected_item["quantity"] -= quantity_to_drop
                    freeslots += freed_slots
                    if freeslots < 0:
                        freeslots = abs(freeslots)
                    if selected_item["quantity"] == 0:
                        current_inventory.pop(item_choice - 1)
                    print(f"Dropped {quantity_to_drop}x '{selected_item['name']}' and freed {freed_slots} slots.")
                    if freeslots >= total_slots_required:
                        print(f"You picked up {item['quantity']}x {item['name']}!")
                        freeslots -= total_slots_required
                        if freeslots < 0:
                            freeslots = abs(freeslots)
                        current_inventory.append(item)
                        if current_inventory_name:
                            while freeslots < total_slots_required:
                                print("Still not enough free slots after dropping items.")
                                print("Would you like to drop another item? (y/n): ", end="")
                                drop_choice = input().strip().lower()
                                if drop_choice == "y":
                                    if current_inventory:
                                        print("Select another item to drop:")
                                        for i, inv_item in enumerate(current_inventory, start=1):
                                            print(f"[{i}] {inv_item['name']} (Quantity: {inv_item['quantity']}, Slots: {inv_item['inventoryslots']})")
                                        item_choice = get_user_choice(len(current_inventory))
                                        selected_item = current_inventory[item_choice - 1]
                                        print(f"How many '{selected_item['name']}' would you like to drop? (1-{selected_item['quantity']}):")
                                        quantity_to_drop = get_user_choice(selected_item['quantity'])
                                        freed_slots = selected_item["inventoryslots"] * quantity_to_drop
                                        selected_item["quantity"] -= quantity_to_drop
                                        freeslots += freed_slots
                                        if freeslots < 0:
                                            freeslots = abs(freeslots)
                                        if selected_item["quantity"] == 0:
                                            current_inventory.pop(item_choice - 1)
                                        print(f"Dropped {quantity_to_drop}x '{selected_item['name']}' and freed {freed_slots} slots.")
                                    else:
                                        print("Your inventory is empty. Nothing to drop.")
                                        break
                                else:
                                    print(f"You chose not to pick up {item['name']}.")
                                    return
                            print(f"You picked up {item['quantity']}x {item['name']}!")
                            freeslots -= total_slots_required
                            if freeslots < 0:
                                freeslots = abs(freeslots)
                            current_inventory.append(item)
                            if current_inventory_name:
                                save_inventory_to_file(current_inventory, current_inventory_name)
                else:
                    print("Your inventory is empty. Nothing to drop.")
            else:
                print(f"You chose not to pick up {item['name']}.")
    else:
        print(f"You chose not to pick up {item['name']}.")
    print("")
    input("Press any key to continue...")

def manage_inventory():
    global current_inventory, current_inventory_name, freeslots, storage, gold
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("Inventory Management")
        print(f"Current Inventory: {current_inventory_name or 'None'}")
        print("")
        options = ["Create New Inventory", "Save Current Inventory", "Load Inventory", "View Current Inventory", 
                   "Remove Item from Inventory", "Move Items to/from Storage", "Transfer Saves from Previous Versions", 
                   "Delete Saves", "Transfer Items to Other Players", "Equip Items", "Back to Main Menu"]
        print_menu(options)
        choice = get_user_choice(len(options))

        if choice == 1:
            current_inventory_name = input("Enter a name for the new inventory: ").strip() + ".save"
            current_inventory = []
            freeslots = 10
            storage = []
            gold = 0
            save_inventory_to_file(current_inventory, current_inventory_name)
            print(f"New inventory '{current_inventory_name}' created.")
        elif choice == 2:
            if current_inventory_name:
                save_inventory_to_file(current_inventory, current_inventory_name)
            else:
                print("No inventory loaded to save. Please load or create an inventory first.")
        elif choice == 3:
            os.system("cls" if os.name == "nt" else "clear")
            files = [f for f in os.listdir(saves_folder) if f.endswith(".save")]
            if not files:
                print("No saved inventories found.")
            else:
                files = [f for f in files if f not in ["previousinventory.save", "trader.save", "transfers.save"]]
                if not files:
                    print("No saved inventories found.")
                else:
                    print("Available Inventories:")
                    print_menu(files)
                    file_choice = get_user_choice(len(files))
                    selected_file = files[file_choice - 1]
                    try:
                        file_path = os.path.join(saves_folder, selected_file)
                        with open(file_path, "r") as file:
                            encoded_data = file.read()
                            data_loaded = json.loads(base64.b64decode(encoded_data).decode("utf-8"))
                            save_version = data_loaded.get("version", None)
                            if save_version in incompatible_saves:
                                print(f"Save file '{selected_file}' is marked as incompatible with the current version.")
                                input("Press any key to continue...")
                                continue
                    except Exception as e:
                        print(f"Error checking save file compatibility: {e}")
                        input("Press any key to continue...")
                        continue
                    current_inventory_name = selected_file
                    current_inventory = load_inventory_from_file(current_inventory_name) or []
                    if not current_inventory_name:
                        print("No inventory loaded! Please load or create an inventory first.")
                        input("Press any key to continue...")
                        continue
                    print(f"Loaded inventory '{current_inventory_name}'.")
            try:
                os.makedirs(saves_folder, exist_ok=True)
                with open(previous_inventory_file, "w") as file:
                    encoded_name = base64.b64encode(current_inventory_name.encode("utf-8")).decode("utf-8")
                    file.write(encoded_name)
            except Exception as e:
                print(f"Error saving previous inventory: {e}")
        elif choice == 4:
            if not current_inventory_name:
                print("No inventory loaded! Please load or create an inventory first.")
                input("Press any key to continue...")
                continue
            if current_inventory:
                print("Current Inventory Items:")
                for item in current_inventory:
                    print(f"- {item['name']} (Rarity: {item['rarity']}, Value: ${item['value']*item['quantity']}, Quantity: {item['quantity']}, Slots: {item['inventoryslots']})")
                print("")
                print("Current Storage Items:")
                for item in storage:
                    print(f"- {item['name']} (Rarity: {item['rarity']}, Value: ${item['value']*item['quantity']}, Quantity: {item['quantity']}, Slots: {item['inventoryslots']})")
                print("")
                print(f"Free Slots: {freeslots}")
                print("Gold: $" + str(gold))
            else:
                print("Your inventory is empty.")
                print("")
                if storage:
                    print("Current Storage Items:")
                    for item in storage:
                        print(f"- {item['name']} (Rarity: {item['rarity']}, Value: ${item['value']*item['quantity']}, Quantity: {item['quantity']}, Slots: {item['inventoryslots']})")
                else:
                    print("Your storage is empty.")
                print("")
                print(f"Free Slots: {freeslots}")
        elif choice == 5:
            if not current_inventory_name:
                print("No inventory loaded! Please load or create an inventory first.")
                input("Press any key to continue...")
                continue
            os.system("cls" if os.name == "nt" else "clear")
            if current_inventory:
                print("Select an item to remove:")
                for i, item in enumerate(current_inventory, start=1):
                    print(f"[{i}] {item['name']} (Rarity: {item['rarity']}, Value: ${item['value']}, Quantity: {item['quantity']})")
                item_choice = get_user_choice(len(current_inventory))
                removed_item = current_inventory[item_choice - 1]
                print(f"How many '{removed_item['name']}' would you like to remove? (1-{removed_item['quantity']}):")
                quantity_to_remove = get_user_choice(removed_item['quantity'])
                removed_item["quantity"] -= quantity_to_remove
                freeslots += removed_item["inventoryslots"] * quantity_to_remove
                if freeslots < 0:
                    freeslots = abs(freeslots)
                if removed_item["quantity"] == 0:
                    current_inventory.pop(item_choice - 1)
                    print(f"Removed all of '{removed_item['name']}' from inventory.")
                else:
                    print(f"Removed {quantity_to_remove}x '{removed_item['name']}' from inventory.")
                if current_inventory_name:
                    save_inventory_to_file(current_inventory, current_inventory_name)
            else:
                print("Your inventory is empty. Nothing to remove.")
        elif choice == 6:
            if not current_inventory_name:
                print("No inventory loaded! Please load or create an inventory first.")
                input("Press any key to continue...")
                continue
            os.system("cls" if os.name == "nt" else "clear")
            print("Storage Management")
            print("")
            storage_options = ["Move Items to Storage", "Move Items from Storage", "Back"]
            print_menu(storage_options)
            storage_choice = get_user_choice(len(storage_options))

            if storage_choice == 1:
                if current_inventory:
                    print("Select an item to move to storage:")
                    for i, item in enumerate(current_inventory, start=1):
                        print(f"[{i}] {item['name']} (Quantity: {item['quantity']}, Slots: {item['inventoryslots']})")
                    item_choice = get_user_choice(len(current_inventory))
                    selected_item = current_inventory[item_choice - 1]
                    print(f"How many '{selected_item['name']}' would you like to move to storage? (1-{selected_item['quantity']}):")
                    quantity_to_move = get_user_choice(selected_item['quantity'])
                    selected_item["quantity"] -= quantity_to_move
                    freeslots += selected_item["inventoryslots"] * quantity_to_move
                    if freeslots < 0:
                        freeslots = abs(freeslots)
                    existing_storage_item = next((item for item in storage if item["name"] == selected_item["name"]), None)
                    if existing_storage_item:
                        existing_storage_item["quantity"] += quantity_to_move
                    else:
                        storage_item = selected_item.copy()
                        storage_item["quantity"] = quantity_to_move
                        storage.append(storage_item)

                    if selected_item["quantity"] == 0:
                        current_inventory.pop(item_choice - 1)
                    print(f"Moved {quantity_to_move}x '{selected_item['name']}' to storage.")
                    if current_inventory_name:
                        save_inventory_to_file(current_inventory, current_inventory_name)
                else:
                    print("Your inventory is empty. Nothing to move to storage.")
            elif storage_choice == 2:
                if storage:
                    print("Select an item to move from storage:")
                    for i, item in enumerate(storage, start=1):
                        print(f"[{i}] {item['name']} (Quantity: {item['quantity']}, Slots: {item['inventoryslots']})")
                    item_choice = get_user_choice(len(storage))
                    selected_item = storage[item_choice - 1]
                    print(f"How many '{selected_item['name']}' would you like to move to inventory? (1-{selected_item['quantity']}):")
                    quantity_to_move = get_user_choice(selected_item['quantity'])
                    total_slots_required = selected_item["inventoryslots"] * quantity_to_move
                    if freeslots >= total_slots_required:
                        selected_item["quantity"] -= quantity_to_move
                        freeslots -= total_slots_required
                        if freeslots < 0:
                            freeslots = abs(freeslots)
                        existing_inventory_item = next((item for item in current_inventory if item["name"] == selected_item["name"]), None)
                        if existing_inventory_item:
                            existing_inventory_item["quantity"] += quantity_to_move
                        else:
                            inventory_item = selected_item.copy()
                            inventory_item["quantity"] = quantity_to_move
                            current_inventory.append(inventory_item)

                        if selected_item["quantity"] == 0:
                            storage.pop(item_choice - 1)
                        print(f"Moved {quantity_to_move}x '{selected_item['name']}' to inventory.")
                        if current_inventory_name:
                            save_inventory_to_file(current_inventory, current_inventory_name)
                    else:
                        print("Not enough free slots in your inventory.")
                else:
                    print("Storage is empty. Nothing to move to inventory.")
        elif choice == 7:
            if os.name == "posix":
                print("Transfer Saves from Previous Versions")
                print("Please paste the directory location of the previous version's saves folder:")
                old_saves_folder = input("Directory: ").strip()

                if not os.path.isdir(old_saves_folder):
                    print("Invalid directory. Please ensure the path is correct.")
                    input("Press any key to continue...")
                    return

                old_save_files = [f for f in os.listdir(old_saves_folder) if f.endswith(".save")]
                if not old_save_files:
                    print("No save files found in the specified directory.")
                    input("Press any key to continue...")
                    return

                print(f"Found {len(old_save_files)} save file(s) in the specified directory.")
                for save_file in old_save_files:
                    old_file_path = os.path.join(old_saves_folder, save_file)
                    try:
                        with open(old_file_path, "r") as file:
                            encoded_data = file.read()
                            data_loaded = json.loads(base64.b64decode(encoded_data).decode("utf-8"))
                            save_version = data_loaded.get("version", None)
                            if save_version is None:
                                print(f"Skipping save file '{save_file}' as it does not contain a version number.")
                                continue
                            if save_version != version:
                                print(f"Warning: Save file '{save_file}' is from version {save_version}, which does not match the current version ({version}).")
                                if save_version in incompatible_saves:
                                    print(f"Skipping save file '{save_file}' as it is marked as incompatible with the current version.")
                                    continue
                            new_file_path = os.path.join(saves_folder, save_file)
                            if os.path.exists(new_file_path):
                                print(f"Save file '{save_file}' already exists in the current saves folder. Skipping.")
                            else:
                                with open(new_file_path, "w") as new_file:
                                    new_file.write(encoded_data)
                                print(f"Transferred save file '{save_file}' to the current saves folder.")
                    except Exception as e:
                        print(f"Error transferring save file '{save_file}': {e}")
                input("Press any key to continue...")
            elif os.name == "nt":
                print("Transfer Saves from Previous Versions")
                print("Please paste the directory location of the previous version's saves folder:")
                old_saves_folder = input("Directory: ").strip()

                if not os.path.isdir(old_saves_folder):
                    print("Invalid directory. Please ensure the path is correct.")
                    return

                old_save_files = [f for f in os.listdir(old_saves_folder) if f.endswith(".save")]
                if not old_save_files:
                    print("No save files found in the specified directory.")
                    return

                print(f"Found {len(old_save_files)} save file(s) in the specified directory.")
                for save_file in old_save_files:
                    old_file_path = os.path.join(old_saves_folder, save_file)
                    try:
                        with open(old_file_path, "r") as file:
                            encoded_data = file.read()
                            data_loaded = json.loads(base64.b64decode(encoded_data).decode("utf-8"))
                            save_version = data_loaded.get("version", None)
                            if save_version is None:
                                print(f"Skipping save file '{save_file}' as it does not contain a version number.")
                                continue
                            if save_version != version:
                                print(f"Warning: Save file '{save_file}' is from version {save_version}, which does not match the current version ({version}).")
                                if save_version in incompatible_saves:
                                    print(f"Skipping save file '{save_file}' as it is marked as incompatible with the current version.")
                                    continue
                            new_file_path = os.path.join(saves_folder, save_file)
                            if os.path.exists(new_file_path):
                                print(f"Save file '{save_file}' already exists in the current saves folder. Skipping.")
                            else:
                                with open(new_file_path, "w") as new_file:
                                    new_file.write(encoded_data)
                                print(f"Transferred save file '{save_file}' to the current saves folder.")
                    except Exception as e:
                        print(f"Error transferring save file '{save_file}': {e}")
            else:
                print("Unsupported operating system. Please transfer save files manually.")
                input("Press any key to continue...")
        elif choice == 8:
            os.system("cls" if os.name == "nt" else "clear")
            print("Delete Save Files")
            files = [f for f in os.listdir(saves_folder) if f.endswith(".save") and f not in ["previousinventory.save", "trader.save", "transfers.save"]]
            if not files:
                print("No saved inventories found.")
            else:
                print("Available Inventories:")
                print_menu(files)
                file_choice = get_user_choice(len(files))
                file_to_delete = files[file_choice - 1]
                confirm = input(f"Are you sure you want to delete '{file_to_delete}'? (y/n): ").strip().lower()
                if confirm == "y":
                    os.remove(os.path.join(saves_folder, file_to_delete))
                    print(f"Deleted save file '{file_to_delete}'.")
                else:
                    print("Deletion canceled.")
        elif choice == 9:
            transfer_folder = "./transfer"
            transfers_save_file = os.path.join(saves_folder, "transfers.save")
            def load_transfer_ids():
                if not os.path.exists(transfers_save_file):
                    return []
                try:
                    with open(transfers_save_file, "r") as f:
                        encoded = f.read()
                        return json.loads(base64.b64decode(encoded).decode("utf-8"))
                except Exception:
                    return []
            def save_transfer_ids(ids):
                try:
                    encoded = base64.b64encode(json.dumps(ids).encode("utf-8")).decode("utf-8")
                    with open(transfers_save_file, "w") as f:
                        f.write(encoded)
                except Exception as e:
                    print(f"Error saving transfer ids: {e}")
            def transfer_item_out():
                global current_inventory, freeslots
                if not current_inventory:
                    print("Your inventory is empty. Nothing to transfer.")
                    return
                os.makedirs(transfer_folder, exist_ok=True)
                print("Select an item to transfer:")
                for i, item in enumerate(current_inventory, start=1):
                    print(f"[{i}] {item['name']} (Quantity: {item['quantity']}, Slots: {item['inventoryslots']})")
                item_choice = get_user_choice(len(current_inventory))
                selected_item = current_inventory[item_choice - 1]
                print(f"How many '{selected_item['name']}' would you like to transfer? (1-{selected_item['quantity']}):")
                quantity_to_transfer = get_user_choice(selected_item['quantity'])
                transfer_id = str(uuid.uuid4())
                item_data = selected_item.copy()
                item_data["quantity"] = quantity_to_transfer
                item_data["transfer_id"] = transfer_id
                item_data["transfer_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                item_data["transfer_type"] = "item"
                safe_name = "".join(c for c in item_data["name"] if c.isalnum() or c in (' ', '_', '-')).rstrip()
                transfer_file = os.path.join(transfer_folder, f"{safe_name}.transfer")
                encoded_item = base64.b64encode(json.dumps(item_data).encode("utf-8")).decode("utf-8")
                with open(transfer_file, "w") as f:
                    f.write(encoded_item)
                selected_item["quantity"] -= quantity_to_transfer
                freeslots += selected_item["inventoryslots"] * quantity_to_transfer
                if selected_item["quantity"] == 0:
                    current_inventory.pop(item_choice - 1)
                print(f"Transferred {quantity_to_transfer}x '{item_data['name']}' to {transfer_file}.")
            def transfer_gold_out():
                global gold
                if gold <= 0:
                    print("You have no gold to transfer.")
                    return
                os.makedirs(transfer_folder, exist_ok=True)
                print(f"You have ${gold} gold.")
                print("How much gold would you like to transfer? (1-{})".format(gold))
                amount = get_user_choice(gold)
                transfer_id = str(uuid.uuid4())
                gold_data = {
                    "transfer_type": "gold",
                    "amount": amount,
                    "transfer_id": transfer_id,
                    "transfer_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                }
                transfer_file = os.path.join(transfer_folder, f"gold_{transfer_id}.transfer")
                encoded_gold = base64.b64encode(json.dumps(gold_data).encode("utf-8")).decode("utf-8")
                with open(transfer_file, "w") as f:
                    f.write(encoded_gold)
                gold -= amount
                print(f"Transferred ${amount} gold to {transfer_file}.")
            def transfer_item_in():
                global current_inventory, freeslots, gold
                os.makedirs(transfer_folder, exist_ok=True)
                files = [f for f in os.listdir(transfer_folder) if f.endswith(".transfer")]
                if not files:
                    print("No transfer files found.")
                    return
                print("Available transfer files:")
                print_menu(files)
                file_choice = get_user_choice(len(files))
                transfer_file = os.path.join(transfer_folder, files[file_choice - 1])
                try:
                    with open(transfer_file, "r") as f:
                        encoded_item = f.read()
                        item_data = json.loads(base64.b64decode(encoded_item).decode("utf-8"))
                    transfer_id = item_data.get("transfer_id")
                    ids = load_transfer_ids()
                    if transfer_id in ids:
                        print("This transfer has already been imported. Cannot import again.")
                        os.remove(transfer_file)
                        return
                    transfer_time_str = item_data.get("transfer_time")
                    if transfer_time_str:
                        try:
                            import calendar
                            transfer_time = time.strptime(transfer_time_str, "%Y-%m-%d %H:%M:%S")
                            now = time.gmtime()
                            seconds_passed = calendar.timegm(now) - calendar.timegm(transfer_time)
                            if seconds_passed > 30 * 60:
                                print("This transfer file is older than 30 minutes and cannot be imported.")
                                os.remove(transfer_file)
                                return
                        except Exception as e:
                            print(f"Error parsing transfer time: {e}")
                            os.remove(transfer_file)
                            return
                    else:
                        print("No transfer time found in file.")
                        os.remove(transfer_file)
                        return
                    if item_data.get("transfer_type") == "gold":
                        amount = item_data.get("amount", 0)
                        if amount > 0:
                            gold += amount
                            print(f"Imported ${amount} gold into your account.")
                        else:
                            print("Invalid gold amount in transfer file.")
                        ids.append(transfer_id)
                        save_transfer_ids(ids)
                        os.remove(transfer_file)
                    else:
                        total_slots = item_data["inventoryslots"] * item_data["quantity"]
                        if freeslots < total_slots:
                            print("Not enough free slots in your inventory to import this item.")
                            os.remove(transfer_file)
                            return
                        current_inventory.append(item_data)
                        freeslots -= total_slots
                        print(f"Imported {item_data['quantity']}x '{item_data['name']}' into your inventory.")
                        ids.append(transfer_id)
                        save_transfer_ids(ids)
                        os.remove(transfer_file)
                except Exception as e:
                    print(f"Error importing transfer file: {e}")
                    try:
                        os.remove(transfer_file)
                    except Exception:
                        pass
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                print("Item Transfer")
                options = ["Transfer Item", "Transfer Gold", "Import Item", "Back"]
                print_menu(options)
                choice = get_user_choice(len(options))
                if choice == 1:
                    transfer_item_out()
                elif choice == 2:
                    transfer_gold_out()
                elif choice == 3:
                    transfer_item_in()
                elif choice == 4:
                    break
                if current_inventory_name:
                    save_inventory_to_file(current_inventory, current_inventory_name)
                input("Press any key to continue...")
        elif choice == 10:
            global equipped_items
            if equipped_items is None:
                equipped_items = {
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
                }
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                slots = ["torso", "head", "back", "shoulder", "waist", "face", "undertorso", "shoes", "special", "wrist", "exit"]
                print("Equipable Slots:")
                for idx, slot in enumerate(slots, 1):
                    if slot == "exit":
                        print(f"[{idx}] Exit")
                        continue
                    equipped = equipped_items.get(slot)
                    rating = ""
                    if equipped and isinstance(equipped, dict):
                        rating = equipped.get("armorrating", "")
                    print(f"[{idx}] {slot.capitalize()} (Equipped: {equipped['name'] if equipped else 'None'}"
                          f"{', Armor: ' + str(rating) if rating else ''})")
                choice = get_user_choice(len(slots))
                slot_name = slots[choice - 1]
                if slot_name == "exit":
                    break
                current_equipped = equipped_items.get(slot_name)
                slot_items = [item for item in current_inventory if item.get("slot") == slot_name]
                print(f"\n{slot_name.capitalize()} Items in Inventory:")
                if not slot_items:
                    print(f"No {slot_name} items in inventory.")
                else:
                    for i, item in enumerate(slot_items, 1):
                        ar = item.get("armorrating", "")
                        print(f"[{i}] {item['name']} (Rarity: {item['rarity']}, Slots: {item['inventoryslots']}, "
                              f"Added Slots: {item.get('addedslots', 0)}, Armor: {ar if ar else 'N/A'}, Quantity: {item['quantity']})")
                if current_equipped:
                    print(f"\nCurrently equipped: {current_equipped['name']}")
                    if current_equipped.get("armorrating"):
                        print(f"Armor Rating: {current_equipped['armorrating']}")
                    if current_equipped.get("curseofbinding"):
                        print("This item has a curse of binding and cannot be removed.")
                    else:
                        print("Would you like to dequip the current item? (y/n): ", end="")
                        deq = input().strip().lower()
                        if deq == "y":
                            slots_to_remove = current_equipped.get("addedslots", 0)
                            found = False
                            for inv_item in current_inventory:
                                if inv_item["name"] == current_equipped["name"]:
                                    inv_item["quantity"] += 1
                                    found = True
                                    break
                            if not found:
                                item_copy = current_equipped.copy()
                                item_copy["quantity"] = 1
                                current_inventory.append(item_copy)
                            if slots_to_remove > 0:
                                if freeslots - slots_to_remove < 0:
                                    print("Cannot dequip: not enough free slots to remove this item.")
                                else:
                                    freeslots -= slots_to_remove
                                    equipped_items[slot_name] = None
                                    print(f"Dequipped {current_equipped['name']}. Removed {slots_to_remove} slots.")
                            else:
                                equipped_items[slot_name] = None
                                print(f"Dequipped {current_equipped['name']}.")
                            if current_inventory_name:
                                save_inventory_to_file(current_inventory, current_inventory_name)
                else:
                    if slot_items:
                        print(f"\nSelect an item to equip (or 0 to cancel):")
                        for i, item in enumerate(slot_items, 1):
                            ar = item.get("armorrating", "")
                            print(f"[{i}] {item['name']} (Added Slots: {item.get('addedslots', 0)}, Armor: {ar if ar else 'N/A'}, Quantity: {item['quantity']})")
                        print("[0] Cancel")
                        sel = get_user_choice(len(slot_items)+1)
                        if sel == 0 or sel == len(slot_items)+1:
                            continue
                        item = slot_items[sel-1]
                        if item.get("curseofbinding"):
                            print("This item has a curse of binding and cannot be removed once equipped.")
                        else:
                            slots_to_add = item.get("addedslots", 0)
                            item["quantity"] -= 1
                            if item["quantity"] == 0:
                                current_inventory.remove(item)
                            freeslots += slots_to_add
                            equipped_items[slot_name] = item.copy()
                            equipped_items[slot_name]["quantity"] = 1
                            print(f"Equipped {item['name']}. Added {slots_to_add} slots.")
                            if current_inventory_name:
                                save_inventory_to_file(current_inventory, current_inventory_name)
                input("Press any key to continue...")
        elif choice == 11:
            break
        input("Press any key to continue...")

def trader():
    global gold, current_inventory, current_inventory_name, freeslots, tradershop
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        quotes = [
            "Hey everybody! It's me! The Merchant!",
            "Hee hee... Welcome, travellers!",
            "Lamp oil? Rope? Bombs? You want it? It's yours my friend! As long as you have enough gold!",
            "I used to be an adventurer like you, then I took an arrow to the knee…",
            "Some may call this junk. Me, I call them treasures!",
            "Hurry up and buy!",
            "What are ya buyin’?",
            "What would you like to buy?",
            "Cheesed to meet you!",
            "No, I don’t accept haggling, this is a legitimate business I'm running.",
            "I don’t make snake oil, it's a common misconception.",
            "Everything was totally obtained legitimately… So what do you want?",
            "Y’know, I keep hearing about this strange crazy lady going around… I’d look out if I were you.",
            "Everything's for sale, my friends! Everything… except for my crystal you can’t have that.",
            "Everything here is of utmost quality, I assure you!"
        ]
        print("“" + random.choice(quotes) + "”")
        print("")
        print("Gold: $" + str(gold))
        print("")
        traderitems()
        print("Please select an activity:")
        traderoptions = ["Buy Items", "Sell Items", "Quests", "Exit Trader"]
        print_menu(traderoptions)
        choice = get_user_choice(len(traderoptions))
        if choice == 1:
            os.system("cls" if os.name == "nt" else "clear")
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                print("Trader Shop:")
                if not tradershop:
                    print("No items available in the shop.")
                    input("Press any key to return...")
                    break
                for i, item in enumerate(tradershop, start=1):
                    print(f"[{i}] {item['name']} (Rarity: {item['rarity']}, Value: ${item['value']*2}, Quantity: {item['quantity']})")
                print(f"[{len(tradershop)+1}] Back")
                choice = get_user_choice(len(tradershop)+1)
                if choice == len(tradershop)+1:
                    break
                selected_item = tradershop[choice-1]
                os.system("cls" if os.name == "nt" else "clear")
                print(f"{selected_item['name']}")
                if "id" in selected_item:
                    desc_entry = next((d for d in traderitemdescriptions if d["id"] == selected_item["id"]), None)
                    if desc_entry:
                        print(f'"{desc_entry["traderdesc"]}"')
                    print(selected_item["description"])
                else:
                    print(f'"{selected_item["description"]}"')
                print(f"Rarity: {selected_item['rarity']}")
                print(f"Value: ${selected_item['value']*2}")
                print(f"Available Quantity: {selected_item['quantity']}")
                print(f"Inventory Slots per unit: {selected_item['inventoryslots']}")
                print("")
                print(f"You have {freeslots} free slots in your inventory.")
                print(f"Gold: ${gold}")
                print("")
                buy = input("Would you like to buy this item? (y/n): ").strip().lower()
                if buy != "y":
                    continue
                max_qty = selected_item['quantity']
                print(f"How many would you like to buy? (1-{max_qty}):")
                qty = get_user_choice(max_qty)
                total_price = selected_item['value'] * 2 * qty
                total_slots = selected_item['inventoryslots'] * qty
                if gold < total_price:
                    print("You do not have enough gold.")
                    input("Press any key to continue...")
                    continue
                if freeslots > 0:
                    freeslots = abs(freeslots)
                if freeslots < total_slots:
                    print("You do not have enough free slots.")
                    input("Press any key to continue...")
                    continue
                gold -= total_price
                freeslots -= total_slots
                if freeslots < 0:
                    freeslots = abs(freeslots)
                item_copy = selected_item.copy()
                item_copy["quantity"] = qty
                inv_item = next((i for i in current_inventory if i["name"] == item_copy["name"]), None)
                if inv_item:
                    inv_item["quantity"] += qty
                else:
                    current_inventory.append(item_copy)
                selected_item["quantity"] -= qty
                if selected_item["quantity"] == 0:
                    tradershop.pop(choice-1)
                print(f"Bought {qty}x {item_copy['name']} for ${total_price}.")
                if current_inventory_name:
                    save_inventory_to_file(current_inventory, current_inventory_name)
                trader_save_file = os.path.join(saves_folder, "trader.save")
                try:
                    with open(trader_save_file, "r") as file:
                        encoded_data = file.read()
                        trader_data = json.loads(base64.b64decode(encoded_data).decode("utf-8"))
                    trader_data["items"] = tradershop
                    encoded_data = base64.b64encode(json.dumps(trader_data).encode("utf-8")).decode("utf-8")
                    with open(trader_save_file, "w") as file:
                        file.write(encoded_data)
                except Exception as e:
                    print(f"Error updating trader save file: {e}")
                input("Press any key to continue...")
        elif choice == 2:
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                if not current_inventory:
                    print("You have no items to sell.")
                    input("Press any key to continue...")
                    break
                print("Your Inventory:")
                for i, item in enumerate(current_inventory, start=1):
                    print(f"[{i}] {item['name']} (Rarity: {item['rarity']}, Value: ${item['value']} ea, Quantity: {item['quantity']}, Sell Value: ${item['value']//2} ea)")
                print(f"[{len(current_inventory)+1}] Back")
                choice = get_user_choice(len(current_inventory)+1)
                if choice == len(current_inventory)+1:
                    break
                selected_item = current_inventory[choice-1]
                print(f"How many '{selected_item['name']}' would you like to sell? (1-{selected_item['quantity']}):")
                qty = get_user_choice(selected_item['quantity'])
                sell_value = (selected_item['value'] // 2) * qty
                gold += sell_value
                freeslots += selected_item['inventoryslots'] * qty
                if freeslots < 0:
                    freeslots = abs(freeslots)
                selected_item['quantity'] -= qty
                print(f"Sold {qty}x {selected_item['name']} for ${sell_value}.")
                trader_item = next((t_item for t_item in tradershop if t_item["name"] == selected_item["name"]), None)
                if trader_item:
                    trader_item["quantity"] += qty
                else:
                    item_copy = selected_item.copy()
                    item_copy["quantity"] = qty
                    tradershop.append(item_copy)
                if selected_item['quantity'] == 0:
                    current_inventory.pop(choice-1)
                if current_inventory_name:
                    save_inventory_to_file(current_inventory, current_inventory_name)
                trader_save_file = os.path.join(saves_folder, "trader.save")
                try:
                    with open(trader_save_file, "r") as file:
                        encoded_data = file.read()
                        trader_data = json.loads(base64.b64decode(encoded_data).decode("utf-8"))
                    trader_data["items"] = tradershop
                    encoded_data = base64.b64encode(json.dumps(trader_data).encode("utf-8")).decode("utf-8")
                    with open(trader_save_file, "w") as file:
                        file.write(encoded_data)
                except Exception as e:
                    print(f"Error updating trader save file: {e}")
                input("Press any key to continue...")
        elif choice == 3:
            os.system("cls" if os.name == "nt" else "clear")
            quotes = [
                "Hey my loyal sub- I mean customer! I have some jobs for you!",
                "There’s some things I want… mind going out and getting them for me? I can make it worth your while.",
                "If you’re looking for some work… I got a few requests for you.",
                "Got some jobs for you, if you’re interested!",
                "Hey! You! Do this thing for me!",
                "You wouldn’t mind doing this for me, riiiight?"
            ]
            print("“" + random.choice(quotes) + "”")
            print("")
            if not questitems:
                print("No quests available at the moment.")
            else:
                print("Quest Items:")
                for i, item in enumerate(questitems, start=1):
                    print(f"[{i}] {item['name']} (Rarity: {item['rarity']}, Reward: ${min(item['value']*5, 10000)})")
                print(f"[{len(questitems)+1}] Back")
                quest_choice = get_user_choice(len(questitems)+1)
                if quest_choice == len(questitems)+1:
                    pass
                else:
                    quest_item = questitems[quest_choice-1]
                    inv_item = next((i for i in current_inventory if i["name"] == quest_item["name"]), None)
                    if inv_item:
                        reward = min(quest_item["value"]*5, 10000)
                        print(f"You turned in '{quest_item['name']}' and received ${reward}!")
                        gold += reward
                        if inv_item["quantity"] > 1:
                            inv_item["quantity"] -= 1
                        else:
                            current_inventory.remove(inv_item)
                        questitems.pop(quest_choice-1)
                        if current_inventory_name:
                            save_inventory_to_file(current_inventory, current_inventory_name)
                        input("Press any key to continue...")
                    else:
                        print(f"You do not have '{quest_item['name']}' in your inventory.")
                        print(f"If you find it, you can turn it in for ${min(quest_item['value']*5, 10000)} (Rarity: {quest_item['rarity']})")
                        input("Press any key to continue...")
        elif choice == 4:
            break

def bar():
    global gold
    os.system("cls" if os.name == "nt" else "clear")
    print("Gold: $" + str(gold))
    print("Please select an activity:")
    baroptions = ["Play Card Game", "Play Dice Game", "Exit the bar"]
    print_menu(baroptions)
    choice = get_user_choice(len(baroptions))
    if choice == 1:
        cardgames = ["Blackjack", "Poker", "High or Low", "Exit"]
        print_menu(cardgames)
        choice = get_user_choice(len(cardgames))
        if choice == 1:
            os.system("cls" if os.name == "nt" else "clear")
            bet = 0
            dealerbet = 0
            blackjackvalues = {
                "A-S": "Ace",
                "A-H": "Ace",
                "A-D": "Ace",
                "A-C": "Ace",
                "2-S": 2,
                "2-H": 2,
                "2-D": 2,
                "2-C": 2,
                "3-S": 3,
                "3-H": 3,
                "3-D": 3,
                "3-C": 3,
                "4-S": 4,
                "4-H": 4,
                "4-D": 4,
                "4-C": 4,
                "5-S": 5,
                "5-H": 5,
                "5-D": 5,
                "5-C": 5,
                "6-S": 6,
                "6-H": 6,
                "6-D": 6,
                "6-C": 6,
                "7-S": 7,
                "7-H": 7,
                "7-D": 7,
                "7-C": 7,
                "8-S": 8,
                "8-H": 8,
                "8-D": 8,
                "8-C": 8,
                "9-S": 9,
                "9-H": 9,
                "9-D": 9,
                "9-C": 9,
                "10-S": 10,
                "10-H": 10,
                "10-D": 10,
                "10-C": 10,
                "J-S": 10,
                "J-H": 10,
                "J-D": 10,
                "J-C": 10,
                "Q-S": 10,
                "Q-H": 10,
                "Q-D": 10,
                "Q-C": 10,
                "K-S": 10,
                "K-H": 10,
                "K-D": 10,
                "K-C": 10
            }
            print("First to 21 wins.")
            print("Aces are 1 or 11.")
            print("Jacks, Queens, and Kings are 10.")
            print("Joker is removed from the deck.")
            print("Dealer deals 2 cards to you, and 2 cards to their hand.")
            print("")
            print("You will be prompted to hit or stand.")
            print("Hitting will draw a card from the deck.")
            print("Standing will end your turn.")
            print("")
            print("After you stand, the dealer will draw cards until they reach 17.")
            print("If the dealer busts, you win.")
            print("If you bust, the dealer wins.")
            print("If you both bust or stand on the same value, it's a tie.")
            print("")
            print("Blackjack will pay twice your bet plus the dealer's bet.")
            print("If the dealer has blackjack, you do not have to pay twice the bet, you just lose your bet.")
            print("")
            print("If you win, you will receive your bet plus the dealer's bet.")
            print("If you lose, you will lose your bet.")
            print("")
            print("If you tie, both dealer and player will have their stake returned to them.")
            print("")
            print("Dealer will match up to $1000.")
            print("")
            print("You can also enter 'all' to bet all your gold.")
            print("You can enter 0 to play for fun.")
            print("")
            print("You have $" + str(gold) + " to bet.")
            print("")
            bet = input("Bet: ")
            if bet == "all":
                bet = gold
                gold = 0
                if bet > 1000:
                    print("Dealer will only match up to $1000.")
                    dealerbet = 1000
                else:
                    dealerbet = bet
            elif bet == "0":
                bet = 0
                dealerbet = 0
            elif bet < "0":
                print("You can't bet a negative amount.")
                input("Press any key to continue...")
                return
            else:
                try:
                    bet = int(bet)
                    if bet > gold:
                        print("You don't have enough gold to make that bet.")
                        return
                    elif bet > 1000:
                        print("Dealer will only match up to $1000.")
                        dealerbet = 1000
                        gold -= bet
                    else:
                        dealerbet = bet
                        gold -= bet
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    return
            os.system("cls" if os.name == "nt" else "clear")
            playingdeck = card_deck.copy()
            playingdeck.remove({"name": "Joker", "cardface": "🃏︎", "internalname": "Joker"})
            playerhand = []
            dealerhand = []
            playervalue = 0
            dealervalue = 0
            print("Dealer stands at 17.")
            print("Dealer is shuffling the deck...")
            for i in range(5):
                random.shuffle(playingdeck)
            time.sleep(random.uniform(0.5, 1.5))
            print("Dealer has shuffled the deck.")
            print("")
            for i in range(2):
                card = playingdeck.pop(0)
                playerhand.append(card)
                print(f"Player drew: {card['name']} {card['cardface']}")
                if card["internalname"] == "A-S" or card["internalname"] == "A-H" or card["internalname"] == "A-D" or card["internalname"] == "A-C":
                    print("Would you like to count this as 1 or 11?")
                    acevalue = input("1 or 11: ")
                    if acevalue == "1":
                        playervalue += 1
                    elif acevalue == "11":
                        playervalue += 11
                    else:
                        print("Invalid input. Please enter 1 or 11.")
                        return
                else:
                    playervalue += blackjackvalues[card["internalname"]]
            print("")
            for i in range(2):
                card = playingdeck.pop(0)
                dealerhand.append(card)
                if i == 0:
                    print(f"Dealer drew: {card['name']} {card['cardface']}")
                    if card["internalname"] in ["A-S", "A-H", "A-D", "A-C"]:
                        if dealervalue + 11 > 21:
                            dealervalue += 1
                        else:
                            dealervalue += 11
                    else:
                        dealervalue += blackjackvalues[card["internalname"]]
                else:
                    print("Dealer drew: [Hidden Card] 🂠")
                    hidden_card = card
                    if card["internalname"] in ["A-S", "A-H", "A-D", "A-C"]:
                        if dealervalue + 11 > 21:
                            hidden_card_value = 1
                        else:
                            hidden_card_value = 11
                    else:
                        hidden_card_value = blackjackvalues[card["internalname"]]
            print("")
            print("Your hand: ")
            for card in playerhand:
                print(f"{card['name']} {card['cardface']}")
            print("Dealer's hand: ")
            for card in dealerhand:
                print(f"{card['name']} {card['cardface']}")
            print("")
            print(f"Your hand value: {playervalue}")
            print(f"Dealer's hand value: {dealervalue}")
            print("")
            if playervalue == 21:
                print("Blackjack! Player win.")
                gold += bet + dealerbet * 2
                print(f"You won ${bet + dealerbet * 2}.")
                print(f"Your new balance is: ${gold}")
                print("")
                if current_inventory_name:
                    save_inventory_to_file(current_inventory, current_inventory_name)
                input("Press any key to continue...")
                return
            elif dealervalue == 21:
                print("Blackjack! Dealer win.")
                print("")
                if current_inventory_name:
                    save_inventory_to_file(current_inventory, current_inventory_name)
                input("Press any key to continue...")
                return
            else:
                while playervalue < 21:
                    print("Would you like to hit or stand?")
                    print("You have $" + str(bet) + " riding on this hand.")
                    print("1. Hit")
                    print("2. Stand")
                    choice = get_user_choice(2)
                    if choice == 1:
                        card = playingdeck.pop(0)
                        playerhand.append(card)
                        print(f"Player drew: {card['name']} {card['cardface']}")
                        if card["internalname"] == "A-S" or card["internalname"] == "A-H" or card["internalname"] == "A-D" or card["internalname"] == "A-C":
                            print("Would you like to count this as 1 or 11?")
                            acevalue = input("1 or 11: ")
                            if acevalue == "1":
                                playervalue += 1
                            elif acevalue == "11":
                                playervalue += 11
                            else:
                                print("Invalid input. Please enter 1 or 11.")
                                return
                        else:
                            playervalue += blackjackvalues[card["internalname"]]
                        print("")
                        print("Your hand: ")
                        for card in playerhand:
                            print(f"{card['name']} {card['cardface']}")
                        print("Dealer's hand: ")
                        for card in dealerhand:
                            print(f"{card['name']} {card['cardface']}")
                        print("")
                        print(f"Your hand value: {playervalue}")
                        print(f"Dealer's hand value: {dealervalue}")
                        print("")
                        if playervalue > 21:
                            print("Bust! Dealer wins.")
                            print("")
                            if current_inventory_name:
                                save_inventory_to_file(current_inventory, current_inventory_name)
                            input("Press any key to continue...")
                            return
                        elif playervalue == 21:
                            print("21! Player win.")
                            gold += bet + dealerbet
                            print(f"You won ${bet + dealerbet}.")
                            print(f"Your new balance is: ${gold}")
                            print("")
                            if current_inventory_name:
                                save_inventory_to_file(current_inventory, current_inventory_name)
                            input("Press any key to continue...")
                            return
                    if choice == 2:
                        print(f"Dealer's hidden card: {dealerhand[1]['name']} {dealerhand[1]['cardface']}")
                        dealervalue += hidden_card_value
                        print(f"Dealer's hand value: {dealervalue}")
                        print("")
                        if dealervalue < 17:
                            card = playingdeck.pop(0)
                            dealerhand.append(card)
                            print(f"Dealer drew: {card['name']} {card['cardface']}")
                            if card["internalname"] == "A-S" or card["internalname"] == "A-H" or card["internalname"] == "A-D" or card["internalname"] == "A-C":
                                if dealervalue + 11 > 21:
                                    dealervalue += 1
                                else:
                                    dealervalue += 11
                            else:
                                dealervalue += blackjackvalues[card["internalname"]]
                        else:
                            print("Dealer stands.")
                            print("")
                            if playervalue > dealervalue:
                                print("Player wins!")
                                gold += bet + dealerbet
                                print(f"You won ${bet + dealerbet}.")
                                print(f"Your new balance is: ${gold}")
                                print("")
                                if current_inventory_name:
                                    save_inventory_to_file(current_inventory, current_inventory_name)
                                input("Press any key to continue...")
                                return
                            elif playervalue < dealervalue:
                                print("Dealer wins!")
                                print("")
                                if current_inventory_name:
                                    save_inventory_to_file(current_inventory, current_inventory_name)
                                input("Press any key to continue...")
                                return
                            else:
                                gold += bet
                                print("Tie. Money returned.")
                                print("")
                                if current_inventory_name:
                                    save_inventory_to_file(current_inventory, current_inventory_name)
                                input("Press any key to continue...")
                                return
                        print("")
                        if dealervalue > 21:
                            print("Dealer bust! Player wins.")
                            gold += bet + dealerbet
                            print(f"You won ${bet + dealerbet}.")
                            print(f"Your new balance is: ${gold}")
                            print("")
                            if current_inventory_name:
                                save_inventory_to_file(current_inventory, current_inventory_name)
                            input("Press any key to continue...")
                            return
                        elif dealervalue == 21:
                            print("21! Dealer wins.")
                            print("")
                            if current_inventory_name:
                                save_inventory_to_file(current_inventory, current_inventory_name)
                            input("Press any key to continue...")
                            return
                        elif dealervalue >= 17:
                            print("Dealer stands.")
                            print("")
                            if playervalue > dealervalue:
                                print("Player wins!")
                                gold += bet + dealerbet
                                print(f"You won ${bet + dealerbet}.")
                                print(f"Your new balance is: ${gold}")
                                print("")
                                if current_inventory_name:
                                    save_inventory_to_file(current_inventory, current_inventory_name)
                                input("Press any key to continue...")
                                return
                            elif playervalue < dealervalue:
                                print("Dealer wins!")
                                print("")
                                if current_inventory_name:
                                    save_inventory_to_file(current_inventory, current_inventory_name)
                                input("Press any key to continue...")
                                return
                            else:
                                gold += bet
                                print("Tie. Money returned.")
                                print("")
                                if current_inventory_name:
                                    save_inventory_to_file(current_inventory, current_inventory_name)
                                input("Press any key to continue...")
                                return
                        else:
                            while dealervalue < 17:
                                card = playingdeck.pop(0)
                                dealerhand.append(card)
                                print(f"Dealer drew: {card['name']} {card['cardface']}")
                                if card["internalname"] == "A-S" or card["internalname"] == "A-H" or card["internalname"] == "A-D" or card["internalname"] == "A-C":
                                    if dealervalue + 11 > 21:
                                        dealervalue += 1
                                    else:
                                        dealervalue += 11
                                else:
                                    dealervalue += blackjackvalues[card["internalname"]]
                                print("")
                                if dealervalue > 21:
                                    print("Dealer bust! Player wins.")
                                    gold += bet + dealerbet
                                    print(f"You won ${bet + dealerbet}.")
                                    print(f"Your new balance is: ${gold}")
                                    print("")
                                    if current_inventory_name:
                                        save_inventory_to_file(current_inventory, current_inventory_name)
                                    input("Press any key to continue...")
                                    return
                                elif dealervalue == 21:
                                    print("21! Dealer wins.")
                                    print("")
                                    if current_inventory_name:
                                        save_inventory_to_file(current_inventory, current_inventory_name)
                                    input("Press any key to continue...")
                                    return
                                elif dealervalue >= 17:
                                    print("Dealer stands.")
                                    print("")
                                    if playervalue > dealervalue:
                                        print("Player wins!")
                                        gold += bet + dealerbet
                                        print(f"You won ${bet + dealerbet}.")
                                        print(f"Your new balance is: ${gold}")
                                        print("")
                                        if current_inventory_name:
                                            save_inventory_to_file(current_inventory, current_inventory_name)
                                        input("Press any key to continue...")
                                        return
                                    elif playervalue < dealervalue:
                                        print("Dealer wins!")
                                        print("")
                                        if current_inventory_name:
                                            save_inventory_to_file(current_inventory, current_inventory_name)
                                        input("Press any key to continue...")
                                        return
                                    else:
                                        gold += bet
                                        print("Tie. Money returned.")
                                        print("")
                                        if current_inventory_name:
                                            save_inventory_to_file(current_inventory, current_inventory_name)
                                        input("Press any key to continue...")
                                        return
                        
        elif choice == 2:
            print("This is a placeholder, as I cannot be bothered to research how to play poker just to make this right now.")
            print("")
            input("Press any key to continue...")
        elif choice == 3:
            bet = 0
            fun: False
            os.system("cls" if os.name == "nt" else "clear")
            highlowvalues = [
                {"Card": "A-S", "Value": 1, "highPayout": "N/A", "lowPayout": 1},
                {"Card": "A-H", "Value": 1, "highPayout": "N/A", "lowPayout": 1},
                {"Card": "A-D", "Value": 1, "highPayout": "N/A", "lowPayout": 1},
                {"Card": "A-C", "Value": 1, "highPayout": "N/A", "lowPayout": 1},
                {"Card": "2-S", "Value": 2, "highPayout": 1.1, "lowPayout": 10.7},
                {"Card": "2-H", "Value": 2, "highPayout": 1.1, "lowPayout": 10.7},
                {"Card": "2-D", "Value": 2, "highPayout": 1.1, "lowPayout": 10.7},
                {"Card": "2-C", "Value": 2, "highPayout": 1.1, "lowPayout": 10.7},
                {"Card": "3-S", "Value": 3, "highPayout": 1.1, "lowPayout": 5.3},
                {"Card": "3-H", "Value": 3, "highPayout": 1.1, "lowPayout": 5.3},
                {"Card": "3-D", "Value": 3, "highPayout": 1.1, "lowPayout": 5.3},
                {"Card": "3-C", "Value": 3, "highPayout": 1.1, "lowPayout": 5.3},
                {"Card": "4-S", "Value": 4, "highPayout": 1.1, "lowPayout": 3.5},
                {"Card": "4-H", "Value": 4, "highPayout": 1.1, "lowPayout": 3.5},
                {"Card": "4-D", "Value": 4, "highPayout": 1.1, "lowPayout": 3.5},
                {"Card": "4-C", "Value": 4, "highPayout": 1.1, "lowPayout": 3.5},
                {"Card": "5-S", "Value": 5, "highPayout": 1.3, "lowPayout": 2.6},
                {"Card": "5-H", "Value": 5, "highPayout": 1.3, "lowPayout": 2.6},
                {"Card": "5-D", "Value": 5, "highPayout": 1.3, "lowPayout": 2.6},
                {"Card": "5-C", "Value": 5, "highPayout": 1.3, "lowPayout": 2.6},
                {"Card": "6-S", "Value": 6, "highPayout": 1.5, "lowPayout": 2.1},
                {"Card": "6-H", "Value": 6, "highPayout": 1.5, "lowPayout": 2.1},
                {"Card": "6-D", "Value": 6, "highPayout": 1.5, "lowPayout": 2.1},
                {"Card": "6-C", "Value": 6, "highPayout": 1.5, "lowPayout": 2.1},
                {"Card": "7-S", "Value": 7, "highPayout": 1.87, "lowPayout": 1.87},
                {"Card": "7-H", "Value": 7, "highPayout": 1.87, "lowPayout": 1.87},
                {"Card": "7-D", "Value": 7, "highPayout": 1.87, "lowPayout": 1.87},
                {"Card": "7-C", "Value": 7, "highPayout": 1.87, "lowPayout": 1.87},
                {"Card": "8-S", "Value": 8, "highPayout": 2.1, "lowPayout": 1.5},
                {"Card": "8-H", "Value": 8, "highPayout": 2.1, "lowPayout": 1.5},
                {"Card": "8-D", "Value": 8, "highPayout": 2.1, "lowPayout": 1.5},
                {"Card": "8-C", "Value": 8, "highPayout": 2.1, "lowPayout": 1.5},
                {"Card": "9-S", "Value": 9, "highPayout": 2.6, "lowPayout": 1.3},
                {"Card": "9-H", "Value": 9, "highPayout": 2.6, "lowPayout": 1.3},
                {"Card": "9-D", "Value": 9, "highPayout": 2.6, "lowPayout": 1.3},
                {"Card": "9-C", "Value": 9, "highPayout": 2.6, "lowPayout": 1.3},
                {"Card": "10-S", "Value": 10, "highPayout": 3.5, "lowPayout": 1.1},
                {"Card": "10-H", "Value": 10, "highPayout": 3.5, "lowPayout": 1.1},
                {"Card": "10-D", "Value": 10, "highPayout": 3.5, "lowPayout": 1.1},
                {"Card": "10-C", "Value": 10, "highPayout": 3.5, "lowPayout": 1.1},
                {"Card": "J-S", "Value": 11, "highPayout": 5.3, "lowPayout": 1.1},
                {"Card": "J-H", "Value": 11, "highPayout": 5.3, "lowPayout": 1.1},
                {"Card": "J-D", "Value": 11, "highPayout": 5.3, "lowPayout": 1.1},
                {"Card": "J-C", "Value": 11, "highPayout": 5.3, "lowPayout": 1.1},
                {"Card": "Q-S", "Value": 12, "highPayout": 10.7, "lowPayout": 1.1},
                {"Card": "Q-H", "Value": 12, "highPayout": 10.7, "lowPayout": 1.1},
                {"Card": "Q-D", "Value": 12, "highPayout": 10.7, "lowPayout": 1.1},
                {"Card": "Q-C", "Value": 12, "highPayout": 10.7, "lowPayout": 1.1},
                {"Card": "K-S", "Value": 13, "highPayout": "N/A", "lowPayout": 1},
                {"Card": "K-H", "Value": 13, "highPayout": "N/A", "lowPayout": 1},
                {"Card": "K-D", "Value": 13, "highPayout": "N/A", "lowPayout": 1},
                {"Card": "K-C", "Value": 13, "highPayout": "N/A", "lowPayout": 1}
            ]
            print("A card is drawn from the deck.")
            print("You must guess if the next card is higher or lower.")
            print("If you guess correctly, you win.")
            print("If you guess incorrectly, you lose.")
            print("If the same card is drawn, you guess again.")
            print("Payouts are based on the odds of the card drawn.")
            print("Value of the card is based on poker rules.")
            print("Aces are always low.")
            print("Jokers are removed from the deck.")
            print("")
            print("Every draw is 5 gold.")
            input("Press any key to continue...")
            os.system("cls" if os.name == "nt" else "clear")
            playingdeck = card_deck.copy()
            playingdeck.remove({"name": "Joker", "cardface": "🃏︎", "internalname": "Joker"})
            random.shuffle(playingdeck)
            currentcard = playingdeck.pop(0)
            while True:
                if gold < 5:
                    print("You do not have enough money to play.")
                    input("Press any key to continue...")
                    return
                else:
                    print("Current card: " + currentcard["name"] + " " + currentcard["cardface"] + " (Value: " + str(highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == currentcard["internalname"])]["Value"]) + ")")
                    print("")
                    gold -= 5
                    if not playingdeck:
                        print("Deck is empty. Adding a new deck, removing the Joker, and reshuffling...")
                        playingdeck = card_deck.copy()
                        playingdeck.remove({"name": "Joker", "cardface": "🃏︎", "internalname": "Joker"})
                        random.shuffle(playingdeck)
                    if currentcard["internalname"] in ["A-S", "A-H", "A-D", "A-C"]:
                        print("Ace!")
                        print("Returning gold...")
                        gold += 5
                        print("Gold returned!")
                        print("Keep playing or leave?")
                        print("1. Keep playing")
                        print("2. Leave")
                        choice = get_user_choice(2)
                        if choice == 1:
                            currentcard = playingdeck.pop(0)
                            continue
                        elif choice == 2:
                            return
                    elif currentcard["internalname"] in ["K-S", "K-H", "K-D", "K-C"]:
                        print("King!")
                        print("Returning gold...")
                        gold += 5
                        print("Gold returned!")
                        print("Keep playing or leave?")
                        print("1. Keep playing")
                        print("2. Leave")
                        choice = get_user_choice(2)
                        if choice == 1:
                            currentcard = playingdeck.pop(0)
                            continue
                        elif choice == 2:
                            return
                    else:
                        print("High or Low?")
                        print("1. High")
                        print("2. Low")
                        print("3. Exit")
                        choice = get_user_choice(3)
                        if choice == 1:
                            previouscard = currentcard["internalname"]
                            currentcard = playingdeck.pop(0)
                            print(f"Current card: {currentcard['name']} {currentcard['cardface']}")
                            if currentcard["internalname"] == "A-S" or currentcard["internalname"] == "A-H" or currentcard["internalname"] == "A-D" or currentcard["internalname"] == "A-C":
                                print("It was low.")
                                print("Dealer win!")
                                print("")
                                print(f"You lost 5 gold. You have ${gold} left.")
                                print("")
                                input("Press any key to continue...")
                            elif currentcard["internalname"] == "K-S" or currentcard["internalname"] == "K-H" or currentcard["internalname"] == "K-D" or currentcard["internalname"] == "K-C":
                                print("It was high.")
                                print("Player win!")
                                print("")
                                gold += int(5 * highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == previouscard)]["highPayout"])
                                print(f"You won {int(5 * highlowvalues[next(index for index, card in enumerate(highlowvalues) if card['Card'] == previouscard)]['highPayout'])} gold. You now have ${gold}.")
                                print("")
                                input("Press any key to continue...")
                            elif currentcard["internalname"] == previouscard:
                                print("It was the same card.")
                                print("You get to guess again.")
                                print("")
                                gold += 5
                                print(f"You have ${gold} left.")
                                print("")
                                input("Press any key to continue...")
                            elif highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == currentcard["internalname"])]["Value"] > highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == previouscard)]["Value"]:
                                print("It was high.")
                                print("Player win!")
                                print("")
                                gold += int(5 * highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == previouscard)]["highPayout"])
                                print(f"You won {int(5 * highlowvalues[next(index for index, card in enumerate(highlowvalues) if card['Card'] == previouscard)]['highPayout'])} gold. You now have ${gold}.")
                                print("")
                                input("Press any key to continue...")
                            elif highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == currentcard["internalname"])]["Value"] < highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == previouscard)]["Value"]:
                                print("It was low.")
                                print("Dealer win!")
                                print("")
                                print(f"You lost 5 gold. You have ${gold} left.")
                                print("")
                                input("Press any key to continue...")
                        elif choice == 2:
                            previouscard = currentcard["internalname"]
                            currentcard = playingdeck.pop(0)
                            print(f"Current card: {currentcard['name']} {currentcard['cardface']}")
                            if currentcard["internalname"] == "A-S" or currentcard["internalname"] == "A-H" or currentcard["internalname"] == "A-D" or currentcard["internalname"] == "A-C":
                                print("It was low.")
                                print("Player win!")
                                print("")
                                gold += int(5 * highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == previouscard)]["lowPayout"])
                                print(f"You won {int(5 * highlowvalues[next(index for index, card in enumerate(highlowvalues) if card['Card'] == previouscard)]['lowPayout'])} gold. You now have ${gold}.")
                                print("")
                                input("Press any key to continue...")
                            elif currentcard["internalname"] == "K-S" or currentcard["internalname"] == "K-H" or currentcard["internalname"] == "K-D" or currentcard["internalname"] == "K-C":
                                print("It was high.")
                                print("Dealer win!")
                                print("")
                                print(f"You lost 5 gold. You have ${gold} left.")
                                print("")
                                input("Press any key to continue...")
                            elif currentcard["internalname"] == previouscard:
                                print("It was the same card.")
                                print("You get to guess again.")
                                print("")
                                gold += 5
                                print(f"You have ${gold} left.")
                                print("")
                                input("Press any key to continue...")
                            elif highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == currentcard["internalname"])]["Value"] < highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == previouscard)]["Value"]:
                                print("It was low.")
                                print("Player win!")
                                print("")
                                gold += int(5 * highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == previouscard)]["lowPayout"])
                                print(f"You won {int(5 * highlowvalues[next(index for index, card in enumerate(highlowvalues) if card['Card'] == previouscard)]['lowPayout'])} gold. You now have ${gold}.")
                                print("")
                                input("Press any key to continue...")
                            elif highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == currentcard["internalname"])]["Value"] > highlowvalues[next(index for index, card in enumerate(highlowvalues) if card["Card"] == previouscard)]["Value"]:
                                print("It was high.")
                                print("Dealer win!")
                                print("")
                                print(f"You lost 5 gold. You have ${gold} left.")
                                print("")
                                input("Press any key to continue...")
                        elif choice == 3:
                            os.system("cls" if os.name == "nt" else "clear")
                            return
                        os.system("cls" if os.name == "nt" else "clear")
        elif choice == 4:
            return
    elif choice == 2:
        os.system("cls" if os.name == "nt" else "clear")
        diceoptions = ["Craps", "Klondike", "Exit"]
        print_menu(diceoptions)
        choice = get_user_choice(len(diceoptions))
        if choice == 1:
            os.system("cls" if os.name == "nt" else "clear")
            def play_craps():
                global gold
                os.system("cls" if os.name == "nt" else "clear")
                print("Roll a 7 or 11 on the first roll to win.")
                print("Roll a 2, 3, or 12 on the first roll to lose.")
                print("Any other number becomes the 'point.'")
                print("Roll the point again before rolling a 7 to win.")
                print("Roll a 7 before the point to lose.")
                print("")
                print(f"You have ${gold}.")
                print("Enter your bet amount (or 0 to play for fun):")
                try:
                    bet = int(input("Bet: "))
                    if bet > gold:
                        print("You don't have enough gold to make that bet.")
                        input("Press any key to continue...")
                        return
                    elif bet < 0:
                        print("Invalid bet amount.")
                        input("Press any key to continue...")
                        return
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    input("Press any key to continue...")
                    return

                if bet > 0:
                    gold -= bet

                print("Rolling the dice...")
                time.sleep(1)
                die1 = random.randint(1, 6)
                die2 = random.randint(1, 6)
                roll = die1 + die2
                print(f"You rolled: {die1} + {die2} = {roll}")

                if roll in [7, 11]:
                    print("You rolled a natural! You win!")
                    if bet > 0:
                        winnings = bet * 2
                        gold += winnings
                        print(f"You won ${winnings}. Your new balance is ${gold}.")
                elif roll in [2, 3, 12]:
                    print("Craps! You lose.")
                else:
                    point = roll
                    print(f"The point is set to {point}. Keep rolling!")
                    while True:
                        input("Press Enter to roll again...")
                        die1 = random.randint(1, 6)
                        die2 = random.randint(1, 6)
                        roll = die1 + die2
                        print(f"You rolled: {die1} + {die2} = {roll}")
                        if roll == point:
                            print("You hit the point! You win!")
                            if bet > 0:
                                winnings = bet * 2
                                gold += winnings
                                print(f"You won ${winnings}. Your new balance is ${gold}.")
                            break
                        elif roll == 7:
                            print("You rolled a 7! You lose.")
                            break

                input("Press any key to return to the bar menu...")

            play_craps()
        elif choice == 2:
            def play_klondike():
                global gold
                os.system("cls" if os.name == "nt" else "clear")
                print("The game is played with five dice.")
                print("Each player rolls all five dice.")
                print("The goal is to get the highest total score.")
                print("If two players tie, the game is a draw.")
                print("You can bet gold, and the winner takes the pot.")
                print("")
                print(f"You have ${gold}.")
                print("Enter your bet amount:")
                try:
                    bet = int(input("Bet: "))
                    if bet > gold:
                        print("You don't have enough gold to make that bet.")
                        input("Press any key to continue...")
                        return
                    elif bet < 0:
                        print("Invalid bet amount.")
                        input("Press any key to continue...")
                        return
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    input("Press any key to continue...")
                    return

                if bet == 0:
                    print("You cannot bet 0 on this game.")
                    input("Press any key to continue...")
                    return

                gold -= bet
                pot = bet
                npc_players = random.randint(1, 5)
                npc_bets = {}

                print(f"{npc_players} other players have joined the game.")
                for i in range(npc_players):
                    npc_first_name = generate_child_name(parent1, parent2)
                    npc_last_name = random.choice(lastnames)["name"]
                    npc_name = f"{npc_first_name} {npc_last_name}"
                    npc_bet = random.randint(5, 100)
                    npc_bets[npc_name] = npc_bet
                    pot += npc_bet
                    print(f"{npc_name} adds ${npc_bet} to the pot.")

                print(f"The total pot is now ${pot}.")
                print("Rolling your dice...")
                time.sleep(1)
                player_rolls = [random.randint(1, 6) for _ in range(5)]
                player_total = sum(player_rolls)
                print(f"Your rolls: {player_rolls} (Total: {player_total})")

                npc_totals = {}
                for npc_name in npc_bets:
                    print(f"Rolling dice for {npc_name}...")
                    time.sleep(1)
                    npc_rolls = [random.randint(1, 6) for _ in range(5)]
                    npc_total = sum(npc_rolls)
                    npc_totals[npc_name] = npc_total
                    print(f"{npc_name}'s rolls: {npc_rolls} (Total: {npc_total})")

                print("Rolling dealer's dice...")
                time.sleep(1)
                dealer_rolls = [random.randint(1, 6) for _ in range(5)]
                dealer_total = sum(dealer_rolls)
                print(f"Dealer's rolls: {dealer_rolls} (Total: {dealer_total})")

                all_scores = {"You": player_total, **npc_totals, "Dealer": dealer_total}
                winner = max(all_scores, key=all_scores.get)
                winning_score = all_scores[winner]

                print("\nFinal Scores:")
                for player, score in all_scores.items():
                    print(f"{player}: {score}")

                if list(all_scores.values()).count(winning_score) > 1:
                    print("It's a draw!")
                    gold += bet
                    print(f"Your bet of ${bet} has been returned. Your balance is ${gold}.")
                else:
                    if winner == "You":
                        print("You win!")
                        gold += pot
                        print(f"You won the pot of ${pot}. Your new balance is ${gold}.")
                    else:
                        print(f"{winner} wins with a total of {winning_score}!")
                        print("Better luck next time.")

                input("Press any key to continue...")
            play_klondike()
    elif choice == 3:
        return
        
def devtools():
    global gold, current_inventory, current_inventory_name, freeslots
    os.system("cls" if os.name == "nt" else "clear")
    print("Developer Tools")
    print("Version: " + version)
    print("Gold: $" + str(gold))
    print("Loaded inventory: " + str(current_inventory_name))
    print("")
    devoptions = ["Modify values", "Decode Save File", "Exit"]
    print_menu(devoptions)
    choice = get_user_choice(len(devoptions))
    if choice == 1:
        os.system("cls" if os.name == "nt" else "clear")
        modvalues = ["Gold", "Free Slots", "Inventory Name", "Inventory", "Storage", "Exit"]
        print_menu(modvalues)
        choice = get_user_choice(len(modvalues))
        if choice == 1:
            os.system("cls" if os.name == "nt" else "clear")
            print("Current Gold: $" + str(gold))
            new_gold = input("Enter new gold amount: ")
            try:
                gold = int(new_gold)
                print(f"Gold set to ${gold}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == 2:
            os.system("cls" if os.name == "nt" else "clear")
            print("Current Free Slots: " + str(freeslots))
            new_freeslots = input("Enter new free slots amount: ")
            try:
                freeslots = int(new_freeslots)
                print(f"Free slots set to {freeslots}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == 3:
            os.system("cls" if os.name == "nt" else "clear")
            print("Current Inventory Name: " + str(current_inventory_name))
            new_inventory_name = input("Enter new inventory name: ")
            current_inventory_name = new_inventory_name
            print(f"Inventory name set to {current_inventory_name}.")
        elif choice == 4:
            os.system("cls" if os.name == "nt" else "clear")
            print("Current Inventory: " + str(current_inventory))
            print("1. Add Item")
            print("2. Remove Item")
            print("3. Clear Inventory")
            print("4. Exit")
            choice = get_user_choice(4)
            if choice == 1:
                os.system("cls" if os.name == "nt" else "clear")
                print("1. Custom Item")
                print("2. Random Item")
                print("3. Specific Item")
                choice = get_user_choice(3)
                if choice == 1:
                    os.system("cls" if os.name == "nt" else "clear")
                    item_name = input("Enter item name: ")
                    item_value = input("Enter item value: ")
                    item_description = input("Enter item description: ")
                    item_rarity = input("Enter item rarity (common, uncommon, rare, legendary, mythic): ")
                    item_minrand = input("Enter minimum quantity: ")
                    item_maxrand = input("Enter maximum quantity: ")
                    item_inventoryslots = input("Enter inventory slots: ")
                    item_quantity = input("Enter quantity: ")
                    new_item = {
                        "name": item_name,
                        "value": int(item_value),
                        "description": item_description,
                        "rarity": item_rarity,
                        "minrand": int(item_minrand),
                        "maxrand": int(item_maxrand),
                        "inventoryslots": int(item_inventoryslots),
                        "quantity": int(item_quantity)
                    }
                    current_inventory.append(new_item)
                    print(f"Added custom item '{item_name}' to inventory.")
                elif choice == 2:
                    os.system("cls" if os.name == "nt" else "clear")
                    categories_with_weights = {
                    "ammo": 25,
                    "healing_and_magic": 25,
                    "melee_weapons": 15,
                    "armor_and_defense": 15,
                    "ranged_weapons": 15,
                    "cursed_and_blessed_items": 5
                    }
                    category_key = random.choices(
                        list(categories_with_weights.keys()),
                        weights=categories_with_weights.values(),
                        k=1
                    )[0]
                    category_mapping = {
                        "melee_weapons": melee_weapons,
                        "ranged_weapons": ranged_weapons,
                        "ammo": ammo,
                        "armor_and_defense": armor_and_defense,
                        "healing_and_magic": healing_and_magic,
                        "cursed_and_blessed_items": cursed_and_blessed_items
                    }
                    category = category_mapping[category_key]
                    total_items = random.randint(1, 3)
                    for item_number in range(1, total_items + 1):
                        os.system("cls" if os.name == "nt" else "clear")
                        category = category_mapping[category_key]
                        print(f"Pulling item {item_number} of {total_items}.")
                        main_logic(category)
                elif choice == 3:
                    os.system("cls" if os.name == "nt" else "clear")
                    categories = ["ammo", "healing_and_magic", "melee_weapons", "armor_and_defense", "ranged_weapons", "cursed_and_blessed_items", "traderspecificitems"]
                    print("Select a category:")
                    print_menu(categories)
                    category_choice = get_user_choice(len(categories))
                    category = categories[category_choice - 1]
                    category_mapping = {
                        "melee_weapons": melee_weapons,
                        "ranged_weapons": ranged_weapons,
                        "ammo": ammo,
                        "armor_and_defense": armor_and_defense,
                        "healing_and_magic": healing_and_magic,
                        "cursed_and_blessed_items": cursed_and_blessed_items,
                        "traderspecificitems": traderspecificitems
                    }
                    selected_category = category_mapping[category]
                    print("Select an item to add:")
                    for i, item in enumerate(selected_category, start=1):
                        print(f"[{i}] {item['name']} (Rarity: {item['rarity']}, Value: ${item['value']}, Slots: {item['inventoryslots']})")
                    item_choice = get_user_choice(len(selected_category))
                    selected_item = selected_category[item_choice - 1]
                    print(f"How many '{selected_item['name']}' would you like to add? (1-{selected_item['maxrand']}):")
                    quantity_to_add = get_user_choice(selected_item['maxrand'])
                    item_copy = selected_item.copy()
                    item_copy["quantity"] = quantity_to_add
                    current_inventory.append(item_copy)
                    print(f"Added {quantity_to_add}x '{selected_item['name']}' to inventory.")
    elif choice == 2:
        os.system("cls" if os.name == "nt" else "clear")
        print("Decode Save File")
        print("Enter the name of the save file to decode (without extension):")
        save_file_name = input("Save File Name: ").strip() + ".save"
        save_file_path = os.path.join(saves_folder, save_file_name)
        if not os.path.exists(save_file_path):
            print(f"Save file '{save_file_name}' does not exist.")
        else:
            try:
                with open(save_file_path, "r") as file:
                    encoded_data = file.read()
                    decoded_data = json.loads(base64.b64decode(encoded_data).decode("utf-8"))
                    print("Decoded Save File Content:")
                    print(json.dumps(decoded_data, indent=4))
            except Exception as e:
                print(f"Error decoding save file: {e}")
        input("Press any key to continue...")

def check_for_updates():
    try:
        response = requests.get("https://raw.githubusercontent.com/soli-dstate/lootingprogram-py/main/version.txt")
        if response.status_code == 200:
            latest_version = response.text.strip()
            if latest_version != version:
                if ver.parse(version) > ver.parse(latest_version):
                    print(f"Prerelease copy detected! Current version: {version}, Latest version: {latest_version}")
                    global developmentcopy
                    developmentcopy = True
                else:
                    print(f"Update available! Current version: {version}, Latest version: {latest_version}")
                    print("Would you like to update now? (y/n): ", end="")
                    update_choice = input().strip().lower()
                    if update_choice != "y":
                        print("Update skipped. You can update later by restarting the program.")
                        return
                    print("Attempting to auto-update from GitHub...")
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    if os.name == "nt":
                        exe_name = None
                        for name in os.listdir(current_dir):
                            if name.lower().endswith(".exe"):
                                exe_name = name
                                break
                        if not exe_name:
                            for name in os.listdir(current_dir):
                                if name.lower().endswith(".py"):
                                    exe_name = name
                                    break
                        zip_url = None
                        possible_names = [
                            "loot.python_compiled.zip",
                            "loot-python-compiled.zip",
                            "lootpython.zip",
                            "main.zip"
                        ]
                        try:
                            releases = requests.get("https://api.github.com/repos/soli-dstate/lootingprogram-py/releases").json()
                            if isinstance(releases, list) and releases:
                                for asset in releases[0].get("assets", []):
                                    if asset["name"].endswith(".zip"):
                                        zip_url = asset["browser_download_url"]
                                        break
                        except Exception:
                            pass
                        if not zip_url:
                            for name in possible_names:
                                test_url = f"https://github.com/soli-dstate/lootingprogram-py/raw/main/{name}"
                                r = requests.head(test_url)
                                if r.status_code == 200:
                                    zip_url = test_url
                                    break
                        if not zip_url:
                            print("Could not find update zip file automatically. Please update manually.")
                            return
                        print(f"Downloading update from: {zip_url}")
                        r = requests.get(zip_url, stream=True)
                        update_zip = os.path.join(current_dir, "update_temp.zip")
                        with open(update_zip, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                        print("Download complete. Extracting update...")
                        extract_folder = os.path.join(current_dir, "loot_update_temp")
                        with zipfile.ZipFile(update_zip, "r") as zip_ref:
                            zip_ref.extractall(extract_folder)
                        new_file = None
                        for root, dirs, files in os.walk(extract_folder):
                            for file in files:
                                if file.lower().endswith(".exe") or file.lower().endswith(".py"):
                                    new_file = os.path.join(root, file)
                                    break
                            if new_file:
                                break
                        if not new_file:
                            print("Could not find new program file in update. Update failed.")
                            return
                        if exe_name:
                            try:
                                os.remove(os.path.join(current_dir, exe_name))
                            except Exception:
                                pass
                        shutil.copy2(new_file, current_dir)
                        print(f"Updated file copied to {current_dir}.")
                        try:
                            os.remove(update_zip)
                        except Exception:
                            pass
                        try:
                            shutil.rmtree(extract_folder)
                        except Exception:
                            pass
                        print("Update complete. Please restart the program.")
                        input("Press Enter to exit...")
                        exit(0)
                    else:
                        print(f"Update available! Current version: {version}, Latest version: {latest_version}")
                        print("Would you like to update now? (y/n): ", end="")
                        update_choice = input().strip().lower()
                        if update_choice != "y":
                            print("Update skipped. You can update later by restarting the program.")
                            return
                        print("Attempting to auto-update from GitHub...")
                        py_name = None
                        for name in os.listdir(current_dir):
                            if name.lower().endswith(".py"):
                                py_name = name
                                break
                        src_url = "https://github.com/soli-dstate/lootingprogram-py/archive/refs/heads/main.zip"
                        r = requests.get(src_url, stream=True)
                        update_zip = os.path.join(current_dir, "update_source_temp.zip")
                        with open(update_zip, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                        print("Download complete. Extracting source code...")
                        extract_folder = os.path.join(current_dir, "loot_update_source")
                        with zipfile.ZipFile(update_zip, "r") as zip_ref:
                            zip_ref.extractall(extract_folder)
                        new_py = None
                        for root, dirs, files in os.walk(extract_folder):
                            for file in files:
                                if file == "mainprogram.py":
                                    new_py = os.path.join(root, file)
                                    break
                            if new_py:
                                break
                        if not new_py:
                            print("Could not find new mainprogram.py in update. Update failed.")
                            return
                        if py_name:
                            try:
                                os.remove(os.path.join(current_dir, py_name))
                            except Exception:
                                pass
                        shutil.copy2(new_py, os.path.join(current_dir, "mainprogram.py"))
                        print(f"Updated mainprogram.py copied to {current_dir}.")
                        try:
                            os.remove(update_zip)
                        except Exception:
                            pass
                        try:
                            shutil.rmtree(extract_folder)
                        except Exception:
                            pass
                        print("Update complete. Please restart the program.")
                        input("Press Enter to exit...")
                        exit(0)
            else:
                print("You are using the latest version.")
        else:
            print("Failed to check for updates. Unable to access version file.")
    except Exception as e:
        print(f"Error checking for updates: {e}")
        
def main():
    global current_inventory_name, developmentcopy
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(f"Loot {version}")
        check_for_updates()
        print(f"Current Inventory: {current_inventory_name or 'None'}")
        print("")
        if developmentcopy:
            main_options = ["Easy Loot", "Inventory Management", "Trading", "Bar", "Exit", "Development Options"]
        else:
            main_options = ["Easy Loot", "Inventory Management", "Trading", "Bar", "Exit"]
        print_menu(main_options)
        choice = get_user_choice(len(main_options))

        if choice == 1:
            if not current_inventory_name:
                print("No inventory loaded! Please load or create an inventory first.")
                input("Press any key to continue...")
            else:
                os.system("cls" if os.name == "nt" else "clear")
                opts = ["Chest", "Other"]
                print_menu(opts)
                choice = get_user_choice(len(opts))
                if choice == 1:
                    os.system("cls" if os.name == "nt" else "clear")
                    categories_with_weights = {
                        "ammo": 25,
                        "healing_and_magic": 25,
                        "melee_weapons": 15,
                        "armor_and_defense": 15,
                        "ranged_weapons": 15,
                        "cursed_and_blessed_items": 5
                    }
                    category_mapping = {
                        "melee_weapons": melee_weapons,
                        "ranged_weapons": ranged_weapons,
                        "ammo": ammo,
                        "armor_and_defense": armor_and_defense,
                        "healing_and_magic": healing_and_magic,
                        "cursed_and_blessed_items": cursed_and_blessed_items
                    }
                    total_items = random.randint(1, 3)
                    for item_number in range(1, total_items + 1):
                        os.system("cls" if os.name == "nt" else "clear")
                        category_key = random.choices(
                            list(categories_with_weights.keys()),
                            weights=categories_with_weights.values(),
                            k=1
                        )[0]
                        category = category_mapping[category_key]
                        print(f"Pulling item {item_number} of {total_items}.")
                        main_logic(category)
                elif choice == 2:
                    os.system("cls" if os.name == "nt" else "clear")
                    categories_with_weights = {
                        "junk": 75,
                        "ammo": 7,
                        "healing_and_magic": 5,
                        "melee_weapons": 4,
                        "armor_and_defense": 4,
                        "ranged_weapons": 4,
                        "cursed_and_blessed_items": 1
                    }
                    category_mapping = {
                        "melee_weapons": melee_weapons,
                        "ranged_weapons": ranged_weapons,
                        "ammo": ammo,
                        "armor_and_defense": armor_and_defense,
                        "healing_and_magic": healing_and_magic,
                        "cursed_and_blessed_items": cursed_and_blessed_items,
                        "junk": junk
                    }
                    total_items = random.randint(1, 5)
                    for item_number in range(1, total_items + 1):
                        os.system("cls" if os.name == "nt" else "clear")
                        category_key = random.choices(
                            list(categories_with_weights.keys()),
                            weights=categories_with_weights.values(),
                            k=1
                        )[0]
                        category = category_mapping[category_key]
                        print(f"Pulling item {item_number} of {total_items}.")
                        main_logic(category)
        elif choice == 2:
            manage_inventory()
        elif choice == 3:
            if not current_inventory_name:
                print("No inventory loaded! Please load or create an inventory first.")
                input("Press any key to continue...")
            else:
                trader()
        elif choice == 4:
            if not current_inventory_name:
                print("No inventory loaded! Please load or create an inventory first.")
                input("Press any key to continue...")
            else:
                bar()
        elif choice == 5:
            break
        elif choice == 6 and developmentcopy == True:
            if not current_inventory_name:
                print("No inventory loaded! Please load or create an inventory first.")
                input("Press any key to continue...")
            else:
                devtools()

main()
