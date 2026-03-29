from Classes import *
import re
import string
import time

def read_automaton(choice):
    """
    Reads automaton data from a file, extracting the alphabet and 
    capturing any non-alphabet symbols (like ε) as transitions.
    """
    
    target_id = f"#{choice}"
    auto = Automaton()
    found = False
    data_lines = []

    with open("Automatas.txt", "r", encoding="utf-8") as file:
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
        print(f"Error: Automaton {target_id} not found.")
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

    for trans_line in data_lines[5:]:
        digits = re.findall(r'\d+', trans_line)
        if len(digits) >= 2:
            src = int(digits[0])
            dest = int(digits[-1])
            
            first_num_end = trans_line.find(digits[0]) + len(digits[0])
            last_num_start = trans_line.rfind(digits[-1])
            symbol = trans_line[first_num_end:last_num_start].strip()
            
            if not symbol or symbol in ['ε', 'eps', 'E', 'e']:
                symbol = 'ε'
                
            auto.add_transition(src, symbol, dest)

    print(f"Successfully loaded Automaton {target_id}!")
    return auto

def display_automaton(fa):
    print("\n--- Finite Automaton ---")
    
    # Define columns: State, Initial, Final, and one for each alphabet symbol
    headers = ["State", "Init", "Final"] + [str(s) for s in fa.alphabet]
    col_width = 10 # Standard width for initial FA
    
    header_line = "".join(h.ljust(col_width) for h in headers)
    print(header_line)
    print("-" * len(header_line))

    for state in range(fa.num_states):
        row = []
        row.append(str(state).ljust(col_width))
        row.append("Yes".ljust(col_width) if state in fa.initial_states else " ".ljust(col_width))
        row.append("Yes".ljust(col_width) if state in fa.final_states else " ".ljust(col_width))
        
        for symbol in fa.alphabet:
            # Transitions are sets in your class: {target_states}
            targets = fa.transitions.get(state, {}).get(symbol, set())
            target_str = ",".join(map(str, sorted(list(targets)))) if targets else "-"
            row.append(target_str.ljust(col_width))
        
        print("".join(row))
    input("\nPress Enter to continue...")

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
    for src, transitions_for_state in auto.transitions.items():
        for symbol in transitions_for_state:
            if symbol not in auto.alphabet:
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
    cdfa.state_labels = {0: start_set} 
    
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
                new_id = len(all_sets)
                discovered_sets[next_set] = new_id
                all_sets.append(next_set)
                cdfa.state_labels[new_id] = next_set
            
            target_id = discovered_sets[next_set]
            cdfa.add_transition(current_id, symbol, target_id)
        i += 1

    cdfa.num_states = len(all_sets)
    return cdfa

def display_complete_deterministic_automaton(cdfa):
    print("\n--- Complete Deterministic Finite Automaton (CDFA) ---")
    headers = ["State", "Init", "Final"] + [str(s) for s in cdfa.alphabet]
    
    max_label_len = 0
    if cdfa.state_labels:
        max_label_len = max(len(str(v)) for v in cdfa.state_labels.values())
    col_width = max(max_label_len + 2, 10)
    
    header_line = "".join(h.ljust(col_width) for h in headers)
    print(header_line)
    print("-" * len(header_line))

    for state in range(cdfa.num_states):
        row = []
        row.append(str(state).ljust(col_width))
        row.append("Yes".ljust(col_width) if state in cdfa.initial_states else " ".ljust(col_width))
        row.append("Yes".ljust(col_width) if state in cdfa.final_states else " ".ljust(col_width))
        
        for symbol in cdfa.alphabet:
            target = cdfa.transitions.get(state, {}).get(symbol, set())
            target_str = str(list(target)[0]) if target else "Sink" 
            row.append(target_str.ljust(col_width))
        print("".join(row))

    if cdfa.state_labels:
        print("\nState Composition (CDFA ID -> Original States):")
        print(f"{'CDFA ID'.ljust(12)} | {'Original Set'.ljust(20)}")
        print("-" * 35)
        for cdfa_id, composition in sorted(cdfa.state_labels.items()):
            comp_str = "{" + ",".join(map(str, composition)) + "}"
            print(f"{str(cdfa_id).ljust(12)} | {comp_str}")
    input("\nPress Enter to continue...")

def minimization(auto):
    """
    Performs Moore's algorithm to produce a truly minimal MCDFA.
    It splits states into groups until only those with identical 
    transition behaviors remain together.
    """
    # 1. Initial Split: Non-Final (Group 0) vs Final (Group 1)
    non_final = tuple(sorted(s for s in range(auto.num_states) if s not in auto.final_states))
    final = tuple(sorted(auto.final_states))
    
    partition = []
    if non_final: partition.append(non_final)
    if final: partition.append(final)

    def get_group_id(state, current_partition):
        for i, group in enumerate(current_partition):
            if state in group: return i
        return -1

    iteration = 0
    while True:
        print(f"P{iteration}: {partition}")
        new_partition = []
        
        for group in partition:
            if len(group) <= 1:
                new_partition.append(group)
                continue
            
            # Refine by transition signature
            signatures = {}
            for state in group:
                # signature = (dest_group_on_a, dest_group_on_b, ...)
                sig = tuple(get_group_id(list(auto.transitions[state][char])[0], partition) 
                            for char in auto.alphabet)
                if sig not in signatures:
                    signatures[sig] = []
                signatures[sig].append(state)
            
            for sub_group in signatures.values():
                new_partition.append(tuple(sorted(sub_group)))

        new_partition.sort()
        if new_partition == partition:
            break
        partition = new_partition
        iteration += 1

    # 2. Reconstruct the MCDFA
    mcdfa = Automaton()
    mcdfa.alphabet = auto.alphabet
    mcdfa.alphabet_size = auto.alphabet_size
    mcdfa.num_states = len(partition)
    mcdfa.state_labels = {}
    
    state_to_group = {}
    for i, group in enumerate(partition):
        combined_label = []
        for s in group:
            state_to_group[s] = i
            combined_label.extend(auto.state_labels.get(s, (s,)))
        mcdfa.state_labels[i] = tuple(sorted(set(combined_label)))

    mcdfa.initial_states = list(set(state_to_group[s] for s in auto.initial_states))
    mcdfa.final_states = list(set(state_to_group[s] for s in auto.final_states))

    for i, group in enumerate(partition):
        rep = group[0]
        for char in auto.alphabet:
            target = list(auto.transitions[rep][char])[0]
            mcdfa.add_transition(i, char, state_to_group[target])

    return mcdfa

def display_minimal_automaton(mcdfa):
    print("\n--- Minimal Deterministic Complete Finite Automaton ---")
    
    headers = ["State", "Initial", "Final"] + [str(s) for s in mcdfa.alphabet]
    col_width = max(len(str(x)) for x in mcdfa.state_labels.values()) if mcdfa.state_labels else 10
    col_width = max(col_width, 8)
    
    header_line = "".join(h.ljust(col_width) for h in headers)
    print(header_line)
    print("-" * len(header_line))

    for state in range(mcdfa.num_states):
        row = []
        row.append(str(state).ljust(col_width))
        row.append("Yes".ljust(col_width) if state in mcdfa.initial_states else " ".ljust(col_width))
        row.append("Yes".ljust(col_width) if state in mcdfa.final_states else " ".ljust(col_width))
        
        for symbol in mcdfa.alphabet:
            target = mcdfa.transitions.get(state, {}).get(symbol, set())
            target_str = ",".join(map(str, target)) if target else "-"
            row.append(target_str.ljust(col_width))
        
        print("".join(row))

    if mcdfa.state_labels:
        print("\nState Correspondences (Minimal State -> CDFA States):")
        print(f"{'Minimal ID'.ljust(15)} | {'CDFA States'.ljust(20)}")
        print("-" * 40)
        for m_id, original_labels in sorted(mcdfa.state_labels.items()):
            label_str = str(original_labels)
            print(f"{str(m_id).ljust(15)} | {label_str}")
    input("\nPress Enter to continue...")

def recognize_word(fa, word):
    """
    Verifies if the automaton recognizes the input word by traversing 
    states based on the alphabet symbols provided in the string.
    Returns True (Yes) if the final state is an accepting state, False otherwise.
    """
    if not fa.initial_states:
        return False
        
    current_state = list(fa.initial_states)[0]

    for symbol in word:
        if symbol not in fa.alphabet:
            return False
        
        transitions = fa.transitions.get(current_state, {}).get(symbol, set())
        if not transitions:
            return False
        
        current_state = list(transitions)[0]

    return current_state in fa.final_states




































choice = input("Which FA do you want to use? (01 to 44) : ").strip()
fa = read_automaton(choice)
display_automaton(fa)
time.sleep(0.5)

if is_not_standard_fa(fa):
    rep = input("This automaton is not a standard FA. Do you want to convert it to a standard FA? (y/n) : ").strip().lower()
    if rep == 'y':
        standardize_automaton(fa)
        time.sleep(0.25)
        display_automaton(fa)

else:
     print("This automaton is a standard FA !")

print()
print()
print()

if is_synchrone(fa):
    if is_deterministic(fa):
        if is_not_complete(fa):
            rep = input("Do you want to complete this deterministic FA? (y/n) : ").strip().lower()
            if rep == 'y':
                completion(fa)
                display_complete_deterministic_automaton(fa)
                time.sleep(0.5)
                rep = input("Do you want to minimize if possible this CDFA? (y/n) : ").strip().lower()
                if rep == 'y':
                    fa = minimization(fa)
                    print()
                    time.sleep(0.5)
                    display_minimal_automaton(fa)
        else :
            time.sleep(0.5)
            print("This automaton is complete and deterministic !")
            display_complete_deterministic_automaton(fa)
            time.sleep(0.5)
            rep = input("Do you want to minimize if possible this CDFA? (y/n) : ").strip().lower()
            if rep == 'y':
                fa = minimization(fa)
                print()
                time.sleep(0.5)
                display_minimal_automaton(fa)
    else:
        rep = input("Do you want to determinize and complete this FA? (y/n) : ").strip().lower()
        if rep == 'y':
            fa = determinization_and_completion_of_automaton(fa)
            display_complete_deterministic_automaton(fa)
            time.sleep(0.5)
            rep = input("Do you want to minimize if possible this CDFA? (y/n) : ").strip().lower()
            if rep == 'y':
                fa = minimization(fa)
                print()
                time.sleep(0.5)
                display_minimal_automaton(fa)
    
    print()
    print()
    print("\n--- Word Recognition Test ---")
    print("Type 'end' to stop testing words.")

    while True:
        word = input("\nEnter a word to test: ").strip()
        
        if word.lower() == "end":
            break
            
        if recognize_word(fa, word):
            print(f"The word '{word}' is RECOGNIZED by the automaton.")
        else:
            print(f"The word '{word}' is NOT RECOGNIZED by the automaton.")
            
else:
    print("This automaton is not synchronous")
