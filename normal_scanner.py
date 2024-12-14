from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import socket
import threading
import time
from colorama import Fore, Style
import requests

# Default timeout and exclude list
DEFAULT_TIMEOUT1 = 5
EXCLUDE_LOCATIONS = ["https://jio.com/BalanceExhaust", "http://filter.ncell.com.np/nc"]

# Lock for file writing
file_write_lock = threading.Lock()

# Manual replacement for get_input
def get_input(prompt, default=None):
    user_input = input(prompt).strip()
    return user_input if user_input else default

# Manual replacement for clear_screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Read hosts from file
def get_hosts_from_file(file_path):
    path = Path(file_path)
    if path.is_file():
        try:
            return [line.strip() for line in path.read_text().splitlines() if line.strip()]
        except Exception as e:
            print(Fore.RED + f"Error reading file: {e}")
    return []

# Choose HTTP method
def get_http_method():
    methods = ['GET', 'POST', 'HEAD']
    print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "\nAvailable HTTP methods: " + Fore.YELLOW + ", ".join(methods))
    method = get_input(Fore.CYAN + "\n » Select an HTTP method (default: GET): " + Fore.RESET, "GET").upper()
    return method if method in methods else "GET"

# Format the row for console and file output
def format_row(code, server, port, ip_address, host, use_colors=True):
    return (f"{Fore.GREEN if use_colors else ''}{code:<4} " +
            f"{Fore.CYAN if use_colors else ''}{server:<20} " +
            f"{Fore.YELLOW if use_colors else ''}{port:<5} " +
            f"{Fore.MAGENTA if use_colors else ''}{ip_address:<15} " +
            f"{Fore.LIGHTBLUE_EX if use_colors else ''}{host}{Style.RESET_ALL if use_colors else ''}")

# Check HTTP response
def check_http_response(host, port, method):
    url = f"{'https' if port in ['443', '8443'] else 'http'}://{host}:{port}"
    try:
        response = requests.request(method, url, timeout=DEFAULT_TIMEOUT1, allow_redirects=True)
        if any(exclude in response.headers.get('Location', '') for exclude in EXCLUDE_LOCATIONS):
            return None
        status_code = response.status_code
        server_header = response.headers.get('Server', 'N/A')
        ip_address = get_ip_from_host(host) or 'N/A'
        return (status_code, server_header, port, ip_address, host)
    except requests.exceptions.RequestException:
        return None

# Resolve IP address from hostname
def get_ip_from_host(host):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return "N/A"

# Format elapsed time
def format_time(elapsed_time):
    return f"{int(elapsed_time // 60)}m {int(elapsed_time % 60)}s" if elapsed_time >= 60 else f"{elapsed_time:.2f}s"

# Perform scan
def perform_scan(hosts, ports, output_file, threads, method):
    clear_screen()
    print(Fore.GREEN + Style.BRIGHT + "🔍 Scanning Using HTTP method:", Fore.YELLOW + method)
    
    headers = (Fore.GREEN + Style.BRIGHT + "Code  " + Fore.CYAN + "Server               " +
              Fore.YELLOW + "Port   " + Fore.MAGENTA + "IP Address     " + Fore.LIGHTBLUE_EX + "Host" + Style.RESET_ALL)
    separator = "-" * 65

    # Prepare the output file
    try:
        with open(output_file, 'a') as file:
            file.write(f"{headers}\n{separator}\n")
    except Exception as e:
        print(Fore.RED + f"Error opening output file: {e}")
        return

    print(headers, separator, sep='\n')

    start_time = time.time()  # Initialize start_time here
    total_hosts, scanned_hosts, responded_hosts = len(hosts) * len(ports), 0, 0

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(check_http_response, host, port, method) for host in hosts for port in ports]
        for future in as_completed(futures):
            scanned_hosts += 1
            try:
                result = future.result(timeout=DEFAULT_TIMEOUT1 + 1)
                if result:
                    responded_hosts += 1
                    row = format_row(*result)
                    print(row)
                    with file_write_lock:
                        with open(output_file, 'a') as file:
                            file.write(format_row(*result, use_colors=False) + "\n")
            except Exception:
                pass

            elapsed_time = time.time() - start_time
            print(Style.BRIGHT + f"Scanned {scanned_hosts}/{total_hosts} - Responded: {responded_hosts} - Elapsed: {format_time(elapsed_time)}", end='\r')

    print(f"\n\n{Fore.GREEN}✔ Scan completed! {responded_hosts}/{scanned_hosts} hosts responded.")
    print(f"{Fore.GREEN}Results saved to {output_file}.{Style.RESET_ALL}")
    
    # Print summary
    elapsed_time = time.time() - start_time
    print(f"\n\n{Fore.LIGHTCYAN_EX}============ {Fore.CYAN}{Style.BRIGHT}SCAN SUMMARY{Fore.RESET}{Fore.LIGHTCYAN_EX} ============\n")
    print(f"{Fore.LIGHTGREEN_EX}Total hosts scanned: {Style.BRIGHT}{Fore.YELLOW}{total_hosts}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}Hosts responded:     {Style.BRIGHT}{Fore.YELLOW}{responded_hosts}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}Total time taken:    {Style.BRIGHT}{Fore.YELLOW}{format_time(elapsed_time)}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}HTTP method used:    {Style.BRIGHT}{Fore.YELLOW}{method}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}========================================{Style.RESET_ALL}\n")

    # Add "press enter to go main menu" message
    input(f"{Style.BRIGHT}{Fore.MAGENTA}Press Enter to go to the main menu...{Style.RESET_ALL}")

# Main function
def main():
    # Get file and parameters
    file_path = get_input(Fore.GREEN + Style.BRIGHT + "» Enter file path: " + Fore.YELLOW + Style.BRIGHT, "domain.txt")
    hosts = get_hosts_from_file(file_path)
    if not hosts:
        print(Fore.RED + Style.BRIGHT + "⚠ No valid hosts found in the file.")
        return

    ports_input = get_input(Fore.GREEN + Style.BRIGHT + "» Enter port list (default: 80): " + Fore.YELLOW + Style.BRIGHT, "80").strip()
    ports = ports_input.split(',') if ports_input else ["80"]
    output_file = get_input(Fore.GREEN + Style.BRIGHT + "» Enter output file name (default: results.txt): " + Fore.YELLOW + Style.BRIGHT, "results.txt").strip() or "results.txt"
    threads = int(get_input(Fore.GREEN + Style.BRIGHT + "» Enter number of threads (default: 50): " + Fore.YELLOW + Style.BRIGHT, "50") or "50")
    http_method = get_http_method()

    # Perform the scan
    perform_scan(hosts, ports, output_file, threads, http_method)

if __name__ == "__main__":
    main()