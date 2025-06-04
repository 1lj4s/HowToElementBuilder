# File: simulations\sym_sub_test.py
from Code.core.simulation import BaseSimulation
from Code.converters.rlcg2s import run_rlcg2s
from Code.converters.saver import save_ntwk
from Code.connectors.connector import connect_elements
from Code.vector_fitting.vector_fitting import run_vector_fitting
from Code.symica.sym_spice import run_symspice
from Code.core.utils import get_config
from Code.config import FILES_DIR

class SymSubTest(BaseSimulation):
    def run(self) -> None:
        # Load configuration to get active ports
        config_path = os.path.join(FILES_DIR, "json", "simulation_config.json")
        config = get_config(config_path)
        struct_config = config.get(self.structure.struct_name, {})
        ports_config = struct_config.get("ports", [])
        active_ports = len([p for p in ports_config if p == 'port'])

        # Step 1: Run Talgat
        self.structure.run_talgat(self.current_run)

        # Step 2: Convert RLGC to S-parameters
        ntwk_list = run_rlcg2s(self.structure, self.current_run, return_networks=True)

        # Step 3: Combine and terminate networks
        if ntwk_list:
            combined_ntwk = connect_elements(ntwk_list, self.structure.struct_name, self.current_run)

        # Step 4: Vector fitting with active ports
        run_vector_fitting(self.structure.struct_name, active_ports)

        # Step 5: Run Symica
        run_symspice("SymSubTest")