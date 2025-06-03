import skrf
import numpy as np
import matplotlib.pyplot as plt
import os
import logging
from Code.config import FILES_DIR, FREQUENCY_RANGE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_vector_fitting(struct_name: str, num_ports: int, show_plots: bool = True):
    """
    Выполняет векторную аппроксимацию (Vector Fitting) для создания SPICE-модели из S-параметров.

    Args:
        struct_name: Название структуры (например, 'MLIN', 'MTAPER').
        num_ports: Количество портов структуры.
        show_plots: Если True, отображает графики S-параметров.

    Returns:
        None
    """
    snp_path = os.path.join(FILES_DIR, "snp", f"{struct_name}_test.s{num_ports}p")
    cir_path = os.path.join(FILES_DIR, "cir", f"{struct_name}_test.cir")

    try:
        ntwk = skrf.Network(snp_path)
    except FileNotFoundError:
        logger.error(f"Файл {snp_path} не найден!")
        return

    try:
        vf = skrf.VectorFitting(ntwk)
        vf.auto_fit(
            n_poles_init_real=3,
            n_poles_init_cmplx=6,
            n_poles_add=5,
            model_order_max=100,
            iters_start=3,
            iters_inter=3,
            iters_final=5,
            target_error=0.01,
            alpha=0.03,
            gamma=0.03,
            nu_samples=1.0,
            parameter_type='s'
        )

        vf.write_spice_subcircuit_s(cir_path)
        logger.info(f"SPICE-модель сохранена в файл: {cir_path}")

        if show_plots:
            freq = FREQUENCY_RANGE
            plt.figure(figsize=(10, 8))
            for i in range(ntwk.nports):
                for j in range(ntwk.nports):
                    plt.subplot(ntwk.nports, ntwk.nports, i * ntwk.nports + j + 1)
                    ntwk.plot_s_db(m=i, n=j, label=f'Original S{i+1}{j+1}')
                    s_fit = vf.get_model_response(i=i, j=j, freqs=freq)
                    plt.plot(freq, 20 * np.log10(np.abs(s_fit)), label=f'Fitted S{i+1}{j+1}')
                    plt.xlabel('Frequency (GHz)')
                    plt.ylabel('Magnitude (dB)')
                    plt.legend()
                    plt.grid(True)
            plt.tight_layout()
            plt.show()

    except Exception as e:
        logger.error(f"Ошибка при выполнении векторной аппроксимации: {e}")