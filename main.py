"""Orquestador: lee un archivo con una expresion regular por linea, genera
AFN/AFD/AFD-minimizado con sus imagenes, y simula una cadena w sobre cada uno.
"""

import os
import sys

import graphviz

from shunting_yard import regex_to_postfix
from thompson import build_nfa
from subset_construction import build_dfa
from minimization import minimize_dfa
from simulator import simulate_nfa, simulate_dfa
from graph_renderer import render_nfa, render_dfa

OUTPUT_DIR = "output"


def process_line(index: int, regex: str) -> None:
    print(f"\n=== Regex {index}: {regex} ===")

    postfix, alphabet = regex_to_postfix(regex)
    nfa = build_nfa(postfix, alphabet)
    dfa = build_dfa(nfa)
    min_dfa = minimize_dfa(dfa)

    afn_path = os.path.join(OUTPUT_DIR, f"regex{index}_afn.png")
    afd_path = os.path.join(OUTPUT_DIR, f"regex{index}_afd.png")
    afd_min_path = os.path.join(OUTPUT_DIR, f"regex{index}_afd_min.png")

    render_nfa(nfa, afn_path)
    render_dfa(dfa, afd_path)
    render_dfa(min_dfa, afd_min_path)

    print(f"Imagenes generadas: {afn_path}, {afd_path}, {afd_min_path}")

    w = input(f"Ingresa una cadena w para evaluar contra '{regex}': ")

    print(f"AFN: {'si' if simulate_nfa(nfa, w) else 'no'}")
    print(f"AFD: {'si' if simulate_dfa(dfa, w) else 'no'}")
    print(f"AFD minimizado: {'si' if simulate_dfa(min_dfa, w) else 'no'}")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo_de_regex.txt>")
        sys.exit(1)

    input_path = sys.argv[1]
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    index = 0
    for line in lines:
        regex = line.rstrip("\n\r")
        if not regex:
            continue
        index += 1
        process_line(index, regex)


if __name__ == "__main__":
    try:
        main()
    except graphviz.backend.execute.ExecutableNotFound:
        print(
            "\nNo se encontro el binario 'dot' de Graphviz en el PATH.\n"
            "Instalalo desde https://graphviz.org/download/ y agregalo al PATH "
            "(ver README.md)."
        )
        sys.exit(1)
