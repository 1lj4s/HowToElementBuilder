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
    if table_name == "mtaper": #как исправят название нужно будет убрать это
        table_name = "mmataper"
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
        "variable_params": {}
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
            if "количество" in line:
                continue
            if '=' in line:
                param_name = line.split('=')[0].strip().upper()
                values_str = line.split('=')[1].strip()
                values = [float(v.replace(',', '.').strip()) for v in values_str.split(',')]
                if param_name.lower() in ["w", "w1", "w2", "w3", "w4", "s", "l"]:
                    result["variable_params"][param_name] = [val*1e-6 for val in values]
                else:
                    result["variable_params"][param_name] = values

    return result

def gen_file_name(table_name: str, params: dict, info_data: dict, num_ports, sub) -> str:
    """
    Генерирует имя файла для запроса в БД на основе:
    - table_name: имя таблицы (например, 'mlin')
    - params: параметры из config.py
    - info_data: распарсенные данные из info-файла
    """
    # Базовое имя (например, "MLIN")
    struct = table_name.upper()
    if table_name == "mtaper": #как исправят название нужно будет убрать это
        struct == "MMTAPER"

    if sub == None:
        # Общий случай для всех элементов
        if struct == "MXCLIN":
            parts = [f"M{len(params['W'])}CLIN"]
        else:
            parts = [struct]

        # Добавляем параметры в порядке их упоминания в variable_params
        for param_name in info_data['variable_params'].keys():
            # Маппинг названий параметров (а было бы везде одинаково не пришлось бы так делать)
            config_key = param_name
            if param_name == 'L':
                config_key = 'length'  # Специальный случай для длины
            elif param_name == 'R':
                if table_name != "mcurve":
                    config_key = 'Ro'
            elif param_name == 'THETA':
                config_key = 'Theta'
            elif param_name == 'ANG':
                config_key = 'Angle'

            if config_key in params:
                #if struct in ["MCLIN", "MCFIL", "MXCLIN"] and config_key in ["W", "S"]:
                if isinstance(params[config_key], list):
                    value = params[config_key][0]
                else:
                    value = params[config_key]
                if config_key not in ['Theta', 'Angle']:
                    parts.append(str(int(value * 1e6)))
                else:
                    parts.append(str(int(value)))
            else:
                print(f"{config_key} not in params!")
        return f"{'_'.join(parts)}.s{num_ports}p"
    else:
        return f"{struct}_{int(params['W']*1e6)}_{int(params['length']*1e6)}_{sub}.s{num_ports}p"






def get_sparams_data(path: Union[str, Path], name: str, params, num_ports: int = 2, return_network: bool = False, sub = None):
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
    table_name = name.lower()
    if sub == None:
        info = parse_element_info(table_name)
        print(info)
    else:
        info = None

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

    db_filename = gen_file_name(table_name,params, info, num_ports, sub)
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
                print(f"Comparing with {db_filename} from database")
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