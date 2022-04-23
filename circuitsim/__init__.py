"""
Perform gate-level simulations from python.

Examples
--------
Create a circuit to simulate.

>>> import circuitgraph as cg
>>> c = cg.from_lib("c17")

Initialize a simulator object for this circuit.

>>> from circuitsim import CircuitSimulator
>>> simulator = CircuitSimulator(c)

Simulate some vectors

>>> vectors = [
...     {"N1": 0, "N2": 1, "N3": 0, "N6": 1, "N7": 0},
...     {"N1": 1, "N2": 0, "N3": 0, "N6": 1, "N7": 1}
... ]
>>> result = simulator.simulate(vectors)
>>> result[0] == {"N22": True, "N23": True}
True
>>> result[1] == {"N22": False, "N23": True}
True

Perform x-based simulation. Note that strings must be used instead of
`int`/`bool`s.

>>> vectors = [{"N1": "0", "N2": "0", "N3": "x", "N6": "x", "N7": "1"}]
>>> result = simulator.simulate(vectors, allow_x=True)
>>> result[0] == {"N22": "0", "N23": "x"}
True

"""

from circuitsim.simulation import CircuitSimulator
from circuitsim.simulators import SimulationCompilationError
from circuitsim.simulators import SimulationExecutionError
