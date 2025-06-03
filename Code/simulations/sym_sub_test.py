from Code.core.simulation import BaseSimulation
from Code.converters.rlcg2s import run_rlcg2s
from Code.converters.saver import save_ntwk
from Code.connectors.connector import connect_elements
from Code.vector_fitting.vector_fitting import run_vector_fitting
from Code.symica.sym_spice import run_symspice


class SymSubTest(BaseSimulation):
    def run(self) -> None:
        # Шаг 1: Запуск Talgat
        self.structure.run_talgat(self.current_run)

        # Шаг 2: Преобразование RLGC в S-параметры
        ntwk_list = run_rlcg2s(self.structure, self.current_run, return_networks=True)

        # Шаг 3: Соединение сетей
        if ntwk_list:
            combined_ntwk = connect_elements(ntwk_list, self.structure.struct_name, self.current_run)

        # Шаг 4: Векторная аппроксимация
        run_vector_fitting(self.structure.struct_name, self.structure.num_ports)

        # Шаг 5: Запуск Symica
        run_symspice("SymSubTest")