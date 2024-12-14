import subprocess
import os
import threading
import asyncio
import random
import aiofiles
import platform
from datetime import datetime
import pytz

# Color definitions
RESET = "\033[0m"
BOLD = "\033[1m"
LIGHT_GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
SKY_BLUE = "\033[1;36m"
YELLOW = "\033[93m"
GREEN = "\033[32m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
ORANGE = "\033[38;5;208m"
PINK = "\033[38;5;206m"

COLORS = [LIGHT_GREEN, RED, BLUE, YELLOW, GREEN, PURPLE, CYAN, WHITE, ORANGE, PINK]

write_lock = threading.Lock()

def get_user_info_banner():
    os_info = platform.system()
    version_info = platform.version()
    android_version = platform.release()

    current_time = datetime.now()
    date_str = current_time.strftime('%Y-%m-%d')
    time_str = current_time.strftime('%H:%M:%S')
    
    timezone = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Z %z')
    formatted_timezone = timezone[:-2] + ":" + timezone[-2:]

    country = "India"
    total_width = 36

    color = random.choice(COLORS)
    banner = f"""
    {BOLD}{color}╔{'═' * total_width}╗{RESET}
    {BOLD}{color}║        USER INFORMATION            ║{RESET}
    {BOLD}{color}╠{'═' * total_width}╣{RESET}
    {BOLD}{color}║ OS       : {os_info.ljust(16)}        ║{RESET}
    {BOLD}{color}║ Date     : {date_str.ljust(16)}        ║{RESET}
    {BOLD}{color}║ Time     : {time_str.ljust(16)}        ║{RESET}
    {BOLD}{color}║ Timezone : {formatted_timezone.ljust(16)}        ║{RESET}
    {BOLD}{color}║ Country  : {country.ljust(16)}        ║{RESET}
    {BOLD}{color}╚{'═' * total_width}╝{RESET}
    """
    print(banner)

def show_banner():
    banner = f"""
    ╔════════════════════════════════════╗
    ║     WELCOME TO PAPPPA JI TOOL      ║
    ╠════════════════════════════════════╣
    ║ Coded by    : PAPPPA JI            ║
    ║ Design by   : PAPPPA JI            ║
    ║ Telegram    : @PapppaJi            ║
    ║ Version     : 2.0                  ║
    ╚════════════════════════════════════╝
    """
    color = random.choice(COLORS)
    print(f"{BOLD}{color}{banner}{RESET}")
    get_user_info_banner()

def clear_terminal():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        show_banner()
    except Exception as e:
        print(f"{BOLD}{RED}[WARNING]{RESET} Unable to clear terminal. {e}")

def show_menu():
    menu = f"""
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    {BOLD}{YELLOW}[1]{RESET} - Find Subdomain
    {BOLD}{YELLOW}[2]{RESET} - Scan host's
    {BOLD}{YELLOW}[3]{RESET} - Lite Scanner
    {BOLD}{YELLOW}[4]{RESET} - Extract IP/Domain
    {BOLD}{YELLOW}[5]{RESET} - IP Generator
    {BOLD}{YELLOW}[6]{RESET} - Update Scripts
    {BOLD}{YELLOW}[7]{RESET} - File Splitter     
    {BOLD}{YELLOW}[8]{RESET} - Exit Program
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    """
    print(menu)

def show_subdomain_menu():
    menu = f"""
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    {BOLD}{YELLOW}[1]{RESET} - Find subdomains with Subfinder
    {BOLD}{YELLOW}[2]{RESET} - Find subdomains with API
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    """
    print(menu)

def show_scan_host_menu():
    menu = f"""
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    {BOLD}{YELLOW}[1]{RESET} - Scan host with Bughunter
    {BOLD}{YELLOW}[2]{RESET} - Scan host with Normal Scanner
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    """
    print(menu)

def update_scripts():
    try:
        # Change to the directory and execute the commands
        print(f"{BOLD}{BLUE}Updating scripts...{RESET}")
        command = "git pull origin main && git log -1"
        subprocess.run(command, shell=True, check=True)
        print(f"{BOLD}{GREEN}Scripts updated successfully!{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{BOLD}{RED}Failed to update scripts!{RESET}")
        print(f"{BOLD}{RED}Error Details: {e}{RESET}")
    except FileNotFoundError:
        print(f"{BOLD}{RED}Error: Directory 'AdwanceSNI-2.0' not found. Ensure it exists.{RESET}")
    except Exception as e:
        print(f"{BOLD}{RED}An unexpected error occurred: {e}{RESET}")

def main():
    clear_terminal()
    while True:
        show_menu()
        choice = input(f"{BOLD}{SKY_BLUE}Choose an option (1-8): {RESET}").strip()

        if choice == "1":
            show_subdomain_menu()
            sub_choice = input(f"{BOLD}{SKY_BLUE}Choose an option (1-2): {RESET}").strip()

            if sub_choice == "1":
                print(f"{BOLD}{GREEN}Running Subfinder...{RESET}")
                subprocess.run(["python", "subfinder.py"])
            elif sub_choice == "2":
                print(f"{BOLD}{GREEN}Running Subdomain API lookup...{RESET}")
                subprocess.run(["python", "api_subd.py"])
            else:
                print(f"{BOLD}{RED}Invalid choice! Returning to main menu.{RESET}")

        elif choice == "2":
            show_scan_host_menu()
            sub_choice = input(f"{BOLD}{SKY_BLUE}Choose an option (1-2): {RESET}").strip()

            if sub_choice == "1":
                print(f"{BOLD}{GREEN}Running Bughunter Scanner...{RESET}")
                subprocess.run(["python", "bughunter_scanner.py"])
            elif sub_choice == "2":
                print(f"{BOLD}{GREEN}Running Normal Scanner...{RESET}")
                subprocess.run(["python", "normal_scanner.py"])
            else:
                print(f"{BOLD}{RED}Invalid choice! Returning to main menu.{RESET}")

        elif choice == "3":
            print(f"{BOLD}{GREEN}Running Lite Scanner...{RESET}")
            subprocess.run(["python", "lite_scanner.py"])

        elif choice == "4":
            print(f"{BOLD}{GREEN}Running IP/Domain Extractor...{RESET}")
            subprocess.run(["python", "ip_domain_extractor.py"])

        elif choice == "5":
            print(f"{BOLD}{GREEN}Running IP Generator...{RESET}")
            subprocess.run(["python", "ip_generator.py"])

        elif choice == "6":
            update_scripts()

        elif choice == "7":
            print(f"{BOLD}{GREEN}Running File Splitter...{RESET}")
            subprocess.run(["python", "file_spilter.py"])  # Call the file splitter script

        elif choice == "8":
            print(f"{BOLD}{GREEN}Exiting program...{RESET}")
            break

        else:
            print(f"{BOLD}{RED}Invalid option! Please select a valid option.{RESET}")

if __name__ == "__main__":
    main()