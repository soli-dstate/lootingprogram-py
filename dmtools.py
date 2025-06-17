import os
from packaging import version as ver
import requests
import zipfile
import shutil
import json
import re
import base64
import uuid

version = "1.0.0" # provide version number for comparing to github

developmentcopy = False

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

def check_for_updates(): # define function for checking updates
    try: # use try incase any exceptions reveal themselves
        response = requests.get("https://raw.githubusercontent.com/soli-dstate/lootingprogram-py/main/dmtools.py") # check the dmtools.py file from the github
        if response.status_code == 200: # html code 200; means that the server came back okay
            lines = response.text.splitlines() # splits everything into individual lines
            latest_version = None # defines the latest version as none
            for line in lines:
                if line.strip().startswith("version"): # look for the line that says version
                    parts = line.split("=") # split it with equal
                    if len(parts) == 2: # divide it into x.x.x
                        latest_version = parts[1].strip().strip('"').strip("'")
                        break
            if not latest_version: # provide a solution as to not throw an exception if something goes wrong
                print("Could not determine latest version from dmtools.py.")
                return
            if latest_version != version: # if the latest version and current version don't match, run this
                if ver.parse(version) > ver.parse(latest_version): # if the latest version is bigger than the current version don't update anything (so i don't overwrite my code lolol)
                    print(f"Prerelease copy detected! Current version: {version}, Latest version: {latest_version}")
                    global developmentcopy
                    developmentcopy = True # set developmentcopy to true to enable dev tools
                else: # we don't need to check for anything else as we only need to know if the current revision is later on than the one on github
                    print(f"Update available! Current version: {version}, Latest version: {latest_version}")
                    print("Would you like to update now? (y/n): ", end="")
                    update_choice = input().strip().lower() # get user input with a y/n statement
                    if update_choice != "y":
                        print("Update skipped. You can update later by restarting the program.")
                        return
                    print("Attempting to auto-update from GitHub...")
                    current_dir = os.path.dirname(os.path.abspath(__file__)) # define where the script is located for later
                    if os.name == "nt": # check if this is a windows system
                        exe_name = None # define the exe name as none
                        for name in os.listdir(current_dir): # look for the exe in the script's directory
                            if name.lower().endswith(".exe"):
                                exe_name = name # set the exe's name to the name of the exe... that doesn't even make sense but just trust lol
                                break
                        if not exe_name: # maybe you're a cool guy/gal/genderneutralword and wanna run the python files raw like me
                            for name in os.listdir(current_dir):
                                if name.lower().endswith(".py"): # so now we lookin for the python
                                    exe_name = name
                                    break
                        zip_url = None # define the zip url name as none
                        possible_names = [
                            "dmtools.zip",
                            "dmtools_compiled.zip",
                            "dmtools-compiled.zip",
                            "dmtools.python_compiled.zip",
                            "main.zip"
                        ] # these are lists of names that i would probably set it to, this'll probably bite me in the ass in the future though lol
                        try:
                            releases = requests.get("https://api.github.com/repos/soli-dstate/lootingprogram-py/releases").json() # better get the latest release from github and put it into a json
                            if isinstance(releases, list) and releases:
                                for asset in releases[0].get("assets", []):
                                    if asset["name"].endswith(".zip"):
                                        zip_url = asset["browser_download_url"]
                                        break # try to find the zip url without doing it manually
                        except Exception: # pass everything if there's an exception
                            pass
                        if not zip_url: # shit done hit the fan and now we gotta bruteforce this bad boy
                            for name in possible_names:
                                test_url = f"https://github.com/soli-dstate/lootingprogram-py/raw/main/{name}" # check every url possibility from the possible names
                                r = requests.head(test_url)
                                if r.status_code == 200: # if we got code 200, we got a match!
                                    zip_url = test_url # set the zip url to the url we tested and got a match for
                                    break
                        if not zip_url: # maybe we found nothing because i'm an idiot and did something dumb
                            print("Could not find update zip file automatically. Please update manually.") # better tell you so you can tell me
                            return
                        print(f"Downloading update from: {zip_url}") # otherwise, we be downloading that update now yo
                        r = requests.get(zip_url, stream=True) # now we actually gotta get the url
                        update_zip = os.path.join(current_dir, "update_temp.zip") # we don't actually need everything that we download, so we can just delete this after we extract the exe
                        with open(update_zip, "wb") as f: # open the zip file in write mode
                            for chunk in r.iter_content(chunk_size=8192): # use 8192 byte chunks
                                f.write(chunk) # write the data to each chunk
                        print("Download complete. Extracting update...")
                        extract_folder = os.path.join(current_dir, "dmtools_update_temp") # define the folder to extract to
                        with zipfile.ZipFile(update_zip, "r") as zip_ref: # use zipfile to extract the zip
                            zip_ref.extractall(extract_folder) # extract it to the folder we defined earlier
                        new_file = None # define the new file downloaded from the internet as none
                        for root, dirs, files in os.walk(extract_folder):
                            for file in files:
                                if file.lower().endswith(".exe") or file.lower().endswith(".py"):
                                    new_file = os.path.join(root, file) # extract the exe or .py
                                    break
                            if new_file:
                                break
                        if not new_file: # make room for error and stuff
                            print("Could not find new program file in update. Update failed.")
                            return
                        if exe_name:
                            try:
                                os.remove(os.path.join(current_dir, exe_name)) # remove the old exe
                            except Exception:
                                pass
                        shutil.copy2(new_file, current_dir) # copy the new exe or python file over
                        print(f"Updated file copied to {current_dir}.")
                        try:
                            os.remove(update_zip) # remove the zip
                        except Exception:
                            pass
                        try:
                            shutil.rmtree(extract_folder) # remove the folder we extracted to
                        except Exception:
                            pass
                        print("Update complete. Please restart the program.")
                        input("Press Enter to exit...")
                        os._exit(0)
                    else: # same as above but only for .py files as this is for non-windows systems. i don't develop this for mac cause none of y'all use it lol
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
                        extract_folder = os.path.join(current_dir, "dmtools_update_source")
                        with zipfile.ZipFile(update_zip, "r") as zip_ref:
                            zip_ref.extractall(extract_folder)
                        new_py = None
                        for root, dirs, files in os.walk(extract_folder):
                            for file in files:
                                if file == "dmtools.py":
                                    new_py = os.path.join(root, file)
                                    break
                            if new_py:
                                break
                        if not new_py:
                            print("Could not find new dmtools.py in update. Update failed.")
                            return
                        if py_name:
                            try:
                                os.remove(os.path.join(current_dir, py_name))
                            except Exception:
                                pass
                        shutil.copy2(new_py, os.path.join(current_dir, "dmtools.py"))
                        print(f"Updated dmtools.py copied to {current_dir}.")
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
                        os._exit(0)
            else:
                print("You are using the latest version.")
        else:
            print("Failed to check for updates. Unable to access dmtools.py.")
    except Exception as e:
        print(f"Error checking for updates: {e}")
        
def createtable(): # define createtable def
    os.system("cls" if os.name == "nt" else "clear")
    choice = input("Would you like to create a new table? (y/n): ").strip().lower()
    if choice == "y":
        tables_dir = "tables"
        os.makedirs(tables_dir, exist_ok=True)  # create the tables directory if it doesn't exist
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            tablename = input("Enter the name of the table: ").strip()
            if not tablename:  # if the user didn't enter a name, we just use "table"
                tablename = "table"
            table_path = os.path.join(tables_dir, f"{tablename}.json")
            if os.path.exists(table_path):
                print(f"A table named '{tablename}' already exists. Please choose a different name.")
                input("Press any key to continue...")
                continue
            else:
                break
        with open(table_path, "w") as f:  # create the json file in tables
            f.write("[]")
        print(f"Table '{tablename}' created successfully.")
        input("Press any key to continue...")
    else:
        print("Table creation cancelled.")
        input("Press any key to continue...")
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        options = ["Add item to table", "View table", "Finalize table"]
        print_menu(options)
        choice = get_user_choice(len(options))
        if choice == 1:
            name = None
            value = None
            description = None
            rarity = None
            minrand = 1
            maxrand = None
            inventoryslots = None
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                name = input("Enter the name of the item to add: ").strip()
                if not name:
                    print("Item name cannot be empty. Please try again.")
                    input("Press any key to continue...")
                    continue
                if name:
                    break
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                value = input("Enter the value of the item (in gold): ").strip()
                if not value.isdigit():
                    print("Value must be a number. Please try again.")
                    input("Press any key to continue...")
                    continue
                value = int(value)
                break
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                description = input("Enter a description for the item: ").strip()
                if not description:
                    print("Description cannot be empty. Please try again.")
                    input("Press any key to continue...")
                    continue
                break
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                rarities = ["Common", "Uncommon", "Rare", "Legendary", "Mythic"]
                print("Select the rarity of the item:")
                print_menu(rarities)
                rarity_choice = get_user_choice(len(rarities))
                rarity = rarities[rarity_choice - 1]
                break
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                minrand = input("Enter the minimum random value (default is 1): ").strip()
                if not minrand.isdigit():
                    print("Minimum random value must be a number. Please try again.")
                    input("Press any key to continue...")
                    continue
                minrand = int(minrand) if minrand else 1
                break
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                maxrand = input("Enter the maximum random value for this item. Set to 1 if you only want the player to find one of this item: ")
                if not maxrand.isdigit():
                    print("Maximum random value must be a number. Please try again.")
                    input("Press any key to continue...")
                    continue
                if not maxrand:
                    print("Maximum random value cannot be empty. Please try again.")
                    input("Press any key to continue...")
                    continue
                maxrand = int(maxrand)
                if maxrand < minrand:
                    print("Maximum random value must be greater than or equal to minimum random value. Please try again.")
                    input("Press any key to continue...")
                    continue
                break
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                inventoryslots = input("Enter the number of inventory slots this item takes up (set to 0 to take up none): ").strip()
                if not inventoryslots.isdigit():
                    print("Inventory slots must be a number. Please try again.")
                    input("Press any key to continue...")
                    continue
                if not inventoryslots:
                    print("Inventory slots cannot be empty. Please try again.")
                    input("Press any key to continue...")
                    continue
                inventoryslots = int(inventoryslots)
                if inventoryslots < 0:
                    print("Inventory slots cannot be negative. Please try again.")
                    input("Press any key to continue...")
                    continue
                break
            table_path = os.path.join(tables_dir, f"{tablename}.json")
            existing_ids = set()
            tables_dir = "tables"
            for fname in os.listdir(tables_dir):
                if fname.endswith(".json"):
                    with open(os.path.join(tables_dir, fname), "r") as tf:
                        try:
                            data = json.load(tf)
                            if isinstance(data, list):
                                for item in data:
                                    if "id" in item:
                                        existing_ids.add(item["id"])
                        except Exception:
                            continue
            try:
                mp_url = "https://raw.githubusercontent.com/soli-dstate/lootingprogram-py/main/mainprogram.py"
                mp_response = requests.get(mp_url, timeout=5)
                if mp_response.status_code == 200:
                    ids_in_mp = set(map(int, re.findall(r'"id"\s*:\s*(\d+)', mp_response.text)))
                    existing_ids.update(ids_in_mp)
            except Exception:
                pass
            if os.path.exists(table_path):
                with open(table_path, "r") as f:
                    try:
                        table_data = json.load(f)
                        if not isinstance(table_data, list):
                            table_data = []
                    except json.JSONDecodeError:
                        table_data = []
            else:
                table_data = []
            item_id = 0
            while item_id in existing_ids:
                item_id += 1

            item = {
                "name": name,
                "value": value,
                "description": description,
                "rarity": rarity,
                "minrand": minrand,
                "maxrand": maxrand,
                "inventoryslots": inventoryslots,
                "id": item_id
            }
            table_data.append(item)
            with open(table_path, "w") as f:
                json.dump(table_data, f, indent=4)

            print(f"Item '{name}' added to table '{tablename}' with unique id {item_id}.")
            input("Press any key to continue...")
        if choice == 2:
            os.system("cls" if os.name == "nt" else "clear")
            table_path = os.path.join(tables_dir, f"{tablename}.json")
            if os.path.exists(table_path):
                with open(table_path, "r") as f:
                    try:
                        table_data = json.load(f)
                        if not isinstance(table_data, list):
                            print("Table is empty or not formatted correctly.")
                            input("Press any key to continue...")
                            return
                        print(f"Items in table '{tablename}':")
                        for item in table_data:
                            print(f"ID: {item.get('id', 'N/A')}, Name: {item['name']}, Value: {item['value']}, Description: {item['description']}, Rarity: {item['rarity']}, Min Rand: {item['minrand']}, Max Rand: {item['maxrand']}, Inventory Slots: {item['inventoryslots']}")
                    except json.JSONDecodeError:
                        print("Table is empty or not formatted correctly.")
            else:
                print(f"Table '{tablename}' does not exist.")
            input("Press any key to continue...")
        if choice == 3:
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                computersafename = input("Please enter a computer-safe name for the table that is unique: ").strip()
                if not computersafename:
                    print("Computer-safe name cannot be empty. Please try again.")
                    input("Press any key to continue...")
                    continue
                if not re.match(r'^[a-zA-Z0-9_]+$', computersafename) or ' ' in computersafename:
                    print("Computer-safe name can only contain letters, numbers, and underscores (no spaces). Please try again.")
                    input("Press any key to continue...")
                    continue
                break
            table_path = os.path.join(tables_dir, f"{tablename}.json")
            finished_dir = "finishedtables"
            os.makedirs(finished_dir, exist_ok=True)
            if os.path.exists(table_path):
                with open(table_path, "r") as f:
                    try:
                        table_data = json.load(f)
                        if not isinstance(table_data, list):
                            print("Table is empty or not formatted correctly.")
                            input("Press any key to continue...")
                            return
                    except json.JSONDecodeError:
                        print("Table is empty or not formatted correctly.")
                        input("Press any key to continue...")
                        return
                py_table = f"{computersafename} = {json.dumps(table_data, indent=4)}"
                py_table_path = os.path.join(finished_dir, f"{computersafename}_table.json")
                with open(py_table_path, "w") as pyf:
                    pyf.write(py_table)
                print(f"Python table saved as '{py_table_path}'.")
                shutil.move(table_path, os.path.join(finished_dir, f"{tablename}.json"))
            else:
                print(f"Table '{tablename}' does not exist.")
            input("Press any key to continue...")
            break
            
def createitem(): # define createitem def
    os.system("cls" if os.name == "nt" else "clear")
    choice = input("Would you like to create a new item? (y/n): ").strip().lower()
    if choice == "y":
        name = None
        value = None
        description = None
        rarity = None
        minrand = 1
        maxrand = None
        inventoryslots = None
        quantity = None
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            name = input("Enter the name of the item: ").strip()
            if not name:
                print("Item name cannot be empty. Please try again.")
                input("Press any key to continue...")
                continue
            break
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            value = input("Enter the value of the item (in gold): ").strip()
            if not value.isdigit():
                print("Value must be a number. Please try again.")
                input("Press any key to continue...")
                continue
            value = int(value)
            break
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            description = input("Enter a description for the item: ").strip()
            if not description:
                print("Description cannot be empty. Please try again.")
                input("Press any key to continue...")
                continue
            break
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            rarities = ["Common", "Uncommon", "Rare", "Legendary", "Mythic"]
            print("Select the rarity of the item:")
            print_menu(rarities)
            rarity_choice = get_user_choice(len(rarities))
            rarity = rarities[rarity_choice - 1]
            break
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            minrand = input("Enter the minimum random value (default is 1): ").strip()
            if not minrand.isdigit():
                print("Minimum random value must be a number. Please try again.")
                input("Press any key to continue...")
                continue
            minrand = int(minrand) if minrand else 1
            break
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            maxrand = input("Enter the maximum random value for this item. Set to 1 if you only want the player to find one of this item: ")
            if not maxrand.isdigit():
                print("Maximum random value must be a number. Please try again.")
                input("Press any key to continue...")
                continue
            if not maxrand:
                print("Maximum random value cannot be empty. Please try again.")
                input("Press any key to continue...")
                continue
            maxrand = int(maxrand)
            if maxrand < minrand:
                print("Maximum random value must be greater than or equal to minimum random value. Please try again.")
                input("Press any key to continue...")
                continue
            break
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            inventoryslots = input("Enter the number of inventory slots this item takes up (set to 0 to take up none): ").strip()
            if not inventoryslots.isdigit():
                print("Inventory slots must be a number. Please try again.")
                input("Press any key to continue...")
                continue
            if not inventoryslots:
                print("Inventory slots cannot be empty. Please try again.")
                input("Press any key to continue...")
                continue
            inventoryslots = int(inventoryslots)
            if inventoryslots < 0:
                print("Inventory slots cannot be negative. Please try again.")
                input("Press any key to continue...")
                continue
            break
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            quantity = input("Enter the quantity of this item: ").strip()
            if not quantity.isdigit():
                print("Quantity must be a number. Please try again.")
                input("Press any key to continue...")
                continue
            if not quantity:
                print("Quantity cannot be empty. Please try again.")
                input("Press any key to continue...")
                continue
            quantity = int(quantity) if quantity else 1
            if quantity <= 0:
                print("Quantity must be greater than 0. Please try again.")
                input("Press any key to continue...")
                continue
            break
        item = {
            "name": name,
            "value": value,
            "description": description,
            "rarity": rarity,
            "minrand": minrand,
            "maxrand": maxrand,
            "inventoryslots": inventoryslots,
            "quantity": quantity,
            "transfer_id": str(uuid.uuid4()),
            "transfer_time": None,
            "transfer_type": "item"
        }
        encoded_item = base64.b64encode(json.dumps(item).encode("utf-8")).decode("utf-8")
        os.makedirs("items", exist_ok=True)
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()
        item_file = os.path.join("items", f"{safe_name}.transfer")
        with open(item_file, "w") as f:
            f.write(encoded_item)
        print(f"Item transfer file saved as '{item_file}'.")
        input("Press any key to continue...")
        
def creategold(): # define creategold def
    os.system("cls" if os.name == "nt" else "clear")
    choice = input("Would you like to create a new gold transfer? (y/n): ").strip().lower()
    if choice == "y":
        amount = None
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            amount = input("Enter the amount of gold to transfer: ").strip()
            if not amount.isdigit():
                print("Amount must be a number. Please try again.")
                input("Press any key to continue...")
                continue
            amount = int(amount)
            if amount <= 0:
                print("Amount must be greater than 0. Please try again.")
                input("Press any key to continue...")
                continue
            break
        gold_transfer = {
            "amount": amount,
            "transfer_id": str(uuid.uuid4()),
            "transfer_time": None,
            "transfer_type": "gold"
        }
        encoded_gold = base64.b64encode(json.dumps(gold_transfer).encode("utf-8")).decode("utf-8")
        os.makedirs("gold", exist_ok=True)
        transfer_file = os.path.join("gold", f"gold_{gold_transfer['transfer_id']}.transfer")
        with open(transfer_file, "w") as f:
            f.write(encoded_gold)
        print(f"Gold transfer file saved as '{transfer_file}'.")
        input("Press any key to continue...")
            
def main(): # define main def
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        check_for_updates()
        print("DM Tools")
        mainoptions = ["Create table", "Create item for transfer", "Create gold for transfer", "Exit"]
        print_menu(mainoptions)
        choice = get_user_choice(len(mainoptions))
        if choice == 1:
            createtable()
        if choice == 2:
            createitem()
        if choice == 3:
            creategold()
        if choice == 4:
            break
        
main()
