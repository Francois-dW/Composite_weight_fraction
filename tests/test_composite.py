"""
Test cases for composite material analysis tool.

This file demonstrates how to use the composite analysis classes and functions
with specific material parameters.
"""

import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from src.Mech_tool_composite import Matrix, Fiber, Composite_mix, Composite_case
from src.Mech_tool_composite import plot_weight_volume_relations, plot_composite_density
from src.Mech_tool_composite import plot_mechanical_properties, plot_fiber_length_efficiency
from src.Mech_tool_composite import plot_all_graphs


def test_case_1():
    """
    Test case with parameters from the reference document:
    
    Parameters: Weight/volume relations
    - Fibre density: 2.60 g/cm³
    - Matrix density: 1.16 g/cm³
    - Fibre porosity factor: 0.00
    - Matrix porosity factor: 0.00
    - Max. fibre volume fraction: 0.60
    - Transition fibre weight fraction: 0.77
    
    Parameters: Mechanical properties
    - Fibre stiffness: 80 GPa
    - Matrix stiffness: 3.5 GPa
    - Fibre orientation efficiency factor: 1.00
    - Porosity efficiency exponent: 2
    - Fibre length: 10000 mm (10 m)
    - Fibre diameter: 16 μm (0.016 mm)
    - Fibre aspect ratio: 625000
    """
    
    print("=" * 60)
    print("TEST CASE 1: Composite Fiber Analysis")
    print("=" * 60)
    
    # Create Matrix instance
    # Note: Converting g/cm³ to kg/m³: multiply by 1000
    matrix_density = 1.16 * 1000  # 1160 kg/m³
    matrix_porosity = 0.00
    matrix_stiffness = 3.5  # GPa
    matrix_poisson = 0.40
    
    matrix = Matrix(
        density=matrix_density,
        porosity=matrix_porosity,
        stiffness=matrix_stiffness,
        poisson_ratio=matrix_poisson
    )
    
    print("\nMatrix Properties:")
    print(f"  Density: {matrix.rho} kg/m³ ({matrix.rho/1000:.2f} g/cm³)")
    print(f"  Porosity factor (α_pm): {matrix.alpha_pm}")
    print(f"  Stiffness (E_m): {matrix.E} GPa")
    print(f"  Poisson's ratio (ν_m): {matrix.nu}")
    print(f"  Shear stiffness (G_m): {matrix.shear_stiffness():.3f} GPa")
    
    # Create Fiber instance
    # Note: Converting g/cm³ to kg/m³: multiply by 1000
    fiber_density = 2.60 * 1000  # 2600 kg/m³
    fiber_porosity = 0.00
    fiber_stiffness = 80  # GPa
    fiber_eta0 = 1.00  # Orientation efficiency factor
    fiber_length = 10000  # mm (10 m)
    fiber_diameter = 0.016  # mm (16 μm)
    
    # Calculate initial length efficiency factor (will be calculated more accurately later)
    fiber_eta1 = 0.95  # Initial estimate
    
    fiber = Fiber(
        density=fiber_density,
        porosity=fiber_porosity,
        stiffness=fiber_stiffness,
        orientation_efficiency_factor=fiber_eta0,
        length_efficiency_factor=fiber_eta1,
        length=fiber_length,
        diameter=fiber_diameter
    )
    
    print("\nFiber Properties:")
    print(f"  Density: {fiber.rho} kg/m³ ({fiber.rho/1000:.2f} g/cm³)")
    print(f"  Porosity factor (α_pf): {fiber.alpha_pf}")
    print(f"  Stiffness (E_f): {fiber.E} GPa")
    print(f"  Orientation efficiency (η₀): {fiber.eta0}")
    print(f"  Length efficiency (η₁): {fiber.eta1}")
    print(f"  Length (L): {fiber.L} mm")
    print(f"  Diameter (D): {fiber.D} mm")
    print(f"  Aspect ratio (L/D): {fiber.aspect_ratio():.0f}")
    
    # Calculate accurate length efficiency factor
    G_m = matrix.shear_stiffness()
    eta1_calculated = fiber.calculate_length_efficiency_factor(G_m)
    fiber.eta1 = eta1_calculated
    print(f"  Calculated length efficiency (η₁): {eta1_calculated:.6f}")
    
    # Create Composite mix
    composite = Composite_mix(fiber=fiber, matrix=matrix)
    
    print("\nComposite Mix Created")
    
    # Test with specific fiber volume fraction
    V_f_max = 0.60
    
    # Create a test case and calculate transition weight fraction
    test_case = Composite_case(
        composite_mix=composite,
        max_volume_fiber=V_f_max
    )
    
    W_f_trans = test_case.calculate_transition_weight_fiber()
    print(f"\nTransition fibre weight fraction (W_f_trans): {W_f_trans:.2f}")
    
    # Test Case A (W_f < W_f_trans)
    print("\n" + "-" * 60)
    print("CASE A: W_f = 0.40 (below transition)")
    print("-" * 60)
    
    case_a = Composite_case(
        composite_mix=composite,
        fiber_mass_fraction=0.40,
        max_volume_fiber=V_f_max
    )
    
    print(f"Case type: {case_a.determine_case()}")
    V_f_a, V_m_a, V_p_a = case_a.calculate_volume_fractions_case_a()
    print(f"  Fiber volume fraction (V_f): {V_f_a:.4f}")
    print(f"  Matrix volume fraction (V_m): {V_m_a:.4f}")
    print(f"  Porosity (V_p): {V_p_a:.4f}")
    print(f"  Sum check (should be 1.0): {V_f_a + V_m_a + V_p_a:.4f}")
    
    rho_c_a = case_a.calculate_composite_density()
    E_c_a = case_a.calculate_composite_stiffness()
    print(f"  Composite density (ρ_c): {rho_c_a:.2f} kg/m³ ({rho_c_a/1000:.3f} g/cm³)")
    print(f"  Composite stiffness (E_c): {E_c_a:.2f} GPa")
    
    # Test Case B (W_f > W_f_trans)
    print("\n" + "-" * 60)
    print("CASE B: W_f = 0.90 (above transition)")
    print("-" * 60)
    
    case_b = Composite_case(
        composite_mix=composite,
        fiber_mass_fraction=0.90,
        max_volume_fiber=V_f_max
    )
    
    print(f"Case type: {case_b.determine_case()}")
    V_f_b, V_m_b, V_p_b = case_b.calculate_volume_fractions_case_b()
    print(f"  Fiber volume fraction (V_f): {V_f_b:.4f}")
    print(f"  Matrix volume fraction (V_m): {V_m_b:.4f}")
    print(f"  Porosity (V_p): {V_p_b:.4f}")
    print(f"  Sum check (should be 1.0): {V_f_b + V_m_b + V_p_b:.4f}")
    
    rho_c_b = case_b.calculate_composite_density()
    E_c_b = case_b.calculate_composite_stiffness()
    print(f"  Composite density (ρ_c): {rho_c_b:.2f} kg/m³ ({rho_c_b/1000:.3f} g/cm³)")
    print(f"  Composite stiffness (E_c): {E_c_b:.2f} GPa")
    
    # Generate plots
    print("\n" + "=" * 60)
    print("GENERATING PLOTS")
    print("=" * 60)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    W_f_range = (0.0, 1.0)
    
    # Plot 1: Weight/volume relations
    print("\nGenerating Weight/volume relations plot...")
    plot_weight_volume_relations(composite, V_f_max, W_f_range)
    plt.savefig(os.path.join(output_dir, 'weight_volume_relations.png'), dpi=300, bbox_inches='tight')
    print("  Saved as: output/weight_volume_relations.png")
    plt.close()
    
    # Plot 2: Composite density
    print("Generating Composite density plot...")
    plot_composite_density(composite, V_f_max, W_f_range, include_no_porosity=True)
    plt.savefig(os.path.join(output_dir, 'composite_density.png'), dpi=300, bbox_inches='tight')
    print("  Saved as: output/composite_density.png")
    plt.close()
    
    # Plot 3: Mechanical properties
    print("Generating Mechanical properties plot...")
    plot_mechanical_properties(composite, V_f_max, W_f_range)
    plt.savefig(os.path.join(output_dir, 'mechanical_properties.png'), dpi=300, bbox_inches='tight')
    print("  Saved as: output/mechanical_properties.png")
    plt.close()
    
    # Plot 4: Fiber length efficiency
    print("Generating Fiber length efficiency plot...")
    plot_fiber_length_efficiency(composite, W_f_range)
    plt.savefig(os.path.join(output_dir, 'fiber_length_efficiency.png'), dpi=300, bbox_inches='tight')
    print("  Saved as: output/fiber_length_efficiency.png")
    plt.close()
    
    # Plot all graphs in one figure
    print("Generating combined plot with all graphs...")
    fig = plot_all_graphs(composite, V_f_max, W_f_range)
    plt.savefig(os.path.join(output_dir, 'all_graphs_combined.png'), dpi=300, bbox_inches='tight')
    print("  Saved as: output/all_graphs_combined.png")
    plt.show()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


def test_case_2():
    """
    Additional test case with different material parameters.
    Example: Short fiber composite with higher porosity.
    """
    
    print("\n\n" + "=" * 60)
    print("TEST CASE 2: Short Fiber Composite with Porosity")
    print("=" * 60)
    
    # Matrix with some porosity
    matrix = Matrix(
        density=1200,  # kg/m³
        porosity=0.05,  # 5% porosity
        stiffness=4.0,  # GPa
        poisson_ratio=0.35
    )
    
    # Shorter fibers with porosity
    fiber = Fiber(
        density=2400,  # kg/m³
        porosity=0.02,  # 2% porosity
        stiffness=70,  # GPa
        orientation_efficiency_factor=0.8,  # Random orientation
        length_efficiency_factor=0.9,
        length=5,  # mm
        diameter=0.010  # mm
    )
    
    print("\nMatrix Properties:")
    print(f"  Density: {matrix.rho/1000:.2f} g/cm³")
    print(f"  Porosity: {matrix.alpha_pm}")
    print(f"  Stiffness: {matrix.E} GPa")
    
    print("\nFiber Properties:")
    print(f"  Density: {fiber.rho/1000:.2f} g/cm³")
    print(f"  Porosity: {fiber.alpha_pf}")
    print(f"  Stiffness: {fiber.E} GPa")
    print(f"  Aspect ratio: {fiber.aspect_ratio():.0f}")
    
    composite = Composite_mix(fiber=fiber, matrix=matrix)
    
    # Update fiber length efficiency
    G_m = matrix.shear_stiffness()
    fiber.eta1 = fiber.calculate_length_efficiency_factor(G_m)
    print(f"  Calculated η₁: {fiber.eta1:.4f}")
    
    V_f_max = 0.50
    test_case = Composite_case(composite_mix=composite, max_volume_fiber=V_f_max)
    W_f_trans = test_case.calculate_transition_weight_fiber()
    print(f"\nTransition weight fraction: {W_f_trans:.3f}")
    
    # Generate combined plot
    print("\nGenerating plots...")
    fig = plot_all_graphs(composite, V_f_max, W_f_range=(0.0, 1.0))
    plt.savefig('test_case_2_all_graphs.png', dpi=300, bbox_inches='tight')
    print("  Saved as: test_case_2_all_graphs.png")
    plt.show()
    
    print("\nTest Case 2 Complete")


if __name__ == "__main__":
    # Run test case 1 (main test case with parameters from document)
    test_case_1()
    
    # Uncomment to run test case 2
    # test_case_2()
