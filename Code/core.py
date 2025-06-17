from talgat.talgatsession import TalgatSession
from rlcg2s.rlcg2s import RLGC2SConverter
from vectorfitting.vectorfitting import SParamProcessor
from rlcg2s.process_touchstone import make_one_end_line
import numpy as np
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
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as tmp:
                tmp.write(shared_code)
                shared_path = tmp.name

            session.proc.stdin.write(f"exec(open(r'''{shared_path}''').read())\n")
            session.proc.stdin.flush()

            params = self.struct_params.copy()
            params.update(self.subst_params)
            params.update(self.sim_params)

            if self.struct_name == "MRSTUB2W": #TODO допилить MRSTUB2W
                script_code = open(os.path.join(self.paths["talgat_code"], "M1LIN.py"), encoding="utf-8").read()
                start_talgat = time.time()
                results_mtaper = []
                for i, w in enumerate(range(self.struct_params["W"]/self.struct_params["N"], self.struct_params["W"])):
                    params.update({"W": w, "L": (self.struct_params["L"]/self.struct_params["N"])*i})
                    results_mtaper[i] = session.run_script(params, script_code)
                print(f"Completed TALGAT simulation in {time.time() - start_talgat:.2f} sec")
                print("Performing interpolation")
            elif self.struct_name == "MTAPER":
                script_code = open(os.path.join(self.paths["talgat_code"], "M1LIN.py"), encoding="utf-8").read()
                start_talgat = time.time()
                results_mtaper = []
                for i, w in enumerate(range(self.struct_params["W"] / self.struct_params["N"], self.struct_params["W"])):
                    params.update({"W": w, "L": (self.struct_params["L"] / self.struct_params["N"]) * i})
                    results_mtaper[i] = session.run_script(params, script_code)
                print(f"Completed TALGAT simulation for {self.struct_name} in {time.time() - start_talgat:.2f} sec")
                print("Performing interpolation")
            else:
                if self.struct_name in self.m1lin:
                    script_code = open(os.path.join(self.paths["talgat_code"], "M1LIN.py"),
                                       encoding="utf-8").read()
                elif self.struct_name in self.mnlin:
                    script_code = open(os.path.join(self.paths["talgat_code"], "MNLIN.py"),
                                       encoding="utf-8").read()
                else:
                    script_code = open(os.path.join(self.paths["talgat_code"], f"{self.struct_name}.py"),
                               encoding="utf-8").read()
                start_talgat = time.time()
                result = session.run_script(params, script_code)
                print(f"Completed TALGAT simulation for {self.struct_name} in {time.time() - start_talgat:.2f} sec")


            if "Z0" not in params.keys():
                print(f"Warning, can't find Z0 for '{self.struct_name}', using default 50 Ohm")
                params.update({"Z0":50})

            # Convert RLGC to S-parameters
            if self.struct_name != "MTAPER":
                converter = RLGC2SConverter(params, [result])
                s_params, rlgc_struct = converter.convert()
                print(f"S-params shape for {self.struct_name}: {s_params.shape}")
                match self.struct_name:
                    case "MLSC":
                        s_params = make_one_end_line(s_params=np.moveaxis(s_params, 2, 0), freq=converter.freq_range,
                                                     Z0=params["Z0"], gamma=-1)
                    case "MLEF":
                        s_params = make_one_end_line(s_params=np.moveaxis(s_params, 2, 0), freq=converter.freq_range,
                                             Z0=params["Z0"], gamma=1)
            else:
                for result in results_mtaper:
                    converter = RLGC2SConverter(params, [result])
                    s_params, rlgc_struct = converter.convert()
                    print(f"S-params shape for {self.struct_name}: {s_params.shape}")
                    #TODO Добавить послед соединение s параметров

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
                # Create SParamProcessor
                processor = SParamProcessor(
                    s_params=s_params,
                    freqs=self.sim_params['freq_range'],
                    z0=params['Z0'],
                    name=f"{self.struct_name}"
                )
                processor.perform_vector_fitting(**params['vf_params'])

                subcircuit = processor.generate_subcircuit(
                    fitted_model_name=f"{self.struct_name}_equiv_no_ref",
                    create_reference_pins=False
                )
                print("Vector fitting performed")

            converter.save_to_snp(s_params, filename=os.path.join(self.paths["SNP_DIR"], f"{self.struct_name}"))
        else: #self.struct_params["MODELTYPE"] == "2D_Quasistatic"
            raise NotImplementedError(f'Model type "{self.struct_params["MODELTYPE"]}" for "{self.struct_name}" not implemented yet')

        # Optionally perform vector fitting




if __name__ == "__main__":
    #results = run_all()
    print("Can't run core without main.py")