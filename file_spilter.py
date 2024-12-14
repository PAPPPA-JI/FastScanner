import os
import shutil

# Color codes (for terminal output formatting)
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
BLUE = '\033[34m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Config file path (for saving user preferences)
CONFIG_FILE = os.path.expanduser("~/.domainsplitter_config")

# Display the custom ASCII banner
def print_banner():
    print(f"{BLUE}{BOLD}")
    print("          DOMAIN SPLITTING TOOL")
    print("                     ______")
    print("  Developed by     .-\"      \".   PAPPPA")
    print("                 /            \\")
    print("  Release at     |              |   14/12/2024")
    print("                |,  .-.  .-.  ,|")
    print("                | )(__/  \\__)( |")
    print("                |/     /\\     \\|")
    print("      (@_       (_     ^^     _)")
    print(" _     ) \\_______\\__|IIIIII|__/__________________________")
    print("(_)@8@8{}<________|-\\IIIIII/-|___________________________>")
    print("       )_/        \\          /")
    print("      (@           `--------` ")
    print("                Version: 2.0 - Initial Release")
    print(f"{RESET}")

# Step 1: Get the file path from the user
def get_file_path():
    print(f"{YELLOW}{BOLD}Enter Domain file path{RESET}")
    file_path = input("➡️ File Path: ")
    return file_path

# Check if the file exists and is a text file
def check_file(file_path):
    if os.path.isfile(file_path) and file_path.lower().endswith(".txt"):
        print(f"{GREEN}{BOLD}✅ 𝗙𝗶𝗹𝗲 𝘄𝗮𝘀 𝗳𝗼𝘂𝗻𝗱!{RESET}")
        return True
    else:
        print(f"{RED}{BOLD}❌ File not found or invalid format. Ensure it is a .txt file.{RESET}")
        return False

# Step 2: Get suggested number of parts based on file size and line count
def calculate_parts(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        line_count = len(lines)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # in MB
        print(f"{BLUE}{BOLD}Total lines: {line_count}, File size: {file_size:.2f} MB{RESET}")

        suggested_parts = (line_count // 200) + 1
        print(f"{YELLOW}{BOLD}Suggested parts: approximately {suggested_parts}.{RESET}")
        return line_count
    except Exception as e:
        print(f"{RED}{BOLD}❌ Error reading the file: {e}{RESET}")
        return None

# Step 3: Get the number of parts from the user
def get_num_parts():
    while True:
        print(f"{YELLOW}{BOLD}Enter number of parts:{RESET}")
        try:
            num_parts = int(input("➡️ Number of parts: "))
            if num_parts > 0:
                return num_parts
            else:
                print(f"{RED}{BOLD}❌ Please enter a valid positive integer.{RESET}")
        except ValueError:
            print(f"{RED}{BOLD}❌ Please enter a valid positive integer.{RESET}")

# Step 4: Get the file prefix for the output files
def get_file_prefix():
    saved_prefix = None
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as config_file:
                lines = config_file.readlines()
                saved_prefix = lines[0].strip().split('=')[1] if len(lines) > 0 else None
                print(f"{YELLOW}{BOLD}Previous prefix: {saved_prefix}{RESET}")
        except Exception as e:
            print(f"{RED}{BOLD}❌ Error reading config file: {e}{RESET}")
    
    print(f"{YELLOW}{BOLD}Enter file prefix (default: 'part'):{RESET}")
    file_prefix = input("➡️ File prefix: ") or "part"
    return file_prefix

# Step 5: Get the save location from the user
def get_output_path():
    saved_path = None
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as config_file:
                lines = config_file.readlines()
                saved_path = lines[1].strip().split('=')[1] if len(lines) > 1 else None
                print(f"{YELLOW}{BOLD}Previous save location: {saved_path}{RESET}")
        except Exception as e:
            print(f"{RED}{BOLD}❌ Error reading config file: {e}{RESET}")
    
    print(f"{YELLOW}{BOLD}Enter save location (default: '/storage/emulated/0/'):{RESET}")
    output_path = input("➡️ Save location: ") or "/storage/emulated/0/"
    if not os.path.isdir(output_path):
        try:
            print(f"{YELLOW}{BOLD}Directory not found, creating it.{RESET}")
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            print(f"{RED}{BOLD}❌ Error creating directory: {e}{RESET}")
            return None
    return output_path

# Step 6: Splitting process
def split_file(file_path, num_parts, file_prefix, output_path, line_count):
    try:
        lines_per_part = (line_count + num_parts - 1) // num_parts  # rounding up

        print(f"{BLUE}{BOLD}Splitting in progress... Please wait.{RESET}")
        
        with open(file_path, 'r') as file:
            lines = file.readlines()

        part_number = 1
        for i in range(0, line_count, lines_per_part):
            part_filename = os.path.join(output_path, f"{file_prefix}_{part_number}.txt")
            with open(part_filename, 'w') as part_file:
                part_file.writelines(lines[i:i + lines_per_part])
            part_number += 1

        print(f"{GREEN}{BOLD}🎉 File has been split into {num_parts} parts and saved at {output_path}!{RESET}")

        # Summary
        print(f"{BLUE}{BOLD}")
        print("=========================================")
        print(f"Process Summary:")
        print(f"➡️ Total lines: {line_count}")
        print(f"➡️ Lines per part: {lines_per_part}")
        print(f"➡️ Number of parts: {num_parts}")
        print(f"➡️ Output directory: {output_path}")
        print("=========================================")
        print(f"{RESET}")
    except Exception as e:
        print(f"{RED}{BOLD}❌ Error splitting the file: {e}{RESET}")

# Save current settings for next time
def save_config(file_prefix, output_path):
    try:
        with open(CONFIG_FILE, 'w') as config_file:
            config_file.write(f"saved_prefix={file_prefix}\n")
            config_file.write(f"saved_path={output_path}\n")
    except Exception as e:
        print(f"{RED}{BOLD}❌ Error saving config file: {e}{RESET}")

def main():
    print_banner()
    
    file_path = get_file_path()
    
    if not check_file(file_path):
        return
    
    line_count = calculate_parts(file_path)
    if line_count is None:
        return
    
    num_parts = get_num_parts()
    
    file_prefix = get_file_prefix()
    output_path = get_output_path()
    if not output_path:
        return
    
    # Save settings for future use
    save_config(file_prefix, output_path)
    
    split_file(file_path, num_parts, file_prefix, output_path, line_count)

if __name__ == "__main__":
    main()