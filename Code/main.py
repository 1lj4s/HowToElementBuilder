import numpy as np
from pathlib import Path
from MoM2D.MoM2Dsession import MoM2DSession
from rlcg2s.rlcg2s import RLGC2SConverter

def main():
    # Define project base path (absolute path to project directory)
    project_path = Path(r"E:\Saves\pycharm\HowToElementBuilder").resolve()
    base_path = project_path / "Code" / "Files"

    # Define paths
    paths = {
        "OUTPUT_DIR": str((base_path / "output").resolve()),
        "SCRIPT_DIR": str((base_path / "scripts").resolve())
    }

    # Create directories if they don't exist
    for path in paths.values():
        Path(path).mkdir(parents=True, exist_ok=True)

    # Define simulation parameters
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

    # User input for structure selection
    available_structs = ["MLIN", "MSTEP", "TFR"]
    while True:
        struct_name = input(f"Enter structure name {', '.join(available_structs)} or exit: ").strip()
        if struct_name.lower() == 'exit':
            print("[MAIN] Exiting program.")
            return
        if struct_name in available_structs:
            break
        print(f"[MAIN] Invalid structure. Please choose from {', '.join(available_structs)} or 'exit'.")

    # Initialize parameters
    params = {**STRUCTURES[struct_name], **SUBSTRATES["MSUB"], **SIMULATIONS["SPARAM"]}

    # Load scripts
    shared_code = open(Path(paths["SCRIPT_DIR"]) / "shared.py", encoding="utf-8").read()
    script_code = open(Path(paths["SCRIPT_DIR"]) / "M1LIN.py", encoding="utf-8").read()

    # Initialize MoM2DSession
    exe_path = r"C:\Program Files\TALGAT 2021\PythonClient.exe"
    session = MoM2DSession(exe_path)

    try:
        # Run simulation
        result = session.run_script(params, shared_code + "\n" + script_code)

        # Convert to S-parameters
        converter = RLGC2SConverter(params, [result])
        s_params, rlgc_struct = converter.convert()

        # Save S-parameters to file
        output_filename = f"{struct_name}_output.s{params['NumPorts']*2}p"
        output_path = Path(paths["OUTPUT_DIR"]) / output_filename
        converter.save_to_snp(s_params, str(output_path))

        # Print results
        print(f"[MAIN] Simulation completed for {struct_name}")
        print(f"[MAIN] S-parameters saved to {output_path}")
        if "error" in result:
            print(f"[MAIN] Error: {result['error']}")

    except Exception as e:
        print(f"[MAIN] Error during simulation: {str(e)}")

    finally:
        session.close()

if __name__ == "__main__":
    main()