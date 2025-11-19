"""
Test script to verify the alpha_pf estimation and optimization
"""
import numpy as np
import sys
sys.path.append('src')

from Mech_tool_composite import Matrix, Fiber, Composite_mix, Composite_case

# Test data from sample_experimental_data.csv
experimental_data = [
    {'W_f': 0.359, 'V_f': 0.201, 'V_m': 0.755, 'V_p': 0.043, 'rho_c': 1.286},
    {'W_f': 0.381, 'V_f': 0.217, 'V_m': 0.741, 'V_p': 0.042, 'rho_c': 1.312},
    {'W_f': 0.387, 'V_f': 0.224, 'V_m': 0.747, 'V_p': 0.028, 'rho_c': 1.341},
    {'W_f': 0.458, 'V_f': 0.224, 'V_m': 0.558, 'V_p': 0.217, 'rho_c': 1.384},
    {'W_f': 0.632, 'V_f': 0.224, 'V_m': 0.275, 'V_p': 0.501, 'rho_c': 1.444},
    {'W_f': 0.752, 'V_f': 0.224, 'V_m': 0.156, 'V_p': 0.620, 'rho_c': 1.477}
]

print("=" * 70)
print("FIBER POROSITY FACTOR (α_pf) ESTIMATION TEST")
print("=" * 70)

# Method 1: Simple V_p / V_f ratio
print("\nMethod 1: Simple Estimation (α_pf ≈ V_p / V_f)")
print("-" * 70)
estimates = []
for data in experimental_data:
    alpha_pf = data['V_p'] / data['V_f'] if data['V_f'] > 0 else 0
    estimates.append(alpha_pf)
    print(f"W_f={data['W_f']:.3f}: V_p={data['V_p']:.3f}, V_f={data['V_f']:.3f} → α_pf ≈ {alpha_pf:.4f}")

mean_alpha_pf = np.mean(estimates)
std_alpha_pf = np.std(estimates)
print(f"\nStatistics:")
print(f"  Mean:     {mean_alpha_pf:.4f}")
print(f"  Std Dev:  {std_alpha_pf:.4f}")
print(f"  Min:      {np.min(estimates):.4f}")
print(f"  Max:      {np.max(estimates):.4f}")

# Method 2: Optimization
print("\n" + "=" * 70)
print("Method 2: Optimization to Find Best α_pf")
print("-" * 70)

from scipy.optimize import minimize

# Material properties from previous test
initial_params = {
    'fiber_density': 2.114,
    'matrix_density': 0.998,
    'fiber_porosity': 0.135,  # Initial guess
    'matrix_porosity': 0.012,
    'v_f_max': 0.223,
    'fiber_stiffness': 230.0,
    'matrix_stiffness': 2.8,
    'matrix_poisson': 0.35,
    'fiber_length': 3.0,
    'fiber_diameter': 0.007,
    'fiber_eta0': 0.75,
    'porosity_exp': 2.0
}

def objective_alpha_pf_only(params):
    """Objective function for optimizing only alpha_pf"""
    alpha_pf = params[0]
    
    # Create material objects
    # Fiber(density, porosity, stiffness, orientation_efficiency_factor, length_efficiency_factor, length, diameter)
    fiber = Fiber(
        density=initial_params['fiber_density'],
        porosity=alpha_pf,
        stiffness=initial_params['fiber_stiffness'],
        orientation_efficiency_factor=initial_params['fiber_eta0'],
        length_efficiency_factor=0.0,  # Will be recalculated
        length=initial_params['fiber_length'],
        diameter=initial_params['fiber_diameter']
    )
    
    # Matrix(density, porosity, stiffness, poisson_ratio)
    matrix = Matrix(
        density=initial_params['matrix_density'],
        porosity=initial_params['matrix_porosity'],
        stiffness=initial_params['matrix_stiffness'],
        poisson_ratio=initial_params['matrix_poisson']
    )
    
    # Calculate eta1
    G_m = matrix.shear_stiffness()
    fiber.eta1 = fiber.calculate_length_efficiency_factor(G_m)
    
    composite = Composite_mix(fiber, matrix)
    
    error = 0
    for data in experimental_data:
        try:
            case = Composite_case(
                composite,
                fiber_mass_fraction=data['W_f'],
                max_volume_fiber=initial_params['v_f_max'],
                porosity_efficiency_exponent=initial_params['porosity_exp']
            )
            
            if case.determine_case() == 'Case A':
                V_f_calc, V_m_calc, V_p_calc = case.calculate_volume_fractions_case_a()
            else:
                V_f_calc, V_m_calc, V_p_calc = case.calculate_volume_fractions_case_b()
            
            # Calculate relative squared errors
            error += ((V_f_calc - data['V_f']) / max(data['V_f'], 0.01))**2
            error += ((V_m_calc - data['V_m']) / max(data['V_m'], 0.01))**2
            error += ((V_p_calc - data['V_p']) / max(data['V_p'], 0.01))**2
        except:
            error += 1000
    
    return error

# Test with initial value
initial_alpha_pf = initial_params['fiber_porosity']
initial_error = objective_alpha_pf_only([initial_alpha_pf])
print(f"Initial α_pf: {initial_alpha_pf:.6f}")
print(f"Initial error: {initial_error:.6e}")

# Run optimization
print("\nRunning optimization...")
result = minimize(
    objective_alpha_pf_only,
    [initial_alpha_pf],
    method='L-BFGS-B',
    bounds=[(0.0, 0.5)],
    options={'maxiter': 100}
)

optimal_alpha_pf = result.x[0]
final_error = result.fun

print(f"\nOptimization Results:")
print(f"  Status: {result.message}")
print(f"  Success: {result.success}")
print(f"  Iterations: {result.nit}")
print(f"\n  Optimal α_pf: {optimal_alpha_pf:.6f}")
print(f"  Final error: {final_error:.6e}")
print(f"  Change: {optimal_alpha_pf - initial_alpha_pf:+.6f} ({100*(optimal_alpha_pf - initial_alpha_pf)/max(initial_alpha_pf, 0.01):+.1f}%)")

if initial_error > 0:
    improvement = 100 * (initial_error - final_error) / initial_error
    print(f"  Improvement: {improvement:.1f}%")

# Verify with optimal value
print("\n" + "=" * 70)
print("VERIFICATION: Volume Fractions with Optimal α_pf")
print("-" * 70)

# Fiber(density, porosity, stiffness, orientation_efficiency_factor, length_efficiency_factor, length, diameter)
fiber = Fiber(
    density=initial_params['fiber_density'],
    porosity=optimal_alpha_pf,
    stiffness=initial_params['fiber_stiffness'],
    orientation_efficiency_factor=initial_params['fiber_eta0'],
    length_efficiency_factor=0.0,
    length=initial_params['fiber_length'],
    diameter=initial_params['fiber_diameter']
)

# Matrix(density, porosity, stiffness, poisson_ratio)
matrix = Matrix(
    density=initial_params['matrix_density'],
    porosity=initial_params['matrix_porosity'],
    stiffness=initial_params['matrix_stiffness'],
    poisson_ratio=initial_params['matrix_poisson']
)

G_m = matrix.shear_stiffness()
fiber.eta1 = fiber.calculate_length_efficiency_factor(G_m)

composite = Composite_mix(fiber, matrix)

print(f"{'W_f':<8} {'V_f(exp)':<10} {'V_f(calc)':<10} {'V_m(exp)':<10} {'V_m(calc)':<10} {'V_p(exp)':<10} {'V_p(calc)':<10}")
print("-" * 70)

for data in experimental_data:
    case = Composite_case(
        composite,
        fiber_mass_fraction=data['W_f'],
        max_volume_fiber=initial_params['v_f_max'],
        porosity_efficiency_exponent=initial_params['porosity_exp']
    )
    
    if case.determine_case() == 'Case A':
        V_f_calc, V_m_calc, V_p_calc = case.calculate_volume_fractions_case_a()
    else:
        V_f_calc, V_m_calc, V_p_calc = case.calculate_volume_fractions_case_b()
    
    print(f"{data['W_f']:<8.3f} {data['V_f']:<10.4f} {V_f_calc:<10.4f} "
          f"{data['V_m']:<10.4f} {V_m_calc:<10.4f} "
          f"{data['V_p']:<10.4f} {V_p_calc:<10.4f}")

print("\n" + "=" * 70)
print("COMPARISON SUMMARY")
print("=" * 70)
print(f"Simple estimation (mean V_p/V_f): {mean_alpha_pf:.6f}")
print(f"Optimized value:                  {optimal_alpha_pf:.6f}")
print(f"Difference:                       {abs(mean_alpha_pf - optimal_alpha_pf):.6f}")
print("=" * 70)
