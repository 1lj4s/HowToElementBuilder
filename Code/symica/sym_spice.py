import subprocess
import os
import shutil

def run_symspice(scs_file: str):
    base_dir = os.path.dirname(__file__)
    cir_path = os.path.abspath(os.path.join(base_dir, "..", "..", "Files", "sch", f"{scs_file}.scs"))
    cir_dir = os.path.dirname(cir_path)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    files_dir = os.path.join(project_root, "Files")
    output_dir = os.path.join(files_dir, "sym")
    expected_output = os.path.join(output_dir, f"{scs_file}.s2p")
    output_destination = os.path.join(output_dir, f"{scs_file}.s2p")

    if not os.path.exists(cir_path):
        raise FileNotFoundError(f"Файл {cir_path} не найден")

    os.makedirs(output_dir, exist_ok=True)
    command = ["symspice", os.path.basename(cir_path)]
    try:
        result = subprocess.run(command, cwd=cir_dir, capture_output=True, text=True, check=True)
        print("======= STDOUT =======")
        print(result.stdout)
        print("\n======= STDERR =======")
        print(result.stderr)
        if os.path.exists(expected_output):
            print(f"\n✅ Результат симуляции скопирован в: {output_destination}")
        else:
            print(f"\n⚠️ Выходной файл {expected_output} не найден. Симуляция могла не создать S-параметры.")
        print(f"\n✅ Симуляция {scs_file} завершена успешно.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при выполнении симуляции {scs_file}. Код ошибки: {e.returncode}")
        print("======= STDERR =======")
        print(e.stderr)
    except FileNotFoundError:
        print("\n❌ Ошибка: symspice не найден. Убедитесь, что он установлен и добавлен в PATH")