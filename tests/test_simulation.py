import random
import shutil
import tempfile
import unittest

import circuitgraph as cg

from circuitsim import CircuitSimulator


class TestSimulation(unittest.TestCase):
    def run_simulation_test(self, simulator, num_processes=1):
        num_trials = 10
        num_vectors = 100
        # Exercise random inputs through simulation
        tmpdir = tempfile.mkdtemp(
            prefix=f"circuitsim_TestSimulation_test_simulate_{simulator}"
        )
        c = cg.from_lib("c880")
        simulator = CircuitSimulator(c, tmpdir, simulator=simulator)
        for _ in range(num_trials):
            vectors = []
            for _ in range(num_vectors):
                vectors.append({i: random.choice([True, False]) for i in c.inputs()})
            sim_results = simulator.simulate(vectors, num_processes)
            self.assertEqual(len(vectors), len(sim_results))
            # Verify against sat
            for vector, sim_result in zip(vectors, sim_results):
                sat_result = cg.sat.solve(c, vector)
                self.assertDictEqual(
                    {o: sat_result[o] for o in c.outputs()}, sim_result
                )
        shutil.rmtree(tmpdir)

    def run_simulation_test_x(self, simulator, num_processes=1):
        # Exercise random inputs through simulation
        tmpdir = tempfile.mkdtemp(
            prefix=f"circuitsim_TestSimulation_test_simulate_{simulator}"
        )
        c = cg.Circuit()
        c.add("i0", "input")
        c.add("i1", "input")
        c.add("i2", "input")
        c.add("g0", "and", fanin=["i0", "i1"], output=True)
        c.add("g1", "or", fanin=["i1", "i2"], output=True)
        c.add("o0", "xor", fanin=["g0", "g1"], output=True)

        simulator = CircuitSimulator(c, tmpdir, simulator=simulator)
        vector = {"i0": "0", "i1": "0", "i2": "0"}
        result = {"g0": "0", "g1": "0", "o0": "0"}
        sim_result = simulator.simulate([vector], num_processes, allow_x=True)
        self.assertEqual(len(sim_result), 1)
        self.assertDictEqual(result, sim_result[0])

        vector = {"i0": "x", "i1": "0", "i2": "0"}
        result = {"g0": "0", "g1": "0", "o0": "0"}
        sim_result = simulator.simulate([vector], num_processes, allow_x=True)
        self.assertEqual(len(sim_result), 1)
        self.assertDictEqual(result, sim_result[0])

        vector = {"i0": "x", "i1": "1", "i2": "0"}
        result = {"g0": "x", "g1": "1", "o0": "x"}
        sim_result = simulator.simulate([vector], num_processes, allow_x=True)
        self.assertEqual(len(sim_result), 1)
        self.assertDictEqual(result, sim_result[0])

        shutil.rmtree(tmpdir)

    @unittest.skipIf(shutil.which("vcs") is None, "VCS not installed")
    def test_simulate_vcs(self):
        self.run_simulation_test("vcs")

    @unittest.skipIf(shutil.which("vcs") is None, "VCS not installed")
    def test_simulate_vcs_multiproc(self):
        self.run_simulation_test("vcs", num_processes=4)

    @unittest.skipIf(shutil.which("vcs") is None, "VCS not installed")
    def test_simulate_vcs_x(self):
        self.run_simulation_test_x("vcs")

    @unittest.skipIf(shutil.which("iverilog") is None, "iverilog not installed")
    def test_simulate_iverilog(self):
        self.run_simulation_test("iverilog")

    @unittest.skipIf(shutil.which("iverilog") is None, "iverilog not installed")
    def test_simulate_iverilog_multiproc(self):
        self.run_simulation_test("iverilog", num_processes=4)

    @unittest.skipIf(shutil.which("iverilog") is None, "iverilog not installed")
    def test_simulate_iverilog_x(self):
        self.run_simulation_test_x("iverilog")

    @unittest.skipIf(shutil.which("verilator") is None, "verilator not installed")
    def test_simulate_verilator(self):
        self.run_simulation_test("verilator")

    @unittest.skipIf(shutil.which("verilator") is None, "verilator not installed")
    def test_simulate_verilator_x(self):
        with self.assertRaises(ValueError):
            self.run_simulation_test_x("verilator")

    @unittest.skipIf(shutil.which("iverilog") is None, "iverilog not installed")
    def test_bad_vectors(self):
        tmpdir = tempfile.mkdtemp(prefix="circuitsim_TestSimulation_test_bad_vectors")
        c = cg.from_lib("c880")
        i = c.inputs().pop()
        simulator = CircuitSimulator(c, tmpdir)
        self.assertRaises(ValueError, simulator.simulate, [{i: True}])
        shutil.rmtree(tmpdir)
