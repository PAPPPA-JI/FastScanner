import subprocess
import os
import threading
import asyncio
import random
import aiofiles
import platform
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
import psutil
import pytz
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

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

# Get System Resources
def get_system_resources():
    cpu_count = os.cpu_count() or 2
    memory = psutil.virtual_memory().total / (1024**3)  # GB

    print(f"{BOLD}{LIGHT_GREEN}System Resources Detected:{RESET}")
    print(f"  - CPU Cores: {cpu_count}")
    print(f"  - Memory: {memory:.2f} GB")
    return cpu_count, memory

# Calculate Optimal Config based on CPU and Memory
def calculate_optimal_config(cpu_count, memory):
    workers = min(cpu_count * 2, 15)  # max 15 workers
    if memory < 4:
        workers = min(workers, 5)  # Lower workers for low memory systems

    batch_size = 5 if memory < 4 else 10

    print(f"{BOLD}{LIGHT_GREEN}Optimized Configuration:{RESET}")
    print(f"  - Workers: {workers}")
    print(f"  - Batch Size: {batch_size}")
    return workers, batch_size

# Read Domains from File
async def read_domains(file_name):
    async with aiofiles.open(file_name, 'r') as file:
        domains = await file.readlines()
    return [domain.strip() for domain in domains]

# Subfinder Fetching Function
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
        print(f"{BOLD}{RED}Error fetching subdomains for {domain}: {e}{RESET}")
        return 0

# Batch Domains
def batch_domains(domains, batch_size=20):
    total_domains = len(domains)
    for i in range(0, total_domains, batch_size):
        yield domains[i:i + batch_size]

# Generate Output Path
def get_output_file_path(input_file, output_filename):
    input_dir = os.path.dirname(input_file)
    output_file_path = os.path.join(input_dir, output_filename)
    return output_file_path

# Main Async Function
async def main():
    cpu_count, memory = get_system_resources()
    workers, batch_size = calculate_optimal_config(cpu_count, memory)

    # Prompt user for input immediately
    input_file = input(f"{BOLD}{LIGHT_GREEN}Enter Domain File: {RESET}")
    if not os.path.isfile(input_file):
        print(f"{BOLD}{RED}File not found. Please try again.{RESET}")
        return

    output_filename = input(f"{BOLD}{LIGHT_GREEN}Enter Output file name to Save Subdomain: {RESET}")
    output_file = get_output_file_path(input_file, output_filename)

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
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for domain_batch in batch_domains(domains, batch_size):
                tasks = [get_subdomains_subfinder(domain, output_file) for domain in domain_batch]
                results = await asyncio.gather(*tasks)
                total_subdomains += sum(results)
                progress.update(task, advance=len(domain_batch))
    print(f"{BOLD}{LIGHT_GREEN}Subdomains have been saved in {output_file}.{RESET}")
    print(f"{BOLD}{GREEN}Total Subdomains Found: {total_subdomains}{RESET}")

if __name__ == "__main__":
    asyncio.run(main())