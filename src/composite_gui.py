"""
Composite Material Analysis GUI

A graphical user interface for composite material calculations and visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sys
import os

# Add current directory to path if running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))

from Mech_tool_composite import Matrix, Fiber, Composite_mix, Composite_case


class CompositeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Composite Material Analysis Tool")
        
        # Set window to fullscreen
        self.root.state('zoomed')  # Windows fullscreen
        
        # Alternative for cross-platform fullscreen
        # self.root.attributes('-fullscreen', True)
        
        # Bind Escape key to exit fullscreen (optional)
        self.root.bind('<Escape>', lambda e: self.root.state('normal'))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=3)
        main_container.rowconfigure(0, weight=1)
        
        # Create input panel (left side)
        self.create_input_panel(main_container)
        
        # Create results and plot panel (right side)
        self.create_results_panel(main_container)
        
        # Initialize with default values
        self.load_default_values()
        
    def create_input_panel(self, parent):
        """Create the left panel with input fields"""
        input_frame = ttk.Frame(parent, padding="5")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        input_frame.columnconfigure(1, weight=1)
        
        # Add scrollbar for input panel
        canvas = tk.Canvas(input_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        input_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)
        
        # Title
        title = ttk.Label(scrollable_frame, text="Input Parameters", 
                         font=('Arial', 14, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        row = 1
        
        # Matrix Parameters
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="Matrix Properties", 
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        self.matrix_density = self.create_input_row(
            scrollable_frame, row, "Matrix density (g/cm³):", "1.16")
        row += 1
        
        self.matrix_porosity = self.create_input_row(
            scrollable_frame, row, "Matrix porosity factor:", "0.00")
        row += 1
        
        self.matrix_stiffness = self.create_input_row(
            scrollable_frame, row, "Matrix stiffness (GPa):", "3.5")
        row += 1
        
        self.matrix_poisson = self.create_input_row(
            scrollable_frame, row, "Matrix Poisson's ratio:", "0.40")
        row += 1
        
        # Fiber Parameters
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="Fiber Properties", 
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        self.fiber_density = self.create_input_row(
            scrollable_frame, row, "Fiber density (g/cm³):", "2.60")
        row += 1
        
        self.fiber_porosity = self.create_input_row(
            scrollable_frame, row, "Fiber porosity factor:", "0.00")
        row += 1
        
        self.fiber_stiffness = self.create_input_row(
            scrollable_frame, row, "Fiber stiffness (GPa):", "80")
        row += 1
        
        self.fiber_eta0 = self.create_input_row(
            scrollable_frame, row, "Orientation efficiency (η₀):", "1.00")
        row += 1
        
        self.fiber_length = self.create_input_row(
            scrollable_frame, row, "Fiber length (mm):", "10000")
        row += 1
        
        self.fiber_diameter = self.create_input_row(
            scrollable_frame, row, "Fiber diameter (mm):", "0.016")
        row += 1
        
        # Composite Parameters
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="Composite Parameters", 
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        self.v_f_max = self.create_input_row(
            scrollable_frame, row, "Max fiber volume fraction:", "0.60")
        row += 1
        
        self.porosity_exp = self.create_input_row(
            scrollable_frame, row, "Porosity efficiency exponent (n):", "2")
        row += 1
        
        self.w_f_test = self.create_input_row(
            scrollable_frame, row, "Test fiber weight fraction:", "0.40")
        row += 1
        
        # Buttons
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Calculate", 
                  command=self.calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self.load_default_values).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Plots", 
                  command=self.generate_plots).pack(side=tk.LEFT, padx=5)
        
    def create_input_row(self, parent, row, label_text, default_value):
        """Helper to create a label and entry pair"""
        ttk.Label(parent, text=label_text).grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=3)
        
        entry = ttk.Entry(parent, width=15)
        entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
        entry.insert(0, default_value)
        
        return entry
    
    def create_results_panel(self, parent):
        """Create the right panel for results and plots"""
        results_frame = ttk.Frame(parent, padding="5")
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Results text area
        results_label = ttk.Label(results_frame, text="Calculation Results", 
                                 font=('Arial', 12, 'bold'))
        results_label.grid(row=0, column=0, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Results tab
        results_tab = ttk.Frame(self.notebook)
        self.notebook.add(results_tab, text="Results")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(results_tab)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_scrollbar = ttk.Scrollbar(text_frame)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(text_frame, wrap=tk.WORD, 
                                    font=('Courier', 10),
                                    yscrollcommand=text_scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.results_text.yview)
        
        # Plots tabs (will be created when plots are generated)
        self.plot_tabs = {}
        self.plot_figures = {}  # Store figure objects for saving
    
    def load_default_values(self):
        """Load default parameter values"""
        # Matrix
        self.matrix_density.delete(0, tk.END)
        self.matrix_density.insert(0, "1.16")
        self.matrix_porosity.delete(0, tk.END)
        self.matrix_porosity.insert(0, "0.00")
        self.matrix_stiffness.delete(0, tk.END)
        self.matrix_stiffness.insert(0, "3.5")
        self.matrix_poisson.delete(0, tk.END)
        self.matrix_poisson.insert(0, "0.40")
        
        # Fiber
        self.fiber_density.delete(0, tk.END)
        self.fiber_density.insert(0, "2.60")
        self.fiber_porosity.delete(0, tk.END)
        self.fiber_porosity.insert(0, "0.00")
        self.fiber_stiffness.delete(0, tk.END)
        self.fiber_stiffness.insert(0, "80")
        self.fiber_eta0.delete(0, tk.END)
        self.fiber_eta0.insert(0, "1.00")
        self.fiber_length.delete(0, tk.END)
        self.fiber_length.insert(0, "10000")
        self.fiber_diameter.delete(0, tk.END)
        self.fiber_diameter.insert(0, "0.016")
        
        # Composite
        self.v_f_max.delete(0, tk.END)
        self.v_f_max.insert(0, "0.60")
        self.porosity_exp.delete(0, tk.END)
        self.porosity_exp.insert(0, "2")
        self.w_f_test.delete(0, tk.END)
        self.w_f_test.insert(0, "0.40")
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Ready to calculate. Click 'Calculate' button.\n")
    
    def get_input_values(self):
        """Get all input values and validate them"""
        try:
            # Matrix
            matrix_density = float(self.matrix_density.get()) * 1000  # Convert to kg/m³
            matrix_porosity = float(self.matrix_porosity.get())
            matrix_stiffness = float(self.matrix_stiffness.get())
            matrix_poisson = float(self.matrix_poisson.get())
            
            # Fiber
            fiber_density = float(self.fiber_density.get()) * 1000  # Convert to kg/m³
            fiber_porosity = float(self.fiber_porosity.get())
            fiber_stiffness = float(self.fiber_stiffness.get())
            fiber_eta0 = float(self.fiber_eta0.get())
            fiber_length = float(self.fiber_length.get())
            fiber_diameter = float(self.fiber_diameter.get())
            
            # Composite
            v_f_max = float(self.v_f_max.get())
            porosity_exp = float(self.porosity_exp.get())
            w_f_test = float(self.w_f_test.get())
            
            return {
                'matrix': (matrix_density, matrix_porosity, matrix_stiffness, matrix_poisson),
                'fiber': (fiber_density, fiber_porosity, fiber_stiffness, fiber_eta0, 
                         fiber_length, fiber_diameter),
                'composite': (v_f_max, porosity_exp, w_f_test)
            }
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input value: {str(e)}")
            return None
    
    def calculate(self):
        """Perform calculations and display results"""
        values = self.get_input_values()
        if values is None:
            return
        
        try:
            # Create Matrix
            matrix = Matrix(
                density=values['matrix'][0],
                porosity=values['matrix'][1],
                stiffness=values['matrix'][2],
                poisson_ratio=values['matrix'][3]
            )
            
            # Create Fiber (with initial eta1 estimate)
            fiber = Fiber(
                density=values['fiber'][0],
                porosity=values['fiber'][1],
                stiffness=values['fiber'][2],
                orientation_efficiency_factor=values['fiber'][3],
                length_efficiency_factor=0.95,  # Initial estimate
                length=values['fiber'][4],
                diameter=values['fiber'][5]
            )
            
            # Calculate accurate eta1
            G_m = matrix.shear_stiffness()
            fiber.eta1 = fiber.calculate_length_efficiency_factor(G_m)
            
            # Create Composite mix
            composite = Composite_mix(fiber=fiber, matrix=matrix)
            
            # Calculate transition weight fraction
            v_f_max = values['composite'][0]
            test_case = Composite_case(
                composite_mix=composite,
                max_volume_fiber=v_f_max,
                porosity_efficiency_exponent=values['composite'][1]
            )
            w_f_trans = test_case.calculate_transition_weight_fiber()
            
            # Test with specified W_f
            w_f_test = values['composite'][2]
            case = Composite_case(
                composite_mix=composite,
                fiber_mass_fraction=w_f_test,
                max_volume_fiber=v_f_max,
                porosity_efficiency_exponent=values['composite'][1]
            )
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            
            output = "=" * 60 + "\n"
            output += "COMPOSITE MATERIAL ANALYSIS RESULTS\n"
            output += "=" * 60 + "\n\n"
            
            output += "MATRIX PROPERTIES:\n"
            output += f"  Density: {matrix.rho:.2f} kg/m³ ({matrix.rho/1000:.2f} g/cm³)\n"
            output += f"  Porosity factor (α_pm): {matrix.alpha_pm:.4f}\n"
            output += f"  Stiffness (E_m): {matrix.E:.2f} GPa\n"
            output += f"  Poisson's ratio (ν_m): {matrix.nu:.2f}\n"
            output += f"  Shear stiffness (G_m): {G_m:.3f} GPa\n\n"
            
            output += "FIBER PROPERTIES:\n"
            output += f"  Density: {fiber.rho:.2f} kg/m³ ({fiber.rho/1000:.2f} g/cm³)\n"
            output += f"  Porosity factor (α_pf): {fiber.alpha_pf:.4f}\n"
            output += f"  Stiffness (E_f): {fiber.E:.2f} GPa\n"
            output += f"  Orientation efficiency (η₀): {fiber.eta0:.2f}\n"
            output += f"  Length efficiency (η₁): {fiber.eta1:.6f}\n"
            output += f"  Length (L): {fiber.L:.2f} mm\n"
            output += f"  Diameter (D): {fiber.D:.4f} mm\n"
            output += f"  Aspect ratio (L/D): {fiber.aspect_ratio():.0f}\n\n"
            
            output += "COMPOSITE PARAMETERS:\n"
            output += f"  Max fiber volume fraction (V_f_max): {v_f_max:.2f}\n"
            output += f"  Porosity efficiency exponent (n): {values['composite'][1]:.0f}\n"
            output += f"  Transition fiber weight fraction (W_f_trans): {w_f_trans:.4f}\n\n"
            
            output += "-" * 60 + "\n"
            output += f"TEST CASE: W_f = {w_f_test:.2f}\n"
            output += "-" * 60 + "\n"
            output += f"Case type: {case.determine_case()}\n\n"
            
            if case.determine_case() == 'Case A':
                V_f, V_m, V_p = case.calculate_volume_fractions_case_a()
            else:
                V_f, V_m, V_p = case.calculate_volume_fractions_case_b()
            
            output += "VOLUME FRACTIONS:\n"
            output += f"  Fiber volume fraction (V_f): {V_f:.4f}\n"
            output += f"  Matrix volume fraction (V_m): {V_m:.4f}\n"
            output += f"  Porosity (V_p): {V_p:.4f}\n"
            output += f"  Sum check (should be 1.0): {V_f + V_m + V_p:.4f}\n\n"
            
            rho_c = case.calculate_composite_density()
            E_c = case.calculate_composite_stiffness()
            
            output += "COMPOSITE PROPERTIES:\n"
            output += f"  Composite density (ρ_c): {rho_c:.2f} kg/m³ ({rho_c/1000:.3f} g/cm³)\n"
            output += f"  Composite stiffness (E_c): {E_c:.2f} GPa\n"
            
            output += "\n" + "=" * 60 + "\n"
            output += "Calculation complete!\n"
            output += "Click 'Generate Plots' to visualize the results.\n"
            output += "=" * 60 + "\n"
            
            self.results_text.insert(tk.END, output)
            
            # Store composite for plotting
            self.composite = composite
            self.v_f_max = v_f_max
            self.porosity_exp = values['composite'][1]
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error during calculation:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def generate_plots(self):
        """Generate and display all plots"""
        if not hasattr(self, 'composite'):
            messagebox.showwarning("Warning", "Please run calculations first!")
            return
        
        try:
            # Remove old plot tabs
            for tab_name in list(self.plot_tabs.keys()):
                self.notebook.forget(self.plot_tabs[tab_name])
            self.plot_tabs.clear()
            self.plot_figures.clear()
            
            W_f_range = (0.0, 1.0)
            num_points = 100
            W_f_array = np.linspace(W_f_range[0], W_f_range[1], num_points)
            
            # Calculate data for all plots
            V_f_array = []
            V_m_array = []
            V_p_array = []
            rho_c_array = []
            rho_c_no_porosity_array = []
            E_c_array = []
            eta1_array = []
            
            G_m = self.composite.matrix.shear_stiffness()
            
            for W_f in W_f_array:
                case = Composite_case(
                    self.composite, 
                    fiber_mass_fraction=W_f, 
                    max_volume_fiber=self.v_f_max,
                    porosity_efficiency_exponent=self.porosity_exp
                )
                
                if case.determine_case() == 'Case A':
                    V_f, V_m, V_p = case.calculate_volume_fractions_case_a()
                else:
                    V_f, V_m, V_p = case.calculate_volume_fractions_case_b()
                
                V_f_array.append(V_f)
                V_m_array.append(V_m)
                V_p_array.append(V_p)
                
                rho_c = case.calculate_composite_density()
                rho_c_array.append(rho_c)
                
                total = V_f + V_m
                V_f_norm = V_f / total if total > 0 else 0
                V_m_norm = V_m / total if total > 0 else 0
                rho_no_p = V_f_norm * self.composite.fiber.rho + V_m_norm * self.composite.matrix.rho
                rho_c_no_porosity_array.append(rho_no_p)
                
                E_c = case.calculate_composite_stiffness()
                E_c_array.append(E_c)
                
                eta1 = self.composite.fiber.calculate_length_efficiency_factor(G_m)
                eta1_array.append(eta1)
            
            # Create Plot 1: Weight/volume relations
            self.create_plot_tab(
                "Weight/Volume Relations",
                W_f_array, V_f_array, V_m_array, V_p_array,
                xlabel='Fibre weight fraction',
                ylabel='Volume fractions',
                title='Weight/volume relations'
            )
            
            # Create Plot 2: Composite density
            self.create_density_plot_tab(
                "Composite Density",
                W_f_array, rho_c_array, rho_c_no_porosity_array
            )
            
            # Create Plot 3: Mechanical properties
            self.create_single_plot_tab(
                "Mechanical Properties",
                W_f_array, E_c_array,
                xlabel='Fibre weight fraction',
                ylabel='Composite stiffness (GPa)',
                title='Mechanical properties'
            )
            
            # Create Plot 4: Fiber length efficiency
            self.create_single_plot_tab(
                "Fiber Length Efficiency",
                W_f_array, eta1_array,
                xlabel='Fibre weight fraction',
                ylabel='Fibre length efficiency factor',
                title='Fibre length efficiency factor',
                ylim=(0.9, 1.0)
            )
            
            messagebox.showinfo("Success", "All plots generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error generating plots:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def create_plot_tab(self, tab_name, x_data, y1_data, y2_data, y3_data, 
                       xlabel, ylabel, title):
        """Create a tab with weight/volume relations plot"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=tab_name)
        self.plot_tabs[tab_name] = tab
        
        # Create container for plot and button
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(x_data, y1_data, 'r-', label='Fibre volume fraction', linewidth=2)
        ax.plot(x_data, y2_data, 'b-', label='Matrix volume fraction', linewidth=2)
        ax.plot(x_data, y3_data, 'y-', label='Porosity', linewidth=2)
        
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        fig.tight_layout()
        
        # Store figure for saving
        self.plot_figures[tab_name] = fig
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add save button below the plot
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(button_frame, text="Save This Plot", 
                  command=lambda: self.save_plot(tab_name)).pack(side=tk.RIGHT)
    
    def create_density_plot_tab(self, tab_name, x_data, y1_data, y2_data):
        """Create a tab with density plot"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=tab_name)
        self.plot_tabs[tab_name] = tab
        
        # Create container for plot and button
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Convert to g/cm³ for plotting
        y1_gcm3 = [y/1000 for y in y1_data]
        y2_gcm3 = [y/1000 for y in y2_data]
        
        ax.plot(x_data, y1_gcm3, 'k-', label='Composite density', linewidth=2)
        ax.plot(x_data, y2_gcm3, 'k--', label='Composite density, no porosity', linewidth=1)
        
        ax.set_xlabel('Fibre weight fraction', fontsize=10)
        ax.set_ylabel('Composite density (g/cm³)', fontsize=10)
        ax.set_title('Composite density', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        
        fig.tight_layout()
        
        # Store figure for saving
        self.plot_figures[tab_name] = fig
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add save button below the plot
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(button_frame, text="Save This Plot", 
                  command=lambda: self.save_plot(tab_name)).pack(side=tk.RIGHT)
    
    def create_single_plot_tab(self, tab_name, x_data, y_data, 
                              xlabel, ylabel, title, ylim=None):
        """Create a tab with a single line plot"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=tab_name)
        self.plot_tabs[tab_name] = tab
        
        # Create container for plot and button
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(x_data, y_data, 'k-', linewidth=2)
        
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        if ylim:
            ax.set_ylim(ylim)
        
        fig.tight_layout()
        
        # Store figure for saving
        self.plot_figures[tab_name] = fig
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add save button below the plot
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(button_frame, text="Save This Plot", 
                  command=lambda: self.save_plot(tab_name)).pack(side=tk.RIGHT)
    
    def save_plot(self, tab_name):
        """Save a specific plot to a chosen location"""
        if tab_name not in self.plot_figures:
            messagebox.showwarning("Warning", "No plot available to save.")
            return
        
        # Ask user for save location
        default_filename = tab_name.lower().replace(" ", "_").replace("/", "_") + ".png"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ],
            title="Save Plot As"
        )
        
        if file_path:
            try:
                fig = self.plot_figures[tab_name]
                fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save plot:\n{str(e)}")


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = CompositeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
