import os
import sys
import base64
import json

EXCLUDED_FILES = ["previousinventory.save", "trader.save", "transfers.save"]

def get_base_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)

def main():
    base_dir = get_base_dir()
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        saves_dir = os.path.join(base_dir, 'saves')
    else:
        saves_dir = os.path.join(base_dir, '..', 'saves')
    saves_dir = os.path.abspath(saves_dir)
    saves = [
        f for f in os.listdir(saves_dir)
        if os.path.isfile(os.path.join(saves_dir, f)) and f not in EXCLUDED_FILES
    ]

    if not saves:
        print("No save files found.")
        return

    print("Available saves:")
    for idx, save in enumerate(saves):
        print(f"{idx + 1}: {save}")

    choice = input("Select a save file by number: ")
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(saves):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return

    save_file = saves[idx]
    save_path = os.path.join(saves_dir, save_file)

    with open(save_path, 'rb') as f:
        encoded = f.read()

    try:
        decoded = base64.b64decode(encoded)
        data = json.loads(decoded.decode('utf-8'))
    except Exception as e:
        print(f"Failed to decode or parse save: {e}")
        return

    data['name'] = os.path.splitext(save_file)[0]
    data['version'] = "3.0.9"

    new_encoded = base64.b64encode(json.dumps(data).encode('utf-8'))

    with open(save_path, 'wb') as f:
        f.write(new_encoded)

    print(f"Save '{save_file}' updated successfully.")
