from Classes import *

import re
import string
import time


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
    # Condition 1: Check for exactly one initial state
    if len(auto.initial_states) != 1:
        print("More or less than 1 intial state ! Not Standard.")
        return True # Non-standard: 0 or multiple initial states 
    
    unique_entry = auto.initial_states[0]

    # Condition 2: Check if any transition arrives at that unique entry point
    # We iterate through all states and all symbols in the transitions dictionary
    for state in auto.transitions:
        for symbol in auto.transitions[state]:
            destinations = auto.transitions[state][symbol]
            # If the unique_entry is found in any set of destination states, it's non-standard
            if unique_entry in destinations:
                print("1 initial state, but destination to 1 or more transitions ! Not Standard.")
                return True # Non-standard: transition arrives at the unique entry 

    # If both conditions are met, it is a standard automaton
    return False

def standardize_automaton(auto):
    # 1. Define the ID for the new unique initial state i
    # We use the current number of states as the new index
    new_initial_state = auto.num_states
    
    # 2. Check if the new state i should be terminal (final)
    # i is terminal if any original initial state was terminal
    is_terminal = False
    for state in auto.initial_states:
        if state in auto.final_states:
            is_terminal = True
    
    # 3. Create new transitions departing from i
    # For each transition going out of the original initial state(s)
    for init_state in auto.initial_states:
        if init_state in auto.transitions:
            for symbol, destinations in auto.transitions[init_state].items():
                for dest in destinations:
                    # Create transition from i with same label and target
                    auto.add_transition(new_initial_state, symbol, dest)
    
    # 4. Update the automaton structure
    # Update total count of states
    auto.num_states += 1
    
    # Set the new state as the unique entry point
    auto.initial_states = [new_initial_state]
    
    # If the condition was met, add the new state to final states
    if is_terminal:
        auto.final_states.append(new_initial_state)
    
    print(f"Standardized: Added new unique initial state {new_initial_state}.")

def display_automaton(auto):
    print(f"Alphabet size : {auto.alphabet_size}")
    print(f"Alphabet : {auto.alphabet}")
    print(f"Number of states : {auto.num_states}")
    print(f"Initial states : {auto.initial_states}")
    print(f"Final States : {auto.final_states}")
    print(f"Transitions : {auto.transitions}")
    for state in auto.transitions:
        for symbol, target_state in auto.transitions[state].items():
            for target in target_state:
                print(f"{state} -{symbol}-> {target}")
    print(f"Is this a standard FA? : {'No' if is_not_standard_fa(auto) else 'Yes'}") 


fa = read_automaton()
display_automaton(fa)
time.sleep(0.5)
if is_not_standard_fa(fa):
    rep = input("This automaton is not a standard FA. Do you want to convert it to a standard FA? (y/n) : ").strip().lower()
    if rep == 'y':
        standardize_automaton(fa)
        time.sleep(0.25)
        display_automaton(fa)
