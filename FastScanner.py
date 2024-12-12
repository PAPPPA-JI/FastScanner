import subprocess
import os
import threading
import asyncio
import random
import aiohttp
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
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
    ╔═══════════════════════════════════╗
    ║  Subdomain Finder & Scanner Tool  ║
    ╠═══════════════════════════════════╣
    ║ Coded by    : PAPPPA JI           ║
    ║ Design by   : PAPPPA JI           ║
    ║ Telegram    : @PapppaJi           ║
    ║ Version     : 1.1                 ║
    ╚═══════════════════════════════════╝
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

async def read_domains(file_name):
    async with aiofiles.open(file_name, 'r') as file:
        domains = await file.readlines()
    return [domain.strip() for domain in domains]

async def get_subdomains_subfinder(domain, output_file):
    try:
        print(f"{BOLD}{YELLOW}Fetching subdomains for: {BLUE}{domain}{RESET}")
        process = await asyncio.create_subprocess_exec(
            'subfinder', '-d', domain, '-silent',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            print(f"{BOLD}{RED}Error fetching subdomains for {domain}: {stderr.decode()}{RESET}")
            return 0
        else:
            subdomains = stdout.decode().splitlines()
            clean_subdomains = [line.strip() for line in subdomains if line.strip()]
            with write_lock:
                with open(output_file, 'a') as out_file:
                    for subdomain in clean_subdomains:
                        out_file.write(f"{subdomain}\n")
            print(f"{BOLD}{GREEN}Subdomains saved for: {domain}{RESET}")
            return len(clean_subdomains)
    except Exception as e:
        print(f"{BOLD}{RED}Error fetching subdomains for {BLUE}{domain}: {e}{RESET}")
        return 0

def scan_subdomains_with_bughunter(input_file, output_file):
    try:
        print(f"{BOLD}{YELLOW}Scanning subdomains from: {BLUE}{input_file}{RESET}")
        subprocess.run(['bughunter-go', 'scan', 'direct', '-f', input_file, '-o', output_file], check=True)
        print(f"{BOLD}{GREEN}Bug scanning completed! Results saved to {output_file}.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{BOLD}{RED}Error during bug scanning: {e}{RESET}")
    except FileNotFoundError as fnf_error:
        print(f"{BOLD}{RED}FileNotFoundError: {fnf_error}{RESET}")

def batch_domains(domains, batch_size=20):
    total_domains = len(domains)
    for i in range(0, total_domains, batch_size):
        yield domains[i:i + batch_size]

def show_menu():
    menu = f"""
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    {BOLD}{YELLOW}[1]{RESET} - Find Subdomains
    {BOLD}{YELLOW}[2]{RESET} - Scan Subdomains
    {BOLD}{YELLOW}[3]{RESET} - Exit Program
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    """
    print(menu)

def get_output_file_path(input_file, output_filename):
    # Input file ke directory ko get karna
    input_dir = os.path.dirname(input_file)
    # Ussi directory mein output file ka full path create karna
    output_file_path = os.path.join(input_dir, output_filename)
    return output_file_path

async def main():
    clear_terminal()
    while True:
        show_menu()
        choice = input(f"{BOLD}{SKY_BLUE} Choose an option (1/2/3): {RESET}").strip()
        if choice == "1":
            input_file = input(f"{BOLD}{LIGHT_GREEN}Enter Domain File: {RESET}")
            if not os.path.isfile(input_file):
                print(f"{BOLD}{RED}File not found. Please try again.{RESET}")
                continue

            # Output file ka naam user se lena
            output_filename = input(f"{BOLD}{LIGHT_GREEN}Enter Output file name to Save Subdomain: {RESET}")
            # Ussi directory mein output file ka path get karna
            output_file = get_output_file_path(input_file, output_filename)

            # Output file ko initialize karna
            with open(output_file, 'w') as f:
                pass

            domains = await read_domains(input_file)
            total_domains = len(domains)
            total_subdomains = 0
            with Progress(
                SpinnerColumn(),
                BarColumn(),
                TextColumn("[progress.description]{task.description}"),
                TextColumn("[progress.percentage]{task.completed}/{task.total}"),
            ) as progress:
                task = progress.add_task("[cyan]Processing Domains...", total=total_domains)
                with ProcessPoolExecutor(max_workers=5) as executor:
                    for domain_batch in batch_domains(domains, batch_size=5):
                        tasks = [get_subdomains_subfinder(domain, output_file) for domain in domain_batch]
                        results = await asyncio.gather(*tasks)
                        total_subdomains += sum(results)
                        progress.update(task, advance=len(domain_batch))
            print(f"{BOLD}{LIGHT_GREEN}Subdomains have been saved in {output_file}.{RESET}")
            print(f"{BOLD}{GREEN}Total Subdomains Found: {total_subdomains}{RESET}")

        elif choice == "2":
            scan_file = input(f"{BOLD}{LIGHT_GREEN}Enter file to scan subdomains: {RESET}")
            if not os.path.isfile(scan_file):
                print(f"{BOLD}{RED}File not found. Please try again.{RESET}")
                continue

            output_filename = input(f"{BOLD}{LIGHT_GREEN}Enter output file name (default: Scanned.txt): {RESET}") or "Scanned.txt"
            # Ussi directory mein output file ka path get karna
            output_file = get_output_file_path(scan_file, output_filename)

            scan_subdomains_with_bughunter(scan_file, output_file)

        elif choice == "3":
            confirm_exit()
        else:
            print(f"{BOLD}{RED}Invalid choice. Please select a valid option.{RESET}")

def confirm_exit():
    confirm = input(f"{BOLD}{RED}Are you sure you want to exit? (y/n): {RESET}")
    if confirm.lower() == 'y':
        print(f"{BOLD}{GREEN}Exiting program...{RESET}")
        exit()
    else:
        print(f"{BOLD}{GREEN}Returning to the main menu...{RESET}")

if __name__ == "__main__":
    asyncio.run(main())