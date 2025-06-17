import subprocess
import os
#from typing import Optional
#from Code.symica.symicanetlist_01 import generate_netlist
from pathlib import Path

class SymicaSession:
    def __init__(self, paths: dict, struct_name: str, struct_params: dict, subs: dict, simul: dict, symspice_path: str = None):
        """
        Инициализирует сессию Symica с путем к симулятору.
        :type structure: dict
        """
        if symspice_path == None:
            self.symspice_path = r"C:\Program Files\Symica\bin\symspice.exe"
        self.paths = paths
        self.struct_name = struct_name
        self.struct_params = struct_params
        self.substrate = subs
        self.simul = simul

    def generate_netlist(self, out_name: str, num_ports: int):
        model_type = self.struct_params["MODELTYPE"]

        netlist_lines = [
            "simulator lang=local",
            "global 0\n"
        ]
        ports = [str(x) for x in range(1,num_ports+1)]
        zeros = ['0'] * num_ports
        ports_zeros = []
        for p, z in zip(ports, zeros):
            ports_zeros.append(p)
            ports_zeros.append(z)

        if model_type == "2D_Quasistatic":
            s2p_path = os.path.join(self.paths["SNP_DIR"], f"{self.struct_name}.s{num_ports}p")
            netlist_lines.append(f'NPORT0 {" ".join(ports_zeros)} nport file="{s2p_path}"')
            for idx, port in enumerate(ports):
                netlist_lines.append(f'PORT{idx} {port} 0 port r=50 num={idx + 1} type=sine rptstart=1 rpttimes=0')

        elif model_type == "Verilog":
            verilog_path = os.path.join(self.paths["VERILOG_DIR"], f"{self.struct_name}.va")
            netlist_lines.append(f'ahdl_include "{verilog_path}"')
            element_ports = [f"p{i + 1}" for i in range(num_ports)]

            # params = " ".join([f"{k} = {v}" for k, v in structure.items() if k not in {"MODELTYPE", "SUBSTRATE", "SIMULATION"}])
            structure_params = {k: v for k, v in self.struct_params.items() if k not in {"MODELTYPE", "SUBSTRATE", "SIMULATION"}}
            all_params = {**self.substrate, **structure_params}
            params = " ".join([f"{k} = {v}" for k, v in all_params.items()])

            netlist_lines.append(f'I0 {" ".join(element_ports)} {self.struct_name} {params}')

            for idx, port in enumerate(element_ports):
                netlist_lines.append(f'PORT{idx + 1} {port} 0 port r=50 num={idx + 1} type=sine rptstart=1 rpttimes=0')

        elif model_type == "Subcircuit":
            sub_path = os.path.join(self.paths["SUBCIRCUIT_DIR"], f"{self.struct_name}.cir")
            netlist_lines.append(f'include "{sub_path}"')
            element_ports = [f"p{i + 1}" for i in range(num_ports)]

            # params = " ".join([f"{k} = {v}" for k, v in structure.items() if k not in {"MODELTYPE", "SUBSTRATE", "SIMULATION"}])
            structure_params = {k: v for k, v in self.struct_params.items() if k not in {"MODELTYPE", "SUBSTRATE", "SIMULATION"}}
            all_params = {**self.substrate, **structure_params}
            params = " ".join([f"{k} = {v}" for k, v in all_params.items()])

            netlist_lines.append(f'U1 {" ".join(element_ports)} {self.struct_name} {params}')

            for idx, port in enumerate(element_ports):
                netlist_lines.append(
                    f'PORT{idx + 1} {port} 0 port r=50 num={idx + 1} type=sine fundname=aaa '
                    f'ampl=0.0001 freq=5000000000 data=0 rptstart=1 rpttimes=0 mag=1e-006'
                )

        # Анализ
        f_start, f_stop = self.simul["freq_range"][0], self.simul["freq_range"][-1]
        points = len(self.simul["freq_range"])
        f_step = (f_stop - f_start) / points
        analysis_path = os.path.join(self.paths["OUTPUT_DIR"], f"{out_name}.s{num_ports}p")
        netlist_lines.append(
            f'\nSPSweep sp start={f_start:.0f} stop={f_stop:.0f} step={f_step} file="{analysis_path}"')

        # Завершающие опции
        netlist_lines.append(
            "\nDEFAULT_OPTIONS options tnom=27 temp=27  acout=0 fast_spice=0 reltol=1.000000e-003 rawfmt=nutascii")

        for line in netlist_lines:
            print(line)
        # Сохраняем файл
        if not os.path.exists(self.paths["NETLIST_DIR"]):
            os.mkdir(self.paths["NETLIST_DIR"])
        filepath = os.path.join(self.paths["NETLIST_DIR"], f"{out_name}.scs")
        with open(filepath, 'w') as f:
            f.write("\n".join(netlist_lines))

        print(f"[symnetlist] Netlist saved to {filepath}")
        return (filepath)

    def run_simulation(self, cir_path: str) -> dict:
        """
        Запускает симуляцию SymSpice на основе cir-файла.

        :param cir_path: Абсолютный путь к .cir или .scs файлу.
        :return: Словарь с полями stdout, stderr и status.
        """
        if not os.path.isfile(cir_path):
            return {"error": f"Файл {cir_path} не найден"}

        cir_dir = os.path.dirname(cir_path)
        cir_file = os.path.basename(cir_path)

        try:
            # Запуск процесса с Popen для захвата вывода в реальном времени
            process = subprocess.Popen(
                [self.symspice_path, cir_file],
                cwd=cir_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            output_lines = []
            # Чтение вывода построчно
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                print("[SYMSPICE]", line.strip())
                output_lines.append(line.strip())
                # Проверка на завершение вывода (если нужно остановиться при определенной строке)
                if line.strip().startswith("{") and line.strip().endswith("}"):
                    break

            # Ожидание завершения процесса и получение кода возврата
            returncode = process.wait()

            return {
                "status": "ok" if returncode == 0 else "error",
                "stdout": "\n".join(output_lines),
                "stderr": "",
                "returncode": returncode
            }

        except FileNotFoundError:
            return {"error": f"Симулятор {self.symspice_path} не найден. Убедитесь, что он установлен и в PATH."}
        except Exception as e:
            return {"error": str(e)}


# Пример использования
if __name__ == "__main__":
    # создаем нетлист и возвращаем путь к нему
    NETLIST_DIR = Path("../../Code/Files/symnet/")
    SNP_DIR = Path("../../Code/Files/snp/")
    VERILOG_DIR = Path("../../Code/Files/ver/")
    SUBCIRCUIT_DIR = Path("../../Code/Files/sub/")
    OUTPUT_DIR = Path("../../Files/symout/")
    VERILOG_PORTS = ["n7_1", "n7_2"]
    DEFAULT_PORTS = ["n7_1", "n7_2"]

    # netlist_path = r"D:\saves\Pycharm\HowToElementBuilder\Code\Files\symnet/MSTEP.scs"

    # Работаем с symica
    session = SymicaSession()
    netlist_path = session.generate_netlist("MOPEN", "MOPEN")
    result = session.run_simulation(netlist_path)

    print("[SYMSPICE]", result.get("status", "unknown"))

    if "error" in result:
        print("[SYMSPICE]",  result["error"])