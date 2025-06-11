from talgat.talgatsession import TalgatSession
from rlcg2s.rlcg2s import RLGC2SConverter
from vectorfitting.vectorfitting import SParamProcessor
import tempfile
import os
import time

class Simulation_Handler():
    """
    Main handler, that runs simulation stages in order,  depending on structure and it's params
    """
    def __init__(self, paths: dict, struct_name: str, struct: dict, subst: dict, simul: dict):
        self.paths = paths
        self.struct_name = struct_name
        self.struct_params = struct
        self.subst_params = subst
        self.sim_params = simul
        print("Simulation_Hundler started successfully")

    def run_simulation(self):
        if self.struct_params["MODELTYPE"] == "2D_Quasistatic":
            shared_code = open(os.path.join(self.paths["talgat_code"], "shared.py"), encoding="utf-8").read()
            session = TalgatSession(self.paths["talgat_exe"])
            script_code = open(os.path.join(self.paths["talgat_code"], f"{self.struct_name}.py"), encoding="utf-8").read()
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as tmp:
                tmp.write(shared_code)
                shared_path = tmp.name

            session.proc.stdin.write(f"exec(open(r'''{shared_path}''').read())\n")
            session.proc.stdin.flush()

            params = self.struct_params.copy()
            params.update(self.subst_params)
            params.update(self.sim_params)
            start_talgat = time.time()
            result = session.run_script(params, script_code)
            print(f"Completed TALGAT simulation in {time.time() - start_talgat:.2f} sec")

            if "Z0" not in params.keys():
                print(f"Warning, can't find Z0 for '{self.struct_name}', using default 50 Ohm")
                params.update({"Z0":50})

            # Convert RLGC to S-parameters
            converter = RLGC2SConverter(params, [result])
            s_params, rlgc_struct = converter.convert()
            print(f"S-params shape for {self.struct_name}: {s_params.shape}")



            # Create SParamProcessor
            processor = SParamProcessor(
                s_params=s_params,
                freqs=self.sim_params['freq_range'],
                z0=params['Z0'],
                name=f"{self.struct_name}"
            )
        else:
            raise NotImplementedError(f'Model type "{self.struct_params["MODELTYPE"]}" for "{self.struct_name}" not implemented yet')

        # Optionally perform vector fitting
        if self.sim_params['do_vector_fitting']:
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
            processor.perform_vector_fitting(**params['vf_params'])

            subcircuit = processor.generate_subcircuit(
                fitted_model_name=f"{self.struct_name}_equiv_no_ref",
                create_reference_pins=False
            )
            print("Vector fitting performed")



if __name__ == "__main__":
    #results = run_all()
    print("Can't run core without main.py")