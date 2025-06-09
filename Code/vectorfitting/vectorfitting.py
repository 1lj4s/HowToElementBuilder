import skrf
import numpy as np
from io import StringIO


def get_spice_subcircuit_s(vector_fitting, fitted_model_name='s_equivalent', create_reference_pins=False):
    """
    Generates a SPICE subcircuit string for the vector fitted S-parameter model in memory.

    Parameters:
        vector_fitting (skrf.VectorFitting): The fitted VectorFitting object.
        fitted_model_name (str): Name of the resulting subcircuit, default 's_equivalent'.
        create_reference_pins (bool): If True, include reference pins for each port.
                                     If False, reference nodes are connected to ground (0).

    Returns:
        str: The SPICE subcircuit definition as a string.
    """
    # Create a StringIO buffer to capture the output
    output = StringIO()

    # Extract necessary attributes
    network = vector_fitting.network
    n_ports = network.nports
    poles = vector_fitting.poles
    residues = vector_fitting.residues
    proportional_coeff = vector_fitting.proportional_coeff
    constant_coeff = vector_fitting.constant_coeff
    build_e = np.any(proportional_coeff)

    # Write header
    output.write('* EQUIVALENT CIRCUIT FOR VECTOR FITTED S-MATRIX\n')
    output.write('* Created using custom vector fitting script\n')
    output.write('*\n')

    # Create subcircuit pin string
    if create_reference_pins:
        str_input_nodes = ' '.join(f'p{x + 1} p{x + 1}_ref' for x in range(n_ports))
    else:
        str_input_nodes = ' '.join(f'p{x + 1}' for x in range(n_ports))

    output.write(f'.SUBCKT {fitted_model_name} {str_input_nodes}\n')

    for i in range(n_ports):
        output.write('*\n')
        output.write(f'* Port network for port {i + 1}\n')

        # Reference node
        node_ref_i = f'p{i + 1}_ref' if create_reference_pins else '0'

        # Reference impedance
        z0_i = np.real(network.z0[0, i])
        gain_vccs_a_i = 1 / 2 / np.sqrt(z0_i)
        gain_cccs_a_i = np.sqrt(z0_i) / 2
        gain_b_i = 2 / np.sqrt(z0_i)

        # Dummy voltage source for port current sensing
        output.write(f'V{i + 1} p{i + 1} s{i + 1} 0\n')
        output.write(f'R{i + 1} s{i + 1} {node_ref_i} {z0_i}\n')

        # Transfer of states and inputs from port j to port i
        for j in range(n_ports):
            node_ref_j = f'p{j + 1}_ref' if create_reference_pins else '0'
            z0_j = np.real(network.z0[0, j])
            gain_vccs_a_j = 1 / 2 / np.sqrt(z0_j)
            gain_cccs_a_j = np.sqrt(z0_j) / 2
            idx_S_i_j = i * n_ports + j

            d = constant_coeff[idx_S_i_j] if constant_coeff is not None else 0.0
            e = proportional_coeff[idx_S_i_j] if proportional_coeff is not None else 0.0

            if d != 0.0:
                g_ij = gain_b_i * d * gain_vccs_a_j
                f_ij = gain_b_i * d * gain_cccs_a_j
                output.write(f'Gd{i + 1}_{j + 1} {node_ref_i} s{i + 1} p{j + 1} {node_ref_j} {g_ij}\n')
                output.write(f'Fd{i + 1}_{j + 1} {node_ref_i} s{i + 1} V{j + 1} {f_ij}\n')

            if build_e and e != 0.0:
                g_ij = gain_b_i * e
                output.write(f'Ge{i + 1}_{j + 1} {node_ref_i} s{i + 1} e{j + 1} 0 {g_ij}\n')

            # Residue contributions
            for k in range(len(poles)):
                pole = poles[k]
                residue = residues[idx_S_i_j, k]
                g_re = gain_b_i * np.real(residue)
                g_im = gain_b_i * np.imag(residue)

                if np.imag(pole) == 0.0:
                    xkj = f'x{k + 1}_a{j + 1}'
                    output.write(f'Gr{k + 1}_{i + 1}_{j + 1} {node_ref_i} s{i + 1} {xkj} 0 {g_re}\n')
                else:
                    xk_re_j = f'x{k + 1}_re_a{j + 1}'
                    xk_im_j = f'x{k + 1}_im_a{j + 1}'
                    output.write(f'Gr{k + 1}_re_{i + 1}_{j + 1} {node_ref_i} s{i + 1} {xk_re_j} 0 {g_re}\n')
                    output.write(f'Gr{k + 1}_im_{i + 1}_{j + 1} {node_ref_i} s{i + 1} {xk_im_j} 0 {g_im}\n')

        # State networks driven by port i
        output.write('*\n')
        output.write(f'* State networks driven by port {i + 1}\n')
        for k in range(len(poles)):
            pole = poles[k]
            pole_re = np.real(pole)
            pole_im = np.imag(pole)

            if pole_im == 0.0:
                xki = f'x{k + 1}_a{i + 1}'
                output.write(f'Cx{k + 1}_a{i + 1} {xki} 0 1.0\n')
                output.write(f'Gx{k + 1}_a{i + 1} 0 {xki} p{i + 1} {node_ref_i} {1 * gain_vccs_a_i}\n')
                output.write(f'Fx{k + 1}_a{i + 1} 0 {xki} V{i + 1} {1 * gain_cccs_a_i}\n')
                output.write(f'Rp{k + 1}_a{i + 1} 0 {xki} {-1 / pole_re}\n')
            else:
                xk_re_i = f'x{k + 1}_re_a{i + 1}'
                xk_im_i = f'x{k + 1}_im_a{i + 1}'
                output.write(f'Cx{k + 1}_re_a{i + 1} {xk_re_i} 0 1.0\n')
                output.write(f'Gx{k + 1}_re_a{i + 1} 0 {xk_re_i} p{i + 1} {node_ref_i} {2 * gain_vccs_a_i}\n')
                output.write(f'Fx{k + 1}_re_a{i + 1} 0 {xk_re_i} V{i + 1} {2 * gain_cccs_a_i}\n')
                output.write(f'Rp{k + 1}_re_re_a{i + 1} 0 {xk_re_i} {-1 / pole_re}\n')
                output.write(f'Gp{k + 1}_re_im_a{i + 1} 0 {xk_re_i} {xk_im_i} 0 {pole_im}\n')
                output.write(f'Cx{k + 1}_im_a{i + 1} {xk_im_i} 0 1.0\n')
                output.write(f'Gp{k + 1}_im_re_a{i + 1} 0 {xk_im_i} {xk_re_i} 0 {-1 * pole_im}\n')
                output.write(f'Rp{k + 1}_im_im_a{i + 1} 0 {xk_im_i} {-1 / pole_re}\n')

        # Differentiation network for proportional term
        if build_e:
            output.write('*\n')
            output.write(f'* Network with derivative of input a_{i + 1} for proportional term\n')
            output.write(f'Le{i + 1} e{i + 1} 0 1.0\n')
            output.write(f'Ge{i + 1} 0 e{i + 1} p{i + 1} {node_ref_i} {gain_vccs_a_i}\n')
            output.write(f'Fe{i + 1} 0 e{i + 1} V{i + 1} {gain_cccs_a_i}\n')

    output.write(f'.ENDS {fitted_model_name}\n')

    # Get the string and close the buffer
    subcircuit_str = output.getvalue()
    output.close()
    return subcircuit_str


class SParamProcessor:
    """Class to process S-parameters, optionally perform vector fitting, and generate SPICE subcircuits."""

    def __init__(self, s_params, freqs, z0=50.0, name='network'):
        """
        Initialize with S-parameters and frequency data.

        Args:
            s_params (ndarray): S-parameter matrix of shape (n_ports, n_ports, n_freqs).
            freqs (ndarray): Frequency points in Hz.
            z0 (float or ndarray): Reference impedance(s), default 50.0 Ohms.
            name (str): Name for the network, default 'network'.
        """
        self.s_params = np.asarray(s_params)
        self.freqs = np.asarray(freqs)
        self.z0 = z0 if np.isscalar(z0) else np.asarray(z0)
        self.name = name
        self.network = None
        self.vf = None
        self.subcircuits = {}

        # Validate shapes
        if self.s_params.ndim != 3:
            raise ValueError(f"S-parameters must be 3D, got shape {self.s_params.shape}")
        n_ports1, n_ports2, n_freqs = self.s_params.shape
        if n_ports1 != n_ports2:
            raise ValueError(f"S-parameter matrix must be square in port dimensions, got {n_ports1}x{n_ports2}")
        if len(self.freqs) != n_freqs:
            raise ValueError(
                f"Frequency array length {len(self.freqs)} does not match s_params freq dimension {n_freqs}")

        # Create scikit-rf Network
        self._create_network()

    def _create_network(self):
        """Create a scikit-rf Network object from S-parameters."""
        # Transpose s_params to (n_freqs, n_ports, n_ports) for scikit-rf
        s_params_transposed = np.transpose(self.s_params, (2, 0, 1))
        # Convert frequencies to GHz as scikit-rf expects
        freqs_ghz = self.freqs / 1e9
        # Ensure z0 is an array matching number of ports
        n_ports = self.s_params.shape[0]
        if np.isscalar(self.z0):
            z0_array = np.full(n_ports, self.z0)
        else:
            z0_array = self.z0
            if len(z0_array) != n_ports:
                raise ValueError(f"z0 length {len(z0_array)} does not match number of ports {n_ports}")

        self.network = skrf.Network(frequency=freqs_ghz, s=s_params_transposed, z0=z0_array, name=self.name)

    def perform_vector_fitting(self, **vf_params):
        """
        Perform vector fitting on the S-parameters.

        Args:
            **vf_params: Parameters for skrf.VectorFitting.auto_fit (e.g., n_poles_init_real, target_error).
        """
        self.vf = skrf.VectorFitting(self.network)
        self.vf.auto_fit(**vf_params)

    def generate_subcircuit(self, fitted_model_name='s_equivalent', create_reference_pins=False):
        """
        Generate a SPICE subcircuit string in memory.

        Args:
            fitted_model_name (str): Name of the subcircuit.
            create_reference_pins (bool): If True, include reference pins for each port.

        Returns:
            str: SPICE subcircuit string.
        """
        if self.vf is None:
            raise ValueError("Vector fitting must be performed before generating subcircuit.")
        subcircuit = get_spice_subcircuit_s(self.vf, fitted_model_name, create_reference_pins)
        self.subcircuits[fitted_model_name] = subcircuit
        return subcircuit

    def get_network(self):
        """Return the scikit-rf Network object."""
        return self.network

    def get_subcircuits(self):
        """Return dictionary of generated subcircuits."""
        return self.subcircuits


# Example usage
if __name__ == "__main__":
    # Example with a pre-existing .s4p file
    nw_3port = skrf.Network('MXOVER_test.s4p')
    processor = SParamProcessor(nw_3port.s, nw_3port.f, z0=nw_3port.z0, name='test_network')
    processor.perform_vector_fitting(
        n_poles_init_real=3,
        n_poles_init_cmplx=6,
        n_poles_add=5,
        model_order_max=100,
        iters_start=3,
        iters_inter=3,
        iters_final=5,
        target_error=0.01,
        alpha=0.03,
        gamma=0.03,
        nu_samples=1.0,
        parameter_type='s'
    )
    subcircuit_1 = processor.generate_subcircuit(fitted_model_name='s_equivalent_1', create_reference_pins=False)
    subcircuit_2 = processor.generate_subcircuit(fitted_model_name='s_equivalent_2', create_reference_pins=True)
    print(subcircuit_1)
    print()
    print(subcircuit_2)