# symicasession.py

import subprocess
import os
from typing import Optional

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
            result = subprocess.run(
                [self.symspice_path, cir_file],
                cwd=cir_dir,
                capture_output=True,
                text=True,
                check=False
            )

            return {
                "status": "ok" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except FileNotFoundError:
            return {"error": f"Симулятор {self.symspice_path} не найден. Убедитесь, что он установлен и в PATH."}
        except Exception as e:
            return {"error": str(e)}

# Пример использования
if __name__ == "__main__":
    session = SymicaSession()
    cir_file = r"E:\Saves\pycharm\HowToElementBuilder\Code\symica\symsnptest.scs"
    result = session.run_simulation(cir_file)

    print("======= STDOUT =======")
    print(result.get("stdout", ""))
    print("\n======= STDERR =======")
    print(result.get("stderr", ""))
    print("\n======= STATUS =======")
    print(result.get("status", "unknown"))

    if "error" in result:
        print("\n❌", result["error"])
