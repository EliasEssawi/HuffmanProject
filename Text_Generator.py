# -*- coding: utf-8 -*-
"""
Created on Sun May 17 13:07:43 2026

@author: Elias
"""

# text_generator.py

import random
import string
import os
import random
import string


# ------------------------------------------------------------
# Student ID settings
# ------------------------------------------------------------

TOTAL_TEXT_LENGTH = 10_000_000
NUMBER_OF_BLOCKS = 34
Y_LAST_NON_ZERO_DIGIT = 4

# According to the homework rule:
# word length = Y + 2
WORD_LENGTH = Y_LAST_NON_ZERO_DIGIT + 2


# ------------------------------------------------------------
# Function: generate one random lowercase word
# ------------------------------------------------------------

def generate_random_word(word_length):
    """
    Generates one random word using lowercase English letters only.

    Example:
    word_length = 6
    possible output = 'kqzmta'
    """

    letters = string.ascii_lowercase

    # Choose random lowercase letters and join them into one string.
    random_word = ''.join(random.choice(letters) for _ in range(word_length))

    return random_word


# ------------------------------------------------------------
# Function: generate unique random words for all blocks
# ------------------------------------------------------------

def generate_unique_words(number_of_words, word_length):
    """
    Generates a list of unique random words.

    A set is used for fast duplicate checking.
    Checking if a word exists in a set is usually O(1).
    """

    used_words = set()
    unique_words = []

    # Keep generating words until we have enough unique words.
    while len(unique_words) < number_of_words:
        word = generate_random_word(word_length)

        # Add the word only if it was not used before.
        if word not in used_words:
            used_words.add(word)
            unique_words.append(word)

    return unique_words


# ------------------------------------------------------------
# Function: calculate block sizes
# ------------------------------------------------------------

def calculate_block_sizes(total_length, number_of_blocks):
    """
    Calculates the size of each block.

    Because 10,000,000 is not divisible by 34:
    - Blocks 1 to 33 get the rounded block size.
    - Block 34 is adjusted so the final text length is exactly 10,000,000.
    """

    rounded_block_size = round(total_length / number_of_blocks)

    block_sizes = []

    # Create the first 33 blocks with the rounded size.
    for _ in range(number_of_blocks - 1):
        block_sizes.append(rounded_block_size)

    # The last block gets the remaining characters.
    used_length_so_far = sum(block_sizes)
    last_block_size = total_length - used_length_so_far

    block_sizes.append(last_block_size)

    return block_sizes, rounded_block_size

# ------------------------------------------------------------
# Function: Block information save into file block_info.txt
# ------------------------------------------------------------

def save_block_info_to_file(block_words, block_sizes, file_path):
    """
    Saves the generated block words and block sizes into a small text file.

    This file is useful for documentation, debugging, and explaining
    how the generated input text was created.
    """

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("Generated Text Block Information\n")
        file.write("--------------------------------\n\n")

        file.write(f"Number of blocks: {len(block_words)}\n")
        file.write(f"Word length: {WORD_LENGTH}\n")
        file.write(f"Total text length: {sum(block_sizes):,} characters\n\n")

        file.write("Block details:\n")

        for index, (word, size) in enumerate(zip(block_words, block_sizes), start=1):
            file.write(f"Block {index:02d}: word = {word}, size = {size:,} characters\n")
            
# ------------------------------------------------------------
# Function: build one block by repeating its word
# ------------------------------------------------------------

def build_block_from_word(word, block_size):
    """
    Builds one block by repeating the same word until the block is full.

    If the repeated word becomes longer than the required block size,
    we cut the block exactly at block_size.
    """

    # Number of repetitions needed to cover the block size.
    repetitions_needed = (block_size // len(word)) + 1

    # Repeat the word and cut exactly to the requested block size.
    block_text = (word * repetitions_needed)[:block_size]

    return block_text


# ------------------------------------------------------------
# Function: generate the full input text
# ------------------------------------------------------------

def generate_full_text(block_words, block_sizes):
    """
    Generates the complete input text.

    Each block uses one unique random word.
    The final text must be exactly 10,000,000 characters.
    """

    all_blocks = []

    # Build each block from its matching random word.
    for word, block_size in zip(block_words, block_sizes):
        block = build_block_from_word(word, block_size)
        all_blocks.append(block)

    # Join all blocks into one big text.
    full_text = ''.join(all_blocks)

    return full_text

# ------------------------------------------------------------
# Function: ask user before replacing existing files
# ------------------------------------------------------------

def ask_user_before_overwriting(file_paths):
    """
    Checks if one or more output files already exist.

    If files already exist, the user is asked whether to replace them.
    Y means the old files will be overwritten.
    N means the program will stop and keep the existing files.
    """

    existing_files = []

    # Check which output files already exist in the project folder.
    for file_path in file_paths:
        if os.path.exists(file_path):
            existing_files.append(file_path)

    # If no files exist, there is no overwrite problem.
    if not existing_files:
        return True

    print("Warning: The following output file(s) already exist:")

    # Print each existing file clearly for the user.
    for file_path in existing_files:
        print(f"- {file_path}")

    print()
    print("Do you want to replace them and generate new files?")
    print("Y = Yes, replace the existing files")
    print("N = No, keep the existing files and stop the program")

    # Keep asking until the user enters a valid answer.
    while True:
        answer = input("Your choice (Y/N): ").strip().lower()

        if answer == "y":
            print("You chose Y. Old files will be replaced.")
            return True

        if answer == "n":
            print("You chose N. Existing files will be kept. Program stopped.")
            return False

        print("Invalid choice. Please enter Y or N.")
        
# ------------------------------------------------------------
# Function: save generated text to a file
# ------------------------------------------------------------

def save_text_to_file(text, file_path):
    """
    Saves the generated text into a plain .txt file.

    If the file already exists, it will only be overwritten after
    the user confirms this in ask_user_before_overwriting().
    """

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)

# ------------------------------------------------------------
# Function: validate the generated data
# ------------------------------------------------------------

def validate_generated_data(text, block_words, total_length, number_of_blocks):
    """
    Checks that the generated data follows the homework rules.
    """

    all_words_are_unique = len(set(block_words)) == number_of_blocks
    all_words_are_lowercase = all(word.islower() and word.isalpha() for word in block_words)
    text_length_is_correct = len(text) == total_length

    return all_words_are_unique, all_words_are_lowercase, text_length_is_correct


# ------------------------------------------------------------
# Function: print generation information
# ------------------------------------------------------------

def print_generation_report(
    block_words,
    block_sizes,
    rounded_block_size,
    total_text_length,
    number_of_blocks,
    word_length,
    validation_results
):
    """
    Prints a clear report about the generated input text.
    """

    all_words_are_unique, all_words_are_lowercase, text_length_is_correct = validation_results

    print("Student ID settings:")
    print(f"XX = {number_of_blocks}")
    print(f"Y = {Y_LAST_NON_ZERO_DIGIT}")
    print(f"Word length = Y + 2 = {word_length}")
    print()

    print("Text generation settings:")
    print(f"Total target length = {total_text_length:,} characters")
    print(f"Number of blocks = {number_of_blocks}")
    print(f"Rounded block size = {rounded_block_size:,} characters")
    print(f"Blocks 1-{number_of_blocks - 1} size = {rounded_block_size:,} characters")
    print(f"Block {number_of_blocks} size = {block_sizes[-1]:,} characters")
    print(f"Total generated length = {sum(block_sizes):,} characters")
    print()

    print("Random block words:")
    for index, word in enumerate(block_words, start=1):
        print(f"Block {index:02d} word: {word}")

    print()

    print("Validation:")
    print(f"All block words are unique: {all_words_are_unique}")
    print(f"All words contain only lowercase letters: {all_words_are_lowercase}")
    print(f"Generated text length is correct: {text_length_is_correct}")


# ------------------------------------------------------------
# Main function
# ------------------------------------------------------------


def main():
    """
    Main program flow:
    1. Check if output files already exist.
    2. Ask the user if they want to replace existing files.
    3. Generate 34 unique random words.
    4. Calculate block sizes.
    5. Build the full 10,000,000-character text.
    6. Validate the result.
    7. Save the generated text file.
    8. Save the block information file.
    9. Print a clear report.
    """

    output_file_path = "generated_input.txt"
    block_info_file_path = "block_info.txt"

    # Before generating new random text, check if output files already exist.
    # This prevents accidental replacement of the homework input file.
    can_generate_files = ask_user_before_overwriting([
        output_file_path,
        block_info_file_path
    ])

    # If the user chooses N, stop the program safely.
    if not can_generate_files:
        return

    # Generate one unique random word for each block.
    block_words = generate_unique_words(NUMBER_OF_BLOCKS, WORD_LENGTH)

    # Calculate the exact size of each block.
    block_sizes, rounded_block_size = calculate_block_sizes(
        TOTAL_TEXT_LENGTH,
        NUMBER_OF_BLOCKS
    )

    # Build the complete input text.
    generated_text = generate_full_text(block_words, block_sizes)

    # Validate that everything follows the homework requirements.
    validation_results = validate_generated_data(
        generated_text,
        block_words,
        TOTAL_TEXT_LENGTH,
        NUMBER_OF_BLOCKS
    )

    # Stop the program if something is wrong.
    assert validation_results[0], "Error: Not all block words are unique."
    assert validation_results[1], "Error: Some words are not lowercase letters only."
    assert validation_results[2], "Error: Generated text length is not correct."

    # Save the generated text to a .txt file.
    save_text_to_file(generated_text, output_file_path)

    # Save the block words and block sizes to a metadata file.
    save_block_info_to_file(block_words, block_sizes, block_info_file_path)

    # Print the full generation report.
    print_generation_report(
        block_words,
        block_sizes,
        rounded_block_size,
        TOTAL_TEXT_LENGTH,
        NUMBER_OF_BLOCKS,
        WORD_LENGTH,
        validation_results
    )

    print()
    print(f"Generated input text saved to: {output_file_path}")
    print(f"Block information saved to: {block_info_file_path}")


# ------------------------------------------------------------
# Run the program
# ------------------------------------------------------------

if __name__ == "__main__":
    main()