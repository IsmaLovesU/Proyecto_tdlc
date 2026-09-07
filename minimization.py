"""Minimizacion de AFD por particion de equivalencia (algoritmo de Moore /
refinamiento de particiones).
"""

from typing import Dict, FrozenSet, Set

from subset_construction import DFA

_TRAP = -1


def _complete(dfa: DFA):
    """Devuelve (transitions, states) totalizados con un estado trampa
    explicito, necesario para que el refinamiento de particiones distinga
    correctamente los casos sin transicion (rechazo implicito)."""
    states = set(dfa.states) | {_TRAP}
    transitions: Dict[int, Dict[str, int]] = {
        s: dict(dfa.transitions.get(s, {})) for s in dfa.states
    }
    transitions[_TRAP] = {symbol: _TRAP for symbol in dfa.alphabet}
    for s in dfa.states:
        for symbol in dfa.alphabet:
            transitions[s].setdefault(symbol, _TRAP)
    return transitions, states


def _partition_id(partition, state) -> int:
    for i, group in enumerate(partition):
        if state in group:
            return i
    raise ValueError(f"Estado {state} no encontrado en ninguna particion")


def minimize_dfa(dfa: DFA) -> DFA:
    transitions, states = _complete(dfa)
    accepts = set(dfa.accepts)

    accepting = frozenset(s for s in states if s in accepts)
    non_accepting = frozenset(s for s in states if s not in accepts)
    partition = [g for g in (accepting, non_accepting) if g]

    changed = True
    while changed:
        changed = False
        new_partition = []
        for group in partition:
            # Subdivide el grupo segun a que particion transiciona cada
            # estado, para cada simbolo del alfabeto.
            buckets: Dict[tuple, Set[int]] = {}
            for state in group:
                signature = tuple(
                    _partition_id(partition, transitions[state][symbol])
                    for symbol in sorted(dfa.alphabet)
                )
                buckets.setdefault(signature, set()).add(state)
            new_partition.extend(frozenset(b) for b in buckets.values())
        if len(new_partition) != len(partition):
            changed = True
        partition = new_partition

    group_of: Dict[int, int] = {}
    for i, group in enumerate(partition):
        for state in group:
            group_of[state] = i

    trap_group = group_of[_TRAP]

    new_transitions: Dict[int, Dict[str, int]] = {}
    new_accepts: Set[int] = set()
    reachable_groups: Set[int] = set()

    for state in dfa.states:
        g = group_of[state]
        reachable_groups.add(g)
        if state in accepts:
            new_accepts.add(g)
        for symbol in dfa.alphabet:
            target_group = group_of[transitions[state][symbol]]
            if target_group == trap_group:
                continue
            new_transitions.setdefault(g, {})[symbol] = target_group

    # El estado trampa (rechazo implicito) no se incluye como estado real:
    # se conserva el mismo estilo "parcial" que el AFD sin minimizar.
    reachable_groups.discard(trap_group)
    new_transitions.pop(trap_group, None)

    new_start = group_of[dfa.start]

    state_labels = {
        g: frozenset().union(*(dfa.state_labels.get(s, frozenset()) for s in group if s != _TRAP))
        for g, group in enumerate(partition)
        if g in reachable_groups
    }

    return DFA(
        states=reachable_groups,
        transitions=new_transitions,
        start=new_start,
        accepts=new_accepts,
        alphabet=set(dfa.alphabet),
        state_labels=state_labels,
    )
