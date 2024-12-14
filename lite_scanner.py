import os
import aiohttp
import asyncio
from colorama import Fore, Style, init
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# Initialize
init(autoreset=True)

# Constants
DEFAULT_TIMEOUT = 5
BATCH_SIZE = 1000  # Define the batch size

# ANSI escape sequences for colors and bold text
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
PINK = "\033[95m"
RESET = "\033[0m"

# Function to check URL status
async def check_url(session, url, request_type, port):
    if port == 80:
        full_url = f"http://{url}"
    elif port == 443:
        full_url = f"https://{url}"
    
    try:
        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        if request_type == 'GET':
            async with session.get(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'HEAD':
            async with session.head(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'POST':
            async with session.post(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'OPTIONS':
            async with session.options(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'PUT':
            async with session.put(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'TRACE':
            async with session.trace(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'PATCH':
            async with session.patch(full_url, timeout=timeout) as response:
                status = response.status
        else:
            return None

        if status != 302:
            print(f"{BOLD}{status} - {GREEN}{url}{RESET}")
            return (url, status)
        else:
            return None
        
    except Exception as e:
        return None

# Function to process a batch of URLs
async def process_batch(urls, request_type, port, num_threads, progress, task_id):
    async with aiohttp.ClientSession() as session:
        tasks = [check_url(session, url, request_type, port) for url in urls]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            progress.update(task_id, advance=1)
            results.append(result)
        return [url for url in results if url is not None]

# Main function to run the SNI scanner
async def main_sni(file_name, request_type, port, output_file, num_threads):
    with open(file_name, 'r') as file:
        urls = [url.strip() for url in file.readlines()]
    
    total_urls = len(urls)
    valid_urls = []

    progress = Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.description]{task.completed} of {task.total} hosts processed")
    )
    with progress:
        task_id = progress.add_task("[green]Scanning...", total=total_urls)
        print(f"{BOLD}{Fore.GREEN}Scanning Using HTTP method: {request_type}{RESET}")
        print(f"{BOLD}Code                     Host{RESET}")
        print(f"{BOLD}{'-' * 65}{RESET}")
        for start in range(0, total_urls, BATCH_SIZE):
            batch_urls = urls[start:start + BATCH_SIZE]
            batch_valid_urls = await process_batch(batch_urls, request_type, port, num_threads, progress, task_id)
            valid_urls.extend(batch_valid_urls)
    
    if not valid_urls:
        print(f"{BOLD}{PINK}SORRY BRO SNI NHI MILLI{RESET}")
    else:
        save_valid_urls(valid_urls, output_file)
        print(f"{BOLD}{Fore.GREEN}Results saved in {output_file}{RESET}")
    
    # Print summary
    print(f"\n\n{Fore.LIGHTCYAN_EX}============ {Fore.CYAN}{BOLD}SCAN SUMMARY{Fore.RESET}{Fore.LIGHTCYAN_EX} ============\n")
    print(f"{Fore.LIGHTGREEN_EX}Total hosts scanned: {BOLD}{Fore.YELLOW}{total_urls}{RESET}")
    print(f"{Fore.LIGHTGREEN_EX}Hosts responded:     {BOLD}{Fore.YELLOW}{len(valid_urls)}{RESET}")
    print(f"{Fore.LIGHTGREEN_EX}HTTP method used:    {BOLD}{Fore.YELLOW}{request_type}{RESET}")
    print(f"{Fore.LIGHTCYAN_EX}========================================{RESET}\n")

    input(f"{BOLD}{Fore.YELLOW}\nPress Enter to go to the main menu...{RESET}")

# Function to save valid URLs
def save_valid_urls(urls, output_file):
    with open(output_file, "w") as file:
        for url, status in urls:
            if url:  # Ensure the URL is not None
                file.write(f"{url}\n")

# Function to get a valid HTTP method
def get_http_method():
    methods = ['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'TRACE', 'PATCH']
    while True:
        print(f"{BOLD}{Fore.YELLOW}Select the request method:{RESET}")
        for i, method in enumerate(methods, start=1):
            print(f"{BOLD}{Fore.GREEN}[{i}] {method}{RESET}")
        choice = input(f"{BOLD}{Fore.YELLOW}Enter your choice (1-7): {RESET}")
        if choice.isdigit() and 1 <= int(choice) <= 7:
            return methods[int(choice) - 1]
        print(f"{BOLD}{Fore.RED}Invalid choice! Please select a valid method.{RESET}")

# Function to get a valid port
def get_port():
    while True:
        print(f"{BOLD}{Fore.GREEN}Available ports: 80, 443{RESET}")
        port = input(f"{BOLD}{Fore.YELLOW}Select the port (default: 443): {RESET}") or '443'
        if port.isdigit() and (port == '80' or port == '443'):
            return int(port)
        print(f"{BOLD}{Fore.RED}Invalid choice! Please select a valid port.{RESET}")

# Directly start the URL scanning process with manual file name entry
def scan_urls_with_request_methods():
    file_name = input(f"{BOLD}{Fore.YELLOW}Enter file name: {RESET}")

    output_file = input(f"{BOLD}{Fore.YELLOW}Enter output file name for saved URLs (default: Lite_scan.txt): {RESET}") or "Lite_scan.txt"

    request_type = get_http_method()
    port = get_port()

    threads_input = input(f"{BOLD}{Fore.YELLOW}Enter number of threads (default: 10): {RESET}") or '10'
    num_threads = int(threads_input)

    os.system('clear')

    asyncio.run(main_sni(file_name, request_type, port, output_file, num_threads))

# Start the program
if __name__ == "__main__":
    scan_urls_with_request_methods()