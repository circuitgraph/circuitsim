# CircuitSim

An interafce to perform simulations of gate-level HDL designs from python.

## Using the simulator
Simulation can be performed using the `CircuitSimulator` class.

This allows the simulation to be compiled once and then quieried multiple times without having to recompile.

The `CircuitSimulator` accepts circuits in the form of [circuitgraph](https://circuitgraph.github.io/circuitgraph/) `Circuit` objects.

Vectors are accepted and returned as dictionaries mapping input/output names to logical values (`True` or `False`).

## Available simulators

Currently, [iverilog](http://iverilog.icarus.com), [verilator](https://www.veripool.org/verilator/), and VCS are supported. In order to use a given simulator, it must be in your `PATH`.

## Usage Example
```python
import random
import shutil

import circuitgraph as cg

from circuitsim import CircuitSimulator


def main():
    # Exercise 3 random inputs patterns 5 times.
    num_trials = 5
    num_vectors = 3
    c = cg.from_lib("c17")
    simulator = CircuitSimulator(c)
    for sim_num in range(num_trials):
        vectors = []
        for _ in range(num_vectors):
            vectors.append({i: random.choice([True, False])
                           for i in c.inputs()})
        sim_results = simulator.simulate(vectors)
        print(f"Simulation {sim_num}")
        print(f"inputs: {vectors}")
        print(f"outputs: {sim_results}")


if __name__ == "__main__":
    main()
```
