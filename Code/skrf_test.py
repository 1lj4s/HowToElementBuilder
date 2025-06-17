import numpy as np  # for np.allclose() to check that S-params are similar
import os
import skrf as rf
import matplotlib.pyplot as plt

rf.stylely()
# reference LC circuit made in Designer
LC_designer = rf.Network(os.path.join("Files", "snp", "MLIN_test.s2p"), name ="snp")
# scikit-rf: manually connecting networks
line = rf.media.DefinedGammaZ0(frequency=LC_designer.frequency, z0=50)
LC_manual = line.inductor(24e-9) ** line.capacitor(70e-12)

# scikit-rf: using Circuit builder
port1 = rf.Circuit.Port(frequency=LC_designer.frequency, name='port1', z0=50)
port2 = rf.Circuit.Port(frequency=LC_designer.frequency, name='port2', z0=50)
cap1 = rf.Circuit.SeriesImpedance(frequency=LC_designer.frequency, name='cap1', z0=50,
                                 Z=1/(1j*LC_designer.frequency.w*70e-12))
cap2 = rf.Circuit.SeriesImpedance(frequency=LC_designer.frequency, name='cap2', z0=50,
                                 Z=1/(1j*LC_designer.frequency.w*10e-12))
ind = rf.Circuit.SeriesImpedance(frequency=LC_designer.frequency, name='ind', z0=50,
                                 Z=1j*LC_designer.frequency.w*24e-9)
res = rf.Circuit.SeriesImpedance(frequency=LC_designer.frequency, name='res', z0=50,
                                 Z=1000)
gnd = rf.Circuit.Ground(LC_designer.frequency, name='GND')

# NB: it is also possible to create 2-port lumped elements like:
# line = rf.media.DefinedGammaZ0(frequency=LC_designer.frequency, z0=50)
# cap = line.capacitor(70e-12, name='cap')
# ind = line.inductor(24e-9, name='ind')

connections = [
    [(port1, 0), (LC_designer, 0)],
    [(LC_designer, 1), (cap1, 0), (ind,0)],
    [(ind, 1), (cap2, 0)],
    [(cap2, 1), (res, 0)],
    [(res, 1), (cap1, 1), (gnd, 0)]
]
circuit = rf.Circuit(connections)
LC_from_circuit = circuit.network

print(np.allclose(LC_designer.s, LC_manual.s))
print(np.allclose(LC_designer.s, LC_from_circuit.s))
circuit.plot_graph(network_labels=True, edge_labels=True, port_labels=True)
plt.show()
LC_from_circuit.plot_s_db()
LC_from_circuit.write_touchstone("skrf_test", form="db")
plt.show()
