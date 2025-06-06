import skrf
import os
import logging
from Code.converters.saver import save_ntwk
from Code.config import FILES_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_elements(ntwk_list, struct_name, current_run, connection_type="series"):
    """
    Combines a list of Network objects into one (series or parallel) and saves the result.

    Args:
        ntwk_list: List of skrf.Network objects.
        struct_name: Name of the structure (e.g., 'MLIN', 'MTAPER', 'MLEF').
        current_run: Name of the current run (e.g., 'test').
        connection_type: Type of connection ('series' or 'parallel').

    Returns:
        Tuple of combined skrf.Network object and the saved filename, or None if the list is empty.
    """
    if not ntwk_list:
        logger.warning("No Network objects available for combining.")
        return None

    try:
        combined = ntwk_list[0]
        if struct_name == "MLEF":
            # Convert 2-port to 1-port for MLEF
            combined = convert_s2p_to_s1p(combined)
        else:
            if connection_type == "series":
                for ntwk in ntwk_list[1:]:
                    combined = combined ** ntwk
            elif connection_type == "parallel":
                logger.warning("Parallel connection not implemented yet.")
                return None
            else:
                raise ValueError(f"Connection type {connection_type} not supported")

        snp_dir = os.path.join(FILES_DIR, "snp")
        num_ports = combined.nports
        obj_name = save_ntwk(combined, snp_dir, struct_name, current_run)
        logger.info(f"Combined network saved for {struct_name}_{current_run}")
        return combined, obj_name

    except Exception as e:
        logger.error(f"Error combining networks: {e}")
        return None

def convert_s2p_to_s1p(ntwk: skrf.Network) -> skrf.Network:
    """
    Converts a 2-port S-parameter network to a 1-port network by open-circuiting the second port.

    Args:
        ntwk: A 2-port skrf.Network object.

    Returns:
        A 1-port skrf.Network object representing the S11 parameter with the second port open.
    """
    if ntwk.nports != 2:
        raise ValueError("Input network must be a 2-port network")

    # Get the S-parameters
    s = ntwk.s  # Shape: (n_freq, 2, 2)
    s11 = s[:, 0, 0]
    s12 = s[:, 0, 1]
    s21 = s[:, 1, 0]
    s22 = s[:, 1, 1]

    # For open-circuit termination at port 2, Gamma = 1
    gamma = 1

    # Compute the effective S11 for the 1-port network
    # S11' = S11 + (S12 * S21 * Gamma) / (1 - S22 * Gamma)
    s11_eff = s11 + (s12 * s21 * gamma) / (1 - s22 * gamma)

    # Create a new 1-port Network object
    freq = ntwk.frequency
    s_1port = s11_eff.reshape(-1, 1, 1)  # Shape: (n_freq, 1, 1)
    ntwk_1port = skrf.Network(frequency=freq, s=s_1port, name=f"{ntwk.name}_s1p")

    return ntwk_1port