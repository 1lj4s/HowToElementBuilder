import skrf
import numpy as np

def connect_sparams(sparams_ndarrays, freqs, z0=50):
    """
    Combines a list of 2-port S-parameter arrays into a single skrf.Network via series connection.

    Args:
        sparams_ndarrays (list of np.ndarray): List of 3D arrays with shape (2, 2, Nf) or (Nf, 2, 2)
        freqs (np.ndarray): Frequency array (in Hz) of shape (Nf,)
        z0 (float): Characteristic impedance (defaults to 50 Ohm)

    Returns:
        skrf.Network: Combined network object, or None if input is invalid.
    """
    if not sparams_ndarrays:
        return None

    try:
        networks = []

        for s in sparams_ndarrays:
            s = np.asarray(s)
            if s.shape[0] == 2 and s.shape[1] == 2:
                s = np.transpose(s, (2, 0, 1))  # (2,2,Nf) -> (Nf,2,2)
            elif s.shape[1] != 2 or s.shape[2] != 2:
                raise ValueError(f"Invalid S-parameter shape: {s.shape}")

            ntwk = skrf.Network(s=s, frequency=skrf.Frequency.from_f(freqs, unit='hz'), z0=z0)
            networks.append(ntwk)

        combined = networks[0]
        for ntwk in networks[1:]:
            combined = combined ** ntwk

        return np.transpose(combined.s, (1, 2, 0))

    except Exception:
        return None
