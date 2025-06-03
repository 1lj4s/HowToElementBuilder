import numpy as np
from scipy.linalg import eig, inv


def rlgc2s_t(resistance, inductance, conductance, capacitance, linelength, freq, z0):
    """
    Converts RLGC-parameters of transmission lines to S-parameters
    """
    # 0 Input validation
    if not np.isscalar(z0):
        raise ValueError("Z0 must be a scalar")
    if np.isnan(z0) or np.isinf(z0):
        raise ValueError("Z0 cannot be NaN or Inf")
    if np.any(np.imag(z0) != 0):
        raise ValueError("Z0 cannot be complex")

    freq = np.asarray(freq)
    freqpts = freq.size
    num_lines = resistance.shape[0]

    # Initialize output arrays
    s_params = np.zeros((2 * num_lines, 2 * num_lines, freqpts), dtype=complex)
    z0_matrix = z0 * np.eye(2 * num_lines)

    # For each frequency point
    for freqidx in range(freqpts):
        # Extract RLGC matrices for this frequency
        R = resistance[:, :, freqidx] if resistance.ndim == 3 else resistance
        L = inductance[:, :, freqidx] if inductance.ndim == 3 else inductance
        G = conductance[:, :, freqidx] if conductance.ndim == 3 else conductance
        C = capacitance[:, :, freqidx] if capacitance.ndim == 3 else capacitance

        # Per-unit-length impedance and admittance
        Z = R + 1j * 2 * np.pi * freq[freqidx] * L
        Y = G + 1j * 2 * np.pi * freq[freqidx] * C

        # Eigen decomposition of Z*Y
        D, V = eig(Z @ Y)
        gammaEig = np.sqrt(D)  # propagation constants

        # Calculate gamma matrix
        gamma = V @ np.diag(gammaEig) @ inv(V)

        # Characteristic impedance matrix
        Zc = inv(gamma) @ Z

        # Hyperbolic functions of gamma*length
        cosh_gammaL = V @ np.diag(np.cosh(gammaEig * linelength)) @ inv(V)
        sinh_gammaL = V @ np.diag(np.sinh(gammaEig * linelength)) @ inv(V)

        # ABCD parameters
        A = cosh_gammaL
        B = sinh_gammaL @ Zc
        C = inv(Zc) @ sinh_gammaL
        D = inv(Zc) @ cosh_gammaL @ Zc

        # Z-parameters
        Cinv = inv(C)
        Z11 = A @ Cinv
        Z12 = Z11 @ D - B
        Z21 = Cinv
        Z22 = Z21 @ D

        # Combine Z-parameters
        Z_params = np.block([
            [Z11, Z12],
            [Z21, Z22]
        ])

        # Convert to S-parameters
        s_params[:, :, freqidx] = (Z_params - z0_matrix) @ inv(Z_params + z0_matrix)

    # Prepare output struct
    rlgc_struct = {
        'R': resistance,
        'L': inductance,
        'G': conductance,
        'C': capacitance,
        'Zc': Zc if freqpts == 1 else np.repeat(Zc[:, :, np.newaxis], freqpts, axis=2),
        'gamma': gamma if freqpts == 1 else np.repeat(gamma[:, :, np.newaxis], freqpts, axis=2)
    }

    return s_params, rlgc_struct