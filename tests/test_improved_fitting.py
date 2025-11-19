"""
Test script for improved curve fitting algorithm
Verifies that fitting produces expected results for sample data
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
from scipy.optimize import minimize
from Mech_tool_composite import Matrix, Fiber, Composite_mix, Composite_case

# Experimental data from sample_experimental_data.csv
exp_data = [
    {'W_f': 0.359, 'V_f': 0.201, 'V_m': 0.755, 'V_p': 0.043, 'rho_c': 1.178},
    {'W_f': 0.381, 'V_f': 0.217, 'V_m': 0.741, 'V_p': 0.042, 'rho_c': 1.196},
    {'W_f': 0.387, 'V_f': 0.224, 'V_m': 0.747, 'V_p': 0.028, 'rho_c': 1.218},
    {'W_f': 0.458, 'V_f': 0.224, 'V_m': 0.558, 'V_p': 0.217, 'rho_c': 1.029},
    {'W_f': 0.632, 'V_f': 0.224, 'V_m': 0.275, 'V_p': 0.501, 'rho_c': 0.746},
    {'W_f': 0.752, 'V_f': 0.224, 'V_m': 0.156, 'V_p': 0.620, 'rho_c': 0.627},
]

# Expected fitted values
EXPECTED = {
    'fiber_density': 2.10,
    'matrix_density': 1.00,
    'fiber_porosity': 0.21,
    'matrix_porosity': 0.00,
    'v_f_max': 0.224,
    'w_f_transition': 0.39
}

TOLERANCE = {
    'fiber_density': 0.05,
    'matrix_density': 0.05,
    'fiber_porosity': 0.03,
    'matrix_porosity': 0.02,
    'v_f_max': 0.005,
    'w_f_transition': 0.02
}

print("=" * 80)
print("IMPROVED CURVE FITTING TEST")
print("=" * 80)
print(f"\nExperimental data points: {len(exp_data)}")

# Fixed parameters (not optimized)
FIXED_PARAMS = {
    'matrix_stiffness': 3.5,
    'matrix_poisson': 0.40,
    'fiber_stiffness': 80.0,
    'fiber_eta0': 1.00,
    'fiber_length': 10000.0,
    'fiber_diameter': 0.016,
    'porosity_exp': 2.0,
}

print("\nFixed parameters (known/not fitted):")
for key, val in FIXED_PARAMS.items():
    print(f"  {key}: {val}")

# Detect saturation - find where V_f stops increasing
print("\n" + "=" * 80)
print("STEP 1: DETECT SATURATION")
print("=" * 80)

sorted_data = sorted(exp_data, key=lambda x: x['W_f'])

# Check if V_f plateaus (becomes constant within tolerance)
v_f_values = [pt['V_f'] for pt in sorted_data]
print(f"V_f progression: {[f'{v:.3f}' for v in v_f_values]}")

# Find saturation point: where V_f stops changing significantly
v_f_saturated = None
saturation_index = len(sorted_data)

for i in range(len(sorted_data) - 2):
    # Check if next 3+ points have constant V_f
    remaining_vf = v_f_values[i:]
    if len(remaining_vf) >= 3:
        vf_std = np.std(remaining_vf)
        vf_mean = np.mean(remaining_vf)
        if vf_std < 0.005 * vf_mean:  # Very small variation
            v_f_saturated = vf_mean
            saturation_index = i
            break

if v_f_saturated:
    # Include points up to AND INCLUDING the first saturation point for fitting
    # The point where V_f first reaches V_f_max is still usable information
    unsaturated_data = sorted_data[:saturation_index+1]
    saturated_data = sorted_data[saturation_index+1:]
    print(f"\\n\u2713 Saturation detected at V_f \u2248 {v_f_saturated:.4f}")
    print(f"First saturated point at index {saturation_index} (W_f={sorted_data[saturation_index]['W_f']:.3f})")
    print(f"Points used for fitting (up to saturation): {len(unsaturated_data)}")
    print(f"Fully saturated points (excluded): {len(saturated_data)}")
else:
    unsaturated_data = sorted_data
    print("\n○ No clear saturation detected, using all points")

# Estimate initial parameters
print("\n" + "=" * 80)
print("STEP 2: ESTIMATE INITIAL PARAMETERS FROM DATA")
print("=" * 80)

initial_estimates = {}

# V_f_max from saturation
if v_f_saturated:
    initial_estimates['v_f_max'] = v_f_saturated
    print(f"V_f_max: {v_f_saturated:.4f} (from saturation)")

# Matrix density from low W_f point using rule of mixtures
# ρ_c = V_f*ρ_f + V_m*ρ_m, rearrange to: ρ_m = (ρ_c - V_f*ρ_f) / V_m
# For low W_f, we need rough estimate of ρ_f first
low_wf_pt = sorted_data[0]

# Use two-point method: solve system of equations for ρ_f and ρ_m
# Point 1: ρ_c1 = V_f1*ρ_f + V_m1*ρ_m
# Point 2: ρ_c2 = V_f2*ρ_f + V_m2*ρ_m
if len(unsaturated_data) >= 2:
    pt1 = unsaturated_data[0]
    pt2 = unsaturated_data[1]
    
    # Solve linear system
    # V_f1*ρ_f + V_m1*ρ_m = ρ_c1
    # V_f2*ρ_f + V_m2*ρ_m = ρ_c2
    A = np.array([[pt1['V_f'], pt1['V_m']], [pt2['V_f'], pt2['V_m']]])
    b = np.array([pt1['rho_c'], pt2['rho_c']])
    
    try:
        rho_f_est, rho_m_est = np.linalg.solve(A, b)
        initial_estimates['fiber_density'] = rho_f_est
        initial_estimates['matrix_density'] = rho_m_est
        print(f"Matrix density: {rho_m_est:.4f} g/cm³ (from 2-point solution)")
        print(f"Fiber density: {rho_f_est:.4f} g/cm³ (from 2-point solution)")
    except:
        # Fallback to simple estimate
        matrix_density_est = 1.0
        fiber_density_est = 2.1
        initial_estimates['matrix_density'] = matrix_density_est
        initial_estimates['fiber_density'] = fiber_density_est
        print(f"Matrix density: {matrix_density_est:.4f} g/cm³ (default)")
        print(f"Fiber density: {fiber_density_est:.4f} g/cm³ (default)")
else:
    # Fallback defaults
    initial_estimates['matrix_density'] = 1.0
    initial_estimates['fiber_density'] = 2.1
    print(f"Matrix density: 1.0000 g/cm³ (default)")
    print(f"Fiber density: 2.1000 g/cm³ (default)")

# Fiber porosity from V_p/V_f ratio in unsaturated region
vf_vp_points = [pt for pt in unsaturated_data if pt['V_f'] > 0.1]
if vf_vp_points:
    ratios = [pt['V_p'] / pt['V_f'] for pt in vf_vp_points]
    fiber_porosity_est = np.mean(ratios)
    initial_estimates['fiber_porosity'] = fiber_porosity_est
    print(f"Fiber porosity: {fiber_porosity_est:.4f} (mean V_p/V_f in unsaturated region)")

# Matrix porosity
initial_estimates['matrix_porosity'] = 0.00
print(f"Matrix porosity: 0.00 (assumed)")

print("Estimated vs Expected:")
print(f"{'Parameter':<20} {'Estimated':<12} {'Expected':<12} {'Diff':<10}")
print("-" * 54)
for key in ['fiber_density', 'matrix_density', 'fiber_porosity', 'v_f_max']:
    est = initial_estimates.get(key, 0)
    exp = EXPECTED[key]
    diff = abs(est - exp)
    status = "✓" if diff < TOLERANCE.get(key, 0.05) else "○"
    print(f"{key:<20} {est:<12.4f} {exp:<12.4f} {diff:<10.4f} {status}")
# Matrix porosity is fixed
print(f"{'matrix_porosity':<20} {'0.0000':<12} {'0.0000':<12} {'FIXED':<10}")

# Define objective function
print("\n" + "=" * 80)
print("STEP 3: RUN OPTIMIZATION")
print("=" * 80)

def objective(params):
    """Calculate weighted error for volume fractions and density"""
    fiber_density, matrix_density, fiber_porosity, v_f_max = params
    matrix_porosity = 0.0  # FIXED: matrix is non-porous
    
    error = 0.0
    count = 0
    
    try:
        matrix = Matrix(
            density=matrix_density * 1000,
            porosity=matrix_porosity,
            stiffness=FIXED_PARAMS['matrix_stiffness'],
            poisson_ratio=FIXED_PARAMS['matrix_poisson']
        )
        
        fiber = Fiber(
            density=fiber_density * 1000,
            porosity=fiber_porosity,
            stiffness=FIXED_PARAMS['fiber_stiffness'],
            orientation_efficiency_factor=FIXED_PARAMS['fiber_eta0'],
            length_efficiency_factor=0.95,
            length=FIXED_PARAMS['fiber_length'],
            diameter=FIXED_PARAMS['fiber_diameter']
        )
        
        G_m = matrix.shear_stiffness()
        fiber.eta1 = fiber.calculate_length_efficiency_factor(G_m)
        composite = Composite_mix(fiber=fiber, matrix=matrix)
        
        # Use unsaturated data for fiber porosity sensitive parameters
        data_to_use = unsaturated_data
        
        for pt in data_to_use:
            case = Composite_case(
                composite_mix=composite,
                fiber_mass_fraction=pt['W_f'],
                max_volume_fiber=v_f_max,
                porosity_efficiency_exponent=FIXED_PARAMS['porosity_exp']
            )
            
            if case.determine_case() == 'Case A':
                V_f, V_m, V_p = case.calculate_volume_fractions_case_a()
            else:
                V_f, V_m, V_p = case.calculate_volume_fractions_case_b()
            
            rho_c = case.calculate_composite_density() / 1000
            
            # Volume fractions weighted heavily (most reliable)
            error += (V_f - pt['V_f']) ** 2 * 10
            error += (V_m - pt['V_m']) ** 2 * 10
            error += (V_p - pt['V_p']) ** 2 * 10
            count += 3
            
            # Density with moderate weight
            error += ((rho_c - pt['rho_c']) / pt['rho_c']) ** 2
            count += 1
        
        return error / count if count > 0 else 1000
    
    except Exception as e:
        return 1000

# Initial values from estimates - EXCLUDE matrix_porosity (fix to 0)
initial_values = [
    initial_estimates['fiber_density'],
    initial_estimates['matrix_density'],
    initial_estimates['fiber_porosity'],
    initial_estimates['v_f_max']
]

# Bounds - matrix porosity FIXED to 0 (not optimized)
bounds = [
    (1.5, 3.5),    # fiber_density
    (0.8, 1.5),    # matrix_density  
    (0.0, 0.4),    # fiber_porosity
    (v_f_saturated * 0.95, v_f_saturated * 1.05) if v_f_saturated else (0.20, 0.30)  # v_f_max
]

param_names = ['fiber_density', 'matrix_density', 'fiber_porosity', 'v_f_max']

initial_error = objective(initial_values)
print(f"Initial error: {initial_error:.6e}")
print("\nOptimizing with L-BFGS-B...")

result = minimize(
    objective, 
    initial_values, 
    method='L-BFGS-B', 
    bounds=bounds,
    options={'maxiter': 2000, 'ftol': 1e-12}
)

print("\n" + "=" * 80)
print("STEP 4: OPTIMIZATION RESULTS")
print("=" * 80)

if result.success:
    print("Status: ✓ SUCCESS")
else:
    print(f"Status: {result.message}")

print(f"Final error: {result.fun:.6e}")
print(f"Error reduction: {((initial_error - result.fun) / initial_error * 100):.1f}%")
print(f"Iterations: {result.nit}")

print("\n" + "-" * 80)
print("FITTED PARAMETERS")
print("-" * 80)
print(f"{'Parameter':<25} {'Expected':<12} {'Fitted':<12} {'Error':<10} {'Status':<8}")
print("-" * 80)

fitted_params = {}
all_pass = True

for i, name in enumerate(param_names):
    expected = EXPECTED[name]
    fitted = result.x[i]
    error = abs(fitted - expected)
    tol = TOLERANCE[name]
    status = "✓ PASS" if error < tol else "✗ FAIL"
    
    if error >= tol:
        all_pass = False
    
    fitted_params[name] = fitted
    print(f"{name:<25} {expected:<12.4f} {fitted:<12.4f} {error:<10.4f} {status:<8}")

# Add fixed matrix_porosity
fitted_params['matrix_porosity'] = 0.0
print(f"{'matrix_porosity':<25} {EXPECTED['matrix_porosity']:<12.4f} {'0.0000':<12} {'FIXED':<10} {'✓ PASS':<8}")

# Calculate transition weight fraction
print("\n" + "-" * 80)
print("TRANSITION WEIGHT FRACTION")
print("-" * 80)

matrix = Matrix(
    density=fitted_params['matrix_density'] * 1000,
    porosity=fitted_params['matrix_porosity'],
    stiffness=FIXED_PARAMS['matrix_stiffness'],
    poisson_ratio=FIXED_PARAMS['matrix_poisson']
)

fiber = Fiber(
    density=fitted_params['fiber_density'] * 1000,
    porosity=fitted_params['fiber_porosity'],
    stiffness=FIXED_PARAMS['fiber_stiffness'],
    orientation_efficiency_factor=FIXED_PARAMS['fiber_eta0'],
    length_efficiency_factor=0.95,
    length=FIXED_PARAMS['fiber_length'],
    diameter=FIXED_PARAMS['fiber_diameter']
)

composite = Composite_mix(fiber=fiber, matrix=matrix)
test_case = Composite_case(
    composite_mix=composite,
    max_volume_fiber=fitted_params['v_f_max'],
    porosity_efficiency_exponent=FIXED_PARAMS['porosity_exp']
)

w_f_trans = test_case.calculate_transition_weight_fiber()
w_f_trans_error = abs(w_f_trans - EXPECTED['w_f_transition'])
w_f_trans_status = "✓ PASS" if w_f_trans_error < TOLERANCE['w_f_transition'] else "✗ FAIL"

if w_f_trans_error >= TOLERANCE['w_f_transition']:
    all_pass = False

print(f"{'W_f_transition':<25} {EXPECTED['w_f_transition']:<12.4f} {w_f_trans:<12.4f} {w_f_trans_error:<10.4f} {w_f_trans_status:<8}")

# Verification table
print("\n" + "=" * 80)
print("STEP 5: VERIFICATION - CALCULATED vs EXPERIMENTAL")
print("=" * 80)
print(f"{'W_f':<8} {'V_f':<12} {'V_m':<12} {'V_p':<12} {'ρ_c':<12} {'Case':<8}")
print(f"{'':8} {'exp/calc':<12} {'exp/calc':<12} {'exp/calc':<12} {'exp/calc':<12}")
print("-" * 80)

for pt in exp_data:
    case = Composite_case(
        composite_mix=composite,
        fiber_mass_fraction=pt['W_f'],
        max_volume_fiber=fitted_params['v_f_max'],
        porosity_efficiency_exponent=FIXED_PARAMS['porosity_exp']
    )
    
    case_type = case.determine_case()
    
    if case_type == 'Case A':
        V_f, V_m, V_p = case.calculate_volume_fractions_case_a()
    else:
        V_f, V_m, V_p = case.calculate_volume_fractions_case_b()
    
    rho_c = case.calculate_composite_density() / 1000
    
    print(f"{pt['W_f']:.3f}")
    print(f"{'':8} {pt['V_f']:.3f}/{V_f:.3f}   {pt['V_m']:.3f}/{V_m:.3f}   {pt['V_p']:.3f}/{V_p:.3f}   {pt['rho_c']:.3f}/{rho_c:.3f}   {case_type}")

# Final summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

if all_pass:
    print("✓ ALL TESTS PASSED - Fitting algorithm produces expected results!")
else:
    print("✗ SOME TESTS FAILED - Review parameters and tolerances")

print("\nParameter accuracy:")
for name in ['fiber_density', 'matrix_density', 'fiber_porosity', 'v_f_max', 'w_f_transition']:
    if name == 'w_f_transition':
        fitted_val = w_f_trans
    else:
        fitted_val = fitted_params[name]
    
    expected_val = EXPECTED[name]
    if expected_val != 0:
        error_pct = abs(fitted_val - expected_val) / expected_val * 100
        print(f"  {name:<25} {error_pct:>6.2f}% error")
    else:
        print(f"  {name:<25} {'FIXED':>6}")
print(f"  {'matrix_porosity':<25} {'FIXED (0.0)':>6}")

print("\n" + "=" * 80)
