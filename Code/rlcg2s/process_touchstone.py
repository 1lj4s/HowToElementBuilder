import skrf as rf
import numpy as np

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

def convert_s4p_to_s2p(s_params, freq, Z0, keep_ports=(0, 3), short_ports=(1, 2), gamma = [1, 1]) -> rf.Network:
    """
    Convert s4p to s2
    keep_ports=(0, 3), short_ports=(1, 2) - first line input, second line output
    gamma mb [1, 1] or [-1, -1]. [-1, 1] and [1, -1] not tested yet
    """
    # Тут может быть какая то умная проверка
    # if ntwk4.nports != 4:
    #     raise ValueError("Only 4-port networks are supported")

    rf.stylely()
    frequency_obj = rf.Frequency.from_f(freq, unit='Hz')
    ntwk4 = rf.Network(frequency=frequency_obj, s=s_params, name="snp", z0=Z0)
    s = ntwk4.s  # (n_freq, 4, 4)
    keep_idx = np.array(keep_ports)
    short_idx = np.array(short_ports)

    S11 = s[:, keep_idx[:, None], keep_idx]
    S12 = s[:, keep_idx[:, None], short_idx]
    S21 = s[:, short_idx[:, None], keep_idx]
    S22 = s[:, short_idx[:, None], short_idx]

    Gamma = np.diag([gamma[0], gamma[1]])
    I = np.eye(2)
    S_eff = S11 + S12 @ np.linalg.inv(I - S22 @ Gamma) @ Gamma @ S21
    result_nwrk = rf.Network(frequency=ntwk4.frequency, s=S_eff, name=f"{ntwk4.name}_shorted_reduced")
    return result_nwrk.s

