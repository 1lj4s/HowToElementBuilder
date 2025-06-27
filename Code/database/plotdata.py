import numpy as np
import matplotlib.pyplot as plt
import skrf as rf


def Smodel(ntw_true, ntw_model):
    if ntw_true.nports != ntw_model.nports:
        raise ValueError(f"Число портов не совпадает: {ntw_true.nports} != {ntw_model.nports}")
    if not np.allclose(ntw_true.f, ntw_model.f):
        raise ValueError("Частотные точки не совпадают")

    S_true = ntw_true.s
    S_model = ntw_model.s
    num_frequencies = S_true.shape[0]
    N = S_true.shape[1]
    errors = np.zeros(num_frequencies)

    for freq in range(num_frequencies):
        error_sum = 0.0
        for i in range(N):
            for j in range(N):
                numerator = np.abs(S_true[freq, i, j] - S_model[freq, i, j])
                denominator = 0.5 * (np.abs(S_true[freq, i, j]) + np.abs(S_model[freq, i, j]))
                if denominator != 0:
                    error_sum += numerator / denominator
        errors[freq] = 100 * error_sum / (N ** 2)

    return errors

def ABSmodel(ntw_true, ntw_model):
    if ntw_true.nports != ntw_model.nports:
        raise ValueError(f"Число портов не совпадает: {ntw_true.nports} != {ntw_model.nports}")
    if not np.allclose(ntw_true.f, ntw_model.f):
        raise ValueError("Частотные точки не совпадают")

    S_true = ntw_true.s
    S_model = ntw_model.s
    num_frequencies = S_true.shape[0]
    N = S_true.shape[1]
    errors = np.zeros(num_frequencies)

    for freq in range(num_frequencies):
        error_sum = 0.0
        for i in range(N):
            for j in range(N):
                numerator = np.abs(np.abs(S_true[freq, i, j]) - np.abs(S_model[freq, i, j]))
                denominator = np.abs(S_model[freq, i, j])
                if denominator != 0:
                    error_sum += numerator / denominator
        errors[freq] = 100 * error_sum / (N ** 2)

    return errors

def FHImodel(ntw_true, ntw_model):
    if ntw_true.nports != ntw_model.nports:
        raise ValueError(f"Число портов не совпадает: {ntw_true.nports} != {ntw_model.nports}")
    if not np.allclose(ntw_true.f, ntw_model.f):
        raise ValueError("Частотные точки не совпадают")

    S_true = ntw_true.s
    S_model = ntw_model.s
    num_frequencies = S_true.shape[0]
    N = S_true.shape[1]
    errors = np.zeros(num_frequencies)

    for freq in range(num_frequencies):
        error_sum = 0.0
        for i in range(N):
            for j in range(N):
                numerator = np.abs(np.angle(S_true[freq, i, j]) - np.angle(S_model[freq, i, j]))
                denominator = np.abs(np.angle(S_model[freq, i, j]))
                if denominator != 0:
                    error_sum += numerator / denominator
        errors[freq] = 100 * error_sum / (N ** 2)

    return errors

def plot_networks(ntw_model, ntw_true):
    if ntw_model.nports != ntw_true.nports:
        raise ValueError(f"Число портов не совпадает: {ntw_model.nports} != {ntw_true.nports}")
    if not np.allclose(ntw_model.f, ntw_true.f):
        ntw_model = ntw_model.interpolate_from_f(ntw_true.f)

    N = ntw_true.nports
    freq_ghz = ntw_true.f / 1e9

    errors = Smodel(ntw_true, ntw_model)

    def prepare_data(s_params):

        return [(20 * np.log10(np.abs(s_params[:, i, j])), np.angle(s_params[:, i, j], deg=True))
                for i in range(N) for j in range(N)]

    true_data = prepare_data(ntw_true.s)
    model_data = prepare_data(ntw_model.s)

    n_plots = N * N * 2  # N^2 * 2 (дБ + фаза)
    n_cols = int(np.ceil(np.sqrt(n_plots)))
    n_rows = int(np.ceil(n_plots / n_cols))

    plt.figure(figsize=(5 * n_cols, 4 * n_rows))
    plot_idx = 1

    for i in range(N):
        for j in range(N):
            plt.subplot(n_rows, n_cols, plot_idx)
            plt.plot(freq_ghz, true_data[i * N + j][0], 'b-', label='Истина')
            plt.plot(freq_ghz, model_data[i * N + j][0], 'r:', label='Модель')
            plt.title(f'S{i + 1}{j + 1} (дБ)', fontsize=10)
            plt.xlabel('Частота (GHz)', fontsize=8)
            plt.ylabel('дБ', fontsize=8)
            plt.legend(fontsize=8)
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.xlim(freq_ghz[0], freq_ghz[-1])
            plot_idx += 1

            plt.subplot(n_rows, n_cols, plot_idx)
            plt.plot(freq_ghz, true_data[i * N + j][1], 'b-', label='Истина')
            plt.plot(freq_ghz, model_data[i * N + j][1], 'r:', label='Модель')
            plt.title(f'S{i + 1}{j + 1} Фаза', fontsize=10)
            plt.xlabel('Частота (GHz)', fontsize=8)
            plt.ylabel('Град.', fontsize=8)
            plt.legend(fontsize=8)
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.xlim(freq_ghz[0], freq_ghz[-1])
            plot_idx += 1

    plt.tight_layout()
    # plt.show()

    # Smodel
    plt.figure(figsize=(8, 4))
    plt.plot(freq_ghz, errors, 'g-', label='Ошибка S-параметров', linewidth=2)
    plt.title('Ошибка S-параметров', fontsize=16)
    plt.xlabel('Частота (GHz)', fontsize=14)
    plt.ylabel('Ошибка', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.4)
    plt.xlim(freq_ghz[0], freq_ghz[-1])
    plt.tick_params(axis='both', labelsize=12)
    plt.tight_layout()
    plt.show()


# Пример использования
if __name__ == "__main__":
    ntw_true_s2p = rf.Network(r'C:\Users\Никита Павлов\САПР\DataBase\MTRACE2\MTRACE2_10_30.s2p')
    ntw_model_s2p = rf.Network(r'C:\Users\Никита Павлов\САПР\DataBase\MTRACE2\MTRACE2_10_40.s2p')

    plot_networks(ntw_model_s2p, ntw_true_s2p)