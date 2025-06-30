import time
from config import STRUCTURES, SUBSTRATES, SIMULATIONS, elements_for_subst_check, subst_conditions
import database.postgresql as db
import database.plotdata as plot_db
import os
import core
import numpy as np

def gen_path():
    if os.path.exists(r"C:\Program Files\Talgat 2021\PythonClient.exe"):
        talgat_path = r"C:\Program Files\Talgat 2021\PythonClient.exe"
    elif os.path.exists(r"C:\Program Files\Talgat 2020\PythonClient.exe"):
        talgat_path = r"C:\Program Files\Talgat 2020\PythonClient.exe"
    else:
        while True:
            print("Can't find TALGAT system, please specify path to PythonClient.exe")
            new_path = input()
            if os.path.exists(new_path):
                talgat_path = new_path
                break
    paths = {
        "main": os.path.dirname(os.path.abspath(__file__)),
        "MoM2D_exe": talgat_path,
        "MoM_code": os.path.join(os.path.dirname(os.path.abspath(__file__)), "MoM"),
        "shared": None,
    }
    (paths.update({
        "NETLIST_DIR": os.path.join(paths["main"], "Files", "symnet"),
        "SNP_DIR": os.path.join(paths["main"], "Files","snp"),
        "VERILOG_DIR": os.path.join(paths["main"], "Files", "ver"),
        "SUBCIRCUIT_DIR": os.path.join(paths["main"], "Files", "sub"),
        "OUTPUT_DIR": os.path.join(paths["main"], "Files", "symout"),}))
    return paths

def compare_with_db():
    sub = None
    conntect_to_db = True
    # Определяем суффикс подложки
    if selected_struct in elements_for_subst_check:
        current_W = int(struct_param.get('W', 0) * 1e6)  # конвертируем в микрометры
        current_length = int(struct_param.get('length', 0) * 1e6)

        for sub_type, conditions in subst_conditions.items():
            # Проверяем параметры подложки
            substrate_ok = all(
                np.isclose(subst.get(param, 0), conditions[param])
                for param in ['ER1', 'H', 'T']
            )

            # Проверяем геометрические параметры
            geometry_ok = (
                    current_W in conditions['valid_W'] and
                    current_length in conditions['valid_length']
            )

            if substrate_ok and geometry_ok:
                sub = sub_type
    if sub == None:
        info = db.parse_element_info(selected_struct.lower())

        # Проверка постоянных параметров
        unmatched_params = []
        for param, value in info["fixed_params"].items():
            if not np.isclose(subst[param] * 1e6, info["fixed_params"][param] * 1e6, rtol=0.01):
                print(f"Inconsistency of parameter {param}: {subst[param]} (config) != {value} (info)")
                unmatched_params.append(param)
        if len(unmatched_params) > 0:
            print("Warning! Substrate parameters", ', '.join(unmatched_params), "do not match the parameters in the DB")
            print("S-parameter comparing can be incorrect")

        # Проверка изменяемых параметров
        for parameter, values in info["variable_params"].items():
            #Маппинг названий параметров (а было бы везде одинаково не пришлось бы так делать)
            if parameter == 'L':
                config_key = 'length'  # Специальный случай для длины
            elif parameter == 'R':
                if selected_struct != "MCURVE":
                    config_key = 'Ro'
            elif parameter == 'THETA':
                config_key = 'Theta'
            elif parameter == 'ANG':
                config_key = 'Angle'
            else:
                config_key = parameter

            if config_key in struct_param:
                if selected_struct in ["MCLIN", "MCFIL", "MXCLIN"] and config_key in ["W", "S"]:
                    config_parameter = struct_param[config_key][0]
                else:
                    config_parameter = struct_param[config_key]

                if True not in np.isclose(config_parameter, values, rtol=0.01):
                    print(f"Data for {selected_struct} with parameter {parameter} = {config_parameter} can't be found in DB")
                    return False
            else:
                print(f"Error, parameter {parameter} can't be found in element configuration")
                print("Comparing with DB is impossible")
                return False

    if conntect_to_db:
        networks, info = db.get_sparams_data(path=paths["OUTPUT_DIR"], name=selected_struct,
                                             params=STRUCTURES[selected_struct],
                                             num_ports=num_ports, return_network=True, sub=sub)

        if len(networks) == 2:
            pass
            plot_db.plot_networks(networks[0], networks[1])
            return True
        else:
            print(networks)

if __name__ == "__main__":
    print("[MAIN] Select structure name")
    #Цикл для  ожидания ввода названия структуры
    #TODO реализовать возможность ввода нескольких структур

    available_structs = ["MLIN", "MTRACE2", "MLSC", "MLEF", "MTAPER", "MRSTUB2W", "MCLIN", "MCFIL", "MXCLIN", "MBEND", "MCURVE", "MTEE", "MCROSS", "MXOVER", "MGAPX", "MSTEP", "MOPEN"]
    print("[MAIN] Available structures:", ', '.join(available_structs))
    while True:
        selected_struct = input("[MAIN] Type structure name or exit: ").upper()
        if selected_struct in STRUCTURES.keys():
            if selected_struct not in available_structs:
                print("This structure not implemented yet, please select from", ', '.join(available_structs))
            else:
                break
        elif selected_struct == "exit":
            quit()
        else:
            print("[MAIN] Invalid structure, select from available ones")
            print("[MAIN] Available structures:", ', '.join(available_structs))
    paths = gen_path()

    print("[MAIN] Selected structure - ", selected_struct)
    subst = SUBSTRATES[STRUCTURES[selected_struct]["SUBSTRATE"]]
    sim_param = SIMULATIONS[STRUCTURES[selected_struct]["SIMULATION"]]
    struct_param = STRUCTURES[selected_struct]
    if len(sim_param["freq_range"]) != 335:
        print(f"Warning, number of frequency points is {len(sim_param['freq_range'])} and not equal 335, can't compare with database, continue anyway?")
        while True:
            ans = input("Type Y or N: ")
            if ans.upper() == "Y":
                do_db = False
                break
            elif ans.upper() == "N":
                quit()
            else:
                print("Can't recognise answer")
    else:
        do_db = False
    start = time.time()
    handler = core.Simulation_Handler(paths, selected_struct, STRUCTURES[selected_struct], subst, sim_param)
    handler.m1lin = STRUCTURES["M1LIN_STRUCTS"]
    handler.mnlin = STRUCTURES["MNLIN_STRUCTS"]
    num_ports = handler.run_simulation()
    if selected_struct in ["MLIN", "MTRACE2", "MLSC", "MLEF"]:
        x = int(STRUCTURES[selected_struct]["W"] * 1e6)
        y = int(STRUCTURES[selected_struct]["length"] * 1e6)
        z = None
    elif selected_struct == "MTAPER":
        x = int(STRUCTURES[selected_struct]["W1"] * 1e6)
        y = int(STRUCTURES[selected_struct]["W2"] * 1e6)
        z = int(STRUCTURES[selected_struct]["length"] * 1e6)
    elif selected_struct == "MRSTUB2W":
        x = int(STRUCTURES[selected_struct]["W"] * 1e6)
        y = int(STRUCTURES[selected_struct]["Ro"] * 1e6)
        z = int(STRUCTURES[selected_struct]["Theta"])
    elif selected_struct in ["MCLIN", "MCFIL", "MXCLIN"]:
        x = int(STRUCTURES[selected_struct]["W"][0] * 1e6)
        y = int(STRUCTURES[selected_struct]["length"] * 1e6)
        z = int(STRUCTURES[selected_struct]["S"][0] * 1e6)
    elif selected_struct == "MCURVE":
        x = int(STRUCTURES[selected_struct]["W"] * 1e6)
        y = int(STRUCTURES[selected_struct]["R"] * 1e6)
        z = int(STRUCTURES[selected_struct]["Angle"])
    elif selected_struct == "MTEE":
        x = int(STRUCTURES[selected_struct]["W1"] * 1e6)
        y = int(STRUCTURES[selected_struct]["W2"] * 1e6)
        z = int(STRUCTURES[selected_struct]["W3"] * 1e6)
    elif selected_struct in ["MSTEP", "MXOVER"]:
        x = int(STRUCTURES[selected_struct]["W1"] * 1e6)
        y = int(STRUCTURES[selected_struct]["W2"] * 1e6)
        z = None
    elif selected_struct == "MOPEN":
        x = int(STRUCTURES[selected_struct]["W"] * 1e6)
        y = None
        z = None
    elif selected_struct == "MGAPX":
        x = int(STRUCTURES[selected_struct]["W"] * 1e6)
        y = int(STRUCTURES[selected_struct]["S"] * 1e6)
        z = None
    else:
        do_db = False

    if num_ports == None:
        try:
            num_ports = int(STRUCTURES[selected_struct]["NumPorts"])
        except Exception as e:
            print("Error with ports number calculation, comparing with DB is impossible")
            do_db = False
    if selected_struct == "mtaper":
        print("Structure 'MTAPER' can't be compared for now")
        do_db = False

    if do_db: compare_with_db()

    #results = run_all()
    #print("All simulations completed.")
    #print(f"Completed FULL simulation in {time.time() - start:.2f} sec")