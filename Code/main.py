import time
from config import STRUCTURES, SUBSTRATES, SIMULATIONS
import database.postgresql as db
import database.plotdata as plot_db
import os
import core

def gen_path():
    paths = {
        "main": os.path.dirname(os.path.abspath(__file__)),
        "MoM2D_exe": r"C:\Program Files\Talgat 2021\PythonClient.exe",
        "MoM2D_code": os.path.join(os.path.dirname(os.path.abspath(__file__)), "MoM2D"),
        "shared": None,
    }
    (paths.update({
        "NETLIST_DIR": os.path.join(paths["main"], "Files", "symnet"),
        "SNP_DIR": os.path.join(paths["main"], "Files","snp"),
        "VERILOG_DIR": os.path.join(paths["main"], "Files", "ver"),
        "SUBCIRCUIT_DIR": os.path.join(paths["main"], "Files", "sub"),
        "OUTPUT_DIR": os.path.join(paths["main"], "Files", "symout"),}))
    return paths

if __name__ == "__main__":
    #print("Select structure name")
    #Цикл для  ожидания ввода названия структуры
    #TODO реализовать возможность ввода нескольких структур
    available_structs = ["MLIN", "MLSC", "MLEF", "MTRACE2", "MTAPER", "MRSTUB2W", "MCLIN", "MCFIL", "MBEND", "MCURVE", "MTEE", "MCROSS", "MXOVER", "MGAPX", "MSTEP", "MOPEN", "MLANG"]
    print("[MAIN] Available structures:", ', '.join(available_structs))
    while True:
        selected_struct = input("[MAIN] Type structure name or exit: ")
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
    if len(sim_param["freq_range"])+1 != 336:
        print(f"Warning, number of frequency points is {len(sim_param['freq_range'])+1} and not equal 336, can't compare with database, continue anyway?")
        while True:
            ans = input("Type Y or N: ")
            if ans == "Y":
                do_db = False
                break
            elif ans == "N":
                quit()
            else:
                print("Can't recognise answer")
    else:
        do_db = True
    start = time.time()
    handler = core.Simulation_Handler(paths, selected_struct, STRUCTURES[selected_struct], subst, sim_param)
    handler.m1lin = STRUCTURES["M1LIN_STRUCTS"]
    handler.mnlin = STRUCTURES["MNLIN_STRUCTS"]
    handler.run_simulation()
    if do_db:
        networks = db.get_sparams_data(
            path=paths["OUTPUT_DIR"],
            name=selected_struct,
            x=int(STRUCTURES[selected_struct]["W"]*1e6),
            y=int(STRUCTURES[selected_struct]["length"]*1e6),
            table_name=selected_struct.lower(),
            return_network=True
        )
        plot_db.plot_networks(networks[0], networks[1])
    #results = run_all()
    #print("All simulations completed.")
    #print(f"Completed FULL simulation in {time.time() - start:.2f} sec")