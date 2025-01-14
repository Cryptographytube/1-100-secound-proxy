import os
import time
import requests
import threading
from queue import Queue

proxy_file = 'proxy_list.txt'
active_proxies = []
inactive_proxies = []
proxy_lock = threading.Lock()
result_queue = Queue()

def install_dependencies():
    print("Installing required packages...")
    os.system("pkg update -y && pkg install -y proxychains-ng python nano")
    print("Installation complete.")

def setup_proxychains_config(active_proxy, config_path):
    with open(config_path, 'w') as file:
        file.write("dynamic_chain\n")
        file.write("proxy_dns\n")
        file.write("tcp_read_time_out 15000\n")
        file.write("tcp_connect_time_out 8000\n\n")
        file.write("[ProxyList]\n")
        file.write(f"http {active_proxy.split(':')[0]} {active_proxy.split(':')[1]}\n")
    print(f"Proxychains configured with proxy: {active_proxy}")

def load_proxies():
    with open(proxy_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def check_proxy(proxy):
    try:
        proxies = {"http": proxy, "https": proxy}
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=2)
        if response.status_code == 200:
            with proxy_lock:
                if proxy not in active_proxies:
                    active_proxies.append(proxy)
                    if proxy in inactive_proxies:
                        inactive_proxies.remove(proxy)
            result_queue.put((proxy, True))
        else:
            raise Exception
    except:
        with proxy_lock:
            if proxy not in inactive_proxies:
                inactive_proxies.append(proxy)
            if proxy in active_proxies:
                active_proxies.remove(proxy)
        result_queue.put((proxy, False))

def build_proxy_pool(proxy_list):
    threads = []
    for proxy in proxy_list:
        t = threading.Thread(target=check_proxy, args=(proxy,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

def rotate_proxies(rotation_delay, config_path):
    while True:
        with proxy_lock:
            if active_proxies:
                current_proxy = active_proxies.pop(0)
                active_proxies.append(current_proxy)
                setup_proxychains_config(current_proxy, config_path)
                print(f"Using Proxy: {current_proxy}")
            else:
                print("No active proxies available.")
        time.sleep(rotation_delay)

def display_counts():
    while True:
        with proxy_lock:
            active_count = len(active_proxies)
            inactive_count = len(inactive_proxies)
        print(f"🟢 Active: {active_count} | 🔴 Inactive: {inactive_count}")
        time.sleep(5)

def main():
    install_dependencies()

    # Choose environment: Termux or Kali Linux
    environment_choice = input("Choose your environment (1 for Termux, 2 for Kali Linux): ").strip()
    if environment_choice == "1":
        config_path = '/data/data/com.termux/files/usr/etc/proxychains.conf'
    elif environment_choice == "2":
        config_path = '/etc/proxychains.conf'  # Standard path for Kali Linux
    else:
        print("Invalid choice. Defaulting to Kali Linux path.")
        config_path = '/etc/proxychains.conf'
    
    rotation_delay = input("Enter rotation delay (1-100 seconds): ")
    try:
        rotation_delay = max(1, min(100, int(rotation_delay)))
    except ValueError:
        rotation_delay = 10  # Default to 10 seconds if input is invalid
        print("Invalid input. Using default delay of 10 seconds.")

    proxy_list = load_proxies()
    if not proxy_list:
        print("No proxies in the list!")
        return
    
    threading.Thread(target=rotate_proxies, args=(rotation_delay, config_path), daemon=True).start()
    threading.Thread(target=display_counts, daemon=True).start()

    print("Checking all proxies initially...")
    build_proxy_pool(proxy_list)
    
    while True:
        proxy, status = result_queue.get()
        status_text = "🟢 Active" if status else "🔴 Inactive"
        print(f"{status_text} Proxy: {proxy}")

if __name__ == "__main__":
    main()
