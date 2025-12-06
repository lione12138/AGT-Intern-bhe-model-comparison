"""
pygfunction Complete g-function Model
======================================

Using the pygfunction library for accurate g-function calculations,
implementing BHE temperature response calculation comparable to EED.

Main Features:
1. Accurate multi-borehole g-function calculation
2. Temporal superposition for temperature response
3. Short-term response model
4. Comparison analysis with EED

References:
- Cimmino, M. (2018). pygfunction: an open-source toolbox for the evaluation 
  of thermal response factors for geothermal borehole fields.
- Eskilson, P. (1987). Thermal Analysis of Heat Extraction Boreholes.

Author: AGT Intern Team
Date: 2024-12
"""

import numpy as np
import pygfunction as gt
from scipy.interpolate import interp1d
import warnings


class PygfunctionBHEModel:
    """
    Complete BHE temperature model based on pygfunction
    """
    
    def __init__(self, H, D, r_b, k_s, rho_c_s, R_b, T0):
        """
        Initialize the model
        
        Parameters:
        -----------
        H : float
            Borehole depth [m]
        D : float  
            Buried depth [m]
        r_b : float
            Borehole radius [m]
        k_s : float
            Ground thermal conductivity [W/(m·K)]
        rho_c_s : float
            Ground volumetric heat capacity [J/(m³·K)]
        R_b : float
            Borehole thermal resistance [(m·K)/W]
        T0 : float
            Initial ground temperature [°C]
        """
        self.H = H
        self.D = D
        self.r_b = r_b
        self.k_s = k_s
        self.rho_c_s = rho_c_s
        self.R_b = R_b
        self.T0 = T0
        
        # Calculate derived parameters
        self.alpha_s = k_s / rho_c_s  # Thermal diffusivity [m²/s]
        self.ts = H**2 / (9 * self.alpha_s)  # Characteristic time [s]
        
        # Borehole field and g-function will be initialized later
        self.boreholes = None
        self.gfunc_interp = None
        
    def create_borehole_field(self, N_x, N_y, B_x, B_y=None):
        """
        Create rectangular borehole field
        
        Parameters:
        -----------
        N_x : int
            Number of boreholes in x direction
        N_y : int
            Number of boreholes in y direction
        B_x : float
            Spacing in x direction [m]
        B_y : float, optional
            Spacing in y direction [m], defaults to B_x
        """
        if B_y is None:
            B_y = B_x
            
        self.N_x = N_x
        self.N_y = N_y
        self.N_b = N_x * N_y
        self.B_x = B_x
        self.B_y = B_y
        
        # Create borehole field using pygfunction
        self.boreholes = gt.boreholes.rectangle_field(
            N_x, N_y, B_x, B_y, self.H, self.D, self.r_b
        )
        
        print(f"Created borehole field: {N_x}×{N_y} = {self.N_b} boreholes")
        print(f"Borehole spacing: {B_x}m × {B_y}m")
        print(f"Borehole depth: {self.H}m, radius: {self.r_b*1000}mm")
        
        return self.boreholes
    
    def calculate_gfunction(self, time_values, method='similarities', 
                           boundary_condition='MIFT', display=False):
        """
        Calculate g-function
        
        Parameters:
        -----------
        time_values : array
            Time points [s]
        method : str
            Calculation method ('similarities', 'detailed', 'equivalent')
        boundary_condition : str
            Boundary condition ('UHTR', 'UBWT', 'MIFT')
        display : bool
            Whether to display progress
            
        Returns:
        --------
        gFunc : array
            g-function values
        """
        if self.boreholes is None:
            raise ValueError("Please create borehole field first (create_borehole_field)")
        
        time_values = np.atleast_1d(time_values)
        
        # Calculate g-function using pygfunction
        if method == 'similarities':
            gFunc = gt.gfunction.gFunction(
                self.boreholes, self.alpha_s, time_values,
                boundary_condition=boundary_condition,
                options={'nSegments': 8, 'disp': display}
            )
        elif method == 'equivalent':
            gFunc = gt.gfunction.gFunction(
                self.boreholes, self.alpha_s, time_values,
                boundary_condition=boundary_condition,
                method='equivalent',
                options={'nSegments': 8, 'disp': display}
            )
        else:
            gFunc = gt.gfunction.gFunction(
                self.boreholes, self.alpha_s, time_values,
                boundary_condition=boundary_condition,
                options={'nSegments': 12, 'disp': display}
            )
        
        # Create interpolation function
        self.gfunc_interp = interp1d(
            np.log(time_values), gFunc.gFunc,
            kind='linear', fill_value='extrapolate'
        )
        
        return gFunc.gFunc
    
    def precompute_gfunction(self, t_max=25*365.25*24*3600, n_points=50):
        """
        Precompute g-function for subsequent interpolation
        
        Parameters:
        -----------
        t_max : float
            Maximum time [s]
        n_points : int
            Number of time points
        """
        # Log-distributed time points
        t_min = 100  # Minimum time 100 seconds
        time_values = np.logspace(np.log10(t_min), np.log10(t_max), n_points)
        
        print(f"Precomputing g-function ({n_points} time points)...")
        gFunc = self.calculate_gfunction(time_values)
        print("g-function calculation complete!")
        
        return time_values, gFunc
    
    def get_gfunction(self, t):
        """
        Get g-function value at specified time (using interpolation)
        
        Parameters:
        -----------
        t : float or array
            Time [s]
            
        Returns:
        --------
        g : float or array
            g-function value
        """
        if self.gfunc_interp is None:
            raise ValueError("Please precompute g-function first (precompute_gfunction)")
        
        t = np.atleast_1d(t)
        g = np.zeros_like(t, dtype=float)
        
        valid = t > 0
        g[valid] = self.gfunc_interp(np.log(t[valid]))
        
        return g if len(g) > 1 else g[0]
    
    def temporal_superposition(self, q_history, dt):
        """
        Temporal superposition for temperature response calculation
        
        Using Eskilson's load aggregation method
        
        Parameters:
        -----------
        q_history : array
            Heat load history [W/m], length n
        dt : float or array
            Time step [s]
            
        Returns:
        --------
        T_b : array
            Borehole wall temperature [°C]
        T_f : array
            Fluid temperature [°C]
        """
        n = len(q_history)
        
        # Time step
        if np.isscalar(dt):
            dt = np.ones(n) * dt
        
        # Cumulative time
        time_end = np.cumsum(dt)
        
        # Calculate borehole wall temperature change
        delta_Tb = np.zeros(n)
        
        for i in range(n):
            # Response from each previous load to current time point
            for j in range(i + 1):
                # Load increment
                if j == 0:
                    dq = q_history[j]
                else:
                    dq = q_history[j] - q_history[j-1]
                
                if abs(dq) > 1e-10:
                    # Duration from load j start to time i
                    t_elapsed = time_end[i] - (time_end[j] - dt[j])
                    
                    if t_elapsed > 0:
                        g = self.get_gfunction(t_elapsed)
                        delta_Tb[i] += dq / (2 * np.pi * self.k_s) * g
        
        # Borehole wall temperature
        T_b = self.T0 + delta_Tb
        
        # Fluid temperature = borehole wall temperature + q × Rb
        T_f = T_b + q_history * self.R_b
        
        return T_b, T_f
    
    def calculate_monthly_temperatures(self, q_monthly, n_years):
        """
        Calculate multi-year monthly fluid temperatures
        
        Parameters:
        -----------
        q_monthly : array
            12-month heat loads [W/m]
        n_years : int
            Number of simulation years
            
        Returns:
        --------
        T_b : array
            Borehole wall temperature series [°C]
        T_f : array
            Fluid temperature series [°C]
        time_years : array
            Time [years]
        """
        # Build complete load sequence
        q_history = np.tile(q_monthly, n_years)
        
        # Monthly duration
        dt = 365.25 / 12 * 24 * 3600  # seconds
        
        # Temporal superposition calculation
        T_b, T_f = self.temporal_superposition(q_history, dt)
        
        # Time series
        n_months = n_years * 12
        time_years = (np.arange(n_months) + 1) * (365.25 / 12) / 365.25
        
        return T_b, T_f, time_years
    
    def calculate_peak_temperature(self, T_base, q_peak, t_peak=8*3600):
        """
        Calculate peak load temperature
        
        Parameters:
        -----------
        T_base : float or array
            Base load fluid temperature [°C]
        q_peak : float or array
            Peak load [W/m]
        t_peak : float
            Peak duration [s], default 8 hours
            
        Returns:
        --------
        T_peak : float or array
            Peak temperature [°C]
        """
        # g-function for peak response
        g_peak = self.get_gfunction(t_peak)
        
        # Peak temperature response
        # ΔT = q_peak × (Rb + Rg_short)
        # Rg_short = g(t_peak) / (2πk)
        R_g_peak = g_peak / (2 * np.pi * self.k_s)
        
        T_peak = T_base + q_peak * (self.R_b + R_g_peak)
        
        return T_peak
    
    def summary(self):
        """Print model parameters"""
        print("="*60)
        print("pygfunction BHE Temperature Model Parameters")
        print("="*60)
        print(f"Borehole depth: H = {self.H} m")
        print(f"Buried depth: D = {self.D} m")
        print(f"Borehole radius: r_b = {self.r_b*1000} mm")
        print(f"Ground thermal conductivity: k = {self.k_s} W/(m·K)")
        print(f"Ground thermal diffusivity: α = {self.alpha_s:.2e} m²/s")
        print(f"Characteristic time: ts = {self.ts/(365.25*24*3600):.1f} years")
        print(f"Borehole thermal resistance: Rb = {self.R_b} (m·K)/W")
        print(f"Initial ground temperature: T0 = {self.T0} °C")
        if self.boreholes is not None:
            print(f"\nBorehole field: {self.N_x}×{self.N_y} = {self.N_b} boreholes")
            print(f"Borehole spacing: {self.B_x}m × {self.B_y}m")
        print("="*60)


def load_aggregation_monthly(q_history, times, alpha, k, H, gfunc_values, gfunc_times):
    """
    Load aggregation method for temperature response calculation (monthly resolution)
    
    Parameters:
    -----------
    q_history : array
        Heat load history [W/m]
    times : array
        Time points [s]
    alpha : float
        Thermal diffusivity [m²/s]
    k : float
        Thermal conductivity [W/(m·K)]
    H : float
        Borehole depth [m]
    gfunc_values : array
        Precomputed g-function values
    gfunc_times : array
        Corresponding times [s]
        
    Returns:
    --------
    delta_Tb : array
        Borehole wall temperature change [K]
    """
    # g-function interpolation function
    gfunc_interp = interp1d(
        np.log(gfunc_times), gfunc_values,
        kind='linear', fill_value='extrapolate'
    )
    
    n = len(q_history)
    delta_Tb = np.zeros(n)
    
    for i in range(n):
        for j in range(i + 1):
            # Load increment
            if j == 0:
                dq = q_history[j]
            else:
                dq = q_history[j] - q_history[j-1]
            
            if abs(dq) > 1e-10:
                t_elapsed = times[i+1] - times[j]
                if t_elapsed > 100:  # At least 100 seconds
                    g = gfunc_interp(np.log(t_elapsed))
                    delta_Tb[i] += dq / (2 * np.pi * k) * g
    
    return delta_Tb


# =============================================================================
# EED Compatibility Correction Parameters
# =============================================================================
# Correction parameters determined through comparison analysis with EED

class EEDCompatibilityParams:
    """
    EED Compatibility Correction Parameters
    
    Parameters determined based on comparison analysis with EED software:
    - Effective thermal resistance factor: EED effective resistance = Rb × 2.42
    - Temperature offset: Approximately 3.5°C offset needed
    
    These differences may originate from:
    1. Short-term response model used internally by EED
    2. Differences in boundary conditions
    3. Heat pump COP effects
    """
    
    # Effective thermal resistance multiplier (Rb_eff / Rb)
    R_EFF_FACTOR = 2.42
    
    # Temperature baseline offset [°C]
    T_OFFSET = 3.51
    
    @classmethod
    def adjust_for_eed(cls, T_b, q_history, R_b, T0):
        """
        Adjust pygfunction results for EED compatibility
        
        Parameters:
        -----------
        T_b : array
            Borehole wall temperature calculated by pygfunction [°C]
        q_history : array
            Heat load history [W/m]
        R_b : float
            Borehole thermal resistance [(m·K)/W]
        T0 : float
            Initial ground temperature [°C]
            
        Returns:
        --------
        T_f_eed : array
            Adjusted fluid temperature [°C] (comparable to EED)
        """
        # Use effective thermal resistance
        R_b_eff = R_b * cls.R_EFF_FACTOR
        
        # Calculate fluid temperature
        T_f = T_b + q_history * R_b_eff
        
        # Apply temperature offset
        T_f_eed = T_f + cls.T_OFFSET
        
        return T_f_eed


def create_borehole_field(N_x, N_y, B, H=147.0, D=2.0, r_b=0.075):
    """
    Convenience function: Create rectangular borehole field coordinates
    
    Parameters:
    -----------
    N_x : int
        Number of boreholes in x direction
    N_y : int
        Number of boreholes in y direction
    B : float
        Borehole spacing [m]
    H : float
        Borehole depth [m]
    D : float
        Buried depth [m]
    r_b : float
        Borehole radius [m]
        
    Returns:
    --------
    positions : array
        Borehole coordinates [(N_x*N_y) × 2]
    """
    positions = []
    for i in range(N_x):
        for j in range(N_y):
            positions.append([i * B, j * B])
    return np.array(positions)


if __name__ == "__main__":
    # Test code
    print("Testing pygfunction BHE model...")
    
    # Create model
    model = PygfunctionBHEModel(
        H=147.0,
        D=2.0,
        r_b=0.075,
        k_s=2.5,
        rho_c_s=2.5e6,
        R_b=0.127,
        T0=9.6
    )
    
    model.summary()
    
    # Create borehole field
    model.create_borehole_field(5, 8, 7.0)
    
    # Precompute g-function
    times, gfunc = model.precompute_gfunction()
    
    print(f"\nTime range: {times[0]/(3600):.1f} h ~ {times[-1]/(365.25*24*3600):.1f} years")
    print(f"g-function range: {gfunc[0]:.2f} ~ {gfunc[-1]:.2f}")
    
    print("\n" + "="*60)
    print("EED Compatibility Parameters:")
    print(f"  Effective thermal resistance factor: {EEDCompatibilityParams.R_EFF_FACTOR:.2f}")
    print(f"  Temperature offset: {EEDCompatibilityParams.T_OFFSET:+.2f} °C")
