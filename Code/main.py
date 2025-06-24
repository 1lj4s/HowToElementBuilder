import numpy as np
from pathlib import Path
from MoM.MoMsession import MoMSession
from rlcg2s.rlcg2s import RLGC2SConverter
import os
import tempfile


def main():
    project_path = Path(r"D:\Saves\pycharm\HowToElementBuilder").resolve()
    base_path = project_path / "Code" / "Files"

    paths = {
        "OUTPUT_DIR": str((base_path / "snp").resolve()),
        "SCRIPT_DIR": str((base_path / "scripts").resolve()),
        "MoM_exe": r"C:\Program Files\Talgat 2021\PythonClient.exe"
    }

    for path in [paths["OUTPUT_DIR"], paths["SCRIPT_DIR"]]:
        Path(path).mkdir(parents=True, exist_ok=True)

    if not os.path.isfile(paths["MoM_exe"]):
        print(f"[MAIN] Error: MoM executable not found at {paths['MoM_exe']}")
        return

    STRUCTURES = {
        "MLIN": {
            "W": 70.e-6,
            "L": 2000.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic", # 2D_Quasistatic, 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
        "MIMCAP": {
            "W": 50.e-6,
            "L": 50.e-6,
            "SUBSTRATE": "MSUB2",
            "MODELTYPE": "3D_Quasistatic", # 2D_Quasistatic, 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
        "MNLIN": {
            "W": [70.e-6, 70.e-6],
            "S": [20.e-6],
            "L": 1000.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic", # 2D_Quasistatic, 3D_Quasistatic
            "SIMULATION": "SPARAM",
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
            "TD1": 0.003,
        },
        "MSUB2": {
            "T1": 1.e-6,
            "T2": 1.e-6,
            "H1": 100.e-6,
            "H2": 0.2515e-6,
            "ER0": 1.0,
            "MU0": 1.0,
            "TD0": 0.0,
            "ER1": 12.9,
            "MU1": 1.0001,
            "TD1": 0.003,
            "ER2": 3.0,
            "MU2": 1.0002,
            "TD2": 0.001,
        }
    }
    SIMULATIONS = {
        "SPARAM": {
            "f0": np.linspace(10.e9, 67.e9, 5), # [0.8e9, 1.e9, 5.e9, 10.e9, 50.e9]
            "freq_range": np.linspace(0.1e9, 67.e9, 335),
            "loss": True,
            "sigma": None,
            "seg_cond": 1.0,
            "seg_diel": 1.0,
            "do_vector_fitting": False,
            "Z0": 50,
        }
    }
    # TODO: Добавить потери в проводниках для 3D
    # TODO: Добавить MNLIN
    # TODO: Сделать так, чтобы при rlcg2s для 3D не нужно было нормировать матрицы и сравнить результат с текущим

    available_structs = ["MLIN", "MIMCAP", "MNLIN"]
    print("[MAIN] Available structures:", ', '.join(available_structs))
    while True:
        struct_name = input("[MAIN] Enter structure name or exit: ").strip().upper()
        if struct_name.lower() == 'exit':
            print("[MAIN] Exiting program.")
            return
        if struct_name in available_structs:
            break
        print(f"[MAIN] Invalid structure. Please choose from {', '.join(available_structs)} or 'exit'.")

    params = {**STRUCTURES[struct_name], **SUBSTRATES[STRUCTURES[struct_name]["SUBSTRATE"]], **SIMULATIONS["SPARAM"]}
    model_type = params["MODELTYPE"]

    # Select script files based on MODELTYPE
    if model_type == "2D_Quasistatic":
        shared_script = "shared_2D.py"
        struct_script = f"{struct_name}_2D.py"
    elif model_type == "3D_Quasistatic":
        shared_script = "shared_3D.py"
        struct_script = f"{struct_name}_3D.py"
    else:
        print(f"[MAIN] Error: Unsupported MODELTYPE {model_type}")
        return

    try:
        shared_code = open(Path(paths["SCRIPT_DIR"]) / shared_script, encoding="utf-8").read()
        script_code = open(Path(paths["SCRIPT_DIR"]) / struct_script, encoding="utf-8").read()
    except FileNotFoundError as e:
        print(f"[MAIN] Error: File not found - {e.filename}")
        return

    session = MoMSession(paths["MoM_exe"])
    try:
        # Create a temporary file for shared_code
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as tmp_shared:
            tmp_shared.write(shared_code)
            shared_script_path = tmp_shared.name

        # Execute shared_code first to set up the environment
        session.proc.stdin.write(f"exec(open(r'''{shared_script_path}''').read())\n")
        session.proc.stdin.flush()

        # Create a temporary file for the structure-specific script
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as tmp_script:
            tmp_script.write(script_code)
            script_path = tmp_script.name

        # Run the structure-specific script
        result = session.run_script(params, open(script_path, "r", encoding="utf-8").read())
        if "error" in result:
            print(f"[MAIN] MoM Error: {result['error']}")
            return

        converter = RLGC2SConverter(params, [result])
        s_params, rlgc_struct = converter.convert()
        output_filename = f"{struct_name}.s{s_params.shape[0]}p"
        output_path = Path(paths["OUTPUT_DIR"]) / output_filename
        converter.save_to_snp(s_params, str(output_path))

        print(f"[MAIN] Simulation completed for {struct_name}")
        print(f"[MAIN] S-parameters saved to {output_path}")
        print(f"[MAIN] S-params shape: {s_params.shape}")

    except Exception as e:
        print(f"[MAIN] Error during simulation: {str(e)}")
    finally:
        session.close()
        # Clean up temporary files
        if 'shared_script_path' in locals():
            os.unlink(shared_script_path)
        if 'script_path' in locals():
            os.unlink(script_path)


if __name__ == "__main__":
    main()