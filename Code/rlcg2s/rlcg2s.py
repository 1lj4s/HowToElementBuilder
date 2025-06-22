import numpy as np
import skrf
from scipy.linalg import eig, inv
from scipy.interpolate import interp1d


class RLGC2SConverter:
    """Class to convert RLGC parameters to S-parameters based on input params and results."""

    def __init__(self, params, results, mtaper = False):
        """
        Initialize with params and results dictionaries.

        Args:
            params (dict): Dictionary containing simulation parameters (f0, freq_range, length, Z0, etc.).
            results (list): List of dictionaries containing RLGC matrices (mR, mL, mG, mC).
        """
        self.params = params
        self.results = results
        self.freq_range = np.asarray(params['freq_range'])
        self.f0 = np.asarray(params['f0'])
        self.length = params['length']
        self.z0 = params['Z0']
        self.mtaper = mtaper
        if mtaper:
            self.num_lines = len(results['mL'])
        else:
            self.num_lines = len(results[0]['result']['mL'])
        self.loss = params.get('loss')

    def _interpolate_matrices(self, matrix, freq_orig, freq_new):
        """
        Interpolate RLGC matrices from original frequencies to new frequencies.

        Args:
            matrix (ndarray): Matrix of shape (N, N, len(freq_orig)) to interpolate.
            freq_orig (ndarray): Original frequency points.
            freq_new (ndarray): Target frequency points.

        Returns:
            ndarray: Interpolated matrix of shape (N, N, len(freq_new)).
        """
        n = matrix.shape[0]
        interp_matrix = np.zeros((n, n, len(freq_new)), dtype=matrix.dtype)

        for i in range(n):
            for j in range(n):
                interp_func = interp1d(freq_orig, matrix[i, j, :], kind='linear', fill_value="extrapolate")
                interp_matrix[i, j, :] = interp_func(freq_new)

        return interp_matrix

    def _prepare_matrices(self):
        """
        Prepare RLGC matrices by copying mL, mC and interpolating mR, mG.

        Returns:
            tuple: Interpolated or copied matrices (mR, mL, mG, mC).
        """
        if self.mtaper:
            result = self.results
        else:
            result = self.results[0]['result']
        mL = np.array(result['mL'])[:, :, np.newaxis]
        mC = np.array(result['mC'])[:, :, np.newaxis]
        mR = np.array(result['mR'])
        mG = np.array(result['mG'])

        # Copy mL and mC to all frequencies
        mL = np.repeat(mL, len(self.freq_range), axis=2)
        mC = np.repeat(mC, len(self.freq_range), axis=2)

        if self.loss:
            mR = self._interpolate_matrices(mR, self.f0, self.freq_range)
            mG = self._interpolate_matrices(mG, self.f0, self.freq_range)
        else:
            # Expand zeros array
            mR = np.repeat(mR, len(self.freq_range), axis=2)
            mG = np.repeat(mG, len(self.freq_range), axis=2)

        return mR, mL, mG, mC

    def convert(self):
        """
        Convert RLGC parameters to S-parameters.

        Returns:
            tuple: (s_params, rlgc_struct) where s_params is the S-parameter matrix
                   and rlgc_struct contains RLGC and derived parameters.
        """
        # self._validate_inputs()
        resistance, inductance, conductance, capacitance = self._prepare_matrices()

        freqpts = self.freq_range.size
        num_lines = self.num_lines

        # Initialize output arrays
        s_params = np.zeros((2 * num_lines, 2 * num_lines, freqpts), dtype=complex)
        z0_matrix = self.z0 * np.eye(2 * num_lines)

        # Store characteristic impedance and propagation constants for all frequencies
        Zc_all = np.zeros((num_lines, num_lines, freqpts), dtype=complex)
        gamma_all = np.zeros((num_lines, num_lines, freqpts), dtype=complex)

        # For each frequency point
        for freqidx in range(freqpts):
            # Extract RLGC matrices for this frequency
            R = resistance[:, :, freqidx]
            L = inductance[:, :, freqidx]
            G = conductance[:, :, freqidx]
            C = capacitance[:, :, freqidx]

            # Per-unit-length impedance and admittance
            Z = R + 1j * 2 * np.pi * self.freq_range[freqidx] * L
            Y = G + 1j * 2 * np.pi * self.freq_range[freqidx] * C

            # Eigen decomposition of Z*Y
            D, V = eig(Z @ Y)
            gammaEig = np.sqrt(D)  # Propagation constants

            # Calculate gamma matrix
            gamma = V @ np.diag(gammaEig) @ inv(V)

            # Characteristic impedance matrix
            Zc = inv(gamma) @ Z

            # Hyperbolic functions of gamma*length
            cosh_gammaL = V @ np.diag(np.cosh(gammaEig * self.length)) @ inv(V)
            sinh_gammaL = V @ np.diag(np.sinh(gammaEig * self.length)) @ inv(V)

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

            # Store Zc and gamma
            Zc_all[:, :, freqidx] = Zc
            gamma_all[:, :, freqidx] = gamma

        # Prepare output struct
        rlgc_struct = {
            'R': resistance,
            'L': inductance,
            'G': conductance,
            'C': capacitance,
            'Zc': Zc_all,
            'gamma': gamma_all
        }

        return s_params, rlgc_struct

    def save_to_snp(self, s_params, filename='output.s2p'):
        """
        Save S-parameters to a snp Touchstone file
        """
        n_ports = s_params.shape[0]
        if s_params.shape[0] != s_params.shape[1]:
            raise ValueError(f"[RLCG2S] S-параметры должны быть квадратной матрицей, получено: {s_params.shape}")

        expected_ext = f'.s{n_ports}p'
        if not filename.endswith(expected_ext):
            print(f"[RLCG2S] Предупреждение: ожидалось расширение {expected_ext}, получено {filename}")
            filename = filename.rsplit('.', 1)[0] + expected_ext

        s = np.moveaxis(s_params, 2, 0)
        frequency = skrf.Frequency.from_f(self.freq_range, unit='Hz')
        ntw = skrf.Network(frequency=frequency, s=s, name=filename.replace(expected_ext, ''))
        ntw.write_touchstone(filename=filename.replace(expected_ext, ''))

        print(f"[RLCG2S] Файл {filename} успешно сохранён")