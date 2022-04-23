"""High-level simulation API."""
import tempfile
from pathlib import Path

import circuitgraph as cg
from natsort import natsorted

from circuitsim.codegen import generate_testbench
from circuitsim.simulators import (
    available_simulators,
    compile_simulator,
    execute_simulator,
    parse_simulation_output,
)


class CircuitSimulator:
    """Class for circuit simulation."""

    def __init__(self, ckt, working_dir=None, simulator="iverilog"):
        """
        Create new simulator.

        Parameters
        ----------
        ckt: circuitgraph.Circuit
                The circuit to simulate.
        working_dir: str or pathlib.Path
                The directory to write simulation files to. If `None`, a
                temporary directory will be used.
        simulator: str
                The simulator to use. One of ['iverilog', 'verilator', 'vcs'].

        """
        if simulator not in available_simulators:
            raise ValueError(
                f"Invalid simulator '{simulator}'. Must be one of "
                f"{available_simulators}."
            )
        if ckt.is_cyclic():
            raise ValueError("Cannot simulate cyclic circuit")
        self.simulator = simulator
        self.ckt = ckt
        if working_dir is None:
            self.temp_dir = tempfile.TemporaryDirectory(
                prefix=f"circuitsim_{ckt.name}_"
            )
            self.working_dir = Path(self.temp_dir.name)
        else:
            self.temp_dir = None
            self.working_dir = Path(working_dir)
            self.working_dir.mkdir(exist_ok=True)
        self.inputs = natsorted(list(ckt.inputs()))
        self.outputs = natsorted(list(ckt.outputs()))
        self._initialized = False

    def __del__(self):
        """Remove temporary directory if necessary."""
        if self.temp_dir:
            self.temp_dir.cleanup()

    def _initialize_simulator(self):
        generate_testbench(
            self.working_dir, self.ckt.name, self.inputs, self.outputs, self.simulator
        )
        cg.to_file(self.ckt, self.working_dir / f"{self.ckt.name}.v")
        netlists = [self.working_dir / "tb.v", self.working_dir / f"{self.ckt.name}.v"]
        compile_simulator(self.simulator, netlists, self.working_dir)
        self._initialized = True

    def simulate(self, vectors, num_processes=1, allow_x=False):
        """
        Execute the simulator on a list of vectors.

        Parameters
        ----------
        vectors: list of dict of str:bool
                The vectors to simulate. Each vector is represented as a
                dictionary mapping an input to a logical value.
        num_process: int
                The number of simulation processes to run. Specifying a
                number more than 1 will cause multiple simulations to be
                executed in parallel.
        allow_x: bool
                If True, the inputs/outputs can contain "don't care" or "x"
                values in addition to 0 and 1. Specify an don't care value
                for an input by setting it to "x". The outputs will then be
                returned as a dict of str:str, where each output is either
                "0", "1", or "x".

        Returns
        -------
        list of dict of str:bool or str:str
                The simulation outputs. Each vector is represented as a
                dictionary mapping an output to a logical value. If `allow_x`
                is True, then instead of logic values, each output will be
                mapped to either "0", "1", or "x".

        """
        if not self._initialized:
            self._initialize_simulator()
        if self.simulator == "verilator" and allow_x:
            raise ValueError("Cannot use x-based simulation with verilator")
        execute_simulator(
            self.simulator,
            self.inputs,
            vectors,
            self.working_dir,
            num_processes,
            allow_x=allow_x,
        )
        return parse_simulation_output(
            self.working_dir, self.outputs, num_processes, allow_x=allow_x
        )
