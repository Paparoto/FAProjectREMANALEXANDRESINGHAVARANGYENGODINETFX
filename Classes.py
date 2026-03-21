class Automaton:
    def __init__(self):
        self.alphabet_size = 0
        self.alphabet = [] # ['a', 'b', ...]
        self.num_states = 0
        self.initial_states = []
        self.final_states = []
        self.transitions = {} # Format: { state: { symbol: {target_states} } }

    def add_transition(self, src, symbol, dest):
        if src not in self.transitions:
            self.transitions[src] = {}
        if symbol not in self.transitions[src]:
            self.transitions[src][symbol] = set()
        self.transitions[src][symbol].add(dest)