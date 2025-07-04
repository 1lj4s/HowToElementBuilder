
import time

from matplotlib.style.core import available

# import json
# import numpy as np
from config import STRUCTURES, SUBSTRATES, SIMULATIONS
from talgat.talgatsession import TalgatSession
from rlcg2s.rlcg2s import RLGC2SConverter
from vectorfitting.vectorfitting import SParamProcessor
import tempfile
import os
import core

def gen_path():
    paths = {
        "main": os.path.dirname(os.path.abspath(__file__)),
        "talgat_exe": r"C:\Program Files\TALGAT 2021\PythonClient.exe",
        "talgat_code": os.path.join(os.path.dirname(os.path.abspath(__file__)), "talgat"),
        "shared": None
    }
    # try:
    #     shared_code = open(os.path.join(paths["main"], "talgat", "shared.py"), encoding="utf-8").read()
    #     with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as tmp:
    #         tmp.write(shared_code)
    #         shared_path = tmp.name
    # except Exception as ex:
    #     print(f"Cant create temp file: {ex}")
    #     quit()
    # paths.update({"shared": shared_path})
    return paths


def run_all():
    shared_code = open(os.path.join(main_path, "talgat", "shared.py"), encoding="utf-8").read()
    session = TalgatSession(talgat_path)

    # Write shared.py to a temporary file
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as tmp:
        tmp.write(shared_code)
        shared_path = tmp.name

    session.proc.stdin.write(f"exec(open(r'''{shared_path}''').read())\n")
    session.proc.stdin.flush()

    all_results = {}

    for struct_name, struct_conf in CONFIG.items():
        print(f"Running structure: {struct_name}")
        script_code = open(os.path.join(main_path, "talgat", f"{struct_name}.py"), encoding="utf-8").read()

        struct_results = []
        for params in struct_conf:
            # Add default vector fitting flag and parameters if not specified
            params = params.copy()  # Avoid modifying original CONFIG
            params.setdefault('do_vector_fitting', False)
            params.setdefault('vf_params', {
                'n_poles_init_real': 3,
                'n_poles_init_cmplx': 6,
                'n_poles_add': 5,
                'model_order_max': 100,
                'iters_start': 3,
                'iters_inter': 3,
                'iters_final': 5,
                'target_error': 0.01,
                'alpha': 0.03,
                'gamma': 0.03,
                'nu_samples': 1.0,
                'parameter_type': 's'
            })

            start_talgat = time.time()
            result = session.run_script(params, script_code)
            print(f"Completed TALGAT simulation in {time.time() - start_talgat:.2f} sec")


            # Convert RLGC to S-parameters
            converter = RLGC2SConverter(params, [result])
            s_params, rlgc_struct = converter.convert()
            print(f"S-params shape for {struct_name}: {s_params.shape}")

            # Create SParamProcessor
            processor = SParamProcessor(
                s_params=s_params,
                freqs=params['freq_range'],
                z0=params['Z0'],
                name=f"{struct_name}_{len(struct_results) + 1}"
            )

            # Optionally perform vector fitting
            if params['do_vector_fitting']:
                processor.perform_vector_fitting(**params['vf_params'])

                processor.generate_subcircuit(
                    fitted_model_name=f"{struct_name}_equiv_no_ref",
                    create_reference_pins=False
                )
                # processor.generate_subcircuit(
                #     fitted_model_name=f"{struct_name}_equiv_with_ref",
                #     create_reference_pins=True
                # )
                # print(f"\nSubcircuits for {struct_name}_{len(struct_results) + 1}:")
                # for subcircuit_name, subcircuit_text in processor.get_subcircuits().items():
                #     print(f"\n--- {subcircuit_name} ---")
                #     print(subcircuit_text)
            struct_results.append({
                "params": params,
                "s_params": s_params,
                "rlgc": rlgc_struct,
                "processor": processor
            })


        all_results[struct_name] = struct_results

    # Clean up temporary file
    os.remove(shared_path)
    session.close()

    return all_results

if __name__ == "__main__":
    #print("Select structure name")
    #Цикл для  ожидания ввода названия структуры
    #TODO реализовать возможность ввода нескольких структур
    available_structs = ["M1LIN", "M2LIN", "MNLIN"]
    print("Available structures:", ', '.join(STRUCTURES))
    while True:
        selected_struct = input("Type structure name or exit: ")
        if selected_struct in STRUCTURES.keys():
            if selected_struct not in available_structs:
                print("This structure not implemented yet, please select from", ', '.join(available_structs))
            else:
                break
        elif selected_struct == "exit":
            quit()
        else:
            print("Invalid structure, select from available ones")
            print("Available structures:", ', '.join(STRUCTURES))
    paths = gen_path()
    start = time.time()
    print("Selected structure - ", selected_struct)
    subst = SUBSTRATES[STRUCTURES[selected_struct]["SUBSTRATE"]]
    sim_param = SIMULATIONS[STRUCTURES[selected_struct]["SIMULATION"]]
    handler = core.Simulation_Handler(paths, selected_struct, STRUCTURES[selected_struct], subst, sim_param)
    handler.run_simulation()
    #results = run_all()
    #print("All simulations completed.")
    #print(f"Completed FULL simulation in {time.time() - start:.2f} sec")