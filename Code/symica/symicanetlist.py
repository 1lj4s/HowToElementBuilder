import os


class SymicaNetlist:
    def __init__(self, working_dir: str, freq_range: list = None):
        """
        Initialize the SymicaNetlist generator.

        Args:
            working_dir (str): Directory for input/output files (e.g., 'E:/Saves/pycharm/SubprocessTest/symica').
            freq_range (list, optional): Frequency range in Hz [start, stop, step]. Defaults to [0.1e9, 67e9, 0.1e9].
        """
        self.working_dir = os.path.abspath(working_dir)
        self.freq_range = freq_range if freq_range else [0.1e9, 0.2e9, 67e9]
        self.sym_dir = os.path.join(self.working_dir, "Files", "sym")
        self.snp_dir = os.path.join(self.working_dir, "Files", "snp")
        self.cir_dir = os.path.join(self.working_dir, "Files", "cir")
        os.makedirs(self.sym_dir, exist_ok=True)
        os.makedirs(self.snp_dir, exist_ok=True)
        os.makedirs(self.cir_dir, exist_ok=True)

    def generate_netlist(self, simulation_type: str, structure_name: str, num_ports: int,
                         input_file: str = None, subcircuit_text: str = None) -> str:
        """
        Generate a SymSpice netlist string.

        Args:
            simulation_type (str): Type of simulation ('SymSnpTest', 'SymSubTest', 'CustomCir').
            structure_name (str): Name of the structure (e.g., 'MLIN', 'TFR').
            num_ports (int): Number of ports for the structure.
            input_file (str, optional): Path to input file (.sNp for SymSnpTest, .cir for SymSubTest/CustomCir).
            subcircuit_text (str, optional): Subcircuit definition text for CustomCir.

        Returns:
            str: Generated netlist string.
        """
        # Common initial lines
        netlist = [
            "simulator lang=local",
            "global 0",
            ""
        ]

        # Convert frequency range to GHz
        freq_start = self.freq_range[0] / 1e9  # GHz
        freq_stop = self.freq_range[-1] / 1e9  # GHz
        freq_step = (self.freq_range[1] - self.freq_range[0]) / 1e9  # GHz
        output_path = os.path.join(self.sym_dir, f"{structure_name}_test.s{num_ports}p").replace("\\", "/")

        if simulation_type == "SymSnpTest":
            if not input_file:
                raise ValueError("SymSnpTest requires an input .sNp file")
            input_path = os.path.abspath(input_file).replace("\\", "/")
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file {input_path} not found")

            # Add NPORT
            nport_nodes = " ".join(f"{i + 1} 0" for i in range(num_ports))
            netlist.append(f"NPORT0 {nport_nodes} nport file=\"{input_path}\"")
            netlist.append("")

            # Add ports
            for i in range(num_ports):
                netlist.append(
                    f"PORT{i} {i + 1} 0 port r=50 num={i + 1} type=sine rptstart=1 rpttimes=0"
                )
            netlist.append("")

            # Add SPSweep
            netlist.append(
                f"SPSweep sp start={freq_start}G stop={freq_stop}G step={freq_step}G file=\"{output_path}\""
            )

        elif simulation_type == "SymSubTest":
            if not input_file:
                raise ValueError("SymSubTest requires an input .cir file")
            input_path = os.path.abspath(input_file).replace("\\", "/")
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file {input_path} not found")

            netlist.append(f"include \"{input_path}\"")
            netlist.append("")

            # Add element U1
            nodes = " ".join(f"p{i + 1}" for i in range(num_ports))
            netlist.append(f"U1 {nodes} s_equivalent")
            netlist.append("")

            # Add ports
            for i in range(num_ports):
                netlist.append(
                    f"PORT{i + 1} p{i + 1} 0 port r=50 num={i + 1} type=sine fundname=aaa ampl=0.0001 "
                    f"freq=5000000000 data=0 rptstart=1 rpttimes=0 mag=1e-006"
                )
            netlist.append("")

            # Add sp analysis
            netlist.append(
                f"sp sp start={freq_start}G stop={freq_stop}G dec=401 file=\"{output_path}\""
            )

        elif simulation_type == "CustomCir":
            if not subcircuit_text:
                raise ValueError("CustomCir requires subcircuit_text")

            # Add subcircuit definition
            netlist.append(subcircuit_text)
            netlist.append("")

            # Add instance
            nodes = " ".join(f"p{i + 1}" for i in range(num_ports))
            netlist.append(f"X1 {nodes} {structure_name}")
            netlist.append("")

            # Add ports
            for i in range(num_ports):
                netlist.append(
                    f"PORT{i + 1} p{i + 1} 0 port r=50 num={i + 1} type=sine fundname=aaa ampl=0.0001 "
                    f"freq=5000000000 data=0 rptstart=0 mag=1e-006"
                )
            netlist.append("")

            # Add sp analysis
            netlist.append(
                f"sp sp start={freq_start}G stop={freq_stop}G dec=401 file=\"{output_path}\""
            )

        else:
            raise ValueError(f"Unsupported simulation type: {simulation_type}")

        # Add DEFAULT_OPTIONS
        if simulation_type == "SymSnpTest":
            netlist.append("DEFAULT_OPTIONS options tnom=27 temp=27 reltol=1.000000e-03")
        else:
            netlist.append(
                "DEFAULT_OPTIONS options tnom=27 temp=27 acout=0 fast_spice=0 reltol=1.000000e-003 rawfmt=nutascii"
            )

        return "\n".join(netlist)


if __name__ == "__main__":
    # Example usage
    import numpy as np
    freqs = np.linspace(0.1e9, 67e9, 100)
    print(freqs)
    netlist_gen = SymicaNetlist(working_dir="E:/Saves/pycharm/SubprocessTest/symica")

    # Example for SymSnpTest
    snp_netlist = netlist_gen.generate_netlist(
        simulation_type="SymSnpTest",
        structure_name="MLIN",
        num_ports=2,
        input_file="E:/Saves/pycharm/SubprocessTest/symica/MLIN_test.s2p"
    )
    print("SymSnpTest Netlist:")
    print(snp_netlist)
    print("\n")

    # Example for CustomCir
    subcircuit_text = """
subckt MLIN p1 p2
R1 p1 p2 50
ends MLIN
"""
    custom_netlist = netlist_gen.generate_netlist(
        simulation_type="CustomCir",
        structure_name="MLIN",
        num_ports=2,
        subcircuit_text=subcircuit_text
    )
    print("CustomCir Netlist:")
    print(custom_netlist)