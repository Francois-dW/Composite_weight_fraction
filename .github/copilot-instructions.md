# Composite Material Analysis Tool - AI Agent Guide

## Project Overview

Python-based GUI application for analyzing fiber-reinforced composite materials. Uses Tkinter for UI, matplotlib for visualization, and implements theoretical models (Halpin-Tsai, rule of mixtures) for predicting mechanical properties based on constituent materials.

**Two GUI versions:**
- `composite_gui.py` - Standard single-material analysis
- `composite_gui_advanced.py` - Multi-material comparison with experimental data fitting (primary version)

## Architecture

### Core Components

1. **`src/Mech_tool_composite.py`** - Core calculation engine
   - `Matrix` class: matrix material properties (density, stiffness, porosity, Poisson's ratio)
   - `Fiber` class: fiber properties (density, stiffness, geometry, efficiency factors η₀/η₁)
   - `Composite_mix` class: combines fiber + matrix, calculates composite properties
   - `Composite_case` class: handles two analysis cases:
     - **Case A** (W_f < W_f_transition): Excess matrix, V_f limited by W_f
     - **Case B** (W_f ≥ W_f_transition): Excess fiber, V_f = V_f_max (saturation)
   - Plotting functions for weight/volume relations, density, stiffness, efficiency

2. **`src/composite_gui_advanced.py`** - Advanced GUI (3000+ lines)
   - `MaterialConfig` class: stores complete material configuration
   - `ExperimentalDataPoint` class: single measurement (W_f, V_f, E_c, ρ_c, etc.)
   - `CompositeGUIAdvanced` class: main application
   - `CurveFittingDialog` class: parameter optimization using scipy L-BFGS-B
   - Supports unlimited materials, comparison plots, CSV import/export
   - Tabbed interface: Inputs, Results, Comparison Table, Experimental Data, Help

### Data Flow

```
User Input → MaterialConfig → Composite_case.determine_case() 
  → Case A: calculate_volume_fractions_case_a() (excess matrix)
  → Case B: calculate_volume_fractions_case_b() (fiber saturation)
  → calculate_composite_stiffness() using E_c = (η₀·η₁·V_f·E_f + V_m·E_m)(1-V_p)^n
  → calculate_composite_density() using ρ_c = V_f·ρ_f + V_m·ρ_m
```

### Key Formulas

- **Composite stiffness**: `E_c = (η₀·η₁·V_f·E_f + V_m·E_m)(1-V_p)^n`
- **Fiber length efficiency**: `η₁ = 1 - tanh(βL/2)/(βL/2)` where `β = 2G_m/(E_f·ln(κ/aspect_ratio))`
- **Transition weight fraction**: Calculated from `V_f_max`, determines Case A vs B boundary
- **Volume fraction constraint**: `V_f + V_m + V_p = 1`

## Development Workflows

### Running the Application

```powershell
# Standard version
python run_gui.py

# Advanced version (recommended)
python run_gui_advanced.py

# Direct execution
python src/composite_gui_advanced.py
```

### Running Tests

```powershell
# Core calculation tests
python tests/test_composite.py

# Specific test scripts for experimental features
python test_alpha_pf_estimation.py    # Fiber porosity estimation
python test_fitting.py                # Curve fitting validation
python test_saturation_filtering.py   # Case A/B classification
```

### Building Executables

Uses PyInstaller with `.spec` files:

```powershell
# Standard version
pyinstaller CompositeAnalysisTool.spec

# Advanced version
pyinstaller CompositeAnalysisToolAdvanced.spec
```

**Critical for builds:** 
- `.spec` files include TCL/Tk runtime paths (conda env: `WTT1`)
- Must bundle `src/*.py` files explicitly
- `console=False` for GUI (no terminal window)

### Dependencies

Installed via conda environment `WTT1`:
- numpy, matplotlib, scipy (curve fitting)
- tkinter (included with Python, TCL/Tk required for PyInstaller)
- PIL (for image handling in GUI)

No `requirements.txt` exists - install manually: `pip install numpy matplotlib scipy`

## Project-Specific Conventions

### Units Convention

**CRITICAL:** Density units differ between API and GUI
- GUI displays: g/cm³ (user-friendly)
- Internal calculations: kg/m³ (SI units)
- **Conversion:** multiply by 1000 when creating Matrix/Fiber instances
- Stiffness: always GPa
- Length: mm, Diameter: mm

Example from `test_composite.py`:
```python
matrix_density = 1.16 * 1000  # GUI shows 1.16 g/cm³, pass 1160 kg/m³
matrix = Matrix(density=matrix_density, ...)
```

### Case Determination Logic

The application **automatically** determines analysis case:
- Does NOT require user to specify Case A vs B
- `Composite_case.__init__()` accepts various input combinations:
  - `fiber_mass_fraction` (W_f) OR `weight_fiber`/`weight_matrix`
  - `max_volume_fiber` (V_f_max) determines saturation point
- `determine_case()` compares W_f to transition point

### Experimental Data Integration & Curve Fitting

**Improved fitting algorithm (Nov 2025):**
1. **Saturation detection**: Automatically finds where V_f plateaus by checking for constant values
   - Includes first saturation point in fitting data
   - Excludes fully saturated points to avoid confounding porosity estimates
2. **Smart initial estimates**: Solves 2-point system of equations for densities
   - Uses ρ_c = V_f·ρ_f + V_m·ρ_m for two unsaturated points
   - Estimates fiber porosity from mean V_p/V_f ratio
3. **Proper data weighting**: Volume fractions weighted 10x higher than density (more reliable)
4. **Tight bounds**: Matrix porosity bounded 0-0.05 (typically non-porous)

**To get expected results (ρ_f=2.1, ρ_m=1.0, α_pf=0.21, α_pm=0.0, V_f_max=0.224):**
1. Import `sample_experimental_data.csv` via "Import from CSV" button
2. Click "🔧 Fit Parameters" button
3. Select optimization target: **"Minimize volume fraction errors (V_f, V_m, V_p)"**
4. Check these 4 parameters ONLY (DO NOT check Matrix porosity):
   - ☑ Matrix density (ρ_m)
   - ☑ Fiber density (ρ_f)
   - ☑ Fiber porosity factor (α_pf)
   - ☑ Max fiber volume fraction (V_f_max)
   - ☐ Matrix porosity factor (α_pm) - LEAVE UNCHECKED (fixed at 0)
5. Click "▶ Run Fitting" - should detect 3 unsaturated points, achieve error ~2.7e-4
6. Click "✓ Apply Parameters" to update inputs

**Critical for successful fitting:**
- Need 3+ points up to saturation for robust estimation
- Volume fraction target works best (V_f/V_m/V_p more reliable than density)
- Algorithm auto-detects saturation and uses smart initial guesses
- Validates against `test_improved_fitting.py` (fiber_density: 0.96%, matrix_density: 0.24%, v_f_max: 0.29% error)

### File Format Conventions

**Configuration files (`.json`):**
```json
{
  "materials": [
    {
      "name": "...",
      "fiber_name": "...",
      "matrix_name": "...",
      "inputs": {...},
      "results": {...},
      "experimental_data": [...]
    }
  ]
}
```

**Experimental data CSV:**
```csv
W_f,V_f,V_m,V_p,E_c,rho_c,Notes
0.359,0.201,0.755,0.043,25.5,1.178,Sample 1
```
- W_f required, others optional
- Alternative column names: `Wf`, `rho_c`/`density`
- Import: `CurveFittingDialog` or "Import from CSV" button

### Plotting Multi-Material Comparisons

When generating plots with multiple materials:
- Use `colorsys.hsv_to_rgb()` for automatic color assignment
- Theoretical curves: solid lines
- Experimental points: scatter markers (○□△ for V_f/V_m/V_p)
- Color consistency: same material = same color across all tabs
- Legend: `f"{material.name} (theory)"` / `f"{material.name} (exp)"`

## Common Pitfalls

1. **Mixing density units** - Always convert g/cm³ → kg/m³ for calculations
2. **Forgetting case transition** - Case B behavior differs fundamentally from Case A
3. **Optimizing all parameters** - Leads to overfitting; fit 3-4 parameters max
4. **Ignoring saturation** - Don't use Case B points for estimating fiber porosity (α_pf)
5. **Path issues in specs** - Update conda env paths if rebuilding executables

## Testing Strategy

- **Core logic tests:** `tests/test_composite.py` validates formulas with reference case
- **Standalone scripts:** `test_*.py` in root validate specific features (fitting, filtering)
- **No pytest/unittest framework** - tests are executable Python scripts with print statements
- Run tests when modifying `Mech_tool_composite.py` calculations

## Documentation

Extensive markdown documentation in `docs/`:
- `EXPERIMENTAL_DATA_GUIDE.md` - Experimental data and curve fitting
- `WORKFLOW_DIAGRAM.md` - ASCII workflow diagrams
- `README.md` in `docs/` indexes all documentation

Main README provides feature comparison, but for implementation details check source comments.

## Quick Reference

**Add new material property calculation:**
1. Add to `Composite_mix` or `Composite_case` class
2. Update `perform_calculation()` in GUI
3. Add display in `display_results()`
4. Update CSV export if needed (`export_detailed_csv()`)

**Add experimental data field:**
1. Update `ExperimentalDataPoint` class
2. Modify `ExperimentalDataDialog` form
3. Update CSV import/export parsers
4. Add to plotting if visualizing

**Debug calculation mismatch:**
1. Check Case A vs B - use `print(case.determine_case())`
2. Verify units (density g/cm³ vs kg/m³)
3. Compare with `test_composite.py` reference values
4. Check efficiency factors: η₁ auto-calculated, η₀ user input
