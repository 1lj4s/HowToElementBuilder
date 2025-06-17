import skrf as rf

def make_one_end_line(s_params, freq: list, Z0: float, gamma: int):
    """
    Makes MLSC or MLEF from MCLIN by shorting or opening one port
    :param s_params: dict with s_pramaps, shape (n_freq, 2, 2)
    :param freq: frequency list
    :param Z0: Z0 for network
    :param gamma: -1 for short and 1 for open (to ground)
    :return: S-params for 1 port network
    """

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

    s = s_params  # Shape: (n_freq, 2, 2)
    s11 = s[:, 0, 0]
    s12 = s[:, 0, 1]
    s21 = s[:, 1, 0]
    s22 = s[:, 1, 1]

    # For open-circuit termination at port 2, Gamma = 1
    #gamma = -1 # 1 хх если кз то -1

    # Compute the effective S11 for the 1-port network
    # S11' = S11 + (S12 * S21 * Gamma) / (1 - S22 * Gamma)
    s11_eff = s11 + (s12 * s21 * gamma) / (1 - s22 * gamma)

    # Create a new 1-port Network object
    s_1port = s11_eff.reshape(-1, 1, 1)  # Shape: (n_freq, 1, 1)
    ntwk_1port = rf.Network(frequency=freq, s=s_1port, name="test_s1p")
    # ntwk_1port.write_touchstone("test_s1p", form="db")
    return ntwk_1port.s

