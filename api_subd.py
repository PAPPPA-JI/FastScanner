from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from threading import Lock
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
import re
import os

console = Console()
file_write_lock = Lock()
session = requests.Session()
DEFAULT_TIMEOUT = 10

# Improved domain validation using regex
def validate_domain(domain):
    domain_pattern = re.compile(
        r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}$"  # Matches domains like example.com, test.co.uk
    )
    return bool(domain_pattern.match(domain))

# Clean wildcard subdomains (e.g. *.example.com)
def clean_subdomain(subdomain):
    if subdomain.startswith("*."):
        return subdomain[2:]  # Remove wildcard from subdomain
    return subdomain

# Fetch a URL with retries (handles request exceptions)
def fetch_with_retries(url, retries=3, timeout=DEFAULT_TIMEOUT):
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=timeout)
            if response.status_code == 200:
                return response
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                console.print(f"[bold red]Error fetching {url} after {retries} retries: {str(e)}[/bold red]")
    return None

# Fetch subdomains from CRT.sh
def crtsh_subdomains(domain):
    subdomains = set()
    response = fetch_with_retries(f"https://crt.sh/?q=%25.{domain}&output=json")
    if response and response.headers.get('Content-Type') == 'application/json':
        for entry in response.json():
            subdomains.update(entry['name_value'].splitlines())
    return subdomains

# Fetch subdomains from HackerTarget
def hackertarget_subdomains(domain):
    subdomains = set()
    response = fetch_with_retries(f"https://api.hackertarget.com/hostsearch/?q={domain}")
    if response and 'text' in response.headers.get('Content-Type', ''):
        subdomains.update([line.split(",")[0] for line in response.text.splitlines()])
    return subdomains

# Fetch subdomains from RapidDNS
def rapiddns_subdomains(domain):
    subdomains = set()
    response = fetch_with_retries(f"https://rapiddns.io/subdomain/{domain}?full=1")
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('td'):
            text = link.get_text(strip=True)
            if text.endswith(f".{domain}"):
                subdomains.add(text)
    return subdomains

# Fetch subdomains using provided function
def fetch_subdomains(source_func, domain):
    try:
        return source_func(domain)
    except Exception as e:
        console.print(f"[bold red]Error fetching subdomains for {domain} using {source_func.__name__}: {str(e)}[/bold red]")
        return set()

# Process each domain to fetch subdomains from all sources
def process_domain(domain, sources, output_file, progress, task_id):
    subdomains = set()
    console.print(f"[bold yellow]Fetching subdomains for:[/bold yellow] [bold blue]{domain}[/bold blue]")
    
    for source in sources:
        fetched_subdomains = fetch_subdomains(source, domain)
        cleaned_subdomains = {clean_subdomain(sub) for sub in fetched_subdomains}
        subdomains.update(cleaned_subdomains)
        progress.update(task_id, advance=1)

    console.print(f"[bold green] Subdomains saved for {domain}[/bold green]")

    # Safely write subdomains to file
    with file_write_lock:
        try:
            with open(output_file, "a", encoding="utf-8") as file:
                for subdomain in sorted(subdomains):
                    file.write(f"{subdomain}\n")
        except IOError as e:
            console.print(f"[bold red]Error writing to file: {e}[/bold red]")

    return subdomains

# Main function to find subdomains
def find_subdomains():
    sources = [crtsh_subdomains, hackertarget_subdomains, rapiddns_subdomains]
    console.print("[bold yellow][1] Single domain[/bold yellow]")
    console.print("[bold yellow][2] Multiple domains[/bold yellow]")
    
    console.print("[bold green]» Enter your choice: [/bold green]", end="")
    choice = input().strip()
    
    # Handle single domain input
    if choice == '1':
        console.print("[bold green]» Enter domain: [/bold green]", end="")
        domain = input().strip()
        if not domain or not validate_domain(domain):
            console.print("[bold red]⚠ Invalid domain format or empty domain.[/bold red]")
            return
        domains = [domain]
        console.print("[bold green]» Enter the output file name (without extension): [/bold green]", end="")
        output_file = input().strip()
        if not output_file:
            output_file = f"{domain}_subdomains.txt"
    
    # Handle multiple domains input from file
    elif choice == '2':
        console.print("[bold green]» Enter file path: [/bold green]", end="")
        file_path = input().strip()
        if not os.path.exists(file_path):
            console.print("[bold red]⚠ File not found.[/bold red]")
            return
        try:
            with open(file_path, "r") as file:
                domains = [line.strip() for line in file if line.strip()]
            console.print("[bold green]» Enter the output file name (without .txt): [/bold green]", end="")
            output_file = input().strip()
            if not output_file:
                output_file = f"{file_path.split('/')[-1].split('.')[0]}_subdomains.txt"
        except Exception as e:
            console.print(f"[bold red]⚠ Error reading file: {e}[/bold red]")
            return
    
    else:
        console.print("[bold red]⚠ Invalid choice.[/bold red]")
        return

    console.print(f"[bold yellow]Starting subdomain finding...[/bold yellow]")
    total_tasks = len(domains) * len(sources)
    total_subdomains = 0

    # Use the rich library's Progress bar for real-time feedback
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[bold blue]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:

        task_id = progress.add_task("Processing", total=total_tasks)
        
        # Execute subdomain fetching concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(process_domain, domain, sources, output_file, progress, task_id): domain for domain in domains
            }
            for future in as_completed(futures):
                total_subdomains += len(future.result())
    
    console.print(f"\n[bold green] Subdomains saved in {output_file}[/bold green]")
    console.print(f"[bold green] Total subdomains found: {total_subdomains}[/bold green]")

    # Pause before returning to the main menu
    input(f"\nPress Enter to go to the main menu...")

if __name__ == "__main__":
    find_subdomains()