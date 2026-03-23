from Classes import *
import re
import string
import time

def read_automaton():
    """Reads automaton data from a file based on user ID selection and maps it to the class."""
    choice = input("Which FA do you want to use? from (01 to 44) : ").strip()
    target_id = f"#{choice}"

    auto = Automaton()
    found = False
    data_lines = []

    with open("Automatas.txt", "r") as file:
        for line in file:
            line = line.strip()
            if not line: continue 

            if line == target_id:
                found = True
                continue

            if found and line.startswith("#"):
                break

            if found:
                data_lines.append(line)

    if not found:
        print(f"Error: Automaton {target_id} not found in file.")
        return None

    auto.alphabet_size = int(data_lines[0])
    auto.alphabet = list(string.ascii_lowercase[:auto.alphabet_size])
    auto.num_states = int(data_lines[1])

    init_parts = data_lines[2].split()
    if len(init_parts) > 1:
        auto.initial_states = list(map(int, init_parts[1:]))

    final_parts = data_lines[3].split()
    if len(final_parts) > 1:
        auto.final_states = list(map(int, final_parts[1:]))

    num_transitions = int(data_lines[4])

    for trans_line in data_lines[5:]:
        match = re.match(r"(\d+)([a-zA-Z])(\d+)", trans_line)
        if match:
            src = int(match.group(1))
            symbol = match.group(2)
            dest = int(match.group(3))
            auto.add_transition(src, symbol, dest)

    print(f"Successfully loaded Automaton {target_id}!")
    return auto

def display_automaton(auto):
    """Prints the properties and transition table of the automaton for user inspection."""
    print(f"Alphabet size : {auto.alphabet_size}")
    print(f"Alphabet : {auto.alphabet}")
    print(f"Number of states : {auto.num_states}")
    print(f"Initial states : {auto.initial_states}")
    print(f"Final States : {auto.final_states}")
    for state in auto.transitions:
        for symbol, target_state in auto.transitions[state].items():
            for target in target_state:
                print(f"{state} -{symbol}-> {target}") 

def is_not_standard_fa(auto):
    """Checks if the FA is non-standard by looking for multiple entries or transitions pointing to the entry."""
    if len(auto.initial_states) != 1:
        return True 
    
    unique_entry = auto.initial_states[0]

    for state in auto.transitions:
        for symbol in auto.transitions[state]:
            destinations = auto.transitions[state][symbol]
            if unique_entry in destinations:
                return True 

    return False

def standardize_automaton(auto):
    """Converts a non-standard FA into a standard one by adding a new unique initial state."""
    new_initial_state = auto.num_states
    is_terminal = False
    for state in auto.initial_states:
        if state in auto.final_states:
            is_terminal = True
    
    for init_state in auto.initial_states:
        if init_state in auto.transitions:
            for symbol, destinations in auto.transitions[init_state].items():
                for dest in destinations:
                    auto.add_transition(new_initial_state, symbol, dest)
    
    auto.num_states += 1
    auto.initial_states = [new_initial_state]
    
    if is_terminal:
        auto.final_states.append(new_initial_state)
    
    print(f"Standardized: Added new unique initial state {new_initial_state}.")

def is_synchrone(auto):
    """Determines if the automaton is synchronous by checking for the absence of epsilon transitions."""
    for state in auto.transitions:
        if 'ε' in auto.transitions[state] or '' in auto.transitions[state]:
            return False 
            
    return True 

def is_deterministic(auto):
    """Checks if the FA is deterministic by verifying a single entry point and unique transitions per symbol."""
    rule1 = True
    rule2 = True
    if len(auto.initial_states) > 1:
        rule1=False
    
    for state in auto.transitions:
        for symbol in auto.transitions[state]:
            destinations = auto.transitions[state][symbol]
            if len(destinations) > 1:
                rule2=False
    
    if rule1 and rule2:
        return True
                
    if not rule1:
        print("Multiple entries ! ")
    if not rule2:
        print("Multiple arrows for the same label coming out of the same state !")
    print("Non deterministic !")
    return False

def is_not_complete(auto):
    """Checks if any state in the FA lacks a transition for any symbol in the alphabet."""
    for state_id in range(auto.num_states):
        if state_id not in auto.transitions:
            print(f"{state_id} doesn't have any transitions ! Not complete !")
            return True 
        
        symbols_defined = auto.transitions[state_id].keys()
        for char in auto.alphabet:
            if char not in symbols_defined:
                print(f"{char} doesn't point into any destination of {state_id}")
                return True 
                
    return False

def completion(auto):
    """Makes a deterministic FA complete by adding a sink state for all missing transitions."""
    sink_state = auto.num_states
    sink_needed = False
    
    for state_id in range(auto.num_states):
        if state_id not in auto.transitions:
            auto.transitions[state_id] = {}
            
        for symbol in auto.alphabet:
            if symbol not in auto.transitions[state_id]:
                auto.add_transition(state_id, symbol, sink_state)
                sink_needed = True
                
    if sink_needed:
        for symbol in auto.alphabet:
            auto.add_transition(sink_state, symbol, sink_state)
        
        auto.num_states += 1
        print(f"Completion: Added Sink State (State {sink_state}) to make the FA total.")
        
    return auto

def determinization_and_completion_of_automaton(auto):
    """Transforms an NFA into a Complete Deterministic Finite Automaton using the subset construction method."""
    start_set = tuple(sorted(set(auto.initial_states)))
    all_sets = [start_set]
    discovered_sets = {start_set: 0}
    
    cdfa = Automaton()
    cdfa.alphabet = auto.alphabet
    cdfa.alphabet_size = auto.alphabet_size
    cdfa.initial_states = [0]
    
    i = 0
    while i < len(all_sets):
        current_set = all_sets[i]
        current_id = i
        
        if any(s in auto.final_states for s in current_set):
            if current_id not in cdfa.final_states:
                cdfa.final_states.append(current_id)

        for symbol in auto.alphabet:
            next_set_builder = set()
            for state in current_set:
                if state in auto.transitions and symbol in auto.transitions[state]:
                    next_set_builder.update(auto.transitions[state][symbol])
            
            next_set = tuple(sorted(next_set_builder))

            if next_set not in discovered_sets:
                discovered_sets[next_set] = len(all_sets)
                all_sets.append(next_set)
            
            target_id = discovered_sets[next_set]
            cdfa.add_transition(current_id, symbol, target_id)
            
        i += 1

    cdfa.num_states = len(all_sets)
    return cdfa

def display_complete_deterministic_automaton(auto):
    """Displays the CDFA and explicitly shows state composition using the required format."""
    print(f"Alphabet size : {auto.alphabet_size}")
    print(f"Alphabet : {auto.alphabet}")
    print(f"Number of states : {auto.num_states}")
    print(f"Initial state : {auto.initial_states}")
    print(f"Final States : {auto.final_states}")
    for state in auto.transitions:
        for symbol, target_state in auto.transitions[state].items():
            for target in target_state:
                # 'state' and 'target' will be strings like "1.2" or "Puits"
                print(f"{state} -{symbol}-> {target}")

fa = read_automaton()
display_automaton(fa)
time.sleep(0.5)

if is_not_standard_fa(fa):
    rep = input("This automaton is not a standard FA. Do you want to convert it to a standard FA? (y/n) : ").strip().lower()
    if rep == 'y':
        standardize_automaton(fa)
        time.sleep(0.25)
        display_automaton(fa)

if is_synchrone(fa):
    if is_deterministic(fa):
        if is_not_complete(fa):
            rep = input("Do you want to complete this deterministic FA? (y/n) : ").strip().lower()
            if rep == 'y':
                completion(fa)
        else :
            time.sleep(0.5)
            print("This automaton is complete and deterministic !")
            display_complete_deterministic_automaton(fa)
    else:
        rep = input("Do you want to determinize and complete this FA? (y/n) : ").strip().lower()
        if rep == 'y':
            fa = determinization_and_completion_of_automaton(fa)
            display_complete_deterministic_automaton(fa)
else:
    print("This automaton is not synchrone")