import skrf as rf
from pathlib import Path
import re
from typing import List, Union, Dict
from sqlalchemy import create_engine, text
import numpy as np
import os

from Code.database.plotdata import plot_networks

# Database connection parameters
DB_USER = os.getenv("DB_USER", "Zhechev")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Isqweasd123")
DB_HOST = os.getenv("DB_HOST", "26.144.128.68")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(DB_URL)

import re
from typing import Dict, List

def parse_element_info(table_name: str) -> Dict:
    """Извлекает и парсит файл описания элемента из таблицы 'info'."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT s_params ->> 'raw_text' FROM info WHERE filename = :filename"),
            {"filename": f"{table_name.upper()}.txt"}
        )
        content = result.scalar()

    if not content:
        raise ValueError(f"Описание для {table_name} не найдено в БД")
    """Автоматически парсит info-файл, определяя параметры без хардкодинга."""
    result = {
        "fixed_params": {},
        "variable_params": {},
        "freq_range": {"start": 0.1e9, "stop": 67e9, "step": 0.2e9}  # Фиксированные значения
    }

    # Парсинг постоянных параметров (всё что между "Постоянные параметры" и "Диапазон частот")
    fixed_section = re.search(r"Постоянные параметры.*?:(.*?)(?:Диапазон частот|$)", content, re.DOTALL)
    if fixed_section:
        for param_match in re.finditer(r"([^=;]+)\s*=\s*([^;]+)", fixed_section.group(1)):
            param_name = param_match.group(1).strip().upper()
            param_value = param_match.group(2).strip().replace(',', '.')
            if param_name == "ER":
                param_name = "ER1"
            elif param_name == "TAN":
                param_name = "TD1"
            try:
                if param_name in ["T", "H"]:
                    result["fixed_params"][param_name] = float(param_value)*1e-6
                else:
                    result["fixed_params"][param_name] = float(param_value)
            except ValueError:
                result["fixed_params"][param_name] = param_value  # Оставляем строкой если не число

    # Парсинг переменных параметров (строки после "Диапазон параметров")
    variable_section = re.search(r"Диапазон параметров.*?:\s*(.*?)(?:\n\n|$)", content, re.DOTALL)
    if variable_section:
        for line in variable_section.group(1).split('\n'):
            if '=' in line:
                param_name = line.split('=')[0].strip()
                values_str = line.split('=')[1].strip()
                values = [float(v.replace(',', '.').strip()) for v in values_str.split(',')]
                if param_name.lower() in ["w", "w1", "w2", "w3", "w4", "s", "l"]:
                    result["variable_params"][param_name] = [val*1e-6 for val in values]
                else:
                    result["variable_params"][param_name] = values

    return result

def get_sparams_data(path: Union[str, Path], name: str, x: int, y: int, z: int = None,num_ports: int = 2, table_name: str = None, return_network: bool = False) -> List[Union[str, rf.Network]]:
    """
    Retrieves .snp files or skrf.Network objects: one from filesystem (NAME.snp) and one from database (NAME_X_Y.snp).

    Args:
        path: Path to a file or directory containing NAME.snp (e.g., symout.snp).
        name: Base name for the files (e.g., 'symout' or 'MLIN').
        x: Integer for X in NAME_X_Y.snp (database file).
        y: Integer for Y in NAME_X_Y.snp (database file).
        table_name: Database table name containing NAME_X_Y.snp data.
        return_network: If True, returns skrf.Network objects; if False, returns file paths.

    Returns:
        List of file paths (str) or skrf.Network objects for matching files.
        :param z:
    """
    result = []
    name = name.upper()
    info = parse_element_info(table_name)
    print("info: \n", info)


    # 1. Retrieve NAME.snp from filesystem
    path = Path(path)
    file_pattern = rf'^{name}\.s\d+p$'
    if path.is_file() and re.match(file_pattern, path.name, re.IGNORECASE):
        if return_network:
            try:
                result.append(rf.Network(str(path)))
            except Exception as e:
                print(f"Error processing {path}: {str(e)}")
        else:
            result.append(str(path))
    elif path.is_dir():
        for p in path.iterdir():
            if p.is_file() and re.match(file_pattern, p.name, re.IGNORECASE):
                if return_network:
                    try:
                        result.append(rf.Network(str(p)))
                    except Exception as e:
                        print(f"Error processing {p}: {str(e)}")
                else:
                    result.append(str(p))

    # 2. Retrieve NAME_X_Y.snp from database
    if y == None and z == None:
        db_filename = f"{name}_{x}.s{num_ports}p"
    elif y != None and z == None:
        db_filename = f"{name}_{x}_{y}.s{num_ports}p"
    else:
        db_filename = f"{name}_{x}_{y}_{z}.s{num_ports}p"
    try:
        with engine.connect() as conn:
            query = text(f"""
                SELECT s_params, metadata
                FROM {table_name}
                WHERE filename = :filename
            """)
            result_db = conn.execute(query, {"filename": db_filename})
            row = result_db.fetchone()

            if row:
                s_params, metadata = row  # Already dictionaries due to JSONB
                if return_network:
                    # Construct skrf.Network from database data
                    net = rf.Network()
                    net.f = s_params['frequencies']
                    nports = metadata['ports']
                    s_data = np.zeros((len(net.f), nports, nports), dtype=complex)
                    for i in range(nports):
                        for j in range(nports):
                            s_db = np.array(s_params[f"s{i+1}{j+1}_db"])
                            s_deg = np.array(s_params[f"s{i+1}{j+1}_deg"])
                            s_data[:, i, j] = 10 ** (s_db / 20) * np.exp(1j * np.deg2rad(s_deg))
                    net.s = s_data
                    net.name = db_filename
                    result.append(net)
                else:
                    result.append(db_filename)
            else:
                print(f"File {db_filename} not found in table {table_name}")
    except Exception as e:
        print(f"Error retrieving {db_filename} from database: {str(e)}")

    if not result:
        print(f"No matching .snp files found for {name} in filesystem or {db_filename} in database")

    return result, info


if __name__ == "__main__":

    # Get skrf.Network objects
    networks = get_sparams_data(path=r"D:\HowToElementBuilder\Code\Files\symout", name="MLIN", x=100, y=500,
                                table_name="mlin", return_network=True)


    #ntw_model, ntw_true = networks
    #ntw_model = rf.Network(r"D:\HowToElementBuilder\Code\Files\snp\MLIN.s2p")
    print(networks)
    #print(ntw_model)
    plot_networks(networks[0], networks[1])