# -*- coding: utf-8 -*-
"""

@author: Elias

Adaptive Huffman Coding with Inertia

This file implements Adaptive Huffman Coding with an INERTIA parameter.

The algorithm reads the input text character by character.
Before encoding each character, a Huffman tree is built from the current
symbol weights. Then the character is encoded, and its weight is increased.

After every INERTIA encoded characters, all weights are divided by 2
using integer division. Any weight that becomes 0 is reset to 1.

This creates a fading memory effect:
recent characters have stronger influence than very old characters.

This file produces:
1. adaptive_huffman_results.csv
2. adaptive_best_output.txt
3. adaptive_best_output.bin
"""

import heapq
import csv
import os
import string


# ------------------------------------------------------------
# Project settings
# ------------------------------------------------------------

INPUT_FILE_PATH = "generated_input.txt"

ADAPTIVE_RESULTS_FILE_PATH = "adaptive_huffman_results.csv"
BEST_OUTPUT_TEXT_FILE_PATH = "adaptive_best_output.txt"
BEST_OUTPUT_BINARY_FILE_PATH = "adaptive_best_output.bin"

TOTAL_TEXT_LENGTH = 10_000_000

# Original text uses 8 bits per character.
ORIGINAL_SIZE_BITS = TOTAL_TEXT_LENGTH * 8

# The homework requires testing INERTIA values up to 10,000,000.
INERTIA_VALUES = [
    50,
    100,
    200,
    500,
    1_000,
    2_000,
    5_000,
    10_000,
    20_000,
    50_000,
    100_000,
    10_000_000
]

# The generated text contains only lowercase English letters.
ALPHABET = string.ascii_lowercase


# ------------------------------------------------------------
# Function: read input text from file
# ------------------------------------------------------------

def read_text_file(file_path):
    """
    Reads the generated input text from generated_input.txt.

    The file should already be created by text_generator.py.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return text


# ------------------------------------------------------------
# Function: initialize adaptive weights
# ------------------------------------------------------------

def initialize_symbol_weights():
    """
    Initializes all lowercase letters with weight 1.

    This means all symbols are alive in the model from the beginning.
    Since the alphabet is known in this homework, this is a simple and
    stable way to start the adaptive Huffman model.
    """

    weights = {}

    # Give every lowercase letter an initial weight of 1.
    for symbol in ALPHABET:
        weights[symbol] = 1

    return weights


# ------------------------------------------------------------
# Function: apply inertia fading
# ------------------------------------------------------------

def apply_inertia_to_weights(weights):
    """
    Applies the INERTIA rule.

    Every weight is divided by 2 using integer division.
    If a weight becomes 0, it is reset to 1.
    This keeps all symbols alive in the model.
    """

    for symbol in weights:
        new_weight = weights[symbol] // 2

        # Keep the symbol alive even if integer division gives 0.
        if new_weight == 0:
            new_weight = 1

        weights[symbol] = new_weight


# ------------------------------------------------------------
# Function: build Huffman code lengths from current weights
# ------------------------------------------------------------

def build_huffman_code_lengths_from_weights(weights):
    """
    Builds Huffman code lengths from the current adaptive weights.

    For calculating the encoded size, we do not need the actual binary code.
    We only need the length of the code for each symbol.

    Example output:
    {'a': 4, 'b': 5, 'c': 3, ...}
    """

    heap = []
    unique_id = 0

    # Insert each symbol into the heap as a leaf node.
    for symbol, weight in weights.items():
        heapq.heappush(heap, (weight, unique_id, [symbol]))
        unique_id += 1

    # At the beginning, every code length is 0.
    code_lengths = {}

    for symbol in weights:
        code_lengths[symbol] = 0

    # Repeatedly merge the two nodes with the lowest weights.
    while len(heap) > 1:
        weight_1, _, symbols_1 = heapq.heappop(heap)
        weight_2, _, symbols_2 = heapq.heappop(heap)

        # Every symbol inside the merged nodes gets one extra bit.
        for symbol in symbols_1:
            code_lengths[symbol] += 1

        for symbol in symbols_2:
            code_lengths[symbol] += 1

        merged_weight = weight_1 + weight_2
        merged_symbols = symbols_1 + symbols_2

        heapq.heappush(heap, (merged_weight, unique_id, merged_symbols))
        unique_id += 1

    return code_lengths


# ------------------------------------------------------------
# Function: build actual Huffman codes from current weights
# ------------------------------------------------------------

def build_huffman_codes_from_weights(weights):
    """
    Builds actual Huffman binary codes from the current adaptive weights.

    This is needed only when saving the best encoded output.
    For example:
    {'a': '010', 'b': '1110', ...}
    """

    heap = []
    unique_id = 0

    # Each heap node is:
    # weight, unique_id, tree
    #
    # A leaf tree is just a symbol.
    for symbol, weight in weights.items():
        heapq.heappush(heap, (weight, unique_id, symbol))
        unique_id += 1

    # Build the Huffman tree by merging the two lowest-weight nodes.
    while len(heap) > 1:
        weight_1, _, tree_1 = heapq.heappop(heap)
        weight_2, _, tree_2 = heapq.heappop(heap)

        merged_tree = (tree_1, tree_2)
        merged_weight = weight_1 + weight_2

        heapq.heappush(heap, (merged_weight, unique_id, merged_tree))
        unique_id += 1

    # The final tree is stored inside the only remaining heap item.
    final_tree = heap[0][2]

    codes = {}

    # Traverse the tree and assign 0 to left, 1 to right.
    build_codes_by_traversing_tree(final_tree, "", codes)

    return codes


# ------------------------------------------------------------
# Function: traverse Huffman tree and create codes
# ------------------------------------------------------------

def build_codes_by_traversing_tree(tree, current_code, codes):
    """
    Recursively traverses the Huffman tree.

    Left edge adds 0.
    Right edge adds 1.
    When a symbol is reached, its code is saved.
    """

    # If this node is a symbol, save its code.
    if isinstance(tree, str):
        codes[tree] = current_code
        return

    left_child, right_child = tree

    # Go left and add 0 to the code.
    build_codes_by_traversing_tree(left_child, current_code + "0", codes)

    # Go right and add 1 to the code.
    build_codes_by_traversing_tree(right_child, current_code + "1", codes)


# ------------------------------------------------------------
# Function: calculate compression ratio
# ------------------------------------------------------------

def calculate_compression_ratio(encoded_size_bits, original_size_bits):
    """
    Calculates the compression ratio.

    Formula:
    r = encoded size in bits / original size in bits

    Smaller r means better compression.
    """

    return encoded_size_bits / original_size_bits


# ------------------------------------------------------------
# Function: run adaptive Huffman size calculation
# ------------------------------------------------------------

def calculate_adaptive_encoded_size_bits(text, inertia):
    """
    Runs Adaptive Huffman with a specific INERTIA value.

    This function calculates only the encoded size in bits.
    It does not write the encoded output to a file.

    This is used during the parameter study.
    """

    weights = initialize_symbol_weights()
    encoded_size_bits = 0
    encoded_characters_count = 0

    # Process the input text character by character.
    for character in text:
        code_lengths = build_huffman_code_lengths_from_weights(weights)

        # Add the current code length of this character.
        encoded_size_bits += code_lengths[character]

        # Update the adaptive model after encoding the character.
        weights[character] += 1
        encoded_characters_count += 1

        # Apply inertia after every INERTIA encoded characters.
        if encoded_characters_count % inertia == 0:
            apply_inertia_to_weights(weights)

    return encoded_size_bits


# ------------------------------------------------------------
# Function: run all INERTIA values
# ------------------------------------------------------------

def run_inertia_parameter_study(text):
    """
    Runs Adaptive Huffman for all required INERTIA values.

    For each INERTIA:
    - encoded size in bits is calculated
    - compression ratio is calculated
    - result is stored in a list
    """

    results = []

    print("Starting Adaptive Huffman INERTIA parameter study...")
    print()

    for inertia in INERTIA_VALUES:
        print(f"Running INERTIA = {inertia:,} ...")

        encoded_size_bits = calculate_adaptive_encoded_size_bits(text, inertia)

        compression_ratio = calculate_compression_ratio(
            encoded_size_bits,
            ORIGINAL_SIZE_BITS
        )

        result = {
            "method": "Adaptive Huffman with Inertia",
            "inertia": inertia,
            "encoded_size_bits": encoded_size_bits,
            "compression_ratio": compression_ratio
        }

        results.append(result)

        print(f"Encoded size: {encoded_size_bits:,} bits")
        print(f"Compression ratio r: {compression_ratio:.6f}")
        print()

    return results


# ------------------------------------------------------------
# Function: find best INERTIA result
# ------------------------------------------------------------

def find_best_inertia_result(results):
    """
    Finds the result with the smallest compression ratio.

    Smaller compression ratio means better compression.
    """

    best_result = min(results, key=lambda result: result["compression_ratio"])

    return best_result


# ------------------------------------------------------------
# Function: save adaptive results to CSV
# ------------------------------------------------------------

def save_adaptive_results_to_csv(results, file_path):
    """
    Saves all Adaptive Huffman INERTIA results into a CSV file.

    This file will later be used for:
    - report table
    - graph of r vs. INERTIA
    """

    column_names = [
        "method",
        "inertia",
        "encoded_size_bits",
        "compression_ratio"
    ]

    with open(file_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=column_names)

        writer.writeheader()

        for result in results:
            writer.writerow(result)


# ------------------------------------------------------------
# Class: binary bit writer
# ------------------------------------------------------------

class BinaryBitWriter:
    """
    Helper class for writing bits into a binary file.

    Bits are collected into groups of 8.
    Each group becomes one byte in the binary output file.
    """

    def __init__(self, file_path):
        self.file = open(file_path, "wb")
        self.current_byte = 0
        self.number_of_bits_filled = 0
        self.total_bits_written = 0

    def write_bits(self, bit_string):
        """
        Writes a string of bits, such as '01011', into the binary file.
        """

        for bit in bit_string:
            self.current_byte = self.current_byte << 1

            if bit == "1":
                self.current_byte = self.current_byte | 1

            self.number_of_bits_filled += 1
            self.total_bits_written += 1

            # Once we have 8 bits, write one byte.
            if self.number_of_bits_filled == 8:
                self.file.write(bytes([self.current_byte]))

                self.current_byte = 0
                self.number_of_bits_filled = 0

    def close(self):
        """
        Closes the binary file.

        If the last byte is not full, pad it with zeros on the right.
        """

        if self.number_of_bits_filled > 0:
            remaining_bits = 8 - self.number_of_bits_filled
            self.current_byte = self.current_byte << remaining_bits

            self.file.write(bytes([self.current_byte]))

        self.file.close()


# ------------------------------------------------------------
# Function: ask before overwriting output files
# ------------------------------------------------------------

def ask_user_before_overwriting(file_paths):
    """
    Checks if output files already exist.

    If they exist, the user chooses:
    Y = replace them
    N = keep them and stop
    """

    existing_files = []

    # Check which files already exist.
    for file_path in file_paths:
        if os.path.exists(file_path):
            existing_files.append(file_path)

    # No existing files means we can continue safely.
    if not existing_files:
        return True

    print("Warning: The following output file(s) already exist:")

    for file_path in existing_files:
        print(f"- {file_path}")

    print()
    print("Do you want to replace them?")
    print("Y = Yes, replace the existing files")
    print("N = No, keep the existing files and stop the program")

    while True:
        answer = input("Your choice (Y/N): ").strip().lower()

        if answer == "y":
            print("You chose Y. Existing files will be replaced.")
            print()
            return True

        if answer == "n":
            print("You chose N. Existing files will be kept. Program stopped.")
            return False

        print("Invalid choice. Please enter Y or N.")


# ------------------------------------------------------------
# Function: save best adaptive encoded output
# ------------------------------------------------------------

def save_best_adaptive_encoded_output(text, best_inertia, text_file_path, binary_file_path):
    """
    Encodes the input text again using the best INERTIA value.

    This time, the actual encoded bits are saved into:
    - a text file containing 0 and 1 characters
    - a binary file containing real packed bits
    """

    weights = initialize_symbol_weights()
    encoded_characters_count = 0

    binary_writer = BinaryBitWriter(binary_file_path)

    # Buffer text bits before writing, to avoid slow file writing.
    text_bits_buffer = []
    text_bits_buffer_limit = 100_000

    total_bits_written = 0

    with open(text_file_path, "w", encoding="utf-8") as text_output_file:

        # Encode each character using the current adaptive Huffman tree.
        for character in text:
            codes = build_huffman_codes_from_weights(weights)
            bit_code = codes[character]

            # Write the code to the text output buffer.
            text_bits_buffer.append(bit_code)

            # Write the code to the binary output file.
            binary_writer.write_bits(bit_code)

            total_bits_written += len(bit_code)

            # Update the adaptive model after encoding the character.
            weights[character] += 1
            encoded_characters_count += 1

            # Apply inertia after every best_inertia encoded characters.
            if encoded_characters_count % best_inertia == 0:
                apply_inertia_to_weights(weights)

            # Flush the text buffer if it becomes large enough.
            if sum(len(bits) for bits in text_bits_buffer) >= text_bits_buffer_limit:
                text_output_file.write("".join(text_bits_buffer))
                text_bits_buffer = []

        # Write any remaining bits in the text buffer.
        if text_bits_buffer:
            text_output_file.write("".join(text_bits_buffer))

    binary_writer.close()

    return total_bits_written


# ------------------------------------------------------------
# Function: print best adaptive result
# ------------------------------------------------------------

def print_best_result(best_result):
    """
    Prints the best Adaptive Huffman result clearly.
    """

    print("Best Adaptive Huffman Result")
    print("----------------------------")
    print(f"Best INERTIA: {best_result['inertia']:,}")
    print(f"Encoded size: {best_result['encoded_size_bits']:,} bits")
    print(f"Compression ratio r: {best_result['compression_ratio']:.6f}")
    print()


# ------------------------------------------------------------
# Main function
# ------------------------------------------------------------

def main():
    """
    Main program flow:
    1. Check if adaptive output files already exist.
    2. Read generated_input.txt.
    3. Run Adaptive Huffman for all INERTIA values.
    4. Save all results to CSV.
    5. Find the best INERTIA.
    6. Encode the text again using the best INERTIA.
    7. Save the best encoded output in text and binary formats.
    """

    output_files = [
        ADAPTIVE_RESULTS_FILE_PATH,
        BEST_OUTPUT_TEXT_FILE_PATH,
        BEST_OUTPUT_BINARY_FILE_PATH
    ]

    can_continue = ask_user_before_overwriting(output_files)

    if not can_continue:
        return

    print("Reading generated input text...")
    text = read_text_file(INPUT_FILE_PATH)

    # Make sure the input file has the expected size.
    assert len(text) == TOTAL_TEXT_LENGTH, (
        f"Error: input text length is {len(text):,}, "
        f"expected {TOTAL_TEXT_LENGTH:,}."
    )

    print("Input text loaded successfully.")
    print(f"Input text length: {len(text):,} characters")
    print()

    # Run the full INERTIA parameter study.
    results = run_inertia_parameter_study(text)

    # Save the parameter study results.
    save_adaptive_results_to_csv(results, ADAPTIVE_RESULTS_FILE_PATH)

    print(f"Adaptive Huffman results saved to: {ADAPTIVE_RESULTS_FILE_PATH}")
    print()

    # Find and print the best result.
    best_result = find_best_inertia_result(results)
    print_best_result(best_result)

    print("Saving encoded output using the best INERTIA...")
    print("This may take some time.")

    total_bits_written = save_best_adaptive_encoded_output(
        text,
        best_result["inertia"],
        BEST_OUTPUT_TEXT_FILE_PATH,
        BEST_OUTPUT_BINARY_FILE_PATH
    )

    print()
    print("Best adaptive encoded output saved successfully.")
    print(f"Text encoded file: {BEST_OUTPUT_TEXT_FILE_PATH}")
    print(f"Binary encoded file: {BEST_OUTPUT_BINARY_FILE_PATH}")
    print(f"Total bits written: {total_bits_written:,}")


# ------------------------------------------------------------
# Run the program
# ------------------------------------------------------------

if __name__ == "__main__":
    main()