import requests
import json
import time
import random
import re
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from time import sleep
import pyperclip

console = Console()

def fake_typing(text, delay=0.03):
    for char in text:
        console.print(char, end="", style="bold white", soft_wrap=True)
        sleep(delay)
    print()

def show_banner():
    console.print("""
[bold magenta]
／＞　 フ
| 　_　_|   🍩
／` ミ＿xノ 
／　　　　 |
(　 ヽ＿ヽ_)__)
＼二)
[/bold magenta]
[bold cyan]Tool Lấy Danh Sách Nhóm [/bold cyan]
[green]By: Doremon[/green]
""")

def get_random_color():
    colors = ["cyan", "magenta", "green", "yellow", "red", "blue", "bright_cyan", "bright_magenta"]
    return random.choice(colors)

def display_results(threads):
    table = Table(title="[bold]📋 Danh Sách Nhóm Chat[/bold]", box=box.HEAVY_EDGE, show_lines=True)
    table.add_column("STT", justify="center", style="bold white", no_wrap=True)
    table.add_column("Tên Nhóm", style="bold white")
    table.add_column("ID", style="bold green")
    table.add_column("Thành viên", justify="center", style="bold yellow")
    table.add_column("Tin nhắn", justify="center", style="bold cyan")

    for i, group in enumerate(threads, start=1):
        row_color = get_random_color()
        table.add_row(
            f"[{row_color}]{i}[/{row_color}]",
            f"[{row_color}]{group['thread_name']}[/{row_color}]",
            f"[{row_color}]{group['thread_id']}[/{row_color}]",
            f"[{row_color}]{group['participant_count']}[/{row_color}]",
            f"[{row_color}]{group['message_count']}[/{row_color}]"
        )

    console.print(table)

def get_facebook_id_from_cookie(cookie):
    try:
        c_user_match = re.search(r"c_user=(\d+)", cookie)
        return c_user_match.group(1) if c_user_match else "Unknown"
    except:
        return "Unknown"

class FacebookThreadExtractor:
    def __init__(self, cookie):
        self.cookie = cookie
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ]
        self.facebook_tokens = {}

    def get_facebook_tokens(self):
        headers = {
            'Cookie': self.cookie,
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }

        sites = ['https://www.facebook.com', 'https://mbasic.facebook.com']

        for site in sites:
            try:
                response = self.session.get(site, headers=headers, timeout=10)
                c_user_match = re.search(r"c_user=(\d+)", self.cookie)
                if c_user_match:
                    self.facebook_tokens["FacebookID"] = c_user_match.group(1)
                fb_dtsg_match = re.search(r'"token":"(.*?)"', response.text)
                if not fb_dtsg_match:
                    fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
                if fb_dtsg_match:
                    self.facebook_tokens["fb_dtsg"] = fb_dtsg_match.group(1)
                jazoest_match = re.search(r'jazoest=(\d+)', response.text)
                if jazoest_match:
                    self.facebook_tokens["jazoest"] = jazoest_match.group(1)
                revision_match = re.search(r'client_revision":(\d+)', response.text)
                if revision_match:
                    self.facebook_tokens["client_revision"] = revision_match.group(1)
                if self.facebook_tokens.get("fb_dtsg") and self.facebook_tokens.get("jazoest"):
                    break
            except:
                continue

        self.facebook_tokens.update({
            "__rev": "1015919737",
            "__req": "1b",
            "__a": "1",
            "__comet_req": "15"
        })

        return len(self.facebook_tokens) > 4

    def get_thread_list(self):
        if not self.get_facebook_tokens():
            return {"error": "Không thể lấy token từ Facebook. Kiểm tra lại cookie."}

        all_threads = []
        before_cursor = None
        facebook_id = self.facebook_tokens.get("FacebookID", "")

        while True:
            form_data = {
                "av": facebook_id,
                "__user": facebook_id,
                "__a": self.facebook_tokens["__a"],
                "__req": self.facebook_tokens["__req"],
                "__hs": "19234.HYP:comet_pkg.2.1..2.1",
                "dpr": "1",
                "__ccg": "EXCELLENT",
                "__rev": self.facebook_tokens["__rev"],
                "__comet_req": self.facebook_tokens["__comet_req"],
                "fb_dtsg": self.facebook_tokens.get("fb_dtsg", ""),
                "jazoest": self.facebook_tokens.get("jazoest", ""),
                "lsd": "null",
                "__spin_r": self.facebook_tokens.get("client_revision", ""),
                "__spin_b": "trunk",
                "__spin_t": str(int(time.time())),
            }

            queries = {
                "o0": {
                    "doc_id": "3336396659757871",
                    "query_params": {
                        "limit": 100,
                        "before": before_cursor,
                        "tags": ["INBOX"],
                        "includeDeliveryReceipts": False,
                        "includeSeqID": True,
                    }
                }
            }

            form_data["queries"] = json.dumps(queries)

            headers = {
                'Cookie': self.cookie,
                'User-Agent': random.choice(self.user_agents),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
                'Origin': 'https://www.facebook.com',
                'Referer': 'https://www.facebook.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-FB-Friendly-Name': 'MessengerThreadListQuery',
                'X-FB-LSD': 'null'
            }

            try:
                response = self.session.post(
                    'https://www.facebook.com/api/graphqlbatch/',
                    data=form_data,
                    headers=headers,
                    timeout=15
                )

                if response.status_code != 200:
                    break

                json_parts = response.text.strip().split('\n')
                valid_json = None
                for part in json_parts:
                    try:
                        parsed = json.loads(part)
                        if "o0" in parsed:
                            valid_json = parsed
                            break
                    except:
                        continue

                if not valid_json:
                    break

                threads = valid_json["o0"]["data"]["viewer"]["message_threads"]["nodes"]
                page_info = valid_json["o0"]["data"]["viewer"]["message_threads"].get("page_info", {})
                before_cursor = page_info.get("end_cursor")

                for thread in threads:
                    if not thread.get("thread_key") or not thread["thread_key"].get("thread_fbid"):
                        continue
                    participants = thread.get("all_participants", {}).get("edges", [])
                    participant_ids = [p["node"]["messaging_actor"]["id"] for p in participants if "node" in p and "messaging_actor" in p["node"]]
                    if facebook_id not in participant_ids:
                        continue
                    thread_info = {
                        "thread_id": thread["thread_key"]["thread_fbid"],
                        "thread_name": thread.get("name", "Không có tên"),
                        "message_count": thread.get("messages_count", 0),
                        "participant_count": len(participants)
                    }
                    all_threads.append(thread_info)

                if not page_info.get("has_next_page"):
                    break

                time.sleep(1)

            except Exception as e:
                return {"error": f"Lỗi: {str(e)}"}

        return {
            "success": True,
            "thread_count": len(all_threads),
            "threads": all_threads,
            "facebook_id": facebook_id
        }

# ==== MAIN RUN ====
if __name__ == '__main__':
    os.system("cls" if os.name == "nt" else "clear")
    show_banner()

    cookie = Prompt.ask("[yellow]🍪 Nhập cookie Facebook[/yellow]")
    extractor = FacebookThreadExtractor(cookie)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="⏳ Đang lấy dữ liệu nhóm chat...", total=None)
        result = extractor.get_thread_list()

    if "error" in result:
        console.print(f"[red]❌ {result['error']}[/red]")
    else:
        fake_typing(f"\n✅ Đã lấy được {result['thread_count']} nhóm chat từ Facebook ID: {result['facebook_id']}\n", delay=0.02)
        display_results(result["threads"])

        if result["threads"]:
            chon = Prompt.ask("[blue]👉 Chọn số nhóm muốn copy ID (Enter để bỏ qua)[/blue]", default="")
            if chon.isdigit():
                index = int(chon) - 1
                if 0 <= index < len(result["threads"]):
                    pyperclip.copy(result["threads"][index]["thread_id"])
                    console.print("[green]📋 Đã copy ID nhóm vào clipboard.[/green]")
                else:

                    console.print("[yellow]⚠️ Số không hợp lệ.[/yellow]")
