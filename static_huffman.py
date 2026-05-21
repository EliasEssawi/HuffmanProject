# -*- coding: utf-8 -*-
"""

@author: Elias

Created for Adaptive Huffman Coding with Inertia Homework

This file implements Static Huffman Coding in two versions:

1. Static Huffman - Global
   One frequency table is built for the entire generated_input.txt file.

2. Static Huffman - Per Block
   A separate frequency table is built for each of the 34 blocks.

The goal of this file is to calculate:
- encoded size in bits
- frequency table storage size in bits
- total compressed size in bits
- compression ratio r

Compression ratio formula:
r = encoded size in bits / original size in bits

Original text uses plain ASCII/lowercase characters.
So the original size is:
number of characters * 8 bits
"""

import heapq
import csv


# ------------------------------------------------------------
# Project settings
# ------------------------------------------------------------

TOTAL_TEXT_LENGTH = 10_000_000
NUMBER_OF_BLOCKS = 34
INPUT_FILE_PATH = "generated_input.txt"
STATIC_RESULTS_FILE_PATH = "static_huffman_results.csv"


# ------------------------------------------------------------
# Function: read input text from file
# ------------------------------------------------------------

def read_text_file(file_path):
    """
    Reads the generated input text from a plain .txt file.

    The text file should already exist.
    It is created by text_generator.py.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return text


# ------------------------------------------------------------
# Function: calculate block sizes
# ------------------------------------------------------------

def calculate_block_sizes(total_length, number_of_blocks):
    """
    Calculates the same block sizes used in text_generator.py.

    Since 10,000,000 is not divisible by 34:
    - Blocks 1 to 33 have the rounded size.
    - Block 34 is adjusted to keep the total exactly 10,000,000.
    """

    rounded_block_size = round(total_length / number_of_blocks)

    block_sizes = []

    # Add rounded size for the first 33 blocks.
    for _ in range(number_of_blocks - 1):
        block_sizes.append(rounded_block_size)

    # The last block receives the remaining characters.
    used_length_so_far = sum(block_sizes)
    last_block_size = total_length - used_length_so_far

    block_sizes.append(last_block_size)

    return block_sizes


# ------------------------------------------------------------
# Function: split text into blocks
# ------------------------------------------------------------

def split_text_into_blocks(text, block_sizes):
    """
    Splits the full text into blocks according to the calculated sizes.

    This is needed for Static Huffman - Per Block.
    Each block will get its own frequency table and Huffman code.
    """

    blocks = []
    start_index = 0

    # Cut the text block by block using the known block sizes.
    for block_size in block_sizes:
        end_index = start_index + block_size
        block = text[start_index:end_index]
        blocks.append(block)
        start_index = end_index

    return blocks


# ------------------------------------------------------------
# Function: build frequency table
# ------------------------------------------------------------

def build_frequency_table(text):
    """
    Builds a frequency table for the given text.

    Example:
    text = 'aaabbc'
    result = {'a': 3, 'b': 2, 'c': 1}
    """

    frequency_table = {}

    # Count how many times each character appears.
    for character in text:
        if character not in frequency_table:
            frequency_table[character] = 0

        frequency_table[character] += 1

    return frequency_table


# ------------------------------------------------------------
# Function: build Huffman code lengths
# ------------------------------------------------------------

def build_huffman_code_lengths(frequency_table):
    """
    Builds Huffman code lengths from a frequency table.

    We do not need the actual binary codes here.
    For compression size, we only need the length of each code.

    The function returns:
    {'a': 1, 'b': 3, 'c': 3, ...}
    """

    # Special case: empty text.
    if not frequency_table:
        return {}

    # Special case: if there is only one symbol, give it code length 1.
    if len(frequency_table) == 1:
        only_symbol = next(iter(frequency_table))
        return {only_symbol: 1}

    heap = []

    # Each heap item contains:
    # frequency, unique_id, list_of_symbols
    #
    # unique_id prevents Python from comparing symbol lists directly.
    unique_id = 0

    for symbol, frequency in frequency_table.items():
        heapq.heappush(heap, (frequency, unique_id, [symbol]))
        unique_id += 1

    # At the start, every symbol has code length 0.
    code_lengths = {}

    for symbol in frequency_table:
        code_lengths[symbol] = 0

    # Huffman algorithm:
    # repeatedly merge the two lowest-frequency nodes.
    while len(heap) > 1:
        frequency_1, _, symbols_1 = heapq.heappop(heap)
        frequency_2, _, symbols_2 = heapq.heappop(heap)

        # Every symbol inside the merged nodes gets one extra bit.
        for symbol in symbols_1:
            code_lengths[symbol] += 1

        for symbol in symbols_2:
            code_lengths[symbol] += 1

        merged_frequency = frequency_1 + frequency_2
        merged_symbols = symbols_1 + symbols_2

        heapq.heappush(heap, (merged_frequency, unique_id, merged_symbols))
        unique_id += 1

    return code_lengths


# ------------------------------------------------------------
# Function: calculate encoded data size
# ------------------------------------------------------------

def calculate_encoded_data_size_bits(frequency_table, code_lengths):
    """
    Calculates how many bits are needed to encode the text data.

    Formula:
    encoded bits = sum(frequency(symbol) * code_length(symbol))
    """

    encoded_size_bits = 0

    # Add the contribution of each symbol to the encoded size.
    for symbol, frequency in frequency_table.items():
        encoded_size_bits += frequency * code_lengths[symbol]

    return encoded_size_bits


# ------------------------------------------------------------
# Function: calculate stored frequency table size
# ------------------------------------------------------------

def calculate_frequency_table_size_bits(frequency_table):
    """
    Calculates the storage cost of saving a frequency table.

    We must include the stored table size in the compression ratio.

    Simple storage model used here:
    - 8 bits to store the number of symbols in the table.
    - For each symbol:
        8 bits for the character itself.
        32 bits for its frequency.

    So:
    table size = 8 + number_of_symbols * (8 + 32)
    """

    number_of_symbols = len(frequency_table)

    bits_for_number_of_symbols = 8
    bits_for_each_symbol = 8
    bits_for_each_frequency = 32

    table_size_bits = (
        bits_for_number_of_symbols
        + number_of_symbols * (bits_for_each_symbol + bits_for_each_frequency)
    )

    return table_size_bits


# ------------------------------------------------------------
# Function: calculate compression ratio
# ------------------------------------------------------------

def calculate_compression_ratio(total_encoded_size_bits, original_size_bits):
    """
    Calculates the compression ratio.

    Smaller ratio means better compression.
    """

    return total_encoded_size_bits / original_size_bits


# ------------------------------------------------------------
# Function: run Static Huffman - Global
# ------------------------------------------------------------

def run_static_huffman_global(text):
    """
    Runs Static Huffman Coding using one global frequency table.

    Steps:
    1. Build one frequency table for the whole text.
    2. Build Huffman code lengths.
    3. Calculate encoded data size.
    4. Add frequency table storage cost.
    5. Calculate compression ratio.
    """

    frequency_table = build_frequency_table(text)
    code_lengths = build_huffman_code_lengths(frequency_table)

    encoded_data_size_bits = calculate_encoded_data_size_bits(
        frequency_table,
        code_lengths
    )

    table_size_bits = calculate_frequency_table_size_bits(frequency_table)

    total_encoded_size_bits = encoded_data_size_bits + table_size_bits
    original_size_bits = len(text) * 8

    compression_ratio = calculate_compression_ratio(
        total_encoded_size_bits,
        original_size_bits
    )

    return {
        "method": "Static Huffman - Global",
        "encoded_data_size_bits": encoded_data_size_bits,
        "table_size_bits": table_size_bits,
        "total_encoded_size_bits": total_encoded_size_bits,
        "compression_ratio": compression_ratio,
        "number_of_tables": 1
    }


# ------------------------------------------------------------
# Function: run Static Huffman - Per Block
# ------------------------------------------------------------

def run_static_huffman_per_block(blocks):
    """
    Runs Static Huffman Coding separately for each block.

    Each block gets:
    - its own frequency table
    - its own Huffman code lengths
    - its own table storage cost

    The final result is the sum over all blocks.
    """

    total_encoded_data_size_bits = 0
    total_table_size_bits = 0
    original_size_bits = 0

    # Process each block independently.
    for block in blocks:
        frequency_table = build_frequency_table(block)
        code_lengths = build_huffman_code_lengths(frequency_table)

        encoded_data_size_bits = calculate_encoded_data_size_bits(
            frequency_table,
            code_lengths
        )

        table_size_bits = calculate_frequency_table_size_bits(frequency_table)

        total_encoded_data_size_bits += encoded_data_size_bits
        total_table_size_bits += table_size_bits
        original_size_bits += len(block) * 8

    total_encoded_size_bits = (
        total_encoded_data_size_bits
        + total_table_size_bits
    )

    compression_ratio = calculate_compression_ratio(
        total_encoded_size_bits,
        original_size_bits
    )

    return {
        "method": "Static Huffman - Per Block",
        "encoded_data_size_bits": total_encoded_data_size_bits,
        "table_size_bits": total_table_size_bits,
        "total_encoded_size_bits": total_encoded_size_bits,
        "compression_ratio": compression_ratio,
        "number_of_tables": len(blocks)
    }


# ------------------------------------------------------------
# Function: save static Huffman results to CSV
# ------------------------------------------------------------

def save_results_to_csv(results, file_path):
    """
    Saves the static Huffman results into a CSV file.

    This makes it easier to use the results later in the report.
    """

    column_names = [
        "method",
        "encoded_data_size_bits",
        "table_size_bits",
        "total_encoded_size_bits",
        "compression_ratio",
        "number_of_tables"
    ]

    with open(file_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=column_names)

        writer.writeheader()

        for result in results:
            writer.writerow(result)


# ------------------------------------------------------------
# Function: print result nicely
# ------------------------------------------------------------

def print_static_result(result):
    """
    Prints one static Huffman result in a clear format.
    """

    print(result["method"])
    print("-" * len(result["method"]))
    print(f"Encoded data size: {result['encoded_data_size_bits']:,} bits")
    print(f"Frequency table size: {result['table_size_bits']:,} bits")
    print(f"Total encoded size: {result['total_encoded_size_bits']:,} bits")
    print(f"Compression ratio r: {result['compression_ratio']:.6f}")
    print(f"Number of stored tables: {result['number_of_tables']}")
    print()


# ------------------------------------------------------------
# Main function
# ------------------------------------------------------------

def main():
    """
    Main program flow:
    1. Read generated_input.txt.
    2. Validate its length.
    3. Run Static Huffman - Global.
    4. Split text into 34 blocks.
    5. Run Static Huffman - Per Block.
    6. Print results.
    7. Save results into static_huffman_results.csv.
    """

    print("Reading generated input text...")
    text = read_text_file(INPUT_FILE_PATH)

    # Check that the input file has the expected homework size.
    assert len(text) == TOTAL_TEXT_LENGTH, (
        f"Error: input text length is {len(text):,}, "
        f"expected {TOTAL_TEXT_LENGTH:,}."
    )

    print("Input text loaded successfully.")
    print(f"Input text length: {len(text):,} characters")
    print()

    # Run global static Huffman on the full text.
    global_result = run_static_huffman_global(text)

    # Prepare the same block division used by text_generator.py.
    block_sizes = calculate_block_sizes(TOTAL_TEXT_LENGTH, NUMBER_OF_BLOCKS)
    blocks = split_text_into_blocks(text, block_sizes)

    # Run per-block static Huffman.
    per_block_result = run_static_huffman_per_block(blocks)

    # Print both results clearly.
    print_static_result(global_result)
    print_static_result(per_block_result)

    # Save results for later use in the report.
    save_results_to_csv(
        [global_result, per_block_result],
        STATIC_RESULTS_FILE_PATH
    )

    print(f"Static Huffman results saved to: {STATIC_RESULTS_FILE_PATH}")


# ------------------------------------------------------------
# Run the program
# ------------------------------------------------------------

if __name__ == "__main__":
    main()