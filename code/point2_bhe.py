"""
POINT2 BHE Analytical Solution Module
=====================================

This module implements the POINT2 algorithm for simulating Borehole Heat Exchangers (BHE)
in a 2D aquifer with uniform background groundwater flow.

Key features:
- Supports advection-dispersion heat transport
- Multiple BHE configuration with temporal superposition
- Converts thermal parameters to equivalent solute transport parameters

Based on:
- Wexler, E.J., 1992. Analytical solutions for one-, two-, and three-dimensional
  solute transport in ground-water systems with uniform flow, USGS TWRI 03-B7.

Author: AGT Intern Project
Date: December 2025
"""

import numpy as np
from scipy.special import roots_legendre


def integrand_point2(tau, x, y, v, Dx, Dy, xc, yc, lamb):
    """Compute the integrand for POINT2 analytical solution.
    
    This is the time-domain integrand of the 2D advection-dispersion equation
    with a continuous point source.
    """
    return (
        1 / tau * np.exp(
            -(v**2 / (4 * Dx) + lamb) * tau
            - (x - xc) ** 2 / (4 * Dx * tau)
            - (y - yc) ** 2 / (4 * Dy * tau)
        )
    )


def point2(c0, x, y, t, v, n, al, ah, Qa, xc, yc, Dm=0, lamb=0, R=1.0, order=100):
    """
    Compute the 2D concentration/temperature field from a continuous point source
    in an infinite aquifer with uniform background flow.
    
    Source: Wexler (1992) - POINT2 algorithm (equation 76).
    
    Parameters
    ----------
    c0 : float
        Point source concentration/temperature [M/L³ or °C]
    x, y : float or array
        Output location(s) [L]
    t : float or array
        Time(s) to compute output at [T]
    v : float
        Average linear groundwater flow velocity in x-direction [L/T]
    n : float
        Aquifer porosity [-]
    al : float
        Longitudinal dispersivity [L]
    ah : float
        Horizontal transverse dispersivity [L]
    Qa : float
        Volumetric injection rate per unit aquifer thickness [L²/T]
    xc, yc : float
        Point source coordinates [L]
    Dm : float, optional
        Effective molecular diffusion coefficient [L²/T], default=0
    lamb : float, optional
        First-order decay rate [1/T], default=0
    R : float, optional
        Retardation coefficient [-], default=1
    order : int, optional
        Gauss-Legendre quadrature order, default=100
    
    Returns
    -------
    ndarray
        Computed concentrations/temperatures at specified locations and times
    """
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)
    t = np.atleast_1d(t)

    # Dispersion coefficients
    Dx = al * v + Dm
    Dy = ah * v + Dm

    # Apply retardation coefficient
    v = v / R
    Dx = Dx / R
    Dy = Dy / R
    Qa = Qa / R

    if len(t) > 1 and (len(x) > 1 or len(y) > 1):
        raise ValueError(
            "If multiple values for t are specified, only one x and y value are allowed"
        )

    root, weights = roots_legendre(order)

    def integrate(t, x, y):
        F = (
            integrand_point2(
                root * (t - 0) / 2 + (0 + t) / 2, x, y, v, Dx, Dy, xc, yc, lamb
            ).dot(weights)
            * (t - 0)
            / 2
        )
        return F

    integrate_vec = np.vectorize(integrate)

    term = integrate_vec(t, x, y)
    term0 = Qa / (4 * n * np.pi * np.sqrt(Dx * Dy)) * np.exp(v * (x - xc) / (2 * Dx))

    return c0 * term0 * term


def bhe(
    Finj,
    x, y, t,
    xc, yc,
    v,
    n,
    rho_s, c_s, k_s,
    rho_w=1000.0, c_w=4184.0, k_w=0.59,
    al=0.0, ah=0.0,
    T0=0.0,
    order=100,
):
    """
    Simulate the effect of multiple BHEs with time-varying thermal loads
    in a 2D infinite aquifer with uniform background flow.
    
    Uses POINT2 algorithm with heat-to-solute parameter conversion.
    
    Parameters
    ----------
    Finj : 2D array
        Thermal loads. First column: start time [T].
        Other columns: thermal loads per BHE per unit length [W/m].
    x, y : float or array
        Output location(s) [L]
    t : float or array
        Time(s) to compute output at [T]
    xc, yc : float or array
        BHE coordinates [L]
    v : float
        Average linear groundwater flow velocity in x-direction [L/T]
    n : float
        Aquifer porosity [-]
    rho_s : float
        Solid density [kg/m³]
    c_s : float
        Solid specific heat capacity [J/(kg·K)]
    k_s : float
        Solid thermal conductivity [W/(m·K)]
    rho_w : float
        Water density [kg/m³], default=1000
    c_w : float
        Water specific heat capacity [J/(kg·K)], default=4184
    k_w : float
        Water thermal conductivity [W/(m·K)], default=0.59
    al : float
        Longitudinal dispersivity [L], default=0
    ah : float
        Horizontal transverse dispersivity [L], default=0
    T0 : float
        Initial/background temperature [°C], default=0
    order : int
        Gauss-Legendre quadrature order, default=100
    
    Returns
    -------
    ndarray
        Computed temperatures at specified locations and times
    
    Notes
    -----
    Heat-to-solute parameter mapping:
    - kd = c_s / (c_w * rho_w)           : Distribution coefficient
    - k0 = n*k_w + (1-n)*k_s             : Bulk thermal conductivity
    - Dm = k0 / (n * rho_w * c_w)        : Molecular diffusion
    - R = 1 + kd * rho_b / n             : Retardation factor
    """
    Finj = np.atleast_2d(Finj)
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)
    t = np.atleast_1d(t)
    xc = np.atleast_1d(xc)
    yc = np.atleast_1d(yc)

    inj_time = Finj[:, 0]
    Finj = Finj[:, 1:]
    nbhe = Finj.shape[1]

    if not len(xc) == len(yc) == nbhe:
        raise ValueError(
            "xc and yc should have the same length, equal to the number of BHE's."
        )

    # Compute corresponding solute transport parameters
    kd = c_s / (c_w * rho_w)
    k0 = n * k_w + (1 - n) * k_s
    Dm = k0 / (n * rho_w * c_w)
    rho_b = (1 - n) * rho_s
    R = 1 + kd * rho_b / n

    # Define mass injection rates (convert W/m to equivalent concentration)
    # W/m / (kg/m³ * J/kg/K) = J/s/m / (kg/m³ * J/kg/K) = m²/s * K
    Finj = Finj / (rho_w * c_w)
    Qa = 1.0  # Unity injection rate

    def calculate_temp(inj, ti):
        """Calculate temperature from all BHEs at a given time."""
        for i in range(len(inj)):
            if i == 0:
                c = point2(
                    c0=inj[i], x=x, y=y, t=ti, v=v, n=n,
                    al=al, ah=ah, Qa=Qa, xc=xc[i], yc=yc[i],
                    Dm=Dm, R=R, order=order,
                )
            else:
                c += point2(
                    c0=inj[i], x=x, y=y, t=ti, v=v, n=n,
                    al=al, ah=ah, Qa=Qa, xc=xc[i], yc=yc[i],
                    Dm=Dm, R=R, order=order,
                )
        return c

    # Calculate with temporal superposition
    if len(t) == 1:  # Snapshot model
        inj_time = inj_time[inj_time <= t]
        if len(inj_time) == 0:
            raise ValueError("No loading times prior to t.")

        for ix, tinj in enumerate(inj_time):
            if ix == 0:
                temp = np.nan_to_num(calculate_temp(Finj[ix], t - tinj), nan=0.0)
            else:
                temp += np.nan_to_num(
                    calculate_temp(Finj[ix] - Finj[ix - 1], t - tinj), nan=0.0
                )

    elif len(x) > 1 or len(y) > 1:
        raise ValueError(
            "If multiple values for t are specified, only one x and y value are allowed"
        )

    else:  # Time series at one location
        inj_time = inj_time[inj_time <= np.max(t)]
        if len(inj_time) == 0:
            raise ValueError("No loading times prior to t.")

        for ix, tinj in enumerate(inj_time):
            tix = t > tinj
            nt = len(t[tix])
            if ix == 0:
                temp = np.nan_to_num(calculate_temp(Finj[ix], t - tinj), nan=0.0)
            elif nt > 0:
                temp[tix] = temp[tix] + np.nan_to_num(
                    calculate_temp(Finj[ix] - Finj[ix - 1], t[tix] - tinj), nan=0.0
                )

    return temp + T0


# =============================================================================
# Utility functions for temperature conversion
# =============================================================================

def ground_to_fluid_temperature(T_ground, q, R_b):
    """
    Convert ground/cell temperature to fluid temperature.
    
    Parameters
    ----------
    T_ground : float or array
        Ground/cell temperature [°C]
    q : float or array
        Heat transfer rate per unit length [W/m]
        Positive = heat injection (cooling mode)
        Negative = heat extraction (heating mode)
    R_b : float
        Borehole thermal resistance [(m·K)/W]
    
    Returns
    -------
    T_fluid : float or array
        Fluid temperature [°C]
    
    Notes
    -----
    Formula: T_fluid = T_ground + q * R_b
    
    For heat extraction (negative q): T_fluid < T_ground
    For heat injection (positive q): T_fluid > T_ground
    """
    return T_ground + q * R_b


def fluid_to_ground_temperature(T_fluid, q, R_b):
    """
    Convert fluid temperature to ground/cell temperature.
    
    Parameters
    ----------
    T_fluid : float or array
        Fluid temperature [°C]
    q : float or array
        Heat transfer rate per unit length [W/m]
    R_b : float
        Borehole thermal resistance [(m·K)/W]
    
    Returns
    -------
    T_ground : float or array
        Ground/cell temperature [°C]
    """
    return T_fluid - q * R_b


# =============================================================================
# Test function
# =============================================================================

if __name__ == "__main__":
    print("POINT2 BHE Module - Test")
    print("=" * 50)
    
    # Test parameters
    n = 0.2
    rho_s = 2650.0
    c_s = 940.0
    k_s = 1.4
    v = 1.0 / (24 * 3600)  # 1 m/day in m/s
    
    # Single BHE test
    t_test = np.array([1.0]) * 3600 * 24 * 365  # 1 year in seconds
    x_test = 1.0
    y_test = 0.0
    xc = 0.0
    yc = 0.0
    
    # Simple injection: 50 W/m continuous
    Finj = np.array([[0.0, 50.0]])  # [time, load]
    
    T = bhe(Finj, x_test, y_test, t_test, xc, yc, v, n, rho_s, c_s, k_s, T0=10.0)
    
    print(f"Test conditions:")
    print(f"  Groundwater velocity: {v * 24 * 3600:.2f} m/day")
    print(f"  Heat load: 50 W/m")
    print(f"  Time: 1 year")
    print(f"  Observation point: ({x_test}, {y_test}) m downstream")
    print(f"\nResult:")
    print(f"  Temperature at observation point: {T[0]:.2f} °C")
    print("\nTest completed successfully!")
