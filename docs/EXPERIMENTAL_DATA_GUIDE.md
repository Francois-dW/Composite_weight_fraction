# Experimental Data & Curve Fitting Guide

## Overview

The advanced version of the Composite Material Analysis Tool now includes comprehensive experimental data management and curve fitting capabilities. This allows you to:

1. **Add experimental measurements** to compare with theoretical predictions
2. **Import/export data** from CSV files
3. **Visualize experimental points** on all comparison plots
4. **Fit theoretical parameters** to match your experimental data

---

## Features

### 1. Experimental Data Management

#### Adding Data Points
- Click **"📊 Experimental Data"** tab
- Click **"➕ Add Data Point"** button
- Fill in the dialog:
  - **W_f (required)**: Fiber weight fraction
  - **V_f (optional)**: Measured fiber volume fraction
  - **V_m (optional)**: Measured matrix volume fraction
  - **V_p (optional)**: Measured porosity
  - **E_c (optional)**: Measured composite stiffness [GPa]
  - **ρ_c (optional)**: Measured composite density [g/cm³]
  - **Notes**: Additional information about the measurement

#### Editing Data Points
- Select a data point in the table
- Click **"✏️ Edit Selected"**
- Modify values and click OK

#### Deleting Data Points
- Select a data point
- Click **"🗑️ Delete Selected"**
- Confirm deletion

### 2. Import/Export Experimental Data

#### Import from CSV
Click **"📂 Import from CSV"** and provide a CSV file with columns:
```csv
W_f,V_f,V_m,V_p,E_c,rho_c,Notes
0.30,0.25,0.70,0.05,25.5,1.85,Test sample 1
0.40,0.33,0.63,0.04,35.2,1.95,Test sample 2
0.50,0.42,0.54,0.04,45.8,2.05,Test sample 3
```

**Notes:**
- W_f is required
- Other columns are optional (leave empty or use "-" for missing values)
- Column names are case-insensitive
- Alternative column names are supported (e.g., "Wf" for "W_f")

#### Export to CSV
Click **"📊 Export to CSV"** to save current material's experimental data

### 3. Visualization

When you click **"Generate Plots"**, experimental data points automatically appear on the relevant plots:

- **Weight/Volume Relations**: Shows experimental V_f, V_m, V_p as scatter points
  - Circles (○) = V_f measurements
  - Squares (□) = V_m measurements
  - Triangles (△) = V_p measurements

- **Density Comparison**: Shows experimental density as scatter points
  - Circles (○) = ρ_c measurements

- **Stiffness Comparison**: Shows experimental stiffness as scatter points
  - Circles (○) = E_c measurements

**Color Scheme:**
- Each material uses consistent colors across plots
- Experimental points use the same color as their theoretical curves
- Black edges on scatter points improve visibility

### 4. Curve Fitting

#### Opening the Curve Fitting Dialog
1. Add experimental data points to your material
2. Calculate the material properties (click "Calculate")
3. Click **"🔧 Fit Parameters"** button
4. The Curve Fitting Dialog opens

#### Selecting Optimization Target

Choose what to optimize:

- **Minimize stiffness (E_c) error only**: Fits to match E_c measurements
- **Minimize density (ρ_c) error only**: Fits to match density measurements  
- **Minimize combined error**: Fits to match both E_c and ρ_c (recommended)
- **Minimize volume fraction errors**: Fits to match V_f, V_m, V_p measurements

#### Selecting Parameters to Optimize

Choose which parameters to adjust:

**Matrix Properties:**
- ☑ Matrix stiffness (E_m) - Default: ON
- ☐ Matrix Poisson's ratio (ν_m) - Default: OFF

**Fiber Properties:**
- ☑ Fiber stiffness (E_f) - Default: ON
- ☑ Orientation efficiency (η₀) - Default: ON

**Composite Parameters:**
- ☑ Max fiber volume fraction (V_f_max) - Default: ON
- ☐ Porosity exponent (n) - Default: OFF

**Recommendations:**
- Start with default selections (4 parameters)
- Add more parameters if fit quality is poor
- Avoid optimizing too many parameters simultaneously (overfitting risk)

#### Running the Optimization

1. Click **"▶ Run Fitting"**
2. Wait for optimization to complete (typically 5-30 seconds)
3. Review the results:
   - Final error value (lower is better)
   - Original vs fitted parameter values
   - Percent change for each parameter

#### Applying Fitted Parameters

1. Review the fitted parameters
2. Click **"✓ Apply Parameters"**
3. Parameters are automatically:
   - Updated in the input form
   - Recalculated
   - Ready for visualization

---

## Typical Workflow

### Workflow 1: Validate Theoretical Model

1. **Define material** with known properties
2. **Calculate** theoretical curves
3. **Add experimental data** from lab tests
4. **Generate plots** to visualize comparison
5. **Assess agreement** between theory and experiment

### Workflow 2: Determine Unknown Properties

1. **Add experimental data** from measurements
2. **Set initial estimates** for material properties
3. **Calculate** to establish baseline
4. **Open curve fitting dialog**
5. **Select parameters** to optimize
6. **Run fitting** to find best-fit parameters
7. **Apply parameters** and regenerate plots
8. **Iterate** if needed with different parameter selections

### Workflow 3: Compare Multiple Materials

1. **Create multiple materials** (use "+ Add Material")
2. **Add experimental data** to each material
3. **Calculate all** materials
4. **Fit parameters** for each material individually
5. **Generate plots** to see all materials and data together

---

## Tips & Best Practices

### Data Quality
- ✓ Use at least 5-10 experimental points for reliable fitting
- ✓ Spread measurements across different W_f values
- ✓ Include measurements in the range of interest
- ✗ Avoid clustering all points at similar W_f values

### Parameter Selection
- ✓ Start with fewer parameters (3-4)
- ✓ Fit parameters you're most uncertain about
- ✓ Keep well-known properties fixed
- ✗ Don't optimize all parameters at once (overfitting)

### Optimization Targets
- Use **"combined error"** when you have both E_c and ρ_c data
- Use **"stiffness only"** for mechanical testing data
- Use **"density only"** for composition/porosity studies
- Use **"volume fractions"** when you have microstructure measurements

### Interpreting Results
- **Large changes (>50%)**: Original estimates were poor, or model may not fit well
- **Small changes (<10%)**: Good initial estimates, minor refinement
- **Negative values**: Check bounds and physical reasonableness
- **High final error**: Model may be inadequate, or data has high scatter

### Troubleshooting

**Problem: "No suitable experimental data for selected target"**
- Solution: Add measurements for the selected target (E_c, ρ_c, or volume fractions)

**Problem: Optimization fails or gives unreasonable values**
- Check experimental data for errors
- Try fewer parameters
- Verify initial estimates are physically reasonable

**Problem: Poor fit quality after optimization**
- Add more experimental data points
- Consider that theoretical model may have limitations
- Check for systematic measurement errors

---

## Data Persistence

### Saving Configurations
- Experimental data is automatically saved with material configurations
- Use **"💾 Save Configuration"** to save everything to JSON
- All experimental points are preserved

### Loading Configurations
- Use **"📂 Load Configuration"** to restore materials
- Experimental data loads automatically
- Recalculate materials after loading

---

## Advanced Features

### Batch Fitting
For multiple materials:
1. Add experimental data to all materials
2. Fit each material individually using the same parameter selections
3. Compare fitted parameter values across materials
4. Identify trends or outliers

### Sensitivity Analysis
To understand parameter importance:
1. Fit with one parameter at a time
2. Compare error reduction for each parameter
3. Identify which parameters most affect the fit
4. Focus on optimizing the most sensitive parameters

### Custom CSV Format
Your CSV can include any subset of columns:
```csv
W_f,E_c,Notes
0.30,25.5,Sample A
0.40,35.2,Sample B
```

Or:
```csv
W_f,rho_c
0.30,1.85
0.40,1.95
```

---

## Optimization Algorithm

The curve fitting uses **L-BFGS-B** algorithm:
- Bounded optimization (parameters stay within physical ranges)
- Efficient for 1-10 parameters
- Uses gradient-based search
- Tolerates noisy objective functions

**Parameter Bounds:**
- Matrix stiffness: 0.5 - 10.0 GPa
- Matrix Poisson: 0.2 - 0.5
- Fiber stiffness: 10.0 - 500.0 GPa
- Orientation efficiency: 0.1 - 1.0
- V_f_max: 0.3 - 0.9
- Porosity exponent: 1.0 - 5.0

---

## Example Use Cases

### Example 1: Carbon Fiber / Epoxy Characterization
```
Given: 
- Lab measurements of E_c at W_f = [0.3, 0.4, 0.5, 0.6]
- Known: Matrix E_m ≈ 3.5 GPa, Fiber E_f ≈ 230 GPa (from datasheets)
- Unknown: Actual fiber orientation efficiency, V_f_max

Process:
1. Add E_c measurements as experimental data
2. Set E_m = 3.5 GPa, E_f = 230 GPa (fixed)
3. Optimize: η₀ and V_f_max only
4. Apply fitted parameters
5. Use fitted η₀ for future designs with same manufacturing process
```

### Example 2: Natural Fiber Composite Development
```
Given:
- Multiple batches with varying W_f
- Measured both E_c and ρ_c for each
- Uncertain about effective fiber properties

Process:
1. Import CSV with all batch data
2. Initial estimates from literature
3. Optimize: E_f, η₀, V_f_max
4. Compare fitted E_f to literature (validate)
5. Use fitted parameters for material selection
```

### Example 3: Quality Control
```
Given:
- Production samples with target W_f = 0.45
- Measured V_f, V_m, V_p from microscopy
- Need to verify manufacturing consistency

Process:
1. Add volume fraction measurements
2. Calculate theoretical values
3. Compare experimental scatter points vs theoretical line
4. Identify outlier batches
5. Adjust process parameters if systematic deviation exists
```

---

## Future Enhancements

Potential additions for future versions:
- Weighted fitting (trust some measurements more than others)
- Uncertainty estimation (confidence intervals on fitted parameters)
- Multi-objective optimization (Pareto fronts)
- Automated parameter sensitivity analysis
- Monte Carlo uncertainty propagation
- Statistical goodness-of-fit metrics (R², RMSE)

---

## Support

For questions or issues:
1. Check the main **"📖 Help"** tab for general usage
2. Review this guide for experimental data features
3. Verify input data format and units
4. Check console for detailed error messages

---

**Version**: 1.0 with Experimental Data Support  
**Last Updated**: November 2025
