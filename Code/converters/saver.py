import numpy as np
import skrf
import os

def save_to_snp(s_params, freq, filename, mode='save'):
    """
    Сохраняет S-параметры в файл формата Touchstone (.sNp для N-портовых систем).
    """
    n_ports = s_params.shape[0]
    expected_ext = f'.s{n_ports}p'

    # Обновляем имя файла с правильным расширением
    base, ext = os.path.splitext(filename)
    if ext.lower() != expected_ext:
        print(f"Предупреждение: ожидалось расширение {expected_ext}, получено {ext}")
        filename = base + expected_ext

    # Переставляем оси: (n, n, M) -> (M, n, n)
    s = np.moveaxis(s_params, 2, 0)

    # Создаем объект Frequency и Network
    frequency = skrf.Frequency.from_f(freq, unit='Hz')
    ntwk = skrf.Network(frequency=frequency, s=s, name=os.path.basename(base))

    if mode == 'save':
        ntwk.write_touchstone(filename=base)
        print(f"Файл {filename} успешно сохранён")
        return None
    elif mode == 'return':
        return ntwk
    else:
        raise ValueError("mode must be either 'save' or 'return'")

def save_ntwk(ntwk, directory, struct_name, current_run):
    """
    Сохраняет Network объект в файл Touchstone в указанную директорию
    с именем struct_name_current_run.sNp.
    """
    os.makedirs(directory, exist_ok=True)
    num_ports = ntwk.number_of_ports
    filename = f"{struct_name}_{current_run}.s{num_ports}p"
    filepath = os.path.join(directory, filename)

    # ✔️ Надёжное удаление расширения
    filepath_no_ext, _ = os.path.splitext(filepath)

    ntwk.write_touchstone(filepath_no_ext)
    print(f"Сохранён объединённый файл: {filepath}")
    return os.path.basename(filepath)