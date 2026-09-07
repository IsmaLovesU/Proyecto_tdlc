"""Construccion de subconjuntos: convierte un AFN (ver thompson.py) en un
AFD equivalente.
"""

import itertools
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Set

from thompson import NFA, EPSILON


@dataclass
class DFA:
    states: Set[int]
    transitions: Dict[int, Dict[str, int]]
    start: int
    accepts: Set[int]
    alphabet: Set[str]
    # Mapea cada estado del AFD al conjunto de estados del AFN que representa,
    # util para depuracion y para renderizar las imagenes.
    state_labels: Dict[int, FrozenSet[int]] = field(default_factory=dict)

    def add_edge(self, src: int, symbol: str, dst: int) -> None:
        self.transitions.setdefault(src, {})[symbol] = dst


def epsilon_closure(nfa: NFA, states) -> FrozenSet[int]:
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for nxt in nfa.transitions.get(s, {}).get(EPSILON, ()):
            if nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return frozenset(closure)


def _move(nfa: NFA, states, symbol: str) -> Set[int]:
    result: Set[int] = set()
    for s in states:
        result |= nfa.transitions.get(s, {}).get(symbol, set())
    return result


def build_dfa(nfa: NFA) -> DFA:
    """Construccion de subconjuntos (algoritmo de Rabin-Scott)."""
    alphabet = set(nfa.alphabet)
    counter = itertools.count()

    start_set = epsilon_closure(nfa, {nfa.start})
    subset_to_id: Dict[FrozenSet[int], int] = {start_set: next(counter)}
    pending = [start_set]

    transitions: Dict[int, Dict[str, int]] = {}

    while pending:
        curr_set = pending.pop()
        curr_id = subset_to_id[curr_set]
        for symbol in alphabet:
            moved = _move(nfa, curr_set, symbol)
            if not moved:
                continue
            target_set = epsilon_closure(nfa, moved)
            if target_set not in subset_to_id:
                subset_to_id[target_set] = next(counter)
                pending.append(target_set)
            transitions.setdefault(curr_id, {})[symbol] = subset_to_id[target_set]

    accepts = {sid for subset, sid in subset_to_id.items() if nfa.accept in subset}
    state_labels = {sid: subset for subset, sid in subset_to_id.items()}

    return DFA(
        states=set(subset_to_id.values()),
        transitions=transitions,
        start=subset_to_id[start_set],
        accepts=accepts,
        alphabet=alphabet,
        state_labels=state_labels,
    )
