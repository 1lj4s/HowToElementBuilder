import subprocess
import os
from typing import Optional
from Code.symica.symicanetlist_01 import generate_netlist
from pathlib import Path

class SymicaSession:
    def __init__(self, symspice_path: str = r"C:\Program Files\Symica\bin\symspice.exe"):
        """
        Инициализирует сессию Symica с путем к симулятору.
        """
        self.symspice_path = symspice_path

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
    netlist_path = generate_netlist("MOPEN", "MOPEN")

    # netlist_path = r"D:\saves\Pycharm\HowToElementBuilder\Code\Files\symnet/MSTEP.scs"

    # Работаем с symica
    session = SymicaSession()
    result = session.run_simulation(netlist_path)

    print("[SYMSPICE]", result.get("status", "unknown"))

    if "error" in result:
        print("[SYMSPICE]",  result["error"])