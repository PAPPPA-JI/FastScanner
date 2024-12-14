import os
import re
from colorama import Fore, Style, init
import time

# Initialize colorama for colored text in the terminal
init(autoreset=True)

# ANSI escape codes for additional formatting
ORANGE = '\033[38;5;214m'
BOLD = "\033[1m" 
SKY_BLUE = "\033[94m" 
RESET = "\033[0m"  # Reset text formatting

# Helper function for user input
def get_input(prompt):
    return input(prompt)

# Main function to clean text file and extract domains and IPs
def txt_cleaner(file_path, output_file):
    try:
        with open(file_path, 'r') as infile:
            file_contents = infile.readlines()
    except FileNotFoundError:
        print(Fore.RED + "❌ The specified input file does not exist. Please check the filename and try again.")
        return
    except PermissionError:
        print(Fore.RED + "❌ Permission denied. Check file permissions and try again.")
        return
    except Exception as ex:
        print(Fore.RED + f"❌ An error occurred while reading the file: {ex}")
        return

    total_lines = len(file_contents)
    domain_pattern = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b')
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

    domains = set()
    ips = set()

    for i, line in enumerate(file_contents):
        domains.update(domain_pattern.findall(line))
        ips.update(ip_pattern.findall(line))
        # Progress bar update
        print(f"[{'*' * ((i + 1) * 20 // total_lines)}{' ' * (20 - (i + 1) * 20 // total_lines)}] {((i + 1) * 100) // total_lines}% ", end='\r')

    if not domains and not ips:
        print(Fore.YELLOW + "⚠️ No domains or IP addresses were found in the file.")
        return

    try:
        with open(output_file, 'w') as outfile:
            for domain in sorted(domains):
                outfile.write(domain + "\n")
            outfile.write("\n" * 4)
            for ip in sorted(ips):
                outfile.write(ip + "\n")
    except PermissionError:
        print(Fore.RED + "❌ Permission denied while writing to the output file.")
        return
    except Exception as ex:
        print(Fore.RED + f"❌ An error occurred while writing to the file: {ex}")
        return

    print(Fore.GREEN + Style.BRIGHT + f"√ Domains and IP addresses have been saved to '{output_file}'.")
    print("\n")

# Function to create a banner
def create_banner(text):
    terminal_width = os.get_terminal_size().columns
    text_length = len(text)
    if text_length > terminal_width - 4:
        text = text[:terminal_width - 4]

    padding = (terminal_width - text_length - 2) // 2
    banner = f"{'=' * terminal_width}\n"
    banner += f"|{' ' * padding}{text}{' ' * (padding - 1)}|\n"
    banner += f"{'=' * terminal_width}\n"
    return banner

# Main function
def main():
    # Print banner
    banner_text = "IP | Domain Extractor"
    print(Fore.CYAN + Style.BRIGHT + create_banner(banner_text) + Style.RESET_ALL)

    # Get file path from user
    print(Fore.GREEN + Style.BRIGHT + "Enter File Path: " + Style.RESET_ALL, end="")
    file_path = get_input("").strip()

    # Validate file existence
    if not os.path.exists(file_path):
        print(Fore.RED + "❌ The specified file does not exist. Please check the path and try again." + Style.RESET_ALL)
        return

    # Validate file format
    if not file_path.lower().endswith('.txt'):
        print(Fore.RED + "❌ Invalid file format. Ensure it is a .txt file." + Style.RESET_ALL)
        return
    
    # Get output file name from user
    print(Fore.GREEN + Style.BRIGHT + "Enter Output File Name: " + Style.RESET_ALL, end="")
    output_file = get_input("").strip()

    # Ensure .txt extension for output file
    if not output_file.endswith('.txt'):
        output_file += '.txt'

    # Simulate progress bar before starting the cleaning process
    for i in range(21):
        time.sleep(0.1)
        print(f"[{'*' * i}{' ' * (20 - i)}]{i * 5}% ", end='\r')
    print("[********************]100%")

    # Call the text cleaner function
    txt_cleaner(file_path, output_file)

    # Return to the main menu
    input(f"{BOLD}{SKY_BLUE}\nPress Enter to go to main menu...{RESET}")

# Entry point of the script
if __name__ == "__main__":
    main()