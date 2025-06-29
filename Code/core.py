from MoM.MoM2Dsession import MoM2DSession
from rlcg2s.rlcg2s import RLGC2SConverter
from vectorfitting.vectorfitting import SParamProcessor
from rlcg2s.process_touchstone import make_one_end_line
from symica.symicasession import SymicaSession
from rlcg2s.matinterp import matrix_interp
from rlcg2s.paramrecalc import mrstubparamrecalc, mcurveparamrecalc
from connectors.connector import connect_sparams
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

        # Пересчет входных параметров для MRSTUB2W и MCURVE. Пока это будет тут)
        if self.struct_name == "MRSTUB2W":
            W1, W2, length = mrstubparamrecalc(self.struct_params)
            self.struct_params.update({"W1": W1, "W2": W2, "length": length})
        elif self.struct_name == "MCURVE":
            length = mcurveparamrecalc(self.struct_params)
            self.struct_params.update({"length": length})

        print("[CORE] Simulation_Hundler started successfully")

    def run_simulation(self):
        if self.struct_params["MODELTYPE"] in ["2D_Quasistatic", "3D_Quasistatic"]:
            if self.struct_params["MODELTYPE"] == "2D_Quasistatic":
                self.model_method = "2D"
            else:
                self.model_method = "3D"
            shared_code = open(os.path.join(self.paths["MoM_code"], f"shared_{self.model_method}.py"), encoding="utf-8").read()
            session = MoM2DSession(self.paths["MoM2D_exe"])
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as tmp:
                tmp.write(shared_code)
                shared_path = tmp.name

            session.proc.stdin.write(f"exec(open(r'''{shared_path}''').read())\n")
            session.proc.stdin.flush()

            params = self.struct_params.copy()
            params.update(self.subst_params)
            params.update(self.sim_params)

            if self.struct_name in ("MTAPER", "MRSTUB2W"):
                script_code = open(os.path.join(self.paths["MoM_code"], f"M1LIN_{self.model_method}.py"), encoding="utf-8").read()
                start_MoM2D = time.time()
                results_mtaper = []
                if self.struct_params["Taper"] == "Linear":
                    W_values = [self.struct_params["W1"] + i * (self.struct_params["W2"] - self.struct_params["W1"]) / (self.struct_params["N"] - 1) for i in range(self.struct_params["N"])]
                elif self.struct_params["Taper"] == "Exponential":
                    W_values = [self.struct_params["W1"] * (self.struct_params["W2"] / self.struct_params["W1"]) ** (i / (self.struct_params["N"] - 1)) for i in range(self.struct_params["N"])]
                for i, W in enumerate(W_values):
                    params.update({
                        "W": W,
                        "length": self.struct_params["length"] / self.struct_params["N2"]
                    })
                    results_mtaper.append(session.run_script(params, script_code)["result"])
                result = matrix_interp(results_mtaper, self.struct_params["N2"])
                print(f"[CORE] Completed MoM2D simulation for {self.struct_name} in {time.time() - start_MoM2D:.2f} sec")
                print(f"[CORE] Interpolation performed for {self.struct_name}")
            else:
                if self.struct_name in self.m1lin:
                    script_code = open(os.path.join(self.paths["MoM_code"], f"M1LIN_{self.model_method}.py"),
                                       encoding="utf-8").read()
                elif self.struct_name in self.mnlin:
                    script_code = open(os.path.join(self.paths["MoM_code"], f"MNLIN_{self.model_method}.py"),
                                       encoding="utf-8").read()
                else:
                    script_code = open(os.path.join(self.paths["MoM_code"], f"{self.struct_name}_{self.model_method}.py"),
                               encoding="utf-8").read()
                start_MoM2D = time.time()
                result = session.run_script(params, script_code)
                print(f"[CORE] Completed MoM2D simulation for {self.struct_name} in {time.time() - start_MoM2D:.2f} sec")


            if "Z0" not in params.keys():
                print(f"[CORE] Warning, can't find Z0 for '{self.struct_name}', using default 50 Ohm")
                params.update({"Z0":50})

            # Convert RLGC to S-parameters
            if self.struct_name not in ("MTAPER", "MRSTUB2W"):
                converter = RLGC2SConverter(params, [result])
                s_params, rlgc_struct = converter.convert()
                print(f"[CORE] S-params shape for {self.struct_name}: {s_params.shape}")
                match self.struct_name:
                    case "MLSC":
                        s_params = make_one_end_line(s_params=np.moveaxis(s_params, 2, 0), freq=converter.freq_range,
                                                     Z0=params["Z0"], gamma=-1)
                        s_params = np.moveaxis(s_params, 0, 2)
                    case "MLEF":
                        s_params = make_one_end_line(s_params=np.moveaxis(s_params, 2, 0), freq=converter.freq_range,
                                             Z0=params["Z0"], gamma=1)
                        s_params = np.moveaxis(s_params, 0, 2)
                print(f"[CORE] New S-params shape for {self.struct_name}: {s_params.shape}")
            else:
                s_params_list = []
                for res in result:
                    converter = RLGC2SConverter(params, [{'result': res}])
                    s_params, rlgc_struct = converter.convert()
                    s_params_list.append(s_params)
                print(f"[CORE] S-params list length for {self.struct_name}: {len(s_params_list)}")
                print(f"[CORE] Shape of first S-params in list: {s_params_list[0].shape}")
                freqs = self.sim_params['freq_range']
                s_params = connect_sparams(s_params_list, freqs)
                if self.struct_name == "MRSTUB2W":
                    s_params = make_one_end_line(s_params=np.moveaxis(s_params, 2, 0), freq=converter.freq_range,
                                                 Z0=params["Z0"], gamma=1)
                    s_params = np.moveaxis(s_params, 0, 2)

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
                print("[CORE] Vector fitting performed")

            converter.save_to_snp(s_params, filename=os.path.join(self.paths["SNP_DIR"], f"{self.struct_name}"))
        SymSession = SymicaSession(self.paths, self.struct_name, self.struct_params, self.subst_params, self.sim_params)
        if 's_params' in locals():
            netlist_path = SymSession.generate_netlist(self.struct_name, num_ports=s_params.shape[1])
        else:
            netlist_path = SymSession.generate_netlist(self.struct_name, num_ports=self.struct_params['NumPorts'])
        result = SymSession.run_simulation(netlist_path)
        print("[SYMSPICE]", result.get("status", "unknown"))

        if "error" in result:
            print("[SYMSPICE]", result["error"])
        if 's_params' in locals():
            return s_params.shape[1]
        else:
            return self.struct_params['NumPorts']

if __name__ == "__main__":

    print("Can't run core without main.py")