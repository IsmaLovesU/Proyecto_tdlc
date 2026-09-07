"""Simulacion de una cadena w sobre un AFN o un AFD (minimizado o no)."""

from typing import Set

from thompson import NFA, EPSILON
from subset_construction import DFA


def _epsilon_closure(nfa: NFA, states: Set[int]) -> Set[int]:
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for nxt in nfa.transitions.get(s, {}).get(EPSILON, ()):
            if nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return closure


def simulate_nfa(nfa: NFA, w: str) -> bool:
    current = _epsilon_closure(nfa, {nfa.start})
    for ch in w:
        nxt: Set[int] = set()
        for s in current:
            nxt |= nfa.transitions.get(s, {}).get(ch, set())
        if not nxt:
            return False
        current = _epsilon_closure(nfa, nxt)
    return nfa.accept in current


def simulate_dfa(dfa: DFA, w: str) -> bool:
    current = dfa.start
    for ch in w:
        nxt = dfa.transitions.get(current, {}).get(ch)
        if nxt is None:
            return False
        current = nxt
    return current in dfa.accepts
