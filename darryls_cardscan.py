import os
import re
import logging
import sys
import socket
import requests
from typing import List

""" Setup Logging """
log_file_path = 'darryls_scan.log'
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def get_free_memory():
    """ Get the amount of free memory in MB from /proc/meminfo. """
    try:
        with open('/proc/meminfo', 'r') as meminfo:
            for line in meminfo:
                if 'MemAvailable' in line:
                    # Extract the number and convert it from kB to MB
                    free_memory_kb = int(line.split()[1])
                    return free_memory_kb / 1024
    except FileNotFoundError:
        return None

def get_lan_ip():
    """ Get the LAN IP address of the system. """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except socket.error:
        return None

def get_external_ip():
    """ Get the external IP address of the system. """
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException:
        return None

def get_system_info():
    """ Get system information including hostname, local IP, external IP, and free memory. """
    hostname = socket.gethostname()
    lan_ip = get_lan_ip()
    external_ip = get_external_ip()
    free_memory = get_free_memory()
    print("-" * 30)
    logging.info("-" * 30)
    print(f"Hostname: {hostname}")
    logging.info(f"Hostname: {hostname}")
    print(f"LAN IP Address: {lan_ip if lan_ip else 'Not available'}")
    logging.info(f"LAN IP Address: {lan_ip if lan_ip else 'Not available'}")
    print(f"External IP Address: {external_ip if external_ip else 'Not available'}")
    logging.info(f"External IP Address: {external_ip if external_ip else 'Not available'}")
    print(f"Free Memory: {free_memory:.2f} MB" if free_memory is not None else "Free Memory: Not available")
    logging.info(f"Free Memory: {free_memory:.2f} MB" if free_memory is not None else "Free Memory: Not available")
    print("-" * 30)
    logging.info("-" * 30)

def is_luhn_valid(card_number: str) -> bool:
    """ Check if the card number is valid based on Luhn's algorithm. """
    """ Remove any known false positives """
    false_positive_numbers = {'0000000000000000', '00000000000000', '000000000000000000'}
    if card_number in false_positive_numbers:
        return False
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10 == 0

def get_card_type(card_number: str) -> str:
    """ Determine the credit card type based on the card number. """
    card_type = "Unknown"
    first_digit = card_number[0]
    first_two_digits = card_number[:2]
    first_four_digits = card_number[:4]
    first_six_digits = int(card_number[:6])

    if len(card_number) >= 13:
        if first_two_digits in ["34", "37"]:
            card_type = "American Express"
        elif first_four_digits in ["6011"] or (644 <= first_six_digits <= 649) or first_two_digits == "65":
            card_type = "Discover"
        elif 3528 <= first_six_digits <= 3589:
            card_type = "JCB"
        elif 51 <= int(first_two_digits) <= 55:
            card_type = "Mastercard"
        elif 622126 <= first_six_digits <= 622925 or 624000 <= first_six_digits <= 626999 or 628200 <= first_six_digits <= 628899:
            card_type = "UnionPay"
        elif first_digit == "4":
            card_type = "Visa"

    return card_type

def find_potential_card_numbers(s: str) -> List[str]:
    """ Find potential card numbers using regex. Assumes numbers are separated by non-numeric characters. """
    potential_cards = re.findall(r'\b(?:\d[ -]*?){13,19}\b', s)
    return [''.join(filter(str.isdigit, card)) for card in potential_cards]

""" This is our list of ignored file extensions """
ignored_extensions = {'.pdf', '.docx', '.bin', '.exe', '.dll', '.zip', '.rar', '.gz'}  # Add more as needed

def scan_file(file_path: str):
    """ Scan a single file for valid credit card numbers. """
    """ Skip the log file that we create """
    if file_path.endswith(log_file_path):
        return
    if file_path.lower().endswith(tuple(ignored_extensions)):
        logging.info(f"Skipping file: {file_path}")
        return
    logging.info(f"Opening file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            potential_cards = find_potential_card_numbers(content)
            for card in potential_cards:
                if is_luhn_valid(card):
                    card_type = get_card_type(card)
                    print(f"Valid {card_type} card number found in {file_path}: {card}")
                    logging.info(f"Valid {card_type} card number found in {file_path}: {card}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        logging.info(f"Error reading file {file_path}: {e}")

def scan_file_chunk(file_path: str):
    """ Scan a single file for valid credit card numbers by reading in chunks. """
    """ Skip the log file that we create """
    if file_path.endswith(log_file_path):
        return
    if file_path.lower().endswith(tuple(ignored_extensions)):
        logging.info(f"Skipping file: {file_path}")
        return
    logging.info(f"Opening file: {file_path}")
    chunk_size = 1024 * 1024  # Size of each chunk in bytes (1MB in this example)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:  # Break if no more data
                    break

                potential_cards = find_potential_card_numbers(chunk)
                for card in potential_cards:
                    if is_luhn_valid(card):
                        card_type = get_card_type(card)
                        print(f"Valid {card_type} card number found in {file_path}: {card}")
                        logging.info(f"Valid {card_type} card number found in {file_path}: {card}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        logging.info(f"Error reading file {file_path}: {e}")

def scan_directory(path: str, use_chunk_method=False):
    """ Recursively scan a directory for files and analyze each file. """
    ignored_directories = {'/proc', '/sys', '/dev', '/var/log/journal', '/boot', '/tmp', '/var/tmp', '/lost+found', '/mnt', '/media', '/usr', '/bin', '/sbin', '/lib', '/lib64'}
    """
    /sys and /proc: Virtual filesystems providing windows into kernel internals.
    /dev: Contains device files and is not a typical location for stored user data.
    /boot: Contains boot loader files, kernels, and other files needed to boot the operating system.
    /tmp and /var/tmp: Temporary file storage. While it's possible for temporary files to contain sensitive data, these directories are often cleared on reboot or contain transient data.
    /lost+found: Used by the fsck utility for recovering files after a file system check. Files here are usually fragmented and not useful for your scan.
    /mnt and /media: Mount points for temporary mounts and removable media. Scanning here might not be useful, especially if these directories are used for mounting external resources that don't need to be scanned.
    /usr: Contains the majority of user utilities and applications. While there's a possibility of stored data in subdirectories like /usr/local, most contents are static application files.
    /bin, /sbin, /lib, /lib64: Contain binary executables and libraries essential for the system's operation. These directories are unlikely to contain user data.
    """
    scan_method = scan_file_chunk if use_chunk_method else scan_file
    for root, dirs, files in os.walk(path):
        """ Skip ignored directories """
        if any(ignored_dir in root for ignored_dir in ignored_directories):
            continue
        for file in files:
            scan_method(os.path.join(root, file))

""" MAIN """
if __name__ == "__main__":
    """ Print the IP and Hostname """
    get_system_info()
    """ Print the free memory """
    free_memory = get_free_memory()
    if free_memory is not None:
        print(f"Free memory available: {free_memory:.2f} MB")
    use_chunk_method = '-chunk' in sys.argv
    scan_directory('/', use_chunk_method=use_chunk_method)
