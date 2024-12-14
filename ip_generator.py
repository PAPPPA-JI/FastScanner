import os
import ipaddress
from tqdm import tqdm
import logging
import subprocess

# Setup logging configuration
logging.basicConfig(filename='ip_generator.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

def log_event(message):
    logging.info(message)

def save_ips_to_file(ip_list, file_name):
    try:
        # Ensure the directory for the file exists
        directory = os.path.dirname(file_name)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Save the IPs to the file
        with open(file_name, "w") as f:
            for ip in ip_list:
                f.write(f"{ip}\n")
        print(f"\033[1;32mIPs successfully saved to {file_name}\033[0m")
        log_event(f"IPs successfully saved to {file_name}")
    except FileNotFoundError:
        print(f"\033[1;31mError: The specified file path does not exist!\033[0m")
    except IOError as e:
        print(f"\033[1;31mError: Unable to write to file. {e}\033[0m")
    except Exception as e:
        print(f"\033[1;31mUnexpected error occurred: {e}\033[0m")
        log_event(f"Error: {e}")

def is_valid_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False

def get_valid_ip(prompt):
    while True:
        ip = input(prompt)
        if is_valid_ip(ip):
            return ip
        else:
            print("\033[1;31mInvalid IP address. Please enter a valid IP address.\033[0m")

def generate_ips_from_range(start_ip, end_ip, file_name):
    try:
        start = ipaddress.IPv4Address(start_ip)
        end = ipaddress.IPv4Address(end_ip)

        if start > end:
            print("\033[1;31mError: Starting IP must be less than or equal to the Ending IP!\033[0m")
            return

        ip_list = [ipaddress.IPv4Address(ip) for ip in range(int(start), int(end) + 1)]
        total_ips = len(ip_list)
        print(f"\033[1;34mGenerating IPs from {start_ip} to {end_ip}\033[0m")

        with tqdm(total=total_ips, desc="Progress", ncols=75) as pbar:
            save_ips_to_file(ip_list, file_name)
            pbar.update(total_ips)
    except ValueError:
        print(f"\033[1;31mError: Invalid IP address range '{start_ip} - {end_ip}'.\033[0m")
    except Exception as e:
        print(f"\033[1;31mUnexpected error occurred: {e}\033[0m")
        log_event(f"Error: {e}")

def generate_ips_from_cidr(cidr, file_name):
    try:
        network = ipaddress.IPv4Network(cidr, strict=False)
        ip_list = [str(ip) for ip in network.hosts()]
        total_ips = len(ip_list)
        print(f"\033[1;34mGenerating IPs from CIDR {cidr}\033[0m")

        with tqdm(total=total_ips, desc="Progress", ncols=75) as pbar:
            save_ips_to_file(ip_list, file_name)
            pbar.update(total_ips)
    except ValueError:
        print(f"\033[1;31mError: Invalid CIDR '{cidr}'.\033[0m")
    except Exception as e:
        print(f"\033[1;31mUnexpected error occurred: {e}\033[0m")
        log_event(f"Error: {e}")

def parse_file_for_cidr(file_name, output_file):
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if '/' in line:  # Check for CIDR format
                generate_ips_from_cidr(line, output_file)
    except FileNotFoundError:
        print(f"\033[1;31mError: File '{file_name}' not found.\033[0m")
    except Exception as e:
        print(f"\033[1;31mUnexpected error occurred: {e}\033[0m")
        log_event(f"Error: {e}")

def main():
    while True:
        print("\n\033[1;33m" + "="*50 + "\033[0m")
        print("\033[1;34mSelect an option:\033[0m")
        print("1. \033[1;32mEnter IP range manually\033[0m")
        print("2. \033[1;32mEnter CIDR range manually\033[0m")
        print("3. \033[1;32mExtract CIDR ranges from file\033[0m")
        print("4. \033[1;31mExit to Main Menu\033[0m")
        choice = input("\033[1;34mEnter your choice (1/2/3/4): \033[0m")

        if choice == "1":
            start_ip = get_valid_ip("Enter starting IP: ")
            end_ip = get_valid_ip("Enter ending IP: ")
            file_name = "/storage/emulated/0/" + input("Enter output file name (e.g., ips.txt): ")
            generate_ips_from_range(start_ip, end_ip, file_name)

        elif choice == "2":
            cidr = input("Enter CIDR range (e.g., 192.168.1.0/24): ")
            file_name = "/storage/emulated/0/" + input("Enter output file name (e.g., ips.txt): ")
            generate_ips_from_cidr(cidr, file_name)

        elif choice == "3":
            file_name = "/storage/emulated/0/" + input("Enter the filename with CIDR ranges (e.g., cidr_ranges.txt): ")
            output_file = "/storage/emulated/0/" + input("Enter the output file name (e.g., ips.txt): ")
            parse_file_for_cidr(file_name, output_file)

        elif choice == "4":
            print("\033[1;32mRedirecting to Main Menu...\033[0m")
            try:
                subprocess.run(["python", "main.py"])  # Replace "python" with "python3" if needed
            except FileNotFoundError:
                print("\033[1;31mError: 'main.py' not found. Please ensure it is in the same directory.\033[0m")
            break

        else:
            print("\033[1;31mInvalid choice, please try again.\033[0m")

if __name__ == "__main__":
    main()