import os
from Code.config import STRUCTURES, SIMULATIONS, SUBSTRATES
from pathlib import Path

NETLIST_DIR = Path("../../Code/Files/symnet/")
SNP_DIR = Path("../../Code/Files/snp/")
VERILOG_DIR = Path("../../Code/Files/ver/")
SUBCIRCUIT_DIR = Path("../../Code/Files/sub/")
OUTPUT_DIR = Path("../../Code/Files/symout/")
VERILOG_PORTS = ["n7_1", "n7_2"]
DEFAULT_PORTS = ["1", "2"]

def generate_netlist(struct_name: str, out_name: str):
    structure = STRUCTURES[struct_name]
    model_type = structure["MODELTYPE"]
    sim_name = structure["SIMULATION"]
    sim = SIMULATIONS[sim_name]

    netlist_lines = [
        "simulator lang=local",
        "global 0\n"
    ]

    ports = DEFAULT_PORTS if model_type != "Verilog" else VERILOG_PORTS
    n_ports = len(ports)
    zeros = ['0'] * n_ports
    ports_zeros = []
    for p, z in zip(ports, zeros):
        ports_zeros.append(p)
        ports_zeros.append(z)

    if model_type == "2D_Quasistatic":
        s2p_path = SNP_DIR / f"{struct_name}.s{n_ports}p"
        netlist_lines.append(f'NPORT0 {" ".join(ports_zeros)} nport file="{s2p_path.resolve()}"')
        for idx, port in enumerate(ports):
            netlist_lines.append(f'PORT{idx} {port} 0 port r=50 num={idx+1} type=sine rptstart=1 rpttimes=0')

    elif model_type == "Verilog":
        verilog_path = VERILOG_DIR / f"{struct_name}.va"
        netlist_lines.append(f'ahdl_include "{verilog_path.resolve()}"')

        # params = " ".join([f"{k} = {v}" for k, v in structure.items() if k not in {"MODELTYPE", "SUBSTRATE", "SIMULATION"}])
        substrate_name = structure["SUBSTRATE"]
        substrate_params = SUBSTRATES[substrate_name]
        structure_params = {k: v for k, v in structure.items() if k not in {"MODELTYPE", "SUBSTRATE", "SIMULATION"}}
        all_params = {**substrate_params, **structure_params}
        params = " ".join([f"{k} = {v}" for k, v in all_params.items()])

        netlist_lines.append(f'I0 {VERILOG_PORTS[1]} {VERILOG_PORTS[0]} {struct_name} {params}')

        for idx, port in enumerate(VERILOG_PORTS):
            netlist_lines.append(f'PORT{idx} {port} 0 port r=50 num={idx+1} type=sine rptstart=1 rpttimes=0')

    elif model_type == "Subcircuit":
        sub_path = SUBCIRCUIT_DIR / f"{struct_name}.cir"
        netlist_lines.append(f'include "{sub_path.resolve()}"')
        element_ports = [f"p{i+1}" for i in range(n_ports)]

        # params = " ".join([f"{k} = {v}" for k, v in structure.items() if k not in {"MODELTYPE", "SUBSTRATE", "SIMULATION"}])
        substrate_name = structure["SUBSTRATE"]
        substrate_params = SUBSTRATES[substrate_name]
        structure_params = {k: v for k, v in structure.items() if k not in {"MODELTYPE", "SUBSTRATE", "SIMULATION"}}
        all_params = {**substrate_params, **structure_params}
        params = " ".join([f"{k} = {v}" for k, v in all_params.items()])

        netlist_lines.append(f'U1 {" ".join(element_ports)} {struct_name} {params}')

        for idx, port in enumerate(element_ports):
            netlist_lines.append(
                f'PORT{idx+1} {port} 0 port r=50 num={idx+1} type=sine fundname=aaa '
                f'ampl=0.0001 freq=5000000000 data=0 rptstart=1 rpttimes=0 mag=1e-006'
            )

    # Анализ
    f_start, f_stop = sim["freq_range"][0], sim["freq_range"][-1]
    points = len(sim["freq_range"])
    f_step = (f_stop - f_start)/points
    analysis_path = OUTPUT_DIR / f"{out_name}.s{n_ports}p"
    netlist_lines.append(f'\nSPSweep sp start={f_start:.0f} stop={f_stop:.0f} step={f_step} file="{analysis_path.resolve()}"')

    # Завершающие опции
    netlist_lines.append("\nDEFAULT_OPTIONS options tnom=27 temp=27  acout=0 fast_spice=0 reltol=1.000000e-003 rawfmt=nutascii")

    for line in netlist_lines:
        print(line)
    # Сохраняем файл
    NETLIST_DIR.mkdir(parents=True, exist_ok=True)
    filepath = NETLIST_DIR / f"{out_name}.scs"
    with open(filepath, 'w') as f:
        f.write("\n".join(netlist_lines))

    print(f"[symnetlist] Netlist saved to {filepath.resolve()}")
    return(filepath.resolve())

if __name__ == "__main__":
    generate_netlist("MOPEN", "MOPEN")
