import os
import random
import json
import base64
import requests

version = "3.0.0"

freeslots = 10
current_inventory = []
current_inventory_name = None
storage = []
saves_folder = "./saves"

incompatible_saves = [
    "3.0.0developmentcopy",
    "3.0.0developmentcopy2",
]

os.makedirs(saves_folder, exist_ok=True)

def save_inventory_to_file(inventory, file_name):
    file_path = os.path.join(saves_folder, file_name)
    try:
        data_to_save = {
            "version": version,
            "inventory": inventory,
            "freeslots": freeslots,
            "storage": storage
        }
        encoded_data = base64.b64encode(json.dumps(data_to_save).encode("utf-8")).decode("utf-8")
        with open(file_path, "w") as file:
            file.write(encoded_data)
        print(f"Inventory saved to {file_path}")
    except Exception as e:
        print(f"Error saving inventory: {e}")

def load_inventory_from_file(file_name):
    global freeslots, storage
    file_path = os.path.join(saves_folder, file_name)
    try:
        with open(file_path, "r") as file:
            encoded_data = file.read()
            data_loaded = json.loads(base64.b64decode(encoded_data).decode("utf-8"))
            freeslots = data_loaded.get("freeslots", 10)
            storage = data_loaded.get("storage", [])
            return data_loaded.get("inventory", [])
    except FileNotFoundError:
        print(f"Error: File {file_path} does not exist.")
    except Exception as e:
        print(f"Error loading inventory: {e}")
    return None

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
    {"name": "Methamphetamine", "value": 10, "description": "Walter's blue stuff for realsies", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Walter Hartwell White", "value": 10, "description": "Waltuh", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Hank Schrader", "value": 10, "description": "FACKIN ANDROIDS", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "SKYLAR WHITE YO", "value": 10, "description": "my name is skylar white yo", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "JESSE PINKDUDE", "value": 10, "description": "what's up bitch", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
]

melee_weapons = [
    {"name": "Dagger", "value": 30, "description": "A british staple of gang related disputes.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Bowie Knife", "value": 40, "description": "Thats not a knife…", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Military Grade Combat Knife", "value": 50, "description": "Nice, your fruit killin’ skills are remarkable.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Short Sword", "value": 60, "description": "A finely crafted and well edged sword from an unknown blacksmith.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Machete", "value": 60, "description": "A single edged blade used for forest environments or survival situations… but mostly used for killing teenagers at lakes", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Katana", "value": 80, "description": "To master your blade… you must first control your emotions.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Longsword", "value": 95, "description": "A longer blade for more reach, though it requires two hands to effectively use.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 3},
    {"name": "Claymore", "value": 130, "description": "A Highland Claymore of Northern Thedoria origin, its long blade and interesting design gives you a sense of gaelic pride.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 3},
    {"name": "Greatsword", "value": 150, "description": "A very big sword that crushes anything in its path… including your own arm muscles.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 3},
    {"name": "Spear", "value": 60, "description": "A very pointy stick that makes your primal urges for violence surge.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Glaive", "value": 90, "description": "in case single edged weapons that make you bleed wasn’t annoying enough, now you have it on a stick!", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 3},
    {"name": "Wood Axe", "value": 60, "description": "A wood handled axe made for handling wood", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Fire Axe", "value": 80, "description": "An axe designed to break doors and clear house fires, a life saving tool that you are now using to decapitate people.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
]

ranged_weapons = [
    {"name": "Wooden Bow", "value": 10, "description": "A very simple wooden bow, something that you could easily make… but you’re lazy aren’t you?", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Compound Bow", "value": 80, "description": "A more modern take on the simple bow, quiet and hits like a truck.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Wooden Crossbow", "value": 50, "description": "Used by an ancient race of marauders with comically large noses and gray skin, it now belongs to you.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Compound Crossbow", "value": 80, "description": "Crossbows for pretentious rich kids", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Pistol of your choosing", "value": 80, "description": "guns for poor people.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Revolver of your choosing", "value": 80, "description": "you feel the urge to smoke 5 cigarettes and down snake oil while using it", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "SMG of your choosing", "value": 80, "description": "Attack of the killer bees!", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "5.56 Rifle of your choosing", "value": 120, "description": "Freedom at its finest.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "7.62 Rifle of your choosing", "value": 130, "description": "You’re either a communist or really hate keeping things alive… or both.", "rarity": "Legendary", "minrand": 1, "maxrand": 2, "inventoryslots": 1},
    {"name": "308.Sniper Rifle of your choosing", "value": 150, "description": "Sniping's a good job, mate", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "338.Lupua Sniper Rifle of your choosing", "value": 300, "description": "Säkkijärven polkka.", "rarity": "Mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 3},
    {"name": "Empty 50 Caliber. Sniper Rifle of your choosing", "value": 500, "description": "Jokes on you it's empty!", "rarity": "Mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 4},
]


ammo = [
    {"name": ".22 Long Rifle", "value": 1, "description": "A small caliber round, great for plinking and small game.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0},
    {"name": "9x19mm Parabellum", "value": 2, "description": "A widely used pistol round, reliable and effective.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0},
    {"name": ".45 ACP", "value": 3, "description": "A classic American round, known for its stopping power, and the natural subsonic nature.", "rarity": "uncommon", "minrand": 10, "maxrand": 40, "inventoryslots": 0},
    {"name": ".38 Special", "value": 2, "description": "A revolver round, popular for self-defense.", "rarity": "common", "minrand": 10, "maxrand": 40, "inventoryslots": 0},
    {"name": ".357 Magnum", "value": 4, "description": "A powerful revolver round with excellent penetration.", "rarity": "uncommon", "minrand": 10, "maxrand": 30, "inventoryslots": 0},
    {"name": ".44 Magnum", "value": 5, "description": "A very powerful handgun round, for when you need serious firepower.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0},
    {"name": "10mm Auto", "value": 4, "description": "A versatile round, great for both self-defense and hunting.", "rarity": "uncommon", "minrand": 10, "maxrand": 30, "inventoryslots": 0},
    {"name": ".223 Remington", "value": 3, "description": "A popular rifle round, great for varmint hunting.", "rarity": "common", "minrand": 10, "maxrand": 40, "inventoryslots": 0},
    {"name": ".308 Winchester", "value": 6, "description": "A powerful rifle round, excellent for hunting and long-range shooting.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0},
    {"name": "5.45x39mm Soviet", "value": 3, "description": "A standard round for Soviet-era rifles, lightweight and effective.", "rarity": "common", "minrand": 10, "maxrand": 40, "inventoryslots": 0},
    {"name": "5.56x45mm NATO", "value": 4, "description": "A standard NATO round, widely used in modern rifles.", "rarity": "uncommon", "minrand": 10, "maxrand": 30, "inventoryslots": 0},
    {"name": "7.62x51mm NATO", "value": 6, "description": "A powerful NATO round, used in battle rifles and machine guns.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0},
    {"name": ".300 AAC Blackout", "value": 5, "description": "A versatile round, great for suppressed rifles.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0},
    {"name": ".30-06 Springfield", "value": 6, "description": "A classic American hunting round, known for its power.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0},
    {"name": "7.62x39mm Soviet", "value": 4, "description": "A standard round for AK-pattern rifles, reliable and effective.", "rarity": "uncommon", "minrand": 10, "maxrand": 30, "inventoryslots": 0},
    {"name": ".45-70 Government", "value": 7, "description": "A heavy round, great for big game hunting... or hunting humans.", "rarity": "rare", "minrand": 5, "maxrand": 15, "inventoryslots": 0},
    {"name": "12 Gauge", "value": 2, "description": "A versatile shotgun shell, great for hunting and self-defense.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0},
    {"name": "20 Gauge", "value": 2, "description": "A light shotgun shell, great for smaller game.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0},
    {"name": "10 Gauge", "value": 3, "description": "A heavy shotgun shell, great for large game and defense.", "rarity": "uncommon", "minrand": 5, "maxrand": 30, "inventoryslots": 0},
    {"name": ".410 Bore", "value": 1, "description": "A small shotgun shell, great for beginners and small game.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0},
    {"name": "8 Gauge", "value": 4, "description": "A very large shotgun shell, used for real big game.", "rarity": "rare", "minrand": 5, "maxrand": 20, "inventoryslots": 0},
    {"name": "4 Gauge", "value": 5, "description": "An extremely large shotgun shell, rarely used today.", "rarity": "rare", "minrand": 5, "maxrand": 15, "inventoryslots": 0},
    {"name": ".338 Lapua Magnum", "value": 8, "description": "A high-powered sniper round, excellent for long-range precision.", "rarity": "mythic", "minrand": 1, "maxrand": 10, "inventoryslots": 0},
    {"name": ".500 S&W Magnum", "value": 7, "description": "A massive revolver round, known for its incredible power.", "rarity": "rare", "minrand": 5, "maxrand": 15, "inventoryslots": 0},
    {"name": ".500 Nitro Express", "value": 9, "description": "A heavy round, used for hunting dangerous game.", "rarity": "mythic", "minrand": 1, "maxrand": 10, "inventoryslots": 0},
    {"name": ".50 Beowulf", "value": 8, "description": "A powerful round, designed for AR-pattern rifles.", "rarity": "legendary", "minrand": 1, "maxrand": 10, "inventoryslots": 0},
    {"name": ".50 BMG", "value": 10, "description": "A massive round, used in anti-materiel rifles.", "rarity": "mythic", "minrand": 1, "maxrand": 5, "inventoryslots": 0},
    {"name": "Railgun Rail", "value": 15, "description": "A futuristic projectile, used in experimental railguns.", "rarity": "mythic", "minrand": 1, "maxrand": 3, "inventoryslots": 0},
    {"name": "Pepperball", "value": 1, "description": "A non-lethal round, used for crowd control.", "rarity": "common", "minrand": 10, "maxrand": 50, "inventoryslots": 0},
]

armor_and_defense = [
    {"name": "Plate carrier", "value": 95, "description": "An adjustable vest with sleeves for armor plates. The material of the vest appears to be kevlar.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "NIJ Level IIIa soft plate", "value": 50, "description": "A lightweight soft plate offering protection against most handgun rounds.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "NIJ Level III ceramic plate", "value": 120, "description": "A ceramic plate capable of stopping rifle rounds.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "NIJ Level III steel plate", "value": 100, "description": "A durable steel plate offering protection against rifle rounds.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "NIJ Level IV ceramic plate", "value": 200, "description": "A high-grade ceramic plate capable of stopping armor-piercing rounds.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "NIJ Level IV steel plate", "value": 180, "description": "A steel plate offering protection against armor-piercing rounds.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "NIJ Level IV+ ceramic plate", "value": 250, "description": "An advanced ceramic plate with enhanced durability and protection.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "NIJ Level IV+ steel plate", "value": 230, "description": "An advanced steel plate with enhanced durability and protection.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Great helmet", "value": 150, "description": "A large, fully enclosed helmet offering excellent protection.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Bascinet", "value": 120, "description": "A medieval helmet with a pointed top, offering good protection.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Sallet", "value": 130, "description": "A rounded helmet with a visor, popular in the late medieval period.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Barbute", "value": 140, "description": "An open-faced helmet inspired by ancient Greek designs.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Sugarloaf helmet", "value": 160, "description": "A conical helmet offering excellent deflection against strikes.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Nasal helmet", "value": 90, "description": "A simple helmet with a nose guard, popular in the early medieval period.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Full plate chestplate", "value": 300, "description": "A full chestplate offering maximum protection.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 3},
    {"name": "Half plate chestplate", "value": 200, "description": "A partial chestplate offering good protection with more mobility.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Leather armor", "value": 50, "description": "A lightweight leather armor offering basic protection.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Chainmail armor", "value": 150, "description": "A chainmail shirt offering good protection against slashes.", "rarity": "Uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Gambeson chestplate", "value": 80, "description": "A padded armor offering decent protection and comfort.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Brigandine chestplate", "value": 180, "description": "A reinforced chestplate with metal plates sewn into fabric.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Small backpack", "value": 5, "description": "A small bag for carrying items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": -5},
    {"name": "Day pack", "value": 10, "description": "A small backpack for carrying items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": -10},
    {"name": "Bookbag", "value": 12, "description": "A medium-sized backpack for carrying items.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": -12},
    {"name": "Rucksack", "value": 15, "description": "A large backpack for carrying items.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": -15},
    {"name": "Hiking bag", "value": 20, "description": "A durable backpack for carrying items.", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": -20},
    {"name": "Duffel bag", "value": 25, "description": "A duffel bag for carrying a moderate amount of items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": -7},
    {"name": "Tactical backpack", "value": 30, "description": "A tactical backpack for carrying a large amount of items. Has an insert for a plate in the back.", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": -15},
    {"name": "Purse", "value": 5, "description": "A small bag for carrying personal items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": -2},
    {"name": "Vest pouch", "value": 10, "description": "A small pouch for carrying items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": -5},
    {"name": "Fanny pack", "value": 8, "description": "A small bag for carrying items.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": -3},
    {"name": "Shoulder bag", "value": 12, "description": "A small bag for carrying items.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": -10},
    {"name": "Messenger bag", "value": 15, "description": "A small bag for carrying items.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": -12},
]

healing_and_magic = [
    {"name": "Bandage", "value": 5, "description": "A simple bandage to stop bleeding.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0},
    {"name": "First Aid Kit", "value": 20, "description": "A comprehensive kit for treating injuries.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Antidote", "value": 10, "description": "A potion that cures poison.", "rarity": "uncommon", "minrand": 1, "maxrand": 3, "inventoryslots": 0},
    {"name": "Panacea", "value": 25, "description": "A potion that cures all ailments.", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Mana Potion", "value": 20, "description": "A potion that restores magical energy.", "rarity": "rare", "minrand": 1, "maxrand": 3, "inventoryslots": 0},
    {"name": "Apple", "value": 2, "description": "A simple fruit that restores a small amount of health.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0},
    {"name": "Bread", "value": 3, "description": "A loaf of bread that restores a small amount of health.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0},
    {"name": "Cheese Wheel", "value": 15, "description": "A wheel of cheese that restores a medium amount of health.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Steak", "value": 10, "description": "A cooked steak that restores a medium amount of health.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Hardtack", "value": 1, "description": "A hard biscuit that restores a small amount of health.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0},
    {"name": "Honey", "value": 5, "description": "A jar of honey that restores a small amount of health.", "rarity": "common", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Sandwich", "value": 8, "description": "A sandwich that restores a medium amount of health.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Chips", "value": 2, "description": "A bag of chips that restores a small amount of health.", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0},
    {"name": "Energy Drink", "value": 5, "description": "A can of Red Bull that restores a small amount of health. (does not give you wings)", "rarity": "common", "minrand": 1, "maxrand": 5, "inventoryslots": 0},
    {"name": "Health Cure", "value": 30, "description": "A potion that restores a large amount of health.", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Moonshine", "value": 10, "description": "A strong alcoholic beverage that restores a large amount of health.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Bitters", "value": 15, "description": "A strong alcoholic beverage that restores a medium amount of health.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Snake Oil", "value": 20, "description": "A magical potion that restores a large amount of health.", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Miracle Tonic", "value": 25, "description": "A magical potion that restores a large amount of health and cures all ailments.", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Small ornate locket", "value": 5, "description": "A small spherical ornate silver locket on a chain that when opened provides a soft blue glow and provides a constant healing effect. Prolonged exposure may result in death. (SCP-427)", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Red unmarked pill", "value": 25, "description": "A small red pill that when consumed heals all ailments and injuries. (SCP-500)", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Phoenix Feather", "value": 50, "description": "A magical feather that can revive the dead.", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
]

cursed_and_blessed_items = [
    {"name": "Charlotte’s MP3 Player", "value": 1000, "description": "An MP3 player filled with various songs under the artist ‘And One’... can I have it back please?", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Mysterious Dagger", "value": 3000, "description": "Allows you to summon Undertaker for a short period of time when used to sacrifice something.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Model M500 Flash Goggles", "value": 200, "description": "Some sturdy looking goggles that appear flashbang proof… why is it covered in dog hair?", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "M4’s Boots", "value":500, "description": "Made out of an almost ethereal leather, its completely indestructible.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Comedy Wrench", "value": 200, "description": "A basic utility wrench used by past survivors for comedic effect, its unbelievable luck is now in your hands. (+2 to whatever you’re using it for)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Strange Sweater", "value": 200, "description": "A sweater made out of a strange yarn. Prevents bleeding. (+2 resistance)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Strange Shovel", "value": 200, "description": "It's heavy, but it has a good reach! (+1 to attack & parry rolls when using shovel)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Red Headset", "value": 200, "description": "Not again! You should know better!", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Panzerfaust", "value": 500, "description": "The box had some severed fingers inside too, strange…", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Unusual Pink Potion", "value": 350, "description": "I wouldn’t recommend drinking it.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Brazilian made plate carrier", "value": 500, "description": "Its high great materials makes you feel invincible, or at least until someone cuts you in half with swords. (+1 to all stats)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "MEB Biofoam", "value": 200, "description": "Who the hell put this here?! (instantly heals all damage, no matter its severity)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Clown Mask", "value": 200, "description": "AAAAAAAAUGH I NEED A MEDIC BAG! (Gives a 50% price cut to any items bought from traders)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Drill", "value": 200, "description": "This drill is fucking worthless! (unlocks any locked item no matter the difficulty)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 3},
    {"name": "Persica Water", "value": 1, "description": "I found it in a vending machine at the police station. (Instantly heals all damage… but tastes awful)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "M16A1", "value": 300, "description": "Comes with a complimentary eyepatch! (+1 aim & agility when using item)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Cardboard Box", "value": 5, "description": "Huh… just a box. (makes you unable to be spotted, however you cannot do any actions)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Locked Case", "value": 1000, "description": "A locked gun case with green ribbons wrapped around its exterior. There is a 4 number combination lock with a griffin carved into the metal holding it shut.", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 3},
    {"name": "Lost Code", "value": 10, "description": "A lost 4 combination code with a griffin engraved on the back of the card", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Explosion Staff", "value": 10, "description": "A wooden staff wrapped in cloth around the handle with a red orb floating inside. (Allows the usage of the ‘Explosion’ spell)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Chunchunmaru", "value": 10, "description": "A short katana once wielded by a long lost hero. (+1 to all combat stats when using this item)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Stratagem", "value": 10, "description": "Unleashing Democracy! (calls in a free A-10 500kg strike on site that the item is thrown)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Space Stimulant", "value": 10, "description": "A little shot of liberty. (instantly heals all damage & grants +2 to all stats for the next turn)", "rarity": "Legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Weldless Metal Quickrepair", "value": 250, "description": "A small box with a handwritten label slapped on. The label reads ‘Weldless Metal Quickrepair. Simply apply the provided paste and pour the powder on and watch as the metal is instantly bonded, stronger than steel!’ The handwriting is overtly girly and signed Erin Baker on the bottom.", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Gatorade Zero", "value": 10, "description": "Is it in you?", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Percy’s Hat", "value": 100, "description": "the letters ‘HK’ are carved on the interior. (turns you into a complete asshole. -5 charisma with a +2 combat roll bonus)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "HK’s Beret", "value": 100, "description": "Commander, I am all you need. (+5 charisma when worn)", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Everclear", "value": 50, "description": "I just need to try a little harder. (immune to all damage for 1 turn)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "ALVMS MKII", "value": 1000, "description": "’Dispose of immediately’ is written on the side in red marker", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "James’ Beanie", "value": 25, "description": "A pretty cool beanie. (+5 charisma when worn, gives you the urge to rizz up Edytha)", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Carhartt Jacket", "value": 75, "description": "A fairly warm jacket. When worn, you feel the urge to kiss catgirls… (+3 strength, +2 charisma when worn)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Dreamcatcher", "value": 50, "description": "A fairly high quality Native American style dreamcatcher. (When hung up at a home base, all enemies are warded away no matter what)", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Mossberg 500", "value": 1000, "description": "A fairly high quality American made shotgun. The shotgun looks like it’s covered in like… blonde dog hair. (+2 aim when used, you feel patriotism coursing through your veins when you use it)", "rarity": "legendary", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Void Pocket", "value": 2147483647, "description": "A mysterious infinite black pit you can put stuff in.", "rarity": "mythic", "minrand": 1, "maxrand": 1, "inventoryslots": -2147483647},
    {"name": "Glowing Red Vial", "value": 75, "description": "All the labels are written in german, too bad im not reading it for you. (turns you into a Lesser Hexen when consumed)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "The Maid Outfit", "value": 500, "description": "Go ahead. Put it on. (curse of binding)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Helmet Chan’s Helmet", "value": 150, "description": "A green WW2 era tanker helmet with a large chunk of shrapnel buried inside. I think someone wants it back. (+2 Resistance, +1 Aim when worn)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Beaten M1911", "value": 300, "description": "Can take out a tiger! (+2 aim bonus)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Strange MP3 Player", "value": 300, "description": "looks like a normal MP3 player… dunno what else to tell you.", "rarity": "Common", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Pink Flip Phone", "value": 99, "description": "A small plastic pink flip phone, looks like it’s from the early 2000s. Somehow perfect condition… (when picked up, your hair turns purple and you lose -5 intelligence until put back down)", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "Strange Book", "value": 25, "description": "A leather backed book. On the inside cover is written [Silvia Henrikkson]. (when read, the reader slowly turns insane.", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "The Famas", "value": 500, "description": "EUGH UGH- GAH- FRENCH!", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 2},
    {"name": "Taint", "value": 15, "description": "A weird purple plant looking vine thing. It looks like it spreads very quickly, I’d probably destroy it immediately if I were you.", "rarity": "uncommon", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Roon’s Cross", "value": 1000, "description": "when you inch your hand closer, you hear ‘The March of Domination’ playing faintly in the background (turns you into a nazi temporarily and gives you the urge to min max in HOI4)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "American Flag", "value": 1000, "description": "WHAT THE FUCK IS A KILOMETER! (turns you into a hardcore american patriot temporarily)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "USSR Ushanka", "value":1000, "description": "A ring of steel surrounds your rotten city! We will crush all who dare to resist the will of the Red army! Abandon your posts! Abandon your homes! Abandon all hope! URA! (Turns you into a communist temporarily)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "GDR Cap", "value": 1000, "description": "EINS-ZWEI-DREI DIE BESTE PARTEI UND VIER FÜNF SECHS- (turns you into a Socialist and allows you to translate german temporarily)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Cat Ears Headband", "value": 1000, "description": "Hey pal, it's the wrong story. (curse of binding)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Persica’s Cat Headband", "value": 1000, "description": "”Hey there ho there.” (+2 intelligence & perception when worn)", "rarity": "Rare", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Ornate Knife", "value": 25, "description": "A very ornate silver knife with lots of complicated etchings in the blade. (when picked up, you feel the urge to cut yourself on your wrists)", "rarity": "rare", "minrand": 1, "maxrand": 1, "inventoryslots": 1},
    {"name": "ANNA Watch", "value": 5000, "description": "A watch from an unknown company, strangely enough there is an anglerfish carved into the underside of the watch’s frame… (grants the user the ANNA Personal Assistant)", "rarity": "Mythic", "minrand": 1, "maxrand": 1, "inventoryslots": 0},
    {"name": "Yukari’s Bag", "value": 5000, "description": "A lost bag belonging to a brilliant mechanical engineer from Oarai. (allows the usage of 2 special tech items when combined with the ‘ANNA Watch’.", "rarity": "Mythic", "minrand": 1, "maxrand": 1, "inventoryslots": -15},
]

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
                    if selected_item["quantity"] == 0:
                        current_inventory.pop(item_choice - 1)
                    print(f"Dropped {quantity_to_drop}x '{selected_item['name']}' and freed {freed_slots} slots.")
                    if freeslots >= total_slots_required:
                        print(f"You picked up {item['quantity']}x {item['name']}!")
                        freeslots -= total_slots_required
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
    global current_inventory, current_inventory_name, freeslots, storage
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("Inventory Management")
        print(f"Current Inventory: {current_inventory_name or 'None'}")
        print("")
        options = ["Create New Inventory", "Save Current Inventory", "Load Inventory", "View Current Inventory", 
                   "Remove Item from Inventory", "Move Items to/from Storage", "Transfer Saves from Previous Versions", 
                   "Delete Saves", "Back to Main Menu"]
        print_menu(options)
        choice = get_user_choice(len(options))

        if choice == 1:
            current_inventory_name = input("Enter a name for the new inventory: ").strip() + ".save"
            current_inventory = []
            freeslots = 10
            storage = []
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
                print("Available Inventories:")
                print_menu(files)
                file_choice = get_user_choice(len(files))
                current_inventory_name = files[file_choice - 1]
                current_inventory = load_inventory_from_file(current_inventory_name) or []
                if not current_inventory_name:
                    print("No inventory loaded! Please load or create an inventory first.")
                    input("Press any key to continue...")
                    continue
                print(f"Loaded inventory '{current_inventory_name}'.")
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
        elif choice == 8:
            os.system("cls" if os.name == "nt" else "clear")
            print("Delete Save Files")
            files = [f for f in os.listdir(saves_folder) if f.endswith(".save")]
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
            break
        input("Press any key to continue...")

def check_for_updates():
    try:
        response = requests.get("https://raw.githubusercontent.com/soli-dstate/lootingprogram-py/main/version.txt")
        if response.status_code == 200:
            latest_version = response.text.strip()
            if latest_version != version:
                print(f"Update available! Current version: {version}, Latest version: {latest_version}")
                print("Please visit the repository to download the latest version.")
            else:
                print("You are using the latest version.")
        else:
            print("Failed to check for updates. Unable to access version file.")
    except Exception as e:
        print(f"Error checking for updates: {e}")

def main():
    global current_inventory_name
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(f"Loot {version}")
        check_for_updates()
        print(f"Current Inventory: {current_inventory_name or 'None'}")
        print("")
        main_options = ["Easy Loot", "Inventory Management", "Exit"]
        print_menu(main_options)
        choice = get_user_choice(len(main_options))

        if choice == 1:
            if not current_inventory_name:
                print("No inventory loaded! Please load or create an inventory first.")
                input("Press any key to continue...")
            else:
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
        elif choice == 2:
            manage_inventory()
        elif choice == 3:
            break

if __name__ == "__main__":
    main()