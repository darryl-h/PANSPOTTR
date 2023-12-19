import os
import re
import logging

# Setting up logging
logging.basicConfig(filename='darryls_scan.log', level=logging.INFO, format='%(asctime)s - %(message)s')

from typing import List

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

def scan_directory(path: str):
    """ Recursively scan a directory for files and analyze each file. """
    for root, dirs, files in os.walk(path):
        for file in files:
            scan_file(os.path.join(root, file))

# Example usage
scan_directory('/')
