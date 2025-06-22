import numpy as np
from pathlib import Path
from MoM2D.MoM2Dsession import MoM2DSession
from rlcg2s.rlcg2s import RLGC2SConverter
import os

def main():
    project_path = Path(r"E:\Saves\pycharm\HowToElementBuilder").resolve()
    base_path = project_path / "Code" / "Files"

    paths = {
        "OUTPUT_DIR": str((base_path / "snp").resolve()),
        "SCRIPT_DIR": str((base_path / "scripts").resolve()),
        "MoM2D_exe": r"C:\Program Files\Talgat 2021\PythonClient.exe"
    }

    for path in [paths["OUTPUT_DIR"], paths["SCRIPT_DIR"]]:
        Path(path).mkdir(parents=True, exist_ok=True)

    if not os.path.isfile(paths["MoM2D_exe"]):
        print(f"[MAIN] Error: MoM2D executable not found at {paths['MoM2D_exe']}")
        return

    STRUCTURES = {
        "MLIN": {
            "W": 100.e-6,
            "NumPorts": 1,
            "MODELTYPE": "2D_Quasistatic",
        },
        "MSTEP": {
            "W1": 50.e-6,
            "W2": 100.e-6,
            "NumPorts": 2,
            "MODELTYPE": "2D_Quasistatic",
        },
        "TFR": {
            "RS": 50,
            "W": 100.e-6,
            "L": 100.e-6,
            "NumPorts": 2,
            "MODELTYPE": "2D_Quasistatic",
        },
    }
    SUBSTRATES = {
        "MSUB": {
            "T": 1e-6,
            "H": 100.e-6,
            "ER0": 1.0,
            "MU0": 1.0,
            "TD0": 0.0,
            "ER1": 12.9,
            "MU1": 1.0001,
            "TD1": 0.001,
            "seg_cond": 3.0,
            "seg_diel": 1.0
        }
    }
    SIMULATIONS = {
        "SPARAM": {
            "freq_range": np.linspace(0.1e9, 67.e9, 335),
            "f0": [1e9, 5e9, 10e9],
            "Z0": 50,
            "length": 0.1,
            "loss": True,
            "sigma": None
        }
    }

    available_structs = ["MLIN", "MSTEP", "TFR"]
    print("[MAIN] Available structures:", ', '.join(available_structs))
    while True:
        struct_name = input("[MAIN] Enter structure name or exit: ").strip().upper()
        if struct_name.lower() == 'exit':
            print("[MAIN] Exiting program.")
            return
        if struct_name in available_structs:
            break
        print(f"[MAIN] Invalid structure. Please choose from {', '.join(available_structs)} or 'exit'.")
    params = {**STRUCTURES[struct_name], **SUBSTRATES["MSUB"], **SIMULATIONS["SPARAM"]}
    script_file = f"{struct_name}.py"
    try:
        script_code = open(Path(paths["SCRIPT_DIR"]) / script_file, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"[MAIN] Error: {script_file} not found in {paths['SCRIPT_DIR']}")
        return

    session = MoM2DSession(paths["MoM2D_exe"])
    try:
        result = session.run_script(params, script_code)
        if "error" in result:
            print(f"[MAIN] MoM2D Error: {result['error']}")
            return

        converter = RLGC2SConverter(params, [result])
        s_params, rlgc_struct = converter.convert()

        output_filename = f"{struct_name}.s{params['NumPorts']*2}p"
        output_path = Path(paths["OUTPUT_DIR"]) / output_filename
        converter.save_to_snp(s_params, str(output_path))

        print(f"[MAIN] Simulation completed for {struct_name}")
        print(f"[MAIN] S-parameters saved to {output_path}")
        print(f"[MAIN] S-params shape: {s_params.shape}")

    except Exception as e:
        print(f"[MAIN] Error during simulation: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    main()