import subprocess
import json
import os
import tempfile


class SymicaSession:
    def __init__(self, exe_path: str, working_dir: str):
        self.exe_path = os.path.abspath(exe_path)
        self.working_dir = os.path.abspath(working_dir)
        os.makedirs(self.working_dir, exist_ok=True)

    def run_netlist(self, netlist: str, output_filename: str) -> dict:
        # Normalize paths in netlist to use forward slashes
        netlist = netlist.replace("\\", "/")

        # Create temporary .scs file
        with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".scs", encoding="utf-8", dir=self.working_dir
        ) as tmp:
            tmp.write(netlist)
            tmp_path = tmp.name
            tmp_filename = os.path.basename(tmp_path)

        # Run symspice with the input file as a command-line argument
        command = [self.exe_path, "-i", tmp_filename]
        try:
            result = subprocess.run(
                command,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=True
            )
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                print("[SYMICA]", line.strip())
            stderr_lines = result.stderr.splitlines()
            for line in stderr_lines:
                print("[SYMICA ERROR]", line.strip())
        except subprocess.CalledProcessError as e:
            output_lines = e.stdout.splitlines()
            stderr_lines = e.stderr.splitlines()
            for line in output_lines:
                print("[SYMICA]", line.strip())
            for line in stderr_lines:
                print("[SYMICA ERROR]", line.strip())
            os.remove(tmp_path)
            return {
                "netlist": netlist,
                "error": f"Simulation failed with code {e.returncode}",
                "stdout": "\n".join(output_lines),
                "stderr": "\n".join(stderr_lines)
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        # Check for output file
        if os.path.exists(output_filename):
            return {"netlist": netlist, "output_file": output_filename}
        else:
            return {
                "netlist": netlist,
                "error": f"No output file generated at {output_filename}",
                "stdout": "\n".join(output_lines),
                "stderr": "\n".join(stderr_lines)
            }


def main():
    exe_path = r"C:\Program Files\Symica\bin\symspice.exe"
    output_dir = os.path.join(os.path.dirname(__file__), "Files", "sym")
    os.makedirs(output_dir, exist_ok=True)

    # Netlist with consistent output filename
    netlist = r"""
simulator lang=local
global 0
NPORT0 1 0 2 0 nport file="E:/Saves/pycharm/SubprocessTest/symica/MLIN_test.s2p"
PORT0 1 0 port r=50 num=1 type=sine rptstart=1 rpttimes=0
PORT1 2 0 port r=50 num=2 type=sine rptstart=1 rpttimes=0
SPSweep sp start=0.1G stop=67G step=0.1G file="E:/Saves/pycharm/SubprocessTest/symica/MLIN_test1.s2p"
DEFAULT_OPTIONS options tnom=27 temp=27 reltol=1.000000e-03
"""

    output_filename = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "symica", "MLIN_test1.s2p"
    ))

    import time
    start = time.time()
    session = SymicaSession(exe_path, os.path.dirname(output_filename))

    try:
        result = session.run_netlist(netlist, output_filename)
        print(f"Simulation result: {result}")
    except Exception as e:
        print(f"Error: {str(e)}")

    print(f"Completed simulation in {time.time() - start:.2f} sec")


if __name__ == "__main__":
    main()