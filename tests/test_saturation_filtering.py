"""
Test the filtering logic for saturated vs unsaturated points
"""
import numpy as np

# Sample experimental data
experimental_data = [
    {'W_f': 0.359, 'V_f': 0.201, 'V_m': 0.755, 'V_p': 0.043, 'rho_c': 1.286},
    {'W_f': 0.381, 'V_f': 0.217, 'V_m': 0.741, 'V_p': 0.042, 'rho_c': 1.312},
    {'W_f': 0.387, 'V_f': 0.224, 'V_m': 0.747, 'V_p': 0.028, 'rho_c': 1.341},
    {'W_f': 0.458, 'V_f': 0.224, 'V_m': 0.558, 'V_p': 0.217, 'rho_c': 1.384},
    {'W_f': 0.632, 'V_f': 0.224, 'V_m': 0.275, 'V_p': 0.501, 'rho_c': 1.444},
    {'W_f': 0.752, 'V_f': 0.224, 'V_m': 0.156, 'V_p': 0.620, 'rho_c': 1.477}
]

print("=" * 70)
print("FILTERING TEST: Saturated vs Unsaturated Points")
print("=" * 70)

# Sort by W_f
sorted_data = sorted(experimental_data, key=lambda x: x['W_f'])

print("\nAll data points (sorted by W_f):")
for pt in sorted_data:
    print(f"  W_f={pt['W_f']:.3f}: V_f={pt['V_f']:.3f}, V_p={pt['V_p']:.3f}")

# Check for saturation
print("\n" + "-" * 70)
print("Saturation Detection:")
print("-" * 70)

# Look at last 3 points
last_3_vf = [pt['V_f'] for pt in sorted_data[-3:]]
vf_std = np.std(last_3_vf)
vf_mean = np.mean(last_3_vf)

print(f"Last 3 V_f values: {last_3_vf}")
print(f"Mean: {vf_mean:.6f}")
print(f"Std Dev: {vf_std:.6f}")
print(f"Std/Mean: {vf_std/vf_mean:.4f} ({100*vf_std/vf_mean:.2f}%)")

if vf_std < 0.01 * vf_mean:
    v_f_saturation = vf_mean
    print(f"\n✓ SATURATION DETECTED at V_f ≈ {v_f_saturation:.4f}")
    print(f"  (Std dev < 1% of mean → V_f is constant)")
else:
    v_f_saturation = None
    print("\n✗ NO SATURATION (V_f varies significantly)")

# Filter points
print("\n" + "-" * 70)
print("Point Classification:")
print("-" * 70)

if v_f_saturation is not None:
    threshold = v_f_saturation * 0.98
    print(f"Threshold: V_f < {threshold:.4f} (98% of saturation)")
    print()
    
    unsaturated = []
    saturated = []
    
    for pt in sorted_data:
        if pt['V_f'] < threshold:
            unsaturated.append(pt)
            status = "UNSATURATED (Case A)"
        else:
            saturated.append(pt)
            status = "SATURATED (Case B)"
        
        print(f"  W_f={pt['W_f']:.3f}, V_f={pt['V_f']:.3f} → {status}")
    
    print("\n" + "-" * 70)
    print("Summary:")
    print("-" * 70)
    print(f"Total points: {len(sorted_data)}")
    print(f"Unsaturated (for α_pf estimation): {len(unsaturated)}")
    print(f"Saturated (excluded): {len(saturated)}")
    
    if unsaturated:
        print(f"\n✓ Using {len(unsaturated)} unsaturated point(s) for α_pf estimation:")
        for pt in unsaturated:
            alpha_pf_est = pt['V_p'] / pt['V_f']
            print(f"    W_f={pt['W_f']:.3f}: V_p={pt['V_p']:.3f}, V_f={pt['V_f']:.3f} → α_pf ≈ {alpha_pf_est:.4f}")
        
        estimates = [pt['V_p'] / pt['V_f'] for pt in unsaturated]
        print(f"\n  Mean α_pf: {np.mean(estimates):.4f}")
        print(f"  Std Dev:   {np.std(estimates):.4f}")
    else:
        print(f"\n⚠ NO UNSATURATED POINTS!")
        print("  All data is at saturation (V_f_max reached)")
        print("  Cannot estimate fiber porosity from this data.")
        print("\n  REASON:")
        print("    - At saturation, V_f is constant (limited by fiber packing)")
        print("    - Porosity at saturation is due to matrix shortage (Case B)")
        print("    - Fiber porosity (α_pf) only affects Case A behavior")
    
    if saturated:
        print(f"\n✗ Excluding {len(saturated)} saturated point(s):")
        for pt in saturated:
            print(f"    W_f={pt['W_f']:.3f}: V_f={pt['V_f']:.3f} (constant → saturation)")
        
        print("\n  EXPLANATION:")
        print("    At saturation (Case B):")
        print("    - V_f = V_f_max (constant, independent of α_pf)")
        print("    - V_p increases due to lack of matrix, not fiber porosity")
        print("    - α_pf has minimal effect on volume fractions")
        print("    → Cannot use these points to estimate α_pf!")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)

if v_f_saturation is not None and unsaturated:
    print("✓ Valid estimation possible")
    print(f"  Use {len(unsaturated)} unsaturated point(s) where V_f < {threshold:.4f}")
    print("  These points are in Case A where fiber porosity matters")
elif v_f_saturation is not None and not unsaturated:
    print("✗ Cannot estimate α_pf from this data")
    print("  All points are saturated (Case B)")
    print("  Need data at lower W_f where V_f varies")
else:
    print("✓ All points usable")
    print("  No saturation detected, V_f varies across all points")

print("=" * 70)
