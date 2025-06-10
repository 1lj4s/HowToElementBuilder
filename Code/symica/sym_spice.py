import subprocess
import os
from Code.config import FILES_DIR, FREQUENCY_RANGE
from Code.input.input import SimulationConfigBuilder

def generate_scs_content(simulation_type: str, structure_name: str, current_run: str, num_ports: int,
                         input_file: str = None) -> str:
    """
    Генерирует содержимое .scs файла на основе типа симуляции, имени структуры, текущего запуска и числа портов.

    Args:
        simulation_type (str): Тип симуляции ('SymSnpTest', 'SymSubTest', 'CustomCir').
        structure_name (str): Название структуры (например, 'MLIN', 'MTAPER').
        current_run (str): Имя текущего запуска (например, 'test').
        num_ports (int): Количество портов структуры.
        input_file (str, optional): Путь к входному .cir файлу для CustomCir симуляции.

    Returns:
        str: Содержимое .scs файла.
    """
    # Общие начальные строки
    scs_content = [
        "simulator lang=local",
        "global 0",
        ""
    ]

    # Частотный диапазон из config.py
    freq_start = FREQUENCY_RANGE[0] / 1e9  # в ГГц
    freq_stop = FREQUENCY_RANGE[-1] / 1e9  # в ГГц
    freq_step = (FREQUENCY_RANGE[1] - FREQUENCY_RANGE[0]) / 1e9  # в ГГц
    output_path = os.path.join(FILES_DIR, "sym", f"{structure_name}_{current_run}.s{num_ports}p")

    if simulation_type == "SymSnpTest":
        # Путь к входному .snp файлу
        snp_path = os.path.join(FILES_DIR, "snp", f"{structure_name}_{current_run}.s{num_ports}p")
        # Добавление NPORT
        nport_nodes = " ".join(f"{i + 1} 0" for i in range(num_ports))
        scs_content.append(f"NPORT0 {nport_nodes} nport file=\"{snp_path}\"")
        scs_content.append("")

        # Добавление портов
        for i in range(num_ports):
            scs_content.append(
                f"PORT{i} {i + 1} 0 port r=50 num={i + 1} type=sine rptstart=1 rpttimes=0"
            )
        scs_content.append("")

        # SPSweep для SymSnpTest
        scs_content.append(
            f"SPSweep sp start={freq_start}G stop={freq_stop}G step={freq_step}G file=\"{output_path}\""
        )

    elif simulation_type == "SymSubTest":
        # Путь к входному .cir файлу
        cir_path = os.path.join(FILES_DIR, "cir", f"{structure_name}_{current_run}.cir")
        scs_content.append(f"include \"{cir_path}\"")
        scs_content.append("")

        # Добавление элемента U1
        nodes = " ".join(f"p{i + 1}" for i in range(num_ports))
        scs_content.append(f"U1 {nodes} s_equivalent")
        scs_content.append("")

        # Добавление портов
        for i in range(num_ports):
            scs_content.append(
                f"PORT{i + 1} p{i + 1} 0 port r=50 num={i + 1} type=sine fundname=aaa ampl=0.0001 "
                f"freq=5000000000 data=0 rptstart=1 rpttimes=0 mag=1e-006"
            )
        scs_content.append("")

        # sp для SymSubTest
        scs_content.append(
            f"sp sp start={freq_start}G stop={freq_stop}G dec=401 file=\"{output_path}\""
        )

    elif simulation_type == "CustomCir":
        if not input_file:
            raise ValueError("Для CustomCir требуется указать путь к .cir файлу")
        # Проверка существования входного файла
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Входной файл {input_file} не найден")

        scs_content.append(f"include \"{input_file}\"")
        scs_content.append("")

        # Загрузка параметров структуры
        config_builder = SimulationConfigBuilder(os.path.join(FILES_DIR, "json", "simulation_config.json"))
        structure_params = config_builder.get_structure(structure_name)

        nodes = " ".join(f"p{i + 1}" for i in range(num_ports))
        if structure_name == "TFR":
            rs = structure_params.get("RS", 16)
            w = structure_params.get("W", 50e-6)
            l = structure_params.get("L", 50e-6)
            scs_content.append(f"X1 {nodes} sch RS={rs} W={w:.6e} L={l:.6e}")
        elif structure_name == "MOPEN":
            w = structure_params.get("W", 50e-6)
            msub_params = config_builder.get_structure("MSUB")
            h = msub_params.get("H", 100e-6)
            er = msub_params.get("ER1", 12.9)
            scs_content.append(f"X1 p1 0 sch W={w:.6e} H={h:.6e} ER={er:.2f}")
        elif structure_name == "MSTEP":
            w1 = structure_params.get("W1", 50e-6)
            w2 = structure_params.get("W2", 50e-6)
            msub_params = config_builder.get_structure("MSUB")
            h = msub_params.get("H", 100e-6)
            er = msub_params.get("ER1", 12.9)
            scs_content.append(f"X1 {nodes} sch W1={w1:.6e} W2={w2:.6e} H={h:.6e} ER={er:.2f}")
        else:
            msub_params = config_builder.get_structure("MSUB")
            par1 = msub_params.get("ER1", 5)
            par2 = msub_params.get("T", 1e-6)
            scs_content.append(f"X1 {nodes} sch2 par1={par1:.2f} par2={par2:.6e}")
        scs_content.append("")

        # Добавление портов
        for i in range(num_ports):
            scs_content.append(
                f"PORT{i + 1} p{i + 1} 0 port r=50 num={i + 1} type=sine fundname=aaa ampl=0.0001 "
                f"freq=5000000000 data=0 rptstart=0 mag=1e-006"
            )
        scs_content.append("")

        # sp для CustomCir
        scs_content.append(
            f"sp sp start={freq_start}G stop={freq_stop}G dec=401 file=\"{output_path}\""
        )

    else:
        raise ValueError(f"Неподдерживаемый тип симуляции: {simulation_type}")

    # Добавление DEFAULT_OPTIONS
    if simulation_type == "SymSnpTest":
        scs_content.append("DEFAULT_OPTIONS options tnom=27 temp=27 reltol=1.000000e-03")
    else:
        scs_content.append(
            "DEFAULT_OPTIONS options tnom=27 temp=27 acout=0 fast_spice=0 reltol=1.000000e-003 rawfmt=nutascii"
        )

    return "\n".join(scs_content)

def run_symspice(scs_file: str, obj_file: str, structure_name: str, num_ports: int):
    """
    Запускает Symica сгенерировав .scs файл и выполняет симуляцию.

    Args:
        scs_file (str): Тип симуляции ('SymSnpTest', 'SymSubTest', 'CustomCir').
        obj_file (str): Путь к входному файлу (.cir для CustomCir, имя для других).
        structure_name (str): Название структуры.
        num_ports (int): Количество портов структуры.
    """
    base_dir = os.path.dirname(__file__)
    cir_dir = os.path.join(base_dir, "..", "Files", "sch")
    cir_path = os.path.abspath(os.path.join(cir_dir, f"{scs_file}.scs"))
    output_dir = os.path.join(base_dir, "..", "Files", "sym")
    os.makedirs(cir_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Извлекаем current_run из obj_file
    current_run = "test" if scs_file == "CustomCir" else obj_file.replace(f"{structure_name}_", "").split('.')[0]

    # Генерация содержимого .scs файла
    scs_content = generate_scs_content(
        simulation_type=scs_file,
        structure_name=structure_name,
        current_run=current_run,
        num_ports=num_ports,
        input_file=obj_file if scs_file == "CustomCir" else None
    )

    # Запись .scs файла
    try:
        with open(cir_path, 'w', encoding='utf-8') as file:
            file.write(scs_content)
        print(f"Файл {cir_path} успешно создан")
    except Exception as e:
        print(f"Ошибка при создании файла {cir_path}: {e}")
        return

    # Запуск Symica
    command = [os.path.abspath(r"C:\Program Files\Symica\bin\symspice.exe"), os.path.basename(cir_path)]
    try:
        result = subprocess.run(command, cwd=cir_dir, capture_output=True, text=True, check=True)
        print("======= STDOUT =======")
        print(result.stdout)
        print("\n======= STDERR =======")
        print(result.stderr)
        expected_output = os.path.join(output_dir, f"{structure_name}_{current_run}.s{num_ports}p")
        if os.path.exists(expected_output):
            print(f"\n✅ Результат симуляции сохранен в: {expected_output}")
        else:
            print(f"\n⚠️ Выходной файл {expected_output} не найден")
        print(f"\n✅ Симуляция {scs_file} завершена успешно")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при выполнении симуляции {scs_file}. Код ошибки: {e.returncode}")
        print("======= STDERR =======")
        print(e.stderr)
    except FileNotFoundError:
        print("\n❌ Ошибка: symspice не найден. Убедитесь, что он установлен и добавлен в PATH")

# Пример использования:
if __name__ == "__main__":
    run_symspice("SymSnpTest", "MLIN_test.s2p", "MLIN", 2)