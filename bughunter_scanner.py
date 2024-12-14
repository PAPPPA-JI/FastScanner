import subprocess
import os
import threading  # Ensure threading is imported

# Color definitions
RESET = "\033[0m"
BOLD = "\033[1m"
LIGHT_GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
GREEN = "\033[32m"
CYAN = "\033[96m"
ORANGE = "\033[38;5;208m"

write_lock = threading.Lock()

# Scan Subdomains
def scan_subdomains_with_bughunter(input_file, output_file, threads):
    try:
        print(f"{BOLD}{YELLOW}Scanning subdomains from: {BLUE}{input_file}{RESET}")
        cmd = [
            'bughunter-go', 'scan', 'direct', '-f', input_file, '-o', output_file,
            '-t', str(threads)
        ]
        subprocess.run(cmd, check=True)
        print(f"{BOLD}{GREEN}Bug scanning completed! Results saved to {output_file}.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{BOLD}{RED}Error during bug scanning: {e}{RESET}")
    except FileNotFoundError as fnf_error:
        print(f"{BOLD}{RED}File not found: {fnf_error}{RESET}")

# Generate Output Path
def get_output_file_path(input_file, output_filename):
    # Set the fixed path for saving output file
    output_dir = "/storage/emulated/0/"
    
    # Combine it with the output filename
    output_file_path = os.path.join(output_dir, output_filename)
    return output_file_path

# Main Function
def main():
    input_file = input(f"{BOLD}{LIGHT_GREEN}Enter file to scan subdomains: {RESET}")
    if not os.path.isfile(input_file):
        print(f"{BOLD}{RED}File not found. Please try again.{RESET}")
        return

    output_filename = input(f"{BOLD}{LIGHT_GREEN}Enter output file name (default: Scanned.txt): {RESET}") or "Scanned.txt"
    output_file = get_output_file_path(input_file, output_filename)

    threads = input(f"{BOLD}{LIGHT_GREEN}Enter number of threads (default: 10): {RESET}") or "10"

    # Convert threads to int
    try:
        threads = int(threads)
    except ValueError:
        print(f"{BOLD}{RED}Invalid number of threads. Using default value: 10{RESET}")
        threads = 10

    scan_subdomains_with_bughunter(input_file, output_file, threads)

if __name__ == "__main__":
    main()
