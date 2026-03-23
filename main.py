from Classes import *

import re


def read_automaton():
    # 1. Get the user input and format it to match the file (e.g., "03" -> "#03")
    choice = input("Which FA do you want to use? from (01 to 44) : ").strip()
    target_id = f"#{choice}"

    auto = Automaton()
    found = False
    data_lines = []

    with open("Automatas.txt", "r") as file:
        for line in file:
            line = line.strip()
            if not line: continue  # Skip empty lines

            # Check for the start of our target section
            if line == target_id:
                found = True
                continue

            # If we hit the NEXT # section, stop reading
            if found and line.startswith("#"):
                break

            # If we are inside the correct section, collect the line
            if found:
                data_lines.append(line)

    if not found:
        print(f"Error: Automaton {target_id} not found in file.")
        return None

    # 2. Map the collected data to the Automaton class
    # Line 0: Alphabet Size
    auto.alphabet_size = int(data_lines[0])
    # Generate alphabet letters (a, b, c...) based on size
    import string
    auto.alphabet = list(string.ascii_lowercase[:auto.alphabet_size])

    # Line 1: Number of States
    auto.num_states = int(data_lines[1])

    # Line 2: Initial States (Format: "count state1 state2...")
    init_parts = data_lines[2].split()
    if len(init_parts) > 1:
        auto.initial_states = list(map(int, init_parts[1:]))

    # Line 3: Final States (Format: "count state1 state2...")
    final_parts = data_lines[3].split()
    if len(final_parts) > 1:
        auto.final_states = list(map(int, final_parts[1:]))

    # 4. Number of Transitions
    num_transitions = int(data_lines[4])

    # Line 4 and onwards: Transitions (Format: "0a1")
    for trans_line in data_lines[5:]:
        # Regex splits: (digits)(letter)(digits)
        match = re.match(r"(\d+)([a-zA-Z])(\d+)", trans_line)
        if match:
            src = int(match.group(1))
            symbol = match.group(2)
            dest = int(match.group(3))
            auto.add_transition(src, symbol, dest)

    print(f"Successfully loaded Automaton {target_id}!")
    return auto

def is_not_standard_fa(auto):
    # Check for 0 or multiple initial states
    if len(auto.initial_states) != 1:
        return True
    
    # Check for 0 or multiple transitions per symbols
    for state in auto.transitions:
        for symbol in auto.transitions[state]:
            if len(auto.transitions[state][symbol]) != 1:
                return True

    # We look for any symbol that isn't in our formal alphabet (usually represented as 'ε', '#', or '')
    for state in auto.transitions:
        for symbol in auto.transitions[state]:
            if symbol not in auto.alphabet:
                return True

    # Check for 0 or multiple transitions for each symbol in the alphabet for each state
    for state_id in range(auto.num_states):
        if state_id not in auto.transitions:
            return True # Non-standard (Incomplete)
    
        # Get the symbols this specific state currently handles
        symbols_defined = auto.transitions[state_id].keys()
    
        # Check if every letter of the alphabet exists as a key for this state
        for char in auto.alphabet:
            if char not in symbols_defined:
                return True # Non-standard (Missing a transition for this character)
            
    return False

def standardize_automaton(auto):
    pass

def display_automaton(auto):
    print(f"Alphabet size : {auto.alphabet_size}")
    print(f"Alphabet : {auto.alphabet}")
    print(f"Number of states : {auto.num_states}")
    print(f"Initial states : {auto.initial_states}")
    print(f"Final States : {auto.final_states}")
    print(f"Transitions : {auto.transitions}")
    print(f"Is this a standard FA? : {'No' if is_not_standard_fa(auto) else 'Yes'}") 



my_fa = read_automaton()
display_automaton(my_fa)
if is_not_standard_fa(my_fa):
    rep = input("This automaton is not a standard FA. Do you want to convert it to a standard FA? (y/n) : ").strip().lower()
    if rep == 'y':
        standardize_automaton(my_fa)
        display_automaton(my_fa)

