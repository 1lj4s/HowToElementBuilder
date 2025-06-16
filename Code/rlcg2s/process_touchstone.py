import os
import skrf as rf
from skrf.io.general import network_2_spreadsheet
import matplotlib.pyplot as plt

def make_MLSC(s_params, freq, Z0):
    rf.stylely()
    frequency_obj = rf.Frequency.from_f(freq, unit='Hz')
    sparam_ntwrk = rf.Network(frequency=frequency_obj, s=s_params, name="snp", z0=Z0)
    port1 = rf.Circuit.Port(frequency=frequency_obj, name='port1', z0=50)
    gnd = rf.Circuit.Ground(frequency=frequency_obj, name='GND')
    connections = [
        [(port1, 0), (sparam_ntwrk, 0)],
        [(sparam_ntwrk, 1), (gnd, 0)]
    ]
    circuit = rf.Circuit(connections)
    sparam_from_circuit = circuit.network
    #network_2_spreadsheet(sparam_from_circuit,file_name="Out_test.xlsx")
    #sparam_from_circuit.write_spreadsheet(file_name="Out_test.txt")
    print(sparam_from_circuit.s.shape)
    sparam_from_circuit.write_touchstone("skrf_test", form="db")
    #sparam_from_circuit.plot_s_db()
    return sparam_from_circuit.s