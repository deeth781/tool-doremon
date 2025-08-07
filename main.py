import os
import json
import base64
import requests
import subprocess
import importlib.util
from time import sleep
from pathlib import Path
from typing import Dict
from pyfiglet import Figlet
from termcolor import colored

# ====== CONFIG ======
MENU_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/menu.json"  # <- Thay link tại đây
ENCODED_MENU_FILE = "menu_encoded.json"
HIDDEN_DIR = ".data_tool_hidden"

# Tạo thư mục ẩn nếu chưa có
os.makedirs(HIDDEN_DIR, exist_ok=True)

# Fake typing
def fake_type(text, delay=0.01):
    for char in text:
        print(char, end='', flush=True)
        sleep(delay)
    print()

# Loading effect
def loading(msg="Đang khởi chạy tool"):
    for _ in range(3):
        print(f"{msg}.", end="\r")
        sleep(0.2)
        print(f"{msg}..", end="\r")
        sleep(0.2)
        print(f"{msg}...", end="\r")
        sleep(0.2)
    print(" " * 50, end="\r")

# Tải file và mã hóa base64
def fetch_and_encode_menu(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        encoded = base64.b64encode(response.text.encode()).decode()
        with open(ENCODED_MENU_FILE, "w") as f:
            json.dump({"data": encoded}, f)
        return encoded
    else:
        raise Exception("Không thể tải menu.json")

# Giải mã menu
def decode_menu_file(filepath: str) -> Dict:
    with open(filepath, "r") as f:
        data = json.load(f)
    decoded = base64.b64decode(data["data"]).decode()
    return json.loads(decoded)

# Tự cài thư viện nếu thiếu
def ensure_requirements():
    try:
        import pyfiglet
        import termcolor
    except ImportError:
        subprocess.check_call(["pip", "install", "pyfiglet", "termcolor"])

# Hiển thị menu đẹp
def show_ascii_title():
    f = Figlet(font='slant')
    print(colored(f.renderText('Main Tool'), 'cyan'))

# Hiển thị menu các tool con
def show_menu(menu: Dict):
    for i, tool in enumerate(menu["tools"], 1):
        print(colored(f"[{i}] {tool['name']}", 'green'))

# Tải và chạy tool con
def run_tool(tool: Dict):
    tool_url = tool["url"]
    tool_filename = os.path.join(HIDDEN_DIR, tool["name"] + ".py")
    if not os.path.exists(tool_filename):
        with open(tool_filename, "w") as f:
            f.write(requests.get(tool_url).text)
    subprocess.run(["python", tool_filename])

# Xóa file menu gốc
def secure_delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)

# MAIN
def main():
    ensure_requirements()
    show_ascii_title()
    loading("Đang tải menu")
    encoded = fetch_and_encode_menu(MENU_URL)
    menu = decode_menu_file(ENCODED_MENU_FILE)
    secure_delete_file(ENCODED_MENU_FILE)
    fake_type("Menu đã tải và mã hóa. Danh sách tool:", 0.03)
    show_menu(menu)

    try:
        choice = int(input(colored("Chọn tool để chạy: ", "yellow")))
        if 1 <= choice <= len(menu["tools"]):
            run_tool(menu["tools"][choice - 1])
        else:
            print(colored("Lựa chọn không hợp lệ!", "red"))
    except Exception as e:
        print(colored(f"Lỗi: {e}", "red"))

if __name__ == "__main__":
    main()
