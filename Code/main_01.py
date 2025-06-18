import time
import json
import numpy as np
from config import CONFIG
from MoM2D.MoM2Dsession import MoM2DSession
from rlcg2s.rlcg2s import RLGC2SConverter
from vectorfitting.vectorfitting import SParamProcessor
from symica.symicanetlist import SymicaNetlist
from symica.symicasession import SymicaSession
import tempfile
import os


def run_all():
    exe_path = r"C:\Program Files\MoM2D 2021\PythonClient.exe"
    symica_exe_path = r"C:\Program Files\Symica\bin\symspice.exe"
    working_dir = "E:/Saves/pycharm/SubprocessTest/symica"

    # Load shared.py once
    shared_code = open("MoM2D/shared.py", encoding="utf-8").read()
    session = MoM2DSession(exe_path)
    symica_session = SymicaSession(symica_exe_path, working_dir)
    netlist_gen = SymicaNetlist(working_dir)

    # Write shared.py to a temporary file
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as tmp:
        tmp.write(shared_code)
        shared_path = tmp.name

    session.proc.stdin.write(f"exec(open(r'''{shared_path}''').read())\n")
    session.proc.stdin.flush()

    all_results = {}

    for struct_name, struct_conf in CONFIG.items():
        print(f"Running structure: {struct_name}")
        script_code = open(f"MoM2D/{struct_name}.py", encoding="utf-8").read()

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

            start_MoM2D = time.time()
            result = session.run_script(params, script_code)
            print(f"Completed MoM2D simulation in {time.time() - start_MoM2D:.2f} sec")

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

            # Optionally perform vector fitting and generate subcircuit
            subcircuit_text = None
            if params['do_vector_fitting']:
                processor.perform_vector_fitting(**params['vf_params'])
                processor.generate_subcircuit(
                    fitted_model_name=f"{struct_name}_equiv_no_ref",
                    create_reference_pins=False
                )
                print(f"\nSubcircuits for {struct_name}_{len(struct_results) + 1}:")
                for subcircuit_name, text in processor.get_subcircuits().items():
                    print(f"\n--- {subcircuit_name} ---")
                    print(text)
                    subcircuit_text = text

            # Run SymSpice simulation
            output_filename = os.path.join(working_dir, "Files", "sym", f"{struct_name}_test.s2p")
            if subcircuit_text:
                # Use CustomCir for subcircuit
                netlist = netlist_gen.generate_netlist(
                    simulation_type="CustomCir",
                    structure_name=struct_name,
                    num_ports=2,  # Adjust based on your structure
                    subcircuit_text=subcircuit_text
                )
            else:
                # Use SymSnpTest for S-parameters
                # Assume S-parameters are saved to a temporary file
                with tempfile.NamedTemporaryFile("w", delete=False, suffix=".s2p",
                                                 dir=os.path.join(working_dir, "Files", "snp")) as tmp_snp:
                    # This is a placeholder; you need to write s_params to tmp_snp
                    # For now, assume an existing .s2p file
                    input_file = os.path.join(working_dir, "Files", "snp", f"{struct_name}_input.s2p")
                    netlist = netlist_gen.generate_netlist(
                        simulation_type="SymSnpTest",
                        structure_name=struct_name,
                        num_ports=2,  # Adjust based on your structure
                        input_file=input_file
                    )

            start_symica = time.time()
            symica_result = symica_session.run_netlist(netlist, output_filename)
            print(f"Completed SymSpice simulation in {time.time() - start_symica:.2f} sec")
            print(f"SymSpice result: {symica_result}")

            struct_results.append({
                "params": params,
                "s_params": s_params,
                "rlgc": rlgc_struct,
                "processor": processor,
                "symica_result": symica_result
            })

        all_results[struct_name] = struct_results

    # Clean up temporary file
    os.remove(shared_path)
    session.close()
    # symica_session.close()

    return all_results


if __name__ == "__main__":
    start = time.time()
    results = run_all()
    print("All simulations completed.")
    print(f"Completed FULL simulation in {time.time() - start:.2f} sec")