"""Construccion de Thompson: convierte una expresion postfix (ver
shunting_yard.py) en un AFN (automata finito no determinista).
"""

import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Set

from shunting_yard import Token

EPSILON = "$"


@dataclass
class NFA:
    states: Set[int]
    transitions: Dict[int, Dict[str, Set[int]]]
    start: int
    accept: int
    alphabet: Set[str]

    def add_edge(self, src: int, symbol: str, dst: int) -> None:
        self.transitions.setdefault(src, {}).setdefault(symbol, set()).add(dst)


def _new_nfa(alphabet: Set[str]) -> NFA:
    return NFA(states=set(), transitions={}, start=-1, accept=-1, alphabet=set(alphabet))


def build_nfa(postfix: List[Token], alphabet: Set[str]) -> NFA:
    """Construye un AFN a partir de una expresion en postfix, siguiendo las
    reglas clasicas de Thompson. El simbolo '.' (WILDCARD) se expande como la
    union de todos los simbolos del alfabeto detectado en esa expresion.
    """
    nfa = _new_nfa(alphabet)
    counter = itertools.count()

    def new_state() -> int:
        s = next(counter)
        nfa.states.add(s)
        return s

    stack: List[tuple] = []

    for tok in postfix:
        if tok.type == "LITERAL":
            s, a = new_state(), new_state()
            nfa.add_edge(s, tok.value, a)
            stack.append((s, a))

        elif tok.type == "WILDCARD":
            # El wildcard representa la union de los simbolos literales
            # detectados en esta expresion, mas el propio caracter '.'.
            s, a = new_state(), new_state()
            wildcard_symbols = alphabet | {"."}
            for sym in wildcard_symbols:
                nfa.add_edge(s, sym, a)
            stack.append((s, a))

        elif tok.type == "CONCAT":
            s2, a2 = stack.pop()
            s1, a1 = stack.pop()
            nfa.add_edge(a1, EPSILON, s2)
            stack.append((s1, a2))

        elif tok.type == "UNION":
            s2, a2 = stack.pop()
            s1, a1 = stack.pop()
            s, a = new_state(), new_state()
            nfa.add_edge(s, EPSILON, s1)
            nfa.add_edge(s, EPSILON, s2)
            nfa.add_edge(a1, EPSILON, a)
            nfa.add_edge(a2, EPSILON, a)
            stack.append((s, a))

        elif tok.type == "STAR":
            s1, a1 = stack.pop()
            s, a = new_state(), new_state()
            nfa.add_edge(s, EPSILON, s1)
            nfa.add_edge(s, EPSILON, a)
            nfa.add_edge(a1, EPSILON, s1)
            nfa.add_edge(a1, EPSILON, a)
            stack.append((s, a))

        elif tok.type == "PLUS":
            s1, a1 = stack.pop()
            s, a = new_state(), new_state()
            nfa.add_edge(s, EPSILON, s1)
            nfa.add_edge(a1, EPSILON, s1)
            nfa.add_edge(a1, EPSILON, a)
            stack.append((s, a))

        elif tok.type == "QUESTION":
            s1, a1 = stack.pop()
            s, a = new_state(), new_state()
            nfa.add_edge(s, EPSILON, s1)
            nfa.add_edge(s, EPSILON, a)
            nfa.add_edge(a1, EPSILON, a)
            stack.append((s, a))

        else:
            raise ValueError(f"Token postfix inesperado: {tok}")

    if len(stack) != 1:
        raise ValueError("Expresion postfix invalida: no se redujo a un unico fragmento")

    nfa.start, nfa.accept = stack.pop()

    # El alfabeto real puede incluir '.' (por el wildcard) aunque no haya
    # sido un simbolo literal detectado en la tokenizacion original.
    nfa.alphabet = {
        sym
        for edges in nfa.transitions.values()
        for sym in edges
        if sym != EPSILON
    }
    return nfa
