"""Verilog testbench code generation."""
import uuid


def _uniquify(s, l):
    while s in l:
        s += f"_{uuid.uuid4()}"
    return s


def generate_testbench(output_dir, name, inputs, outputs, simulator):
    """
    Generate testbench code that can be used to simulate a circuit.

    Parameters
    ----------
    output_dir: pathlib.Path
            Path to save tb and any extraneous files to.
    name: str
            The name of the module to be simulated.
    inputs: list of str
            The inputs to the module.
    outputs: list of str
            The outputs to the module.
    simulator: str
            The simulator tool to generate a testbench for.

    Returns
    -------
    str
            The generated testbench code.

    """
    if simulator == "verilator":
        tick = _uniquify("tick", inputs + outputs)
        tb = f"module {name}_tb({tick});\n\n"
        tb += f"  input {tick};\n"
        first_sim = _uniquify("first_sim", inputs + outputs)
        tb += f"  reg {first_sim};\n\n"
    else:
        tb = "module tb;\n\n"
    tb += "\n".join(f"  wire {i};" for i in inputs) + "\n\n"
    tb += "\n".join(f"  wire {o};" for o in outputs) + "\n\n"

    tb += f"  {name} {name}_inst(\n"
    tb += ",\n".join(f"    .{i}({i})" for i in inputs + outputs)
    tb += "\n  );\n\n"

    ret = _uniquify("ret", inputs + outputs)
    tb += f"  integer {ret};\n\n"

    input_vector = _uniquify("input_vector", inputs + outputs)
    tb += f"  reg [{len(inputs)-1}:0] {input_vector};\n\n"

    input_concat = "{" + ", ".join(inputs) + "}"
    output_concat = "{" + ", ".join(outputs) + "}"

    tb += f"  assign {input_concat} = {input_vector};\n\n"

    infile = _uniquify("infile", inputs + outputs)
    outfile = _uniquify("outfile", inputs + outputs)
    infile_pointer = _uniquify("infile_pointer", inputs + outputs)
    outfile_pointer = _uniquify("outfile_pointer", inputs + outputs)

    tb += f"  reg [999:0] {infile};\n"
    tb += f"  reg [999:0] {outfile};\n\n"
    tb += f"  integer {infile_pointer};\n"
    tb += f"  integer {outfile_pointer};\n\n"

    tb += "  initial begin\n"
    tb += f'    if (!$value$plusargs("input_file=%s", {infile})) begin\n'
    tb += '      $display("Error opening input file");\n'
    tb += "      $finish;\n"
    tb += "  end\n"
    tb += f'    if (!$value$plusargs("output_file=%s", {outfile})) begin\n'
    tb += '      $display("Error opening output file");\n'
    tb += "      $finish;\n"
    tb += "  end\n"
    tb += f'    {infile_pointer} = $fopen({infile}, "r");\n'
    tb += f'    {outfile_pointer} = $fopen({outfile}, "w");\n'

    if simulator == "verilator":
        tb += f"    {first_sim} = 1;\n"
        tb += "  end\n\n"
        tb += f"  always@(posedge {tick}) begin\n"
        tb += f"    if ({first_sim}) begin\n"
        tb += f"      {first_sim} <= 0;\n"
        tb += "    end\n"
        tb += "    else begin\n"
        tb += f'      $fdisplay({outfile_pointer}, "%b", {output_concat});\n'
        tb += "    end\n"
        tb += f"    if ($feof({infile_pointer})) begin\n"
        tb += f"      $fclose({infile_pointer});\n"
        tb += f"      $fclose({outfile_pointer});\n"
        tb += "      $finish;\n"
        tb += "    end\n"
        tb += f'    $fscanf({infile_pointer}, "%b\\n", {input_vector});\n'
        tb += "  end\n"

        c = '#include "Vtb.h"\n'
        c += '#include "verilated.h"\n'
        c += '#include "verilated_vcd_c.h"\n\n'
        c += "int main(int argc, char **argv, char **env) {\n"
        c += "  Verilated::commandArgs(argc, argv);\n"
        c += "  Vtb* top = new Vtb;\n"
        c += "  while(!Verilated::gotFinish()) {\n"
        c += f"    top->{tick} = 1;\n"
        c += "    top->eval();\n"
        c += f"    top->{tick} = 0;\n"
        c += "    top->eval();\n"
        c += "  }\n"
        c += "}\n"
        with open(output_dir / "tb.cpp", "w") as f:
            f.write(c)
    else:
        tb += f'    {infile_pointer} = $fopen({infile}, "r");\n'
        tb += f'    {outfile_pointer} = $fopen({outfile}, "w");\n'
        tb += f"    while (!$feof({infile_pointer})) begin\n"
        tb += f'      ret = $fscanf({infile_pointer}, "%b\\n", {input_vector});\n'
        tb += f'      #1 $fdisplay({outfile_pointer}, "%b", {output_concat});\n'
        tb += "    end\n"
        tb += f"    $fclose({infile_pointer});\n"
        tb += f"    $fclose({outfile_pointer});\n"
        tb += "  end\n"
    tb += "endmodule\n"

    with open(output_dir / "tb.v", "w") as f:
        f.write(tb)
