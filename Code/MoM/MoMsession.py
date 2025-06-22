import subprocess
import json
import os
import itertools
import numpy as np
import tempfile

class MoMSession:
    def __init__(self, exe_path: str):
        self.proc = subprocess.Popen(
            [exe_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

    def run_script(self, param_dict: dict, main_script: str) -> dict:


        param_code = "\n".join(f"{k} = {repr(v)}" for k, v in param_dict.items())
        full_script = f"""
{param_code}

{main_script}
    """

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as tmp:
            tmp.write(full_script)
            tmp_path = tmp.name

        self.proc.stdin.write(f"exec(open(r'''{tmp_path}''').read())\n")
        self.proc.stdin.flush()

        output_lines = []
        while True:
            line = self.proc.stdout.readline()
            if not line:
                break
            print("[MoM]", line.strip())
            output_lines.append(line.strip())
            if line.strip().startswith("{") and line.strip().endswith("}"):
                break

        os.remove(tmp_path)

        json_line = next((l for l in output_lines if l.startswith("{")), None)
        if json_line:
            return {"params": param_dict, "result": json.loads(json_line)}
        else:
            return {"params": param_dict, "error": "No JSON output"}

    def close(self):
        self.proc.terminate()
        self.proc.wait()

def main():
    # from shared import CalMat  # если потребуется
    exe_path = r"C:\Program Files\MoM2D 2021\PythonClient.exe"
    shared_code = open("../Files/scripts/shared.py", encoding="utf-8").read()
    script_code = open("../Files/scripts/M1LIN.py", encoding="utf-8").read()

    W_values = np.arange(10.e-6, 50.e-6, 5.e-6)
    S_values = [10e-6]

    param_combinations = [
        {
            "W": W,
            "S": S,
            "T": 2e-6,
            "f0": [1e9, 5e9, 10e9],
            "freq_range": np.arange(0.1e9, 67e9, 0.1e9),
            "Z0": 50,
            "length": 0.1,
            "loss": True,
            "sigma": None,
            "H": 100.e-6,
            "ER0": 1.0,
            "ER1": 12.9,
            "MU0": 1.0,
            "MU1": 1.0001,
            "TD0": 0.0,
            "TD1": 0.003,
            "seg_cond": 3.0,
            "seg_diel": 1.0
        }
        for W, S in itertools.product(W_values, S_values)
    ]

    import time
    start = time.time()
    session = MoMSession(exe_path)
    results = []
    for params in param_combinations:
        try:
            result = session.run_script(params, shared_code, script_code)
            results.append(result)
        except Exception as e:
            results.append({"params": params, "error": str(e)})

    session.close()
    print(f"Completed {len(results)} simulations in {time.time() - start:.2f} sec")
    with open("results_single_session.json", "w", encoding="utf-8") as f:
        # json.dump(results, f, indent=2)
        json.dump(results, f, indent=2, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else str(o))

if __name__ == "__main__":
    main()
