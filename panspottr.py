__author__ = "Darryl H"
__copyright__ = "Copyright 2023, Darryl H"
__credits__ = ["Darryl H"]
__license__ = "GPL"
__version__ = "20231228D"
__maintainer__ = "Darryl H"
__status__ = "Production"

import os
import re
import logging
import sys
import socket
import requests
from typing import List
import argparse  # Import argparse module

# Determine if the script is running in basic mode
use_basic_method = '-basic' in sys.argv

# Set of basic ignored file extensions
basic_ignored_extensions = {'.bin', '.exe', '.dll', '.zip', '.rar', '.gz'}

# Additional file types to ignore in basic mode
additional_ignored_extensions = {'.pdf', '.docx', '.rtf'}

# Conditional import for additional file types
if not use_basic_method:
    try:
        import docx
        from PyPDF2 import PdfReader
    except ImportError as e:
        missing_library = str(e).split("'")[1]  # Extract the name of the missing library
        if missing_library == 'docx':
            print("The 'python-docx' library is required but not installed.")
            print("Install it using the command: pip3 install python-docx")
        elif missing_library == 'PyPDF2':
            print("The 'PyPDF2' library is required but not installed.")
            print("Install it using the command: pip3 install PyPDF2")
        sys.exit(1)

""" Logging """
# Configure the logging filename
log_file_path = 'panspottr.log'
# Set the log file to append mode
file_handler = logging.FileHandler(log_file_path, mode='a')
# Configure logging to file with DEBUG level """
file_handler.setLevel(logging.DEBUG)
# Set the log format
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
# Configure logging to console with INFO level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
# Create a logger and add both handlers
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def parse_arguments():
    """
    Parse command line arguments for the script.

    Returns:
        argparse.Namespace: An object containing parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Primary Account Number Scanning, Protection, Observation & Threat Tracking Reporter")
    parser.add_argument('-b', '--basic', action='store_true', help='Enable basic scanning mode')
    parser.add_argument('-u', '--unknown', action='store_true', help='Report unknown card types')
    parser.add_argument('-p', '--path', type=str, default='/', help='Specify path to scan')
    return parser.parse_args()

def get_free_memory():
    """
    Get the amount of free memory in MB from /proc/meminfo.

    Reads the 'MemAvailable' line from /proc/meminfo to find the available memory,
    then converts it from kilobytes to megabytes.

    Returns:
        float: The amount of free memory in megabytes. Returns None if /proc/meminfo is not found.
    """
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
    """
    Get the LAN IP address of the system.

    Attempts to create a UDP connection (which is not actually established) to determine the
    LAN IP address of the machine.

    Returns:
        str: The LAN IP address of the machine. Returns None if an error occurs.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except socket.error:
        return None

def get_external_ip():
    """
    Get the external IP address of the system.

    Makes an HTTP request to an external service (api.ipify.org) to find the public IP address.

    Returns:
        str: The external IP address of the machine. Returns None if an error occurs or the request fails.
    """
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException:
        return None

def get_system_info(args):
    """
    Get and log system information including hostname, local IP, external IP, and free memory.

    Logs system information using the logging module. This includes the system's hostname,
    LAN IP address, external IP address, and available free memory.
    """
    banner = """
                      ___  _   _  _ ___ ___  ___ _____ _____ ___ 
                     | _ \/_\ | \| / __| _ \/ _ \_   _|_   _| _ \\
                     |  _/ _ \| .` \__ \  _/ (_) || |   | | |   /
                     |_|/_/ \_\_|\_|___/_|  \___/ |_|   |_| |_|_\\                     
     Primary Account Number Scanning, Protection, Observation & Threat Tracking Reporter
             Version {}   By: Darryl-h (https://github.com/darryl-h/)
    """.format(__version__)
    logging.info(banner)
    hostname = socket.gethostname()
    lan_ip = get_lan_ip()
    external_ip = get_external_ip()
    free_memory = get_free_memory()
    logging.info("-" * 30)
    logging.info(f"Command line arguments:")
    logging.info(f"Basic mode: {args.basic}")
    logging.info(f"Report unknown cards: {args.unknown}")
    logging.info(f"Scan path: {args.path if args.path else 'Default (/)'}")
    logging.info("-" * 30)
    logging.info(f"Hostname: {hostname}")
    logging.info(f"LAN IP Address: {lan_ip if lan_ip else 'Not available'}")
    logging.info(f"External IP Address: {external_ip if external_ip else 'Not available'}")
    logging.info(f"Free Memory: {free_memory:.2f} MB" if free_memory is not None else "Free Memory: Not available")
    logging.info("-" * 30)

""" File type specific reading functions """
def read_docx(file_path):
    """
    Read and extract text from a DOCX file.

    Args:
        file_path (str): Path to the DOCX file.

    Returns:
        str: The extracted text content from the DOCX file.
    """
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def read_pdf(file_path):
    """
    Read and extract text from a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: The extracted text content from the PDF file.
    """
    content = ""
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            # Use extract_text instead of extractText
            content += page.extract_text()  
    return content

def read_rtf(file_path):
    """
    Read and return content from an RTF file.

    Args:
        file_path (str): Path to the RTF file.

    Returns:
        str: The content of the RTF file.
    """
    with open(file_path, "r", encoding='utf-8', errors='ignore') as file:
        return file.read()

def is_luhn_valid(card_number: str) -> bool:
    """
    Check if a card number is valid based on Luhn's algorithm.

    Args:
        card_number (str): The credit card number to validate.

    Returns:
        bool: True if the card number is valid according to Luhn's algorithm, False otherwise.
    """
    # Remove any known false positives
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
    """
    Determine the credit card type based on the card number.

    Args:
        card_number (str): The credit card number.

    Returns:
        str: The type of the credit card ('American Express', 'Discover', etc.) or 'Unknown'.
    """
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
    """
    Find potential card numbers in a given string using regex.

    Args:
        s (str): The string to search for potential card numbers.

    Returns:
        List[str]: A list of potential card numbers found in the string.
    """
    potential_cards = re.findall(r'\b(?:\d[ -]*?){13,19}\b', s)
    return [''.join(filter(str.isdigit, card)) for card in potential_cards]

""" This is our list of ignored file extensions """
ignored_extensions = {'.pdf', '.docx', '.bin', '.exe', '.dll', '.zip', '.rar', '.gz'}  # Add more as needed

def scan_file(file_path: str, report_unknown=False):
    """
    Scan a single file for valid credit card numbers.

    Args:
        file_path (str): Path to the file to be scanned.
        report_unknown (bool): Flag to report unknown card types.

    This function will ignore certain file types based on their extensions and
    scan others for potential credit card numbers.
    """
    if file_path.endswith(log_file_path):
        return

    # Update the ignored extensions based on the mode
    ignored_extensions = basic_ignored_extensions.copy()
    if use_basic_method:
        ignored_extensions.update(additional_ignored_extensions)

    if file_path.lower().endswith(tuple(ignored_extensions)):
        logging.debug(f"Skipping file: {file_path}")
        return

    logging.debug(f"Opening file: {file_path}")
    try:
        content = ''
        if not use_basic_method:
            # Process special file types
            if file_path.lower().endswith('.docx'):
                content = read_docx(file_path)
            elif file_path.lower().endswith('.pdf'):
                content = read_pdf(file_path)
            elif file_path.lower().endswith('.rtf'):
                content = read_rtf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
        else:
            # Size of each chunk in bytes (1MB in this example)
            chunk_size = 1024 * 1024
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    process_content(chunk, file_path, report_unknown)

        if content:
            process_content(content, file_path, report_unknown)

    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")

def process_content(content: str, file_path: str, report_unknown=False):
    """
    Process the content of a file for valid credit card numbers.

    Args:
        content (str): Content of the file.
        file_path (str): Path of the file being processed.
        report_unknown (bool): Flag to report unknown card types.

    This function processes the content of a file and logs warnings for any valid credit card numbers found.
    """
    potential_cards = find_potential_card_numbers(content)
    for card in potential_cards:
        if is_luhn_valid(card):
            card_type = get_card_type(card)
            if card_type != "Unknown" or report_unknown:
                logging.warning(f"Valid {card_type} card number ({card}) found in {file_path}")

def scan_directory(path: str, report_unknown=False):
    """
    Recursively scan a directory for files and analyze each file for credit card numbers.

    Args:
        path (str): Path of the directory to scan.
        report_unknown (bool): Flag to report unknown card types.

    This function scans each file in a directory and its subdirectories for potential credit card numbers.
    """
    ignored_directories = {'/proc', '/sys', '/dev', '/var/log/journal', '/boot', '/tmp', '/var/tmp', '/lost+found', '/mnt', '/media', '/usr', '/bin', '/sbin', '/lib', '/lib64', '/run', '/srv', '/opt'}
    """
    /sys and /proc: Virtual filesystems providing windows into kernel internals.
    /dev: Contains device files and is not a typical location for stored user data.
    /boot: Contains boot loader files, kernels, and other files needed to boot the operating system.
    /tmp and /var/tmp: Temporary file storage. While it's possible for temporary files to contain sensitive data, these directories are often cleared on reboot or contain transient data.
    /lost+found: Used by the fsck utility for recovering files after a file system check. Files here are usually fragmented and not useful for your scan.
    /mnt and /media: Mount points for temporary mounts and removable media. Scanning here might not be useful, especially if these directories are used for mounting external resources that don't need to be scanned.
    /usr: Contains the majority of user utilities and applications. While there's a possibility of stored data in subdirectories like /usr/local, most contents are static application files.
    /bin, /sbin, /lib, /lib64: Contain binary executables and libraries essential for the system's operation. These directories are unlikely to contain user data.
    /run: runtime data for the system and processes.
    /srv: Contains data for services provided by the system.
    /opt: Used for the installation of add-on application software packages. Contains mostly static application files.
    """
    for root, dirs, files in os.walk(path):
        # Skip ignored directories
        if any(ignored_dir in root for ignored_dir in ignored_directories):
            continue
        for file in files:
            scan_file(os.path.join(root, file), report_unknown)

if __name__ == "__main__":
    args = parse_arguments()
    # Extract arguments
    use_basic_method = args.basic
    report_unknown_cards = args.unknown
    scan_path = args.path
    # Get and log system info
    get_system_info(args)
    logging.debug("-" * 30)
    scan_directory(scan_path, report_unknown=report_unknown_cards)
