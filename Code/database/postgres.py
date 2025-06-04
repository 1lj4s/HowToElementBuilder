# команды для сmd
# sc query postgresql-x64-17 # статус
# net stop postgresql-x64-17 # стоп сервер
# net start postgresql-x64-17 # старт сервер
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import skrf as rf
import json
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import numpy as np
import os
from tqdm import tqdm  # для прогресс-бара

# Параметры подключения
DB_URL = f"postgresql://Zhechev:Isqweasd123@26.144.128.68:5432/postgres"
engine = create_engine(DB_URL)

def create_table():
   """Создает таблицу если не существует"""
   with engine.connect() as conn:
      conn.execute(text("""
           CREATE TABLE IF NOT EXISTS s2p_networks (
               id SERIAL PRIMARY KEY,
               filename TEXT NOT NULL UNIQUE,
               metadata JSONB,
               s_params JSONB,
               upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )
       """))
      conn.commit()

def s2p_to_postgres_corrected(filename):
   try:
      network = rf.Network(filename)

      # Преобразуем данные в правильный формат
      s_params = {
         "frequencies": network.f.tolist(),  # Список частот
         "s_db": [
            [network.s_db[:, 0, 0].tolist(), network.s_db[:, 0, 1].tolist()],  # S11, S12
            [network.s_db[:, 1, 0].tolist(), network.s_db[:, 1, 1].tolist()]  # S21, S22
         ],
         "s_deg": [
            [network.s_deg[:, 0, 0].tolist(), network.s_deg[:, 0, 1].tolist()],
            [network.s_deg[:, 1, 0].tolist(), network.s_deg[:, 1, 1].tolist()]
         ]
      }

      # Запись в PostgreSQL
      with engine.connect() as conn:
         conn.execute(text("""
               INSERT INTO s2p_networks (filename, metadata, s_params)
               VALUES (:filename, :metadata, :s_params)
           """), {
            "filename": filename,
            "metadata": json.dumps({"ports": network.nports}),
            "s_params": json.dumps(s_params)
         })
         conn.commit()
      print(f"Файл {filename} успешно загружен в PostgreSQL!")
   except Exception as e:
      print(f"Ошибка: {e}")


def process_s2p_file(filepath):
   """Обрабатывает один s2p файл и возвращает данные для БД"""
   try:
      net = rf.Network(filepath)
      return {
         "filename": os.path.basename(filepath),
         "metadata": {
            "ports": net.nports,
            "min_freq_hz": float(net.f[0]),
            "max_freq_hz": float(net.f[-1]),
            "points": len(net.f)
         },
         "s_params": {
            "frequencies": net.f.tolist(),
            "s_db": net.s_db.tolist(),  # В формате [n_freq, n_ports_out, n_ports_in]
            "s_deg": net.s_deg.tolist()
         }
      }
   except Exception as e:
      print(f"Ошибка обработки {filepath}: {str(e)}")
      return None


def upload_folder_to_db(folder_path):
   """Загружает все s2p файлы из папки в БД"""
   create_table()  # Убедимся, что таблица с правильной структурой существует

   s2p_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.s2p')]

   if not s2p_files:
      print("В папке не найдено .s2p файлов")
      return

   print(f"Найдено {len(s2p_files)} .s2p файлов для загрузки")

   for filename in tqdm(s2p_files, desc="Загрузка файлов"):
      filepath = os.path.join(folder_path, filename)
      data = process_s2p_file(filepath)

      if data:
         try:
            with engine.connect() as conn:
               # Упрощенный запрос без upload_time
               conn.execute(text("""
                       INSERT INTO s2p_networks (filename, metadata, s_params)
                       VALUES (:filename, :metadata, :s_params)
                       ON CONFLICT (filename) DO UPDATE
                       SET metadata = EXCLUDED.metadata,
                           s_params = EXCLUDED.s_params
                   """), {
                  "filename": data["filename"],
                  "metadata": json.dumps(data["metadata"]),
                  "s_params": json.dumps(data["s_params"])
               })
               conn.commit()

         except Exception as e:
            print(f"Ошибка загрузки {filename} в БД: {str(e)}")

def check_table_exists():
   try:
      with engine.connect() as conn:
         # Проверяем существование таблицы в системном каталоге PostgreSQL
         result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM pg_tables
                    WHERE schemaname = 'public'
                    AND tablename = 's2p_networks'
                )
            """))
         exists = result.scalar()
         return exists
   except Exception as e:
      print(f"Ошибка при проверке таблицы: {e}")
      return False

def recreate_table():
   with engine.connect() as conn:
      conn.execute(text("DROP TABLE IF EXISTS s2p_networks"))
      conn.commit()
   create_table()


def find_and_display_s_params_corrected(filename):
   """Правильное отображение S-параметров для вашего формата данных"""
   with engine.connect() as conn:
      result = conn.execute(
         text("SELECT s_params FROM s2p_networks WHERE filename = :filename"),
         {"filename": filename}
      )

      row = result.fetchone()

      if not row:
         print(f"Файл {filename} не найден в базе данных")
         return

      s_params = row[0]

      try:
         freq = np.array(s_params['frequencies'])
         s_db = np.array(s_params['s_db'])

         # Правильное обращение к S-параметрам:
         # s_db[freq_index, port_out, port_in]
         s11 = s_db[:, 0, 0]  # S11
         s21 = s_db[:, 1, 0]  # S21

         plt.figure(figsize=(12, 6))

         # График S11
         plt.subplot(1, 2, 1)
         plt.plot(freq / 1e9, s11)
         plt.title("S11 (dB)")
         plt.xlabel("Частота (ГГц)")
         plt.ylabel("Амплитуда (dB)")
         plt.grid(True)

         # График S21
         plt.subplot(1, 2, 2)
         plt.plot(freq / 1e9, s21)
         plt.title("S21 (dB)")
         plt.xlabel("Частота (ГГц)")
         plt.ylabel("Амплитуда (dB)")
         plt.grid(True)

         plt.tight_layout()
         plt.show()

      except Exception as e:
         print(f"Ошибка при построении графика: {str(e)}")
         print(f"Размерности: freq={freq.shape}, s_db={s_db.shape}")


def plot_comparison(db_filename, file_path):
   # --- 1. Загрузка из базы данных ---
   with engine.connect() as conn:
      result = conn.execute(
         text("SELECT s_params FROM s2p_networks WHERE filename = :filename"),
         {"filename": db_filename}
      )
      row = result.fetchone()
      if not row:
         print(f"Файл {db_filename} не найден в базе данных")
         return
      s_params_db = row[0]

   freq_db = np.array(s_params_db['frequencies'])
   s_db = np.array(s_params_db['s_db'])  # [n_freq, 2, 2]
   s11_db = s_db[:, 0, 0]
   s21_db = s_db[:, 1, 0]

   # --- 2. Загрузка из локального файла ---
   net_file = rf.Network(file_path)
   freq_file = net_file.f
   s11_file = net_file.s_db[:, 0, 0]
   s21_file = net_file.s_db[:, 1, 0]

   # --- 3. Построение графиков ---
   plt.figure(figsize=(7, 6))

   # S11
   # plt.subplot(1, 2, 1)
   plt.plot(freq_db / 1e9, s11_db, label=f"DB: {db_filename}", linestyle='--')
   plt.plot(freq_file / 1e9, s11_file, label=f"File: {os.path.basename(file_path)}")
   plt.plot(freq_db / 1e9, s21_db, label=f"DB: {db_filename}", linestyle='--')
   plt.plot(freq_file / 1e9, s21_file, label=f"File: {os.path.basename(file_path)}")
   plt.title("S (dB)")
   plt.xlabel("Частота (ГГц)")
   plt.ylabel("Амплитуда (dB)")
   plt.grid(True)
   plt.legend()

   # S21
   # plt.subplot(1, 2, 2)
   # plt.plot(freq_db / 1e9, s21_db, label=f"DB: {db_filename}", linestyle='--')
   # plt.plot(freq_file / 1e9, s21_file, label=f"File: {os.path.basename(file_path)}")
   # plt.title("S21 (dB)")
   # plt.xlabel("Частота (ГГц)")
   # plt.ylabel("Амплитуда (dB)")
   # plt.grid(True)
   # plt.legend()

   plt.tight_layout()
   plt.show()

# if check_table_exists():
#    print("Таблица существует!")
# else:
#    print("Таблица не существует. Создаём...")

# Затем загружаем файл

# create_table()
# s2p_to_postgres_corrected("MBEND_50_40.s2p")
# find_and_display_s_params_corrected("MBEND_50_50.s2p")

# recreate_table()
# folder_path = r"C:\Users\ZYS\PycharmProjects\LaunchTalgat\MBEND"
# upload_folder_to_db(folder_path)


# plot_comparison(
#     db_filename="MLIN_10.0_450.0_.s2p",
#     file_path=r"C:\Users\ZYS\PycharmProjects\HowToElementBuilder\Code\Files\sym\MLIN_test.s2p"
# )