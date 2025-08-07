
import os, re, time, random, sys, socket, platform, getpass
from datetime import datetime, timedelta


REQUIRED = ["requests", "pyfiglet", "colorama", "tabulate", "psutil"]
for lib in REQUIRED:
    try:
        __import__(lib)
    except:
        os.system(f"pip install {lib}")

import requests
import pyfiglet
from colorama import init, Fore, Style
from tabulate import tabulate
import psutil

init(autoreset=True)
BANNER_FONTS = [
    "slant", "3-d", "3x5", "5lineoblique", "alligator", "alligator2", "block",
    "bubble", "bulbhead", "digital", "doom", "isometric1", "isometric2",
    "letters", "nancyj", "ogre", "rectangles", "speed", "starwars", "sub-zero"
]
BANNERS = []
for f in BANNER_FONTS:
    try:
        BANNERS.append(pyfiglet.figlet_format("Doremon", font=f))
    except pyfiglet.FontNotFound:
        pass

def clear_console():
    try:
        os.system("clear" if os.name != "nt" else "cls")
    except:
        print("\033c", end="")

def fake_typing(msg, delay=0.02):
    for ch in msg:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def loading_bar(text, duration=1.5, length=30):
    print(Fore.CYAN + text, end="", flush=True)
    for _ in range(length):
        print(Fore.BLUE + "█", end="", flush=True)
        time.sleep(duration / length)
    print(Style.RESET_ALL)

def section(title):
    print("\n" + Fore.MAGENTA + ">>" + "="*40)
    print(Fore.LIGHTYELLOW_EX + f"🧩 {title}")
    print(Fore.MAGENTA + "="*42 + "\n")

def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(timedelta(seconds=int(uptime_seconds)))
    except:
        try:
            return time.strftime("%H:%M:%S", time.gmtime(time.time() - psutil.boot_time()))
        except:
            return "Không xác định"

def system_info():
    uptime = get_uptime()
    cpu_percent = psutil.cpu_percent(interval=1)
    print(Fore.CYAN + random.choice(BANNERS))
    print(Fore.YELLOW + f"🖥️  OS: {platform.system()} {platform.release()}")
    print(Fore.YELLOW + f"👤 User: {getpass.getuser()}")
    print(Fore.YELLOW + f"📡 IP: {socket.gethostbyname(socket.gethostname())}")
    print(Fore.YELLOW + f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(Fore.YELLOW + f"💾 RAM: {round(psutil.virtual_memory().used / (1024 ** 3), 2)} GB")
    print(Fore.YELLOW + f"🔥 CPU Usage: {cpu_percent}%")
    print(Fore.YELLOW + f"⏱️  Uptime (OS): {uptime}")
    print("="*60)


class Messenger:
    def __init__(self, cookie, box_id):
        self.cookie = cookie
        self.box_id = box_id
        self.session = requests.Session()
        self.user_id = self.get_user_id()
        self.fb_dtsg = None
        self.success = 0
        self.fail = 0
        self.start_time = datetime.now()
        self.init_params()

    def get_user_id(self):
        match = re.search(r"c_user=(\d+)", self.cookie)
        if not match:
            raise Exception("❌ Cookie không hợp lệ")
        return match.group(1)

    def init_params(self):
        headers = {'Cookie': self.cookie, 'User-Agent': 'Mozilla/5.0'}
        urls = ['https://mbasic.facebook.com', 'https://m.facebook.com', 'https://www.facebook.com']
        for url in urls:
            try:
                res = self.session.get(url, headers=headers, timeout=10)
                match = re.search(r'name=[\"\']fb_dtsg[\"\'] value=[\"\'](.*?)[\"\']', res.text)
                if match:
                    self.fb_dtsg = match.group(1)
                    return
            except:
                continue
        raise Exception("❌ Không tìm thấy fb_dtsg")

    def send_message(self, box_id, message):
        if not self.fb_dtsg:
            return False
        timestamp = str(int(time.time() * 1000))
        data = {
            'fb_dtsg': self.fb_dtsg,
            '__user': self.user_id,
            'body': message,
            'action_type': 'ma-type:user-generated-message',
            'timestamp': timestamp,
            'offline_threading_id': timestamp,
            'message_id': timestamp,
            'thread_fbid': box_id,
            'source': 'source:chat:web',
            'client': 'mercury'
        }
        headers = {
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        try:
            res = self.session.post('https://www.facebook.com/messaging/send/', data=data, headers=headers, timeout=10)
            if res.status_code == 200:
                self.success += 1
                return True
            else:
                self.fail += 1
                return False
        except:
            self.fail += 1
            return False

    def get_uptime(self):
        return str(datetime.now() - self.start_time).split('.')[0]


if __name__ == "__main__":
    clear_console()
    system_info()

    section("NHẬP THÔNG TIN")
    cookies = input(Fore.CYAN + "Nhập nhiều cookie (phân tách bằng |):\n> ").strip().split("|")
    box_id = input(Fore.CYAN + "Nhập ID box (thread_fbid): ").strip()
    file_name = input(Fore.CYAN + "Nhập tên file chứa tin nhắn (.txt): ").strip()
    delay = float(input(Fore.CYAN + "⏱️  Nhập delay giữa mỗi tin nhắn (giây): ").strip())

    section("ĐỌC FILE")
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            messages = [line.strip() for line in f if line.strip()]
        print(Fore.GREEN + f"✅ Đã tải {len(messages)} tin nhắn từ file {file_name}")
    except:
        print(Fore.RED + f"❌ Không tìm thấy file {file_name}")
        sys.exit()

    section("KHỞI TẠO BOT")
    bots = []
    for idx, cookie in enumerate(cookies, 1):
        try:
            fake_typing(f"🤖 Bot #{idx} đăng nhập...")
            bot = Messenger(cookie.strip(), box_id)
            print(Fore.GREEN + f"✅ Cookie #{idx} → UID: {bot.user_id}")
            bots.append((idx, bot))
        except Exception as e:
            print(Fore.RED + f"❌ Cookie #{idx} lỗi: {e}")

    section("BẮT ĐẦU GỬI TIN")
    loading_bar("🚀 Đang chạy... Gõ 'exit' bất kỳ lúc nào để dừng.")

    i = 0
    while True:
        for message in messages:
            i += 1
            for idx, bot in bots:
                fake_typing(Fore.YELLOW + f"[{i}] Bot #{idx} → {message}", delay=0.01)
                bot.send_message(bot.box_id, message)

            table = []
            for idx, bot in bots:
                table.append([
                    f"#{idx}", bot.user_id, bot.box_id, bot.get_uptime(),
                    f"{Fore.GREEN}{bot.success}{Style.RESET_ALL}",
                    f"{Fore.RED}{bot.fail}{Style.RESET_ALL}"
                ])
            print("\n" + tabulate(table, headers=["Bot", "UID", "Box", "Uptime", "✅", "❌"], tablefmt="fancy_grid"))

            try:
                user_input = input(Fore.CYAN + "⏩ Nhấn Enter để tiếp tục hoặc gõ 'exit' để thoát: ").strip().lower()
                if user_input == 'exit':
                    print(Fore.GREEN + "✅ Đã thoát.")
                    sys.exit()
            except KeyboardInterrupt:
                print(Fore.RED + "⛔ Dừng bởi người dùng (Ctrl + C)")
                sys.exit()

            time.sleep(delay)
