# Composite Material Analysis Tool

A comprehensive Python application for analyzing composite materials with fiber reinforcement.

## 🚀 Quick Start - Standalone Executable

**Download the ready-to-use executable (no Python installation required):**

📥 [**CompositeAnalysisToolAdvanced.exe**](https://github.com/Francois-dW/Composite_weight_fraction/raw/main/dist/CompositeAnalysisToolAdvanced.exe) (73.8 MB)

Simply download and run - includes all features and dependencies!

---

## 🎯 Version Overview

This project includes **two versions**:

### **Standard Version** (`composite_gui.py`)
- Single material analysis
- Quick calculations
- Basic plotting
- Ideal for: Individual calculations, learning, quick checks

### **Advanced Version** (`composite_gui_advanced.py`) ⭐ RECOMMENDED!
- **Multi-material comparison** (unlimited materials)
- **Naming system** (fiber, matrix, mix names)
- **Data management** (save/load configurations)
- **Experimental data integration** with CSV import/export
- **Curve fitting optimization** for parameter estimation
- **Flexible CSV export** with sampling options
- **Comparison plots** (side-by-side analysis)
- **Comparison table** (all materials at a glance)
- Ideal for: Research, material selection studies, optimization

**See [ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md) for complete guide!**

## Project Structure

```
Composite fiber/
├── src/                                # Source code
│   ├── Mech_tool_composite.py         # Core calculation classes and functions
│   ├── composite_gui.py               # Standard GUI
│   └── composite_gui_advanced.py      # Advanced GUI (NEW!)
├── tests/                              # Test files
│   └── test_composite.py              # Test cases and examples
├── output/                             # Generated plots and results
│   ├── weight_volume_relations.png
│   ├── composite_density.png
│   ├── mechanical_properties.png
│   ├── fiber_length_efficiency.png
│   └── all_graphs_combined.png
├── docs/                               # Documentation
│   ├── CORRECTIONS_SUMMARY.md         # Technical corrections documentation
│   ├── PROJECT_STRUCTURE.md           # Project organization
│   └── ADVANCED_FEATURES.md           # Advanced version guide (NEW!)
├── dist/                               # Standalone executable
│   ├── CompositeAnalysisTool.exe      # Windows executable
│   └── README.txt                      # Executable instructions
├── run_gui.py                          # Standard GUI launcher
├── run_gui_advanced.py                 # Advanced GUI launcher (NEW!)
└── README.md                           # This file
```

## Features

### Core Features (Both Versions)
- **Material Properties Calculation**
  - Matrix properties (density, stiffness, porosity)
  - Fiber properties (density, stiffness, geometry)
  - Composite properties (volume fractions, density, stiffness)

- **Advanced Analysis**
  - Case A and Case B analysis based on fiber weight fraction
  - Transition weight fraction calculation
  - Porosity effects with efficiency exponent
  - Fiber length efficiency factor calculation

- **Visualization**
  - Weight/volume relations plots
  - Composite density curves
  - Mechanical properties graphs
  - Fiber length efficiency plots

- **Graphical User Interface**
  - User-friendly input forms
  - Real-time calculations
  - Interactive plot generation
  - Fullscreen mode

### Advanced Version Exclusive Features ⭐
- **Multi-Material Management**
  - Add unlimited material configurations
  - Switch between materials with dropdown
  - Delete unwanted materials
  - No limitations on comparisons

- **Naming & Organization**
  - Name your fiber materials
  - Name your matrix materials
  - Name your composite mixes
  - Professional documentation support

- **Experimental Data Integration** 🆕
  - Import experimental data from CSV
  - Add/edit/delete data points manually
  - Visualize experimental vs. theoretical data
  - Support for partial data (only W_f required)

- **Curve Fitting Optimization** 🆕
  - Automatic parameter estimation from experimental data
  - Fit densities, porosities, V_f_max, stiffness
  - Multiple optimization targets (stiffness, density, volume fractions)
  - Smart initial value estimation
  - L-BFGS-B optimization algorithm
  - Saturation detection and handling

- **Data Management**
  - Save all configurations to JSON
  - Load previously saved configurations
  - Share material libraries with colleagues
  - Maintain standard material databases

- **Comparison Tools**
  - Side-by-side comparison table
  - Multi-material overlay plots
  - Color-coded visualization
  - Quick material selection

- **Flexible Export Options**
  - **Summary mode**: Current test values only
  - **Detailed mode**: Sampled data across W_f range
    - Custom sample count (10 to 10,000+)
    - Custom W_f range (e.g., 0.3 to 0.7)
  - CSV format for Excel/MATLAB/Python analysis
  - Individual result export to text files

## Installation

### Option 1: Standalone Executable (Easiest)
1. Download [CompositeAnalysisToolAdvanced.exe](https://github.com/Francois-dW/Composite_weight_fraction/raw/main/dist/CompositeAnalysisToolAdvanced.exe)
2. Run the executable - no installation needed!

### Option 2: Python Source Code

#### Requirements
- Python 3.8 or higher
- NumPy
- Matplotlib
- SciPy (for curve fitting)
- tkinter (usually included with Python)

#### Setup
1. Ensure you have Python installed
2. Install required packages:
   ```bash
   pip install numpy matplotlib scipy
   ```

## Usage

### Running the Standard GUI
```bash
python run_gui.py
```

### Running the Advanced GUI ⭐ (Recommended)
```bash
python run_gui_advanced.py
```

Or directly:
```bash
python src/composite_gui_advanced.py
```

### Running Tests
To run the test cases with example parameters:
```bash
python tests/test_composite.py
```

### Using as a Library
```python
from src.Mech_tool_composite import Matrix, Fiber, Composite_mix, Composite_case

# Create materials
matrix = Matrix(density=1160, porosity=0.0, stiffness=3.5)
fiber = Fiber(density=2600, porosity=0.0, stiffness=80, 
              orientation_efficiency_factor=1.0,
              length_efficiency_factor=0.95,
              length=10000, diameter=0.016)

# Create composite
composite = Composite_mix(fiber=fiber, matrix=matrix)

# Analyze specific case
case = Composite_case(composite_mix=composite, 
                     fiber_mass_fraction=0.40,
                     max_volume_fiber=0.60)

# Get results
V_f, V_m, V_p = case.calculate_volume_fractions_case_a()
density = case.calculate_composite_density()
stiffness = case.calculate_composite_stiffness()
```

## GUI Instructions

### Basic Usage
1. **Input Parameters**
   - Fill in material properties in the left panel
   - Default values are pre-loaded from reference case
   - All values can be modified

2. **Calculate**
   - Click "Calculate" button to compute results
   - Results appear in the "Results" tab

3. **Generate Plots**
   - Click "Generate Plots" to visualize data
   - Four plot tabs will be created:
     - Weight/Volume Relations
     - Composite Density
     - Mechanical Properties
     - Fiber Length Efficiency

4. **Reset**
   - Click "Reset to Defaults" to restore original values

### Advanced Features (Advanced Version)
5. **Multi-Material Management**
   - Use "Add Material" to create new configurations
   - Switch between materials using the dropdown
   - "Delete Current" removes selected material

6. **Experimental Data** 🆕
   - Go to "Experimental Data" tab
   - Click "Add Data Point" to enter measurements
   - "Import from CSV" to load multiple points
   - "Export to CSV" to save data

7. **Curve Fitting** 🆕
   - After adding experimental data, click "🔧 Fit Parameters"
   - Select which parameters to optimize
   - Choose optimization target (density, stiffness, or volume fractions)
   - Click "▶ Run Fitting" to optimize
   - Review results and "✓ Apply Parameters" if satisfied

8. **Save/Load**
   - "Save Configuration" to preserve all materials
   - "Load Configuration" to restore saved work

## Key Formulas

### Composite Stiffness
```
E_c = (η₀ η₁ V_f E_f + V_m E_m)(1 - V_p)^n
```

### Composite Density
```
ρ_c = V_f ρ_f + V_m ρ_m
```

### Matrix Shear Stiffness
```
G_m = E_m / (2(1 + ν_m))
```

### Fiber Length Efficiency
```
η₁ = 1 - tanh(βL/2) / (βL/2)
where β = 2G_m / (E_f ln(κ / aspect_ratio))
```

## Reference Case Parameters

- **Matrix:** ρ_m = 1.16 g/cm³, E_m = 3.5 GPa, α_pm = 0.00
- **Fiber:** ρ_f = 2.60 g/cm³, E_f = 80 GPa, α_pf = 0.00
- **Geometry:** L = 10000 mm, D = 0.016 mm (aspect ratio = 625,000)
- **Composite:** V_f_max = 0.60, n = 2

## Latest Updates (November 2025)

- ✅ **Curve fitting optimization** - Automatically estimate material parameters from experimental data
- ✅ **Experimental data integration** - Import/export CSV, visualize experimental vs. theoretical
- ✅ **Improved saturation detection** - Smart handling of Case A/B transitions
- ✅ **Standalone executable** - No Python installation required (73.8 MB download)
- ✅ **Fixed scipy compatibility** - Includes all required dependencies
- ✅ **Enhanced error handling** - Better division by zero protection

## Documentation

- [Advanced Features Guide](docs/ADVANCED_FEATURES.md) - Complete guide to advanced version
- [Experimental Data Guide](docs/EXPERIMENTAL_DATA_GUIDE.md) - Curve fitting and data integration
- [Project Structure](docs/PROJECT_STRUCTURE.md) - Technical documentation
- [Corrections Summary](docs/CORRECTIONS_SUMMARY.md) - Technical corrections log

## Authors

Composite Material Analysis Tool - Created with Python and love for materials science.

## License

This project is provided as-is for educational and research purposes.
