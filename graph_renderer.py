"""Renderizado de AFN/AFD como imagenes PNG usando graphviz."""

import os
from typing import Dict, Iterable, List, Tuple

import graphviz

from thompson import NFA
from subset_construction import DFA


def _group_edges(edges: Iterable[Tuple[int, str, int]]) -> Dict[Tuple[int, int], List[str]]:
    groups: Dict[Tuple[int, int], List[str]] = {}
    for src, symbol, dst in edges:
        groups.setdefault((src, dst), []).append(symbol)
    return groups


def _base_graph(name: str) -> graphviz.Digraph:
    g = graphviz.Digraph(name=name, format="png")
    g.attr(rankdir="LR")
    g.node("__start__", shape="point")
    return g


def _render(g: graphviz.Digraph, output_path: str) -> str:
    directory, filename = os.path.split(output_path)
    directory = directory or "."
    stem, _ext = os.path.splitext(filename)
    os.makedirs(directory, exist_ok=True)
    return g.render(filename=stem, directory=directory, format="png", cleanup=True)


def render_nfa(nfa: NFA, output_path: str) -> str:
    g = _base_graph("AFN")

    for state in sorted(nfa.states):
        shape = "doublecircle" if state == nfa.accept else "circle"
        g.node(str(state), label=f"q{state}", shape=shape)
    g.edge("__start__", str(nfa.start))

    edges = (
        (src, symbol, dst)
        for src, by_symbol in nfa.transitions.items()
        for symbol, dsts in by_symbol.items()
        for dst in dsts
    )
    for (src, dst), symbols in _group_edges(edges).items():
        g.edge(str(src), str(dst), label=", ".join(sorted(symbols)))

    return _render(g, output_path)


def render_dfa(dfa: DFA, output_path: str) -> str:
    g = _base_graph("AFD")

    for state in sorted(dfa.states):
        shape = "doublecircle" if state in dfa.accepts else "circle"
        g.node(str(state), label=f"q{state}", shape=shape)
    g.edge("__start__", str(dfa.start))

    edges = (
        (src, symbol, dst)
        for src, by_symbol in dfa.transitions.items()
        for symbol, dst in by_symbol.items()
    )
    for (src, dst), symbols in _group_edges(edges).items():
        g.edge(str(src), str(dst), label=", ".join(sorted(symbols)))

    return _render(g, output_path)
