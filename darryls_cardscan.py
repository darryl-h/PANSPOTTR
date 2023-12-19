import os
import re
import logging
from typing import List

# Setting up logging
logging.basicConfig(filename='darryls_scan.log', level=logging.INFO, format='%(asctime)s - %(message)s')

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
        print("Could not access /proc/meminfo")
        return None

def is_luhn_valid(card_number: str) -> bool:
    """ Check if the card number is valid based on Luhn's algorithm. """
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10 == 0

def find_potential_card_numbers(s: str) -> List[str]:
    """ Find potential card numbers using regex. Assumes numbers are separated by non-numeric characters. """
    potential_cards = re.findall(r'\b(?:\d[ -]*?){13,19}\b', s)
    return [''.join(filter(str.isdigit, card)) for card in potential_cards]

def scan_file(file_path: str):
    """ Scan a single file for valid credit card numbers. """
    logging.info(f"Opening file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            potential_cards = find_potential_card_numbers(content)
            for card in potential_cards:
                if is_luhn_valid(card):
                    print(f"Valid card number found in {file_path}: {card}")
                    logging.info(f"Valid card number found in {file_path}: {card}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        logging.info(f"Error reading file {file_path}: {e}")

def scan_file_lowmem(file_path: str):
    """ Scan a single file for valid credit card numbers by reading in chunks. """
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
                        print(f"Valid card number found in {file_path}: {card}")
                        logging.info(f"Valid card number found in {file_path}: {card}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        logging.info(f"Error reading file {file_path}: {e}")

def scan_directory(path: str):
    """ Recursively scan a directory for files and analyze each file. """
    for root, dirs, files in os.walk(path):
        for file in files:
            scan_file(os.path.join(root, file))

# Example usage
free_memory = get_free_memory()
if free_memory is not None:
    print(f"Free memory available: {free_memory:.2f} MB")

scan_directory('/')

