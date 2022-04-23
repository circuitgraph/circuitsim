"""Interface with simulators."""
import math
import subprocess
from multiprocessing import Pool
from pathlib import Path

available_simulators = ["iverilog", "verilator", "vcs"]

compile_args = {
    "vcs": ["vcs", "-full64"],
    "iverilog": ["iverilog"],
    "verilator": ["verilator", "--exe", "tb.cpp", "--cc"],
}
post_compile_args = {"verilator": ["make", "-C", "obj_dir", "-f", "Vtb.mk"]}
simulate_args = {
    "vcs": ["./simv", "-q"],
    "iverilog": ["vvp", "a.out"],
    "verilator": ["./obj_dir/Vtb"],
}


class SimulationCompilationError(Exception):
    """Thrown when a simulation fails during compilation."""


class SimulationExecutionError(Exception):
    """Thrown when a simulation fails during execution."""


def _convert_value(v, allow_x=False):
    if v in [True, False, 0, 1]:
        return str(int(v))
    if isinstance(v, str) and v in "01":
        return v
    if allow_x and v.lower() == "x":
        return v.lower()
    raise ValueError(f"Unknown input value '{v}'")


def _convert_values(values, allow_x=False):
    return {k: _convert_value(v, allow_x=allow_x) for k, v in values.items()}


def compile_simulator(simulator, netlists, working_dir):
    """
    Compile a circuit simulation.

    Parameters
    ----------
    simulator: str
            The simulator to use.
    netlist: list of str or pathlib.Path
            The netlists to compile.
    working_dir: str or pathlib.Path
            The path to comiple the simulation in.

    """
    netlists = [str(Path(n).absolute()) for n in netlists]
    working_dir = Path(working_dir)
    with open(working_dir / "compile.log", "w+") as f:
        try:
            subprocess.run(
                compile_args[simulator] + netlists,
                cwd=working_dir,
                stdout=f,
                stderr=f,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            f.seek(0)
            message = f.read()
            raise SimulationCompilationError(message) from e

    if simulator in post_compile_args:
        with open(working_dir / "post_compile.log", "w+") as f:
            try:
                subprocess.run(
                    post_compile_args[simulator],
                    cwd=working_dir,
                    stdout=f,
                    stderr=f,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                f.seek(0)
                message = f.read()
                raise SimulationCompilationError(message) from e


def _run_process(p, simulator, working_dir):
    with open(working_dir / f"simulate_{p}.log", "w") as f:
        return subprocess.run(
            simulate_args[simulator]
            + [f"+input_file=input_file_{p}.txt", f"+output_file=output_file_{p}.txt"],
            cwd=working_dir,
            stdout=f,
            stderr=f,
            check=True,
        )


def execute_simulator(
    simulator, inputs, vectors, working_dir, num_processes, allow_x=False
):
    """
    Execute a compiled simulation.

    Parameters
    ----------
    simulator; str
            The simulator to use.
    inputs: list of str
            The inputs to the module.
    vectors: list of dict of str:bool
            The vectors to simulate. Each vector is represented as a
            dictionary mapping an input to a logical value.
    working_dir: str or pathlib.Path
            The directory to compile and run the simulation in.
    num_process: int
            The number of simulation processes to run. Specifying a
            number more than 1 will cause multiple simulations to be
            executed in parallel.
    allow_x: bool
            If True, the inputs/outputs can contain "don't care" or "x"
            values in addition to 0 and 1. Specify an don't care value
            for an input by setting it to "x".

    """
    working_dir = Path(working_dir)

    vectors_per_process = math.ceil(len(vectors) / num_processes)
    for p, v in enumerate(
        [
            vectors[i : i + vectors_per_process]
            for i in range(0, len(vectors), vectors_per_process)
        ]
    ):
        with open(working_dir / f"input_file_{p}.txt", "w") as f:
            for vector in v:
                vector = _convert_values(vector, allow_x=allow_x)
                try:
                    f.write("".join(vector[i] for i in inputs) + "\n")
                except KeyError as e:
                    missing_inputs = ", ".join(set(inputs) - set(vector))
                    if len(missing_inputs) > 20:
                        missing_inputs = missing_inputs[:17] + "..."
                    raise ValueError(
                        "Value not provided for inputs '{missing_inputs}'"
                    ) from e

    if num_processes > 1:
        with Pool(num_processes) as pool:
            results = pool.starmap_async(
                _run_process,
                [(p, simulator, working_dir) for p in range(num_processes)],
            )

            sim_results = results.get()
            for sim_res in sim_results:
                if sim_res.returncode != 0:
                    with open(working_dir / "simulate.log") as f:
                        message = f.read()
                    raise SimulationExecutionError(message)
    else:
        sim_res = _run_process(0, simulator, working_dir)


def parse_simulation_output(working_dir, outputs, num_processes, allow_x=False):
    """
    Parse the output of a simulation.

    Parameters
    ----------
    working_dir: str or pathlib.Path
            The directory that the simulation was run from.

    Returns
    -------
    list of dict of str to bool
            The simulation results, as a list of dictionaries mapping
            outputs to values.
    num_process: int
            The number of simulation processes that were run.
    allow_x: bool
            If True, the outputs can contain "don't care" or "x"
            values in addition to 0 and 1. The outputs will then be
            returned as a dict of str:str, where each output is either
            "0", "1", or "x".

    Returns
    -------
    list o dict o str:bool or str:str
            The simulation outputs. Each vector is represented as a
            dictionary mapping an output to a logical value. If `allow_x`
            is True, then instead of logic values, each output will be
            mapped to either "0", "1", or "x".

    """
    working_dir = Path(working_dir)
    vectors = []
    for p in range(num_processes):
        with open(working_dir / f"output_file_{p}.txt") as f:
            for line in f:
                if allow_x:
                    if not set(line.strip().lower()) <= {"0", "1", "x"}:
                        raise ValueError(f"Unknown value in simulation output: {line}")
                    vectors.append(dict(zip(outputs, line.strip().lower())))
                else:
                    if not set(line.strip()) <= {"0", "1"}:
                        raise ValueError(f"Unknown value in simulation output: {line}")
                    vectors.append(
                        {o: bool(int(v)) for o, v in zip(outputs, line.strip())}
                    )

    return vectors
