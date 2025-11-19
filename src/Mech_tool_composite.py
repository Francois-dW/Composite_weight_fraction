import numpy as np
import matplotlib.pyplot as plt

class Matrix:
    def __init__(self, density, porosity, stiffness, poisson_ratio=0.40):
        """
        Initialize Matrix material properties.
        
        Parameters:
        -----------
        density : float
            Material density, ρ_m (rho_m) [kg/m³]
        porosity : float
            Matrix porosity constant, α_pm (dimensionless, 0-1)
        stiffness : float
            Matrix Young's modulus (stiffness), E_m [Pa or GPa]
        poisson_ratio : float
            Matrix Poisson's ratio, ν_m (nu_m) (dimensionless), default=0.40
        """
        self.rho = density
        self.alpha_pm = porosity
        self.E = stiffness
        self.nu = poisson_ratio
    
    def shear_stiffness(self):
        """
        Calculate matrix shear stiffness.
        
        Returns:
        --------
        float
            Matrix shear stiffness, G_m = E_m / (2 * (1 + ν_m))
        """
        return self.E / (2 * (1 + self.nu))


class Fiber:
    def __init__(self, density, porosity, stiffness, orientation_efficiency_factor, length_efficiency_factor, length, diameter):
        """
        Initialize Fiber material properties.
        
        Parameters:
        -----------
        density : float
            Fiber density, ρ_f (rho_f) [kg/m³]
        porosity : float
            Fiber porosity constant, α_pf (dimensionless, 0-1)
        stiffness : float
            Fiber Young's modulus (stiffness), E_f [Pa or GPa]
        orientation_efficiency_factor : float
            Fiber orientation efficiency factor, η₀ (eta0) (dimensionless, 0-1)
        length_efficiency_factor : float
            Fiber length efficiency factor, η₁ (eta1) (dimensionless, 0-1)
        length : float
            Fiber length, L [mm or m]
        diameter : float
            Fiber diameter, D [mm or m]
        """
        self.rho = density
        self.alpha_pf = porosity
        self.E = stiffness
        self.eta0 = orientation_efficiency_factor
        self.eta1 = length_efficiency_factor
        self.L = length
        self.D = diameter
    
    def aspect_ratio(self):
        """
        Calculate fiber aspect ratio.
        
        Returns:
        --------
        float
            Fiber aspect ratio, L/D
        """
        return self.L / self.D
    
    def calculate_length_efficiency_factor(self, G_m, kappa=0.907):
        """
        Calculate fiber length efficiency factor η₁.
        
        Parameters:
        -----------
        G_m : float
            Matrix shear stiffness [Pa or GPa]
        kappa : float
            Constant, κ = π / (2√3) ≈ 0.907
        
        Returns:
        --------
        float
            Fiber length efficiency factor, η₁
        """
        beta = 2 * G_m / (self.E * np.log(kappa / self.aspect_ratio()))
        beta_L_over_2 = beta * self.L / 2
        eta1 = 1 - np.tanh(beta_L_over_2) / beta_L_over_2
        return eta1


class Composite_mix:
    def __init__(self, fiber: Fiber, matrix: Matrix):
        """
        Initialize a composite material mix from fiber and matrix.
        
        Parameters:
        -----------
        fiber : Fiber
            Fiber material instance
        matrix : Matrix
            Matrix material instance
        """
        self.fiber = fiber
        self.matrix = matrix
    
    def composite_stiffness(self, V_f, V_m, n=2):
        """
        Calculate composite stiffness using rule of mixtures.
        
        Parameters:
        -----------
        V_f : float
            Fibre volume fraction (dimensionless, 0-1)
        V_m : float
            Matrix volume fraction (dimensionless, 0-1)
        n : float, optional
            Porosity efficiency exponent (default=2)
        
        Returns:
        --------
        float
            Composite stiffness, E_c = (η₀ η₁ V_f E_f + V_m E_m)(1 - V_p)ⁿ
        """
        V_p = self.calculate_porosity(V_f, V_m)
        
        E_c = (self.fiber.eta0 * self.fiber.eta1 * V_f * self.fiber.E + V_m * self.matrix.E) * (1 - V_p) ** n
        return E_c
    
    def calculate_porosity(self, V_f, V_m):
        """
        Calculate composite porosity.
        
        Parameters:
        -----------
        V_f : float
            Fibre volume fraction (dimensionless, 0-1)
        V_m : float
            Matrix volume fraction (dimensionless, 0-1)
        
        Returns:
        --------
        float
            Composite porosity, V_p
        """
        V_p = 1 - V_f - V_m
        return V_p
    
    def composite_density(self, V_f, V_m):
        """
        Calculate composite density.
        
        Parameters:
        -----------
        V_f : float
            Fibre volume fraction (dimensionless, 0-1)
        V_m : float
            Matrix volume fraction (dimensionless, 0-1)
        
        Returns:
        --------
        float
            Composite density, ρ_c = V_f ρ_f + V_m ρ_m
        """
        rho_c = V_f * self.fiber.rho + V_m * self.matrix.rho
        return rho_c

class Composite_case:
    def __init__(self, composite_mix: Composite_mix, weight_fiber=None, weight_matrix=None, 
                 volume_fiber=None, volume_matrix=None, fiber_mass_fraction=None, 
                 max_volume_fiber=None, force_porosity=None, porosity_efficiency_exponent=2):
        """
        Initialize a specific composite case with volume and weight fractions.
        
        Parameters:
        -----------
        composite_mix : Composite_mix
            Composite mix instance containing fiber and matrix
        weight_matrix : float, optional
            Weight of matrix, W_m [kg]
        weight_fiber : float, optional
            Weight of fiber, W_f [kg]
        volume_matrix : float, optional
            Volume fraction of matrix, V_m (dimensionless, 0-1)
        volume_fiber : float, optional
            Volume fraction of fiber, V_f (dimensionless, 0-1)
        fiber_mass_fraction : float, optional
            Fiber mass fraction, W_f (dimensionless, 0-1)
        max_volume_fiber : float, optional
            Maximum fibre volume fraction, V_f_max (dimensionless, 0-1)
        force_porosity : float, optional
            Forced porosity value, V_p (dimensionless, 0-1)
        porosity_efficiency_exponent : float, optional
            Porosity efficiency exponent, n (default=2)
        """
        self.composite_mix = composite_mix
        self.fiber = composite_mix.fiber
        self.matrix = composite_mix.matrix
        self.W_f = fiber_mass_fraction
        self.V_f = volume_fiber
        self.V_m = volume_matrix
        self.V_f_max = max_volume_fiber
        self.weight_fiber = weight_fiber
        self.weight_matrix = weight_matrix
        self.force_porosity = force_porosity
        self.n = porosity_efficiency_exponent
        
        # Calculate transition weight fiber if max volume fiber is provided
        if self.V_f_max and self.fiber and self.matrix:
            self.W_f_trans = self.calculate_transition_weight_fiber()
        else:
            self.W_f_trans = None
    
    def determine_case(self):
        """
        Determine which case (A or B) applies based on fiber weight fraction.
        
        Returns:
        --------
        str
            'Case A' if W_f ≤ W_f_trans, 'Case B' if W_f ≥ W_f_trans, or 'Unknown'
        """
        if self.W_f is None or self.W_f_trans is None:
            return 'Unknown'
        
        if self.W_f <= self.W_f_trans:
            return 'Case A'
        else:
            return 'Case B'
    
    def calculate_transition_weight_fiber(self):
        """
        Calculate transition fibre weight fraction.
        
        Returns:
        --------
        float
            Transition fibre weight fraction, W_f_trans
        """
        rho_f = self.fiber.rho
        rho_m = self.matrix.rho
        alpha_pm = self.matrix.alpha_pm
        alpha_pf = self.fiber.alpha_pf
        V_f_max = self.V_f_max
        
        numerator = V_f_max * rho_f * (1 - alpha_pm)
        denominator = V_f_max * rho_f * (1 + alpha_pm) - V_f_max * rho_m * (1 + alpha_pf) + rho_m
        
        W_f_trans = numerator / denominator
        return W_f_trans
    
    def calculate_volume_fractions_case_a(self):
        """
        Calculate volume fractions for Case A (W_f ≤ W_f_trans).
        
        Returns:
        --------
        tuple
            (V_f, V_m, V_p) - Fiber, matrix, and porosity volume fractions
        """
        if self.W_f is None:
            raise ValueError("Fiber mass fraction W_f is required for Case A calculations")
        
        W_f = self.W_f
        rho_f = self.fiber.rho
        rho_m = self.matrix.rho
        alpha_pf = self.fiber.alpha_pf
        alpha_pm = self.matrix.alpha_pm
        
        # Calculate V_f
        numerator = W_f * rho_m
        denominator = W_f * rho_m * (1 + alpha_pf) + (1 - W_f) * rho_f * (1 + alpha_pm)
        V_f = numerator / denominator
        
        # Calculate V_m
        numerator = (1 - W_f) * rho_f
        denominator = W_f * rho_m * (1 + alpha_pf) + (1 - W_f) * rho_f * (1 + alpha_pm)
        V_m = numerator / denominator
        
        # Calculate V_p
        numerator = W_f * rho_m * alpha_pf + (1 - W_f) * rho_f * alpha_pm
        denominator = W_f * rho_m * (1 + alpha_pf) + (1 - W_f) * rho_f * (1 + alpha_pm)
        V_p = numerator / denominator
        
        self.V_f = V_f
        self.V_m = V_m
        self.V_p = V_p
        
        return V_f, V_m, V_p
    
    def calculate_volume_fractions_case_b(self):
        """
        Calculate volume fractions for Case B (W_f ≥ W_f_trans).
        
        Returns:
        --------
        tuple
            (V_f, V_m, V_p) - Fiber, matrix, and porosity volume fractions
        """
        if self.V_f_max is None or self.W_f is None:
            raise ValueError("V_f_max and W_f are required for Case B calculations")
        
        V_f_max = self.V_f_max
        W_f = self.W_f
        rho_f = self.fiber.rho
        rho_m = self.matrix.rho
        
        # V_f = V_f_max
        V_f = V_f_max
        
        # Calculate V_m
        numerator = (1 - W_f) * rho_f
        denominator = W_f * rho_m
        V_m = V_f_max * numerator / denominator
        
        # Calculate V_p
        V_p = 1 - V_f_max * (1 + ((1 - W_f) * rho_f) / (W_f * rho_m))
        
        self.V_f = V_f
        self.V_m = V_m
        self.V_p = V_p
        
        return V_f, V_m, V_p
    
    def calculate_composite_stiffness(self):
        """
        Calculate composite stiffness for this case.
        
        Returns:
        --------
        float
            Composite stiffness E_c
        """
        if self.V_f is None or self.V_m is None:
            # Try to calculate volume fractions based on case
            case = self.determine_case()
            if case == 'Case A':
                self.calculate_volume_fractions_case_a()
            elif case == 'Case B':
                self.calculate_volume_fractions_case_b()
            else:
                raise ValueError("Cannot determine case or volume fractions")
        
        return self.composite_mix.composite_stiffness(self.V_f, self.V_m, n=self.n)
    
    def calculate_composite_density(self):
        """
        Calculate composite density for this case.
        
        Returns:
        --------
        float
            Composite density ρ_c
        """
        if self.V_f is None or self.V_m is None:
            # Try to calculate volume fractions based on case
            case = self.determine_case()
            if case == 'Case A':
                self.calculate_volume_fractions_case_a()
            elif case == 'Case B':
                self.calculate_volume_fractions_case_b()
            else:
                raise ValueError("Cannot determine case or volume fractions")
        
        return self.composite_mix.composite_density(self.V_f, self.V_m)


def plot_weight_volume_relations(composite_mix: Composite_mix, V_f_max, W_f_range=None, num_points=100):
    """
    Plot Weight/volume relations showing fiber volume fraction, matrix volume fraction, and porosity
    vs fiber weight fraction.
    
    Parameters:
    -----------
    composite_mix : Composite_mix
        Composite mix instance
    V_f_max : float
        Maximum fiber volume fraction
    W_f_range : tuple, optional
        Range of fiber weight fractions (min, max). Default is (0.0, 1.0)
    num_points : int, optional
        Number of points to plot. Default is 100
    """
    if W_f_range is None:
        W_f_range = (0.0, 1.0)
    
    W_f_array = np.linspace(W_f_range[0], W_f_range[1], num_points)
    V_f_array = []
    V_m_array = []
    V_p_array = []
    
    for W_f in W_f_array:
        case = Composite_case(composite_mix, fiber_mass_fraction=W_f, max_volume_fiber=V_f_max)
        
        if case.determine_case() == 'Case A':
            V_f, V_m, V_p = case.calculate_volume_fractions_case_a()
        else:
            V_f, V_m, V_p = case.calculate_volume_fractions_case_b()
        
        V_f_array.append(V_f)
        V_m_array.append(V_m)
        V_p_array.append(V_p)
    
    plt.figure(figsize=(10, 6))
    plt.plot(W_f_array, V_f_array, 'r-', label='Fibre volume fraction')
    plt.plot(W_f_array, V_m_array, 'b-', label='Matrix volume fraction')
    plt.plot(W_f_array, V_p_array, 'y-', label='Porosity')
    
    plt.xlabel('Fibre weight fraction')
    plt.ylabel('Volume fractions')
    plt.title('Weight/volume relations')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(W_f_range)
    plt.ylim(0, 1)
    plt.tight_layout()
    return plt


def plot_composite_density(composite_mix: Composite_mix, V_f_max, W_f_range=None, num_points=100, include_no_porosity=False):
    """
    Plot composite density vs fiber weight fraction.
    
    Parameters:
    -----------
    composite_mix : Composite_mix
        Composite mix instance
    V_f_max : float
        Maximum fiber volume fraction
    W_f_range : tuple, optional
        Range of fiber weight fractions (min, max). Default is (0.0, 1.0)
    num_points : int, optional
        Number of points to plot. Default is 100
    include_no_porosity : bool, optional
        Whether to include a line showing density without porosity. Default is False
    """
    if W_f_range is None:
        W_f_range = (0.0, 1.0)
    
    W_f_array = np.linspace(W_f_range[0], W_f_range[1], num_points)
    rho_c_array = []
    rho_c_no_porosity_array = []
    
    for W_f in W_f_array:
        case = Composite_case(composite_mix, fiber_mass_fraction=W_f, max_volume_fiber=V_f_max)
        rho_c = case.calculate_composite_density()
        rho_c_array.append(rho_c)
        
        if include_no_porosity:
            # Calculate density without porosity (V_p = 0)
            if case.determine_case() == 'Case A':
                V_f, V_m, _ = case.calculate_volume_fractions_case_a()
                # Renormalize to remove porosity
                total = V_f + V_m
                V_f_norm = V_f / total if total > 0 else 0
                V_m_norm = V_m / total if total > 0 else 0
                rho_no_p = V_f_norm * composite_mix.fiber.rho + V_m_norm * composite_mix.matrix.rho
            else:
                V_f, V_m, _ = case.calculate_volume_fractions_case_b()
                total = V_f + V_m
                V_f_norm = V_f / total if total > 0 else 0
                V_m_norm = V_m / total if total > 0 else 0
                rho_no_p = V_f_norm * composite_mix.fiber.rho + V_m_norm * composite_mix.matrix.rho
            rho_c_no_porosity_array.append(rho_no_p)
    
    plt.figure(figsize=(10, 6))
    plt.plot(W_f_array, rho_c_array, 'k-', label='Composite density', linewidth=2)
    
    if include_no_porosity:
        plt.plot(W_f_array, rho_c_no_porosity_array, 'k--', label='Composite density, no porosity', linewidth=1)
    
    plt.xlabel('Fibre weight fraction')
    plt.ylabel('Composite density (g/cm³)')
    plt.title('Composite density')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(W_f_range)
    plt.tight_layout()
    return plt


def plot_mechanical_properties(composite_mix: Composite_mix, V_f_max, W_f_range=None, num_points=100):
    """
    Plot composite stiffness vs fiber weight fraction.
    
    Parameters:
    -----------
    composite_mix : Composite_mix
        Composite mix instance
    V_f_max : float
        Maximum fiber volume fraction
    W_f_range : tuple, optional
        Range of fiber weight fractions (min, max). Default is (0.0, 1.0)
    num_points : int, optional
        Number of points to plot. Default is 100
    """
    if W_f_range is None:
        W_f_range = (0.0, 1.0)
    
    W_f_array = np.linspace(W_f_range[0], W_f_range[1], num_points)
    E_c_array = []
    
    for W_f in W_f_array:
        case = Composite_case(composite_mix, fiber_mass_fraction=W_f, max_volume_fiber=V_f_max)
        E_c = case.calculate_composite_stiffness()
        E_c_array.append(E_c)
    
    plt.figure(figsize=(10, 6))
    plt.plot(W_f_array, E_c_array, 'k-', label='Composite stiffness', linewidth=2)
    
    plt.xlabel('Fibre weight fraction')
    plt.ylabel('Composite stiffness (GPa)')
    plt.title('Mechanical properties')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(W_f_range)
    plt.tight_layout()
    return plt


def plot_fiber_length_efficiency(composite_mix: Composite_mix, W_f_range=None, num_points=100):
    """
    Plot fiber length efficiency factor vs fiber weight fraction.
    
    Parameters:
    -----------
    composite_mix : Composite_mix
        Composite mix instance
    W_f_range : tuple, optional
        Range of fiber weight fractions (min, max). Default is (0.0, 1.0)
    num_points : int, optional
        Number of points to plot. Default is 100
    """
    if W_f_range is None:
        W_f_range = (0.0, 1.0)
    
    W_f_array = np.linspace(W_f_range[0], W_f_range[1], num_points)
    eta1_array = []
    
    G_m = composite_mix.matrix.shear_stiffness()
    
    for W_f in W_f_array:
        eta1 = composite_mix.fiber.calculate_length_efficiency_factor(G_m)
        eta1_array.append(eta1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(W_f_array, eta1_array, 'k-', label='Fibre length eff. factor', linewidth=2)
    
    plt.xlabel('Fibre weight fraction')
    plt.ylabel('Fibre length efficiency factor')
    plt.title('Fibre length efficiency factor')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(W_f_range)
    plt.ylim(0.9, 1.0)
    plt.tight_layout()
    return plt


def plot_all_graphs(composite_mix: Composite_mix, V_f_max, W_f_range=None, num_points=100):
    """
    Generate all four plots in a single figure.
    
    Parameters:
    -----------
    composite_mix : Composite_mix
        Composite mix instance
    V_f_max : float
        Maximum fiber volume fraction
    W_f_range : tuple, optional
        Range of fiber weight fractions (min, max). Default is (0.0, 1.0)
    num_points : int, optional
        Number of points to plot. Default is 100
    """
    if W_f_range is None:
        W_f_range = (0.0, 1.0)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    W_f_array = np.linspace(W_f_range[0], W_f_range[1], num_points)
    
    # Data arrays
    V_f_array = []
    V_m_array = []
    V_p_array = []
    rho_c_array = []
    rho_c_no_porosity_array = []
    E_c_array = []
    eta1_array = []
    
    G_m = composite_mix.matrix.shear_stiffness()
    
    for W_f in W_f_array:
        case = Composite_case(composite_mix, fiber_mass_fraction=W_f, max_volume_fiber=V_f_max)
        
        # Volume fractions
        if case.determine_case() == 'Case A':
            V_f, V_m, V_p = case.calculate_volume_fractions_case_a()
        else:
            V_f, V_m, V_p = case.calculate_volume_fractions_case_b()
        
        V_f_array.append(V_f)
        V_m_array.append(V_m)
        V_p_array.append(V_p)
        
        # Density
        rho_c = case.calculate_composite_density()
        rho_c_array.append(rho_c)
        
        # Density without porosity
        total = V_f + V_m
        V_f_norm = V_f / total if total > 0 else 0
        V_m_norm = V_m / total if total > 0 else 0
        rho_no_p = V_f_norm * composite_mix.fiber.rho + V_m_norm * composite_mix.matrix.rho
        rho_c_no_porosity_array.append(rho_no_p)
        
        # Stiffness
        E_c = case.calculate_composite_stiffness()
        E_c_array.append(E_c)
        
        # Fiber length efficiency
        eta1 = composite_mix.fiber.calculate_length_efficiency_factor(G_m)
        eta1_array.append(eta1)
    
    # Plot 1: Weight/volume relations
    ax1.plot(W_f_array, V_f_array, 'r-', label='Fibre volume fraction')
    ax1.plot(W_f_array, V_m_array, 'b-', label='Matrix volume fraction')
    ax1.plot(W_f_array, V_p_array, 'y-', label='Porosity')
    ax1.set_xlabel('Fibre weight fraction')
    ax1.set_ylabel('Volume fractions')
    ax1.set_title('Weight/volume relations')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(W_f_range)
    ax1.set_ylim(0, 1)
    
    # Plot 2: Composite density
    ax2.plot(W_f_array, rho_c_array, 'k-', label='Composite density', linewidth=2)
    ax2.plot(W_f_array, rho_c_no_porosity_array, 'k--', label='Composite density, no porosity', linewidth=1)
    ax2.set_xlabel('Fibre weight fraction')
    ax2.set_ylabel('Composite density (g/cm³)')
    ax2.set_title('Composite density')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(W_f_range)
    
    # Plot 3: Mechanical properties
    ax3.plot(W_f_array, E_c_array, 'k-', label='Composite stiffness', linewidth=2)
    ax3.set_xlabel('Fibre weight fraction')
    ax3.set_ylabel('Composite stiffness (GPa)')
    ax3.set_title('Mechanical properties')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(W_f_range)
    
    # Plot 4: Fibre length efficiency factor
    ax4.plot(W_f_array, eta1_array, 'k-', label='Fibre length eff. factor', linewidth=2)
    ax4.set_xlabel('Fibre weight fraction')
    ax4.set_ylabel('Fibre length efficiency factor')
    ax4.set_title('Fibre length efficiency factor')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(W_f_range)
    ax4.set_ylim(0, 1.0)
    
    plt.tight_layout()
    return fig

