# CircuitSim

[![Python package](https://github.com/circuitgraph/circuitsim/actions/workflows/python-package.yml/badge.svg)](https://github.com/circuitgraph/circuitsim/actions/workflows/python-package.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

An interafce to perform simulations of gate-level HDL designs from python.

## Installation

CircuitSim requires Python3.6 or greater
The easiest way to install is via PyPi:
```shell
pip install circuitsim
```

Finally, to install in-place with the source, use:
```shell
cd <install location>
git clone https://github.com/circuitgraph/circuitsim.git
cd circuitsim
pip install -e .

In order to perform simulations, you must have at least one of the available simulators installed.
```

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

## Contributing

If you want to develop an improvement for this library, please consider the information below.

Tests are run using the builtin unittest framework. Some basic linting is performed using flake8.
```shell
pip instsall flake8
make test
```

Documentation is built using pdoc3.
```shell
pip install pdoc3
make doc
```

Code should be formatted using [black](https://black.readthedocs.io/en/stable/).
[Pre-commit](https://pre-commit.com) is used to automatically run black on commit.
```shell
pip install black pre-commit
pre-commit install
```
Pre-commit also runs a few other hooks, including a docstring formatter and linter. Docs follow the `numpy` documentation convention.

