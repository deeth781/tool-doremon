import os, sys, json, base64, requests, time
import importlib.util
from pathlib import Path
from colorama import init, Fore
from random import choice
from platform import system

init()

# ====== CÀI THƯ VIỆN ====== #
try:
    import pyfiglet
except ImportError:
    os.system("pip install pyfiglet colorama requests")
    import pyfiglet

# ====== THƯ MỤC TOOL ====== #
TOOL_DIR = ".tools"  # dấu chấm để ẩn thư mục

def fake_typing(text, delay=0.02):
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def ascii_title(text):
    fonts = ["slant", "standard", "3-d", "3x5", "banner3-D", "isometric1", "bubble", "digital"]
    font = choice(fonts)
    return pyfiglet.figlet_format(text, font=font)

def download_menu():
    MENU_URL = "https://raw.githubusercontent.com/deeth781/tool-doremon/main/menu.json"
    response = requests.get(MENU_URL)
    if response.status_code != 200:
        print(Fore.RED + "[!] Không tải được menu.json")
        sys.exit()
    return response.json()

def decode_base64_url(b64):
    return base64.b64decode(b64.encode()).decode()

def download_and_run_tool(tool):
    name = tool["name"]
    url = decode_base64_url(tool["code"])
    filename = url.split("/")[-1]

    Path(TOOL_DIR).mkdir(exist_ok=True)
    path = os.path.join(TOOL_DIR, filename)

    # Tải file về
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        print(Fore.GREEN + f"[✓] Đã tải {filename}")
    except:
        print(Fore.RED + f"[!] Lỗi khi tải {filename}")
        return

    # Chạy file
    try:
        spec = importlib.util.spec_from_file_location("module.name", path)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
    except Exception as e:
        print(Fore.RED + f"[!] Lỗi khi chạy {filename}: {e}")

def hide_folder(path):
    if system() == "Windows":
        os.system(f'attrib +h "{path}"')
    else:
        # UNIX hệ thống đã mặc định ẩn với "." đầu tên
        pass

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + ascii_title("Minato CLI Tool"))
    fake_typing(Fore.YELLOW + "[•] Đang tải menu...", 0.03)

    tools = download_menu()
    hide_folder(TOOL_DIR)

    for i, tool in enumerate(tools):
        print(Fore.GREEN + f"{i+1}. {tool['name']}")
    print()

    try:
        choice_index = int(input(Fore.CYAN + "Chọn tool (số): ")) - 1
        if choice_index not in range(len(tools)):
            raise ValueError
        download_and_run_tool(tools[choice_index])
    except:
        print(Fore.RED + "[!] Lựa chọn không hợp lệ")

    # Xóa menu.json gốc (nếu tồn tại)
    menu_file = "menu.json"
    if os.path.exists(menu_file):
        os.remove(menu_file)

if __name__ == "__main__":
    main()
