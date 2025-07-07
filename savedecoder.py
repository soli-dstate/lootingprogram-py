import os
import base64
import json

SAVE_FOLDER = "./saves/"

def decode_save_file(filename):
    """
    Decodes a .save file from base64 and writes the JSON content to a .py file.
    """
    save_path = os.path.join(SAVE_FOLDER, filename)
    if not filename.endswith('.save'):
        raise ValueError("Input file must have a .save extension.")
    py_filename = filename.replace('.save', '.py')
    py_path = os.path.join(SAVE_FOLDER, py_filename)

    with open(save_path, "rb") as f:
        encoded = f.read()
    decoded_bytes = base64.b64decode(encoded)
    decoded_str = decoded_bytes.decode("utf-8")
    try:
        data = json.loads(decoded_str)
        pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
    except Exception:
        pretty_json = decoded_str

    with open(py_path, "w", encoding="utf-8") as f:
        f.write(pretty_json)

    return py_path

def encode_save_file(py_filename):
    """
    Encodes a .py file (containing JSON) to base64 and writes it as a .save file.
    """
    py_path = os.path.join(SAVE_FOLDER, py_filename)
    if not py_filename.endswith('.py'):
        raise ValueError("Input file must have a .py extension.")
    save_filename = py_filename.replace('.py', '.save')
    save_path = os.path.join(SAVE_FOLDER, save_filename)
    with open(py_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        json.loads(content)
    except Exception:
        pass
    encoded = base64.b64encode(content.encode("utf-8"))
    with open(save_path, "wb") as f:
        f.write(encoded)

    return save_path

def list_save_files():
    """
    Lists all .save files in the SAVE_FOLDER directory.
    """
    return [f for f in os.listdir(SAVE_FOLDER) if f.endswith('.save')]

def main():
    print("Available .save files:")
    save_files = list_save_files()
    for idx, fname in enumerate(save_files, 1):
        print(f"{idx}. {fname}")

    print("\nOptions:")
    print("1. Decode a .save file to .py")
    print("2. Encode a .py file to .save")
    choice = input("Enter your choice (1/2): ").strip()
    if choice == "1":
        file_idx = int(input("Enter the number of the .save file to decode: ").strip())
        if 1 <= file_idx <= len(save_files):
            py_path = decode_save_file(save_files[file_idx - 1])
            print(f"Decoded to {py_path}")
        else:
            print("Invalid selection.")
    elif choice == "2":
        py_files = [f for f in os.listdir(SAVE_FOLDER) if f.endswith('.py')]
        print("Available .py files:")
        for idx, fname in enumerate(py_files, 1):
            print(f"{idx}. {fname}")
        file_idx = int(input("Enter the number of the .py file to encode: ").strip())
        if 1 <= file_idx <= len(py_files):
            save_path = encode_save_file(py_files[file_idx - 1])
            print(f"Encoded to {save_path}")
        else:
            print("Invalid selection.")
    else:
        print("Invalid choice.")
        
main()