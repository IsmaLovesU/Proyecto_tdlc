"""Tokenizacion de expresiones regulares y conversion de infix a postfix
(algoritmo de Shunting Yard de Dijkstra adaptado a operadores de regex).
"""

from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

OPERATOR_CHARS = {"|", "*", "+", "?", ".", "(", ")"}

_UNARY_POSTFIX = {"STAR", "PLUS", "QUESTION"}
_BINARY = {"UNION", "CONCAT"}
_PRECEDENCE = {"UNION": 1, "CONCAT": 2}

_SINGLE_CHAR_TYPES = {
    "|": "UNION",
    "*": "STAR",
    "+": "PLUS",
    "?": "QUESTION",
    ".": "WILDCARD",
    "(": "LPAREN",
    ")": "RPAREN",
}


@dataclass(frozen=True)
class Token:
    type: str
    value: Optional[str] = None

    def __repr__(self) -> str:
        if self.value is not None:
            return f"{self.type}({self.value!r})"
        return self.type


def tokenize(line: str) -> Tuple[List[Token], Set[str]]:
    """Convierte una linea de texto en tokens, respetando escapes con '\\'.

    Devuelve (tokens, alfabeto), donde alfabeto es el conjunto de simbolos
    literales (incluyendo escapados) detectados en esa expresion especifica.
    """
    tokens: List[Token] = []
    alphabet: Set[str] = set()
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch == "\\":
            i += 1
            if i >= n:
                raise ValueError("Escape '\\' al final de la expresion sin caracter siguiente")
            literal = line[i]
            tokens.append(Token("LITERAL", literal))
            alphabet.add(literal)
            i += 1
            continue

        if ch in _SINGLE_CHAR_TYPES:
            tokens.append(Token(_SINGLE_CHAR_TYPES[ch]))
        else:
            tokens.append(Token("LITERAL", ch))
            alphabet.add(ch)
        i += 1

    return tokens, alphabet


def _needs_concat(prev: Token, curr: Token) -> bool:
    prev_can_end = prev.type in ("LITERAL", "WILDCARD", "RPAREN") or prev.type in _UNARY_POSTFIX
    curr_can_start = curr.type in ("LITERAL", "WILDCARD", "LPAREN")
    return prev_can_end and curr_can_start


def insert_concat(tokens: List[Token]) -> List[Token]:
    """Inserta el operador de concatenacion explicito (CONCAT) donde aplique."""
    if not tokens:
        return []

    result: List[Token] = [tokens[0]]
    for prev, curr in zip(tokens, tokens[1:]):
        if _needs_concat(prev, curr):
            result.append(Token("CONCAT"))
        result.append(curr)
    return result


def to_postfix(tokens: List[Token]) -> List[Token]:
    """Shunting Yard: convierte tokens infix (con CONCAT ya insertado) a postfix."""
    output: List[Token] = []
    stack: List[Token] = []

    for tok in tokens:
        if tok.type in ("LITERAL", "WILDCARD"):
            output.append(tok)
        elif tok.type in _UNARY_POSTFIX:
            # Operadores postfijos unarios: aplican de inmediato al ultimo
            # operando emitido, no requieren manejo de precedencia en la pila.
            output.append(tok)
        elif tok.type == "LPAREN":
            stack.append(tok)
        elif tok.type == "RPAREN":
            while stack and stack[-1].type != "LPAREN":
                output.append(stack.pop())
            if not stack:
                raise ValueError("Parentesis desbalanceados: falta '('")
            stack.pop()
        elif tok.type in _BINARY:
            while (
                stack
                and stack[-1].type != "LPAREN"
                and _PRECEDENCE[stack[-1].type] >= _PRECEDENCE[tok.type]
            ):
                output.append(stack.pop())
            stack.append(tok)
        else:
            raise ValueError(f"Token inesperado: {tok}")

    while stack:
        top = stack.pop()
        if top.type == "LPAREN":
            raise ValueError("Parentesis desbalanceados: falta ')'")
        output.append(top)

    return output


def regex_to_postfix(line: str) -> Tuple[List[Token], Set[str]]:
    """Atajo: tokeniza una linea y devuelve (postfix, alfabeto)."""
    tokens, alphabet = tokenize(line)
    tokens = insert_concat(tokens)
    postfix = to_postfix(tokens)
    return postfix, alphabet
