import subprocess
import os
#import shutil

def run_symspice(scs_file: str, obj_file: str):
    base_dir = os.path.dirname(__file__)
    cir_path = os.path.abspath(os.path.join(base_dir, "..", "Files", "sch", f"{scs_file}.scs"))
    cir_dir = os.path.dirname(cir_path)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    files_dir = os.path.join(project_root, "Files")
    if "Snp" in scs_file:
        input_file = os.path.join(files_dir, "snp", obj_file)
    elif "Sub" in scs_file:
        input_file = os.path.join(files_dir, "cir", obj_file)
    output_dir = os.path.join(files_dir, "sym")
    expected_output = os.path.join(output_dir, obj_file)

    if not os.path.exists(cir_path):
        raise FileNotFoundError(f"Файл {cir_path} не найден")

    with open(cir_path, 'r') as file:
        lines = file.readlines()

        # Поиск и замена строки с NPORT0
        for i, line in enumerate(lines):
            if line.startswith("NPORT0 1 0 2 0 nport file="):
                # Разделяем строку по '=', заменяем часть после '=' на новый путь
                parts = line.split('=', 1)  # Делим только по первому '='
                lines[i] = f'{parts[0]}="{input_file}"\n'  # Добавляем кавычки и перенос строки
            if (("Sub" in scs_file) & line.startswith("sp sp")) | (("Snp" in scs_file) & line.startswith("SPSweep sp")):
                parts = line.rsplit('=', 1)  # Делим только по первому '='
                lines[i] = f'{parts[0]}="{expected_output}"\n'  # Добавляем кавычки и перенос строки

    # Запись изменённого файла
    with open(cir_path, 'w') as file:
        file.writelines(lines)

    os.makedirs(output_dir, exist_ok=True)
    command = [os.path.abspath(r"C:\Program Files\Symica\bin\symspice.exe"), os.path.basename(cir_path)]
    try:
        result = subprocess.run(command, cwd=cir_dir, capture_output=True, text=True, check=True)
        print("======= STDOUT =======")
        print(result.stdout)
        print("\n======= STDERR =======")
        print(result.stderr)
        if os.path.exists(expected_output):
            print(f"\n✅ Результат симуляции скопирован в: {expected_output}")
        else:
            print(f"\n⚠️ Выходной файл {expected_output} не найден. Симуляция могла не создать S-параметры.")
        print(f"\n✅ Симуляция {scs_file} завершена успешно.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при выполнении симуляции {scs_file}. Код ошибки: {e.returncode}")
        print("======= STDERR =======")
        print(e.stderr)
    except FileNotFoundError:
        print("\n❌ Ошибка: symspice не найден. Убедитесь, что он установлен и добавлен в PATH")