# File: connectors\connector.py
import skrf
import numpy as np
import os
import logging
from Code.converters.saver import save_ntwk
from Code.config import FILES_DIR
from Code.core.utils import get_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_elements(ntwk_list, struct_name, current_run, connection_type="series"):
    """
    Combines a list of Network objects into one (series or parallel) and applies terminations
    based on the ports configuration, reducing the number of ports accordingly.

    Args:
        ntwk_list: List of skrf.Network objects.
        struct_name: Name of the structure (e.g., 'MLIN', 'MTAPER').
        current_run: Name of the current run (e.g., 'test').
        connection_type: Type of connection ('series' or 'parallel').

    Returns:
        Combined and terminated skrf.Network object or None if the list is empty.
    """
    if not ntwk_list:
        logger.warning("No Network objects available for combination.")
        return None

    try:
        # Load configuration to get ports information
        config_path = os.path.join(FILES_DIR, "json", "simulation_config.json")
        config = get_config(config_path)
        struct_config = config.get(struct_name, {})
        ports_config = struct_config.get("ports", [])
        num_ports = struct_config.get("num_ports", 2)

        if len(ports_config) != num_ports:
            logger.error(f"Ports configuration length ({len(ports_config)}) does not match num_ports ({num_ports}) for {struct_name}")
            return None

        # Combine networks (series connection for now)
        combined = ntwk_list[0]
        if connection_type == "series":
            for ntwk in ntwk_list[1:]:
                combined = combined ** ntwk
        elif connection_type == "parallel":
            logger.warning("Parallel connection not implemented yet.")
            return None
        else:
            raise ValueError(f"Connection type {connection_type} not supported")

        # Apply terminations
        terminated_network = combined
        active_ports = [i for i, p in enumerate(ports_config) if p == 'port']
        terminated_ports = [(i, p) for i, p in enumerate(ports_config) if p in ['r', 'i', 's', 'd']]

        if terminated_ports:
            for port_idx, term_type in terminated_ports:
                if term_type == 'r':
                    # Terminate with 50 Ohm load
                    terminated_network = skrf.network.connect_2ports(
                        terminated_network, port_idx,
                        skrf.Network(z0=50, s=np.array([[[-1]]]), frequency=terminated_network.frequency), 0
                    )
                elif term_type == 'i':
                    # Open circuit (very high impedance, approximate with large resistor)
                    terminated_network = skrf.network.connect_2ports(
                        terminated_network, port_idx,
                        skrf.Network(z0=1e6, s=np.array([[[1]]]), frequency=terminated_network.frequency), 0
                    )
                elif term_type == 's':
                    # Short circuit (zero impedance)
                    terminated_network = skrf.network.connect_2ports(
                        terminated_network, port_idx,
                        skrf.Network(z0=1e-6, s=np.array([[[-1]]]), frequency=terminated_network.frequency), 0
                    )
                elif term_type == 'd':
                    # Placeholder for subcircuit connection
                    logger.warning(f"Subcircuit connection ('d') for port {port_idx+1} not implemented yet.")
                    # Future implementation: Load subcircuit from config or file and connect
                    continue

        # Renumber ports to keep only active (unterminated) ports
        if active_ports:
            # Extract S-parameters for active ports only
            s_active = terminated_network.s[:, active_ports][:, :, active_ports]
            terminated_network = skrf.Network(
                frequency=terminated_network.frequency,
                s=s_active,
                z0=terminated_network.z0[:, active_ports],
                name=f"{struct_name}_{current_run}_terminated"
            )
        else:
            logger.warning("No active ports remaining after terminations.")
            return None

        # Save the resulting network
        snp_dir = os.path.join(FILES_DIR, "snp")
        save_ntwk(terminated_network, snp_dir, struct_name, current_run)
        logger.info(f"Combined and terminated network saved for {struct_name}_{current_run}")
        return terminated_network

    except Exception as e:
        logger.error(f"Error combining or terminating networks: {e}")
        return None