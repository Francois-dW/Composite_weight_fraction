"""
Composite Material Analysis GUI - Advanced Version

A graphical user interface for composite material calculations and visualization
with multi-material comparison and data management capabilities.

FILE STRUCTURE:
    Lines 1-90:     Imports & Helper Classes (Toast notifications)
    Lines 92-125:   Data Classes (ExperimentalDataPoint, MaterialConfig)
    Lines 127-234:  Main CompositeGUIAdvanced class initialization
    Lines 235-285:  Material management (add/delete/switch)
    Lines 287-930:  UI creation (panels, widgets, tabs)
    Lines 931-1100: Event handlers & state management
    Lines 1101-1263: Core calculation methods
    Lines 1264-1502: File I/O (save/load/export)
    Lines 1503-2198: Experimental data management
    Lines 2199-2576: Plotting & visualization
    Lines 2577+:    Dialog classes (experimental data, curve fitting)

MAIN CLASSES:
    - ToastNotification: Temporary success/error messages
    - ExperimentalDataPoint: Single experimental measurement
    - MaterialConfig: Complete material configuration
    - CompositeGUIAdvanced: Main application window
    - ExperimentalDataDialog: Add/edit experimental data
    - CurveFittingDialog: Parameter optimization dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sys
import os
import json
import csv
from datetime import datetime
from scipy.optimize import minimize, differential_evolution

# Add current directory to path if running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))

from Mech_tool_composite import Matrix, Fiber, Composite_mix, Composite_case


class ToastNotification:
    """Auto-dismissing toast notification that appears in the corner"""
    def __init__(self, parent, message, duration=2000, type="success"):
        self.parent = parent
        
        # Create toplevel window
        self.toast = tk.Toplevel(parent)
        self.toast.withdraw()  # Hide initially
        self.toast.overrideredirect(True)  # No window decorations
        
        # Configure appearance based on type
        if type == "success":
            bg_color = "#28a745"  # Green
            fg_color = "white"
            icon = "✓"
        elif type == "error":
            bg_color = "#dc3545"  # Red
            fg_color = "white"
            icon = "✗"
        elif type == "warning":
            bg_color = "#ffc107"  # Yellow
            fg_color = "black"
            icon = "⚠"
        else:  # info
            bg_color = "#17a2b8"  # Blue
            fg_color = "white"
            icon = "ℹ"
        
        # Create frame with padding
        frame = tk.Frame(self.toast, bg=bg_color, padx=15, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon and message
        msg_frame = tk.Frame(frame, bg=bg_color)
        msg_frame.pack()
        
        tk.Label(msg_frame, text=icon, bg=bg_color, fg=fg_color, 
                font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(msg_frame, text=message, bg=bg_color, fg=fg_color,
                font=('Arial', 10), wraplength=300, justify=tk.LEFT).pack(side=tk.LEFT)
        
        # Position in bottom-right corner
        self.toast.update_idletasks()
        screen_width = self.toast.winfo_screenwidth()
        screen_height = self.toast.winfo_screenheight()
        toast_width = self.toast.winfo_width()
        toast_height = self.toast.winfo_height()
        
        x = screen_width - toast_width - 20
        y = screen_height - toast_height - 60
        
        self.toast.geometry(f"+{x}+{y}")
        self.toast.deiconify()  # Show the toast
        
        # Auto-dismiss after duration
        self.toast.after(duration, self.fade_out)
    
    def fade_out(self):
        """Destroy the toast notification"""
        try:
            self.toast.destroy()
        except:
            pass


class ExperimentalDataPoint:
    """Data class for a single experimental measurement"""
    def __init__(self, W_f, V_f=None, V_m=None, V_p=None, E_c=None, rho_c=None, notes=""):
        self.W_f = W_f  # Required
        self.V_f = V_f  # Optional
        self.V_m = V_m  # Optional
        self.V_p = V_p  # Optional
        self.E_c = E_c  # Optional
        self.rho_c = rho_c  # Optional
        self.notes = notes
    
    def to_dict(self):
        return {
            'W_f': self.W_f,
            'V_f': self.V_f,
            'V_m': self.V_m,
            'V_p': self.V_p,
            'E_c': self.E_c,
            'rho_c': self.rho_c,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            W_f=data['W_f'],
            V_f=data.get('V_f'),
            V_m=data.get('V_m'),
            V_p=data.get('V_p'),
            E_c=data.get('E_c'),
            rho_c=data.get('rho_c'),
            notes=data.get('notes', '')
        )


class MaterialConfig:
    """Data class to store a complete material configuration"""
    def __init__(self, name="Untitled", fiber_name="Generic Fiber", matrix_name="Generic Matrix"):
        self.name = name
        self.fiber_name = fiber_name
        self.matrix_name = matrix_name
        
        # Matrix properties (default values)
        self.matrix_density = 1.16
        self.matrix_porosity = 0.00
        self.matrix_stiffness = 3.5
        self.matrix_poisson = 0.40
        
        # Fiber properties (default values)
        self.fiber_density = 2.60
        self.fiber_porosity = 0.00
        self.fiber_stiffness = 80.0
        self.fiber_eta0 = 1.00
        self.fiber_length = 10000.0
        self.fiber_diameter = 0.016
        
        # Composite parameters
        self.v_f_max = 0.60
        self.porosity_exp = 2.0
        self.w_f_test = 0.40
        
        # Results (calculated)
        self.results = None
        self.timestamp = None
        
        # Experimental data
        self.experimental_data = []  # List of ExperimentalDataPoint objects
        
        # Plotting control
        self.plot_enabled = True  # Whether to include this material in plots
    
    def to_dict(self):
        """Convert configuration to dictionary (excluding non-serializable results)"""
        return {
            'name': self.name,
            'fiber_name': self.fiber_name,
            'matrix_name': self.matrix_name,
            'matrix': {
                'density': self.matrix_density,
                'porosity': self.matrix_porosity,
                'stiffness': self.matrix_stiffness,
                'poisson': self.matrix_poisson
            },
            'fiber': {
                'density': self.fiber_density,
                'porosity': self.fiber_porosity,
                'stiffness': self.fiber_stiffness,
                'eta0': self.fiber_eta0,
                'length': self.fiber_length,
                'diameter': self.fiber_diameter
            },
            'composite': {
                'v_f_max': self.v_f_max,
                'porosity_exp': self.porosity_exp,
                'w_f_test': self.w_f_test
            },
            'timestamp': self.timestamp,
            'experimental_data': [pt.to_dict() for pt in self.experimental_data],
            'plot_enabled': self.plot_enabled
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create configuration from dictionary"""
        config = cls(
            name=data.get('name', 'Untitled'),
            fiber_name=data.get('fiber_name', 'Generic Fiber'),
            matrix_name=data.get('matrix_name', 'Generic Matrix')
        )
        
        if 'matrix' in data:
            config.matrix_density = data['matrix'].get('density', 1.16)
            config.matrix_porosity = data['matrix'].get('porosity', 0.00)
            config.matrix_stiffness = data['matrix'].get('stiffness', 3.5)
            config.matrix_poisson = data['matrix'].get('poisson', 0.40)
        
        if 'fiber' in data:
            config.fiber_density = data['fiber'].get('density', 2.60)
            config.fiber_porosity = data['fiber'].get('porosity', 0.00)
            config.fiber_stiffness = data['fiber'].get('stiffness', 80.0)
            config.fiber_eta0 = data['fiber'].get('eta0', 1.00)
            config.fiber_length = data['fiber'].get('length', 10000.0)
            config.fiber_diameter = data['fiber'].get('diameter', 0.016)
        
        if 'composite' in data:
            config.v_f_max = data['composite'].get('v_f_max', 0.60)
            config.porosity_exp = data['composite'].get('porosity_exp', 2.0)
            config.w_f_test = data['composite'].get('w_f_test', 0.40)
        
        config.timestamp = data.get('timestamp')
        
        # Load experimental data
        if 'experimental_data' in data:
            config.experimental_data = [ExperimentalDataPoint.from_dict(pt) 
                                       for pt in data['experimental_data']]
        
        # Load plot enabled flag
        config.plot_enabled = data.get('plot_enabled', True)
        
        return config


class CompositeGUIAdvanced:
    def __init__(self, root):
        self.root = root
        self.root.title("Composite Material Analysis Tool - Advanced")
        
        # Set window to fullscreen
        self.root.state('zoomed')
        
        # Bind Escape key to exit fullscreen
        self.root.bind('<Escape>', lambda e: self.root.state('normal'))
        
        # Material configurations list
        self.materials = []
        self.current_material_index = 0
        
        # Add first material configuration
        self.add_material()
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main container with PanedWindow for resizable panels
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Create frames for left and right panels
        left_frame = ttk.Frame(main_container, padding="5")
        right_frame = ttk.Frame(main_container, padding="5")
        
        # Add frames to PanedWindow
        main_container.add(left_frame, weight=1)
        main_container.add(right_frame, weight=3)
        
        # Create input panel (left side)
        self.create_input_panel(left_frame)
        
        # Create results and plot panel (right side)
        self.create_results_panel(right_frame)
        
        # Load first material
        self.load_material(0)
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def show_toast(self, message, type="success", duration=2000):
        """Show a toast notification"""
        ToastNotification(self.root, message, duration, type)
    
    # ========================================================================
    # MATERIAL MANAGEMENT
    # ========================================================================
    
    def add_material(self):
        """Add a new material configuration"""
        material_num = len(self.materials) + 1
        new_material = MaterialConfig(
            name=f"Mix {material_num}",
            fiber_name=f"Fiber {material_num}",
            matrix_name=f"Matrix {material_num}"
        )
        self.materials.append(new_material)
        return len(self.materials) - 1
    
    # ========================================================================
    # UI CREATION - INPUT PANEL
    # ========================================================================
    
    def create_input_panel(self, parent):
        """Create the left panel with input fields and material management"""
        # Parent is already the left frame from PanedWindow
        input_frame = parent
        
        # Configure grid: canvas expands, scrollbar has fixed width
        input_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=0)  # Fixed width for scrollbar
        
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
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # Bind mouse wheel events when cursor enters/leaves the input panel
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure scrollable_frame columns for consistent spacing
        scrollable_frame.columnconfigure(0, weight=0)  # Labels - fixed width
        scrollable_frame.columnconfigure(1, weight=1)  # Input fields - expand
        
        # Title
        title = ttk.Label(scrollable_frame, text="Material Configuration", 
                         font=('Arial', 14, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        row = 1
        
        # Material selector and management
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Material selection frame
        material_select_frame = ttk.Frame(scrollable_frame)
        material_select_frame.grid(row=row, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(material_select_frame, text="Current Material:", 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.material_combo = ttk.Combobox(material_select_frame, state='readonly', width=20)
        self.material_combo.pack(side=tk.LEFT, padx=5)
        self.material_combo.bind('<<ComboboxSelected>>', self.on_material_selected)
        
        ttk.Button(material_select_frame, text="+ Add Material", 
                  command=self.add_new_material).pack(side=tk.LEFT, padx=2)
        ttk.Button(material_select_frame, text="🗑 Delete", 
                  command=self.delete_material).pack(side=tk.LEFT, padx=2)
        
        row += 1
        
        # Naming section
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="Naming & Identification", 
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        self.mix_name = self.create_input_row(
            scrollable_frame, row, "Mix Name:", "Mix 1")
        row += 1
        
        self.fiber_name = self.create_input_row(
            scrollable_frame, row, "Fiber Name:", "Generic Fiber")
        row += 1
        
        self.matrix_name = self.create_input_row(
            scrollable_frame, row, "Matrix Name:", "Generic Matrix")
        row += 1
        
        # Plot control checkbox
        plot_control_frame = ttk.Frame(scrollable_frame)
        plot_control_frame.grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        self.plot_enabled_var = tk.BooleanVar(value=True)
        self.plot_enabled_check = ttk.Checkbutton(
            plot_control_frame, 
            text="📊 Include in plots (theoretical + experimental)", 
            variable=self.plot_enabled_var,
            command=self.on_plot_enabled_changed
        )
        self.plot_enabled_check.pack(side=tk.LEFT, padx=5)
        row += 1
        
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
                  command=self.calculate_current).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(button_frame, text="Calculate All", 
                  command=self.calculate_all).pack(side=tk.LEFT, padx=5, pady=2)
        row += 1
        
        button_frame2 = ttk.Frame(scrollable_frame)
        button_frame2.grid(row=row, column=0, columnspan=2, pady=5)
        
        ttk.Button(button_frame2, text="Reset to Defaults", 
                  command=self.reset_defaults).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(button_frame2, text="Generate Plots", 
                  command=self.generate_plots).pack(side=tk.LEFT, padx=5, pady=2)
        row += 1
        
        # Data management buttons
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(scrollable_frame, text="Data Management", 
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        data_button_frame = ttk.Frame(scrollable_frame)
        data_button_frame.grid(row=row, column=0, columnspan=2, pady=5)
        
        ttk.Button(data_button_frame, text="💾 Save Configuration", 
                  command=self.save_configuration).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(data_button_frame, text="📂 Load Configuration", 
                  command=self.load_configuration).pack(side=tk.LEFT, padx=5, pady=2)
        row += 1
        
        export_button_frame = ttk.Frame(scrollable_frame)
        export_button_frame.grid(row=row, column=0, columnspan=2, pady=5)
        
        ttk.Button(export_button_frame, text="📊 Export Current Results", 
                  command=self.export_results).pack(side=tk.LEFT, padx=5, pady=2)
        row += 1
        
        export_button_frame2 = ttk.Frame(scrollable_frame)
        export_button_frame2.grid(row=row, column=0, columnspan=2, pady=5)
        
        ttk.Button(export_button_frame2, text="📈 Export Summary CSV", 
                  command=self.export_summary_csv).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(export_button_frame2, text="📊 Export Detailed CSV", 
                  command=self.export_detailed_csv).pack(side=tk.LEFT, padx=5, pady=2)
    
    def create_input_row(self, parent, row, label_text, default_value):
        """Helper to create a label and entry pair"""
        ttk.Label(parent, text=label_text).grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=3)
        
        entry = ttk.Entry(parent, width=15)
        entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
        entry.insert(0, default_value)
        
        return entry
    
    # ========================================================================
    # UI CREATION - RESULTS & TABBED INTERFACE
    # ========================================================================
    
    def create_results_panel(self, parent):
        """Create the right panel for results and plots"""
        # Parent is already the right frame from PanedWindow
        results_frame = parent
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
                                    font=('Courier', 9),
                                    yscrollcommand=text_scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.results_text.yview)
        
        # Comparison tab
        comparison_tab = ttk.Frame(self.notebook)
        self.notebook.add(comparison_tab, text="Comparison Table")
        
        # Create comparison table
        self.create_comparison_table(comparison_tab)
        
        # Experimental Data tab
        exp_data_tab = ttk.Frame(self.notebook)
        self.notebook.add(exp_data_tab, text="📊 Experimental Data")
        self.create_experimental_data_tab(exp_data_tab)
        
        # Help tab
        help_tab = ttk.Frame(self.notebook)
        self.notebook.add(help_tab, text="📖 Help")
        self.create_help_tab(help_tab)
        
        # Plots tabs (will be created when plots are generated)
        self.plot_tabs = {}
        self.plot_figures = {}
    
    def create_comparison_table(self, parent):
        """Create a table to compare all materials"""
        # Frame for table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview for table
        self.comparison_tree = ttk.Treeview(table_frame, 
                                           yscrollcommand=vsb.set,
                                           xscrollcommand=hsb.set,
                                           selectmode='browse')
        
        vsb.config(command=self.comparison_tree.yview)
        hsb.config(command=self.comparison_tree.xview)
        
        # Define columns
        columns = ('Mix', 'Fiber', 'Matrix', 'W_f', 'V_f', 'ρ_c (g/cm³)', 
                  'E_c (GPa)', 'Case', 'Plot', 'Status')
        self.comparison_tree['columns'] = columns
        
        # Format columns
        self.comparison_tree.column('#0', width=0, stretch=tk.NO)
        for col in columns:
            self.comparison_tree.column(col, anchor=tk.CENTER, width=100)
            self.comparison_tree.heading(col, text=col, anchor=tk.CENTER)
        
        # Grid layout
        self.comparison_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.E, tk.W))
        
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def create_experimental_data_tab(self, parent):
        """Create experimental data management tab"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and info
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Experimental Data Management", 
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        ttk.Label(title_frame, 
                 text="Multi-select: Ctrl+Click | Shortcuts: Del, Ctrl+D (duplicate), Ctrl+A (all), Ctrl+C/V (copy/paste)",
                 font=('Arial', 9), foreground='gray').pack(side=tk.LEFT, padx=10)
        
        # Button panel
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="➕ Add Row", 
                  command=self.add_empty_experimental_row).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📂 Import from CSV", 
                  command=self.import_experimental_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📊 Export to CSV", 
                  command=self.export_experimental_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="✏️ Edit Selected", 
                  command=self.edit_experimental_point).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🗑️ Delete Selected", 
                  command=self.delete_experimental_point).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📋 Duplicate", 
                  command=self.duplicate_selected_rows).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="✓ Select All", 
                  command=self.select_all_rows).pack(side=tk.LEFT, padx=2)
        
        # Second row of buttons
        button_frame2 = ttk.Frame(main_frame)
        button_frame2.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Button(button_frame2, text="🔧 Fit Parameters", 
                  command=self.open_curve_fitting_dialog).pack(side=tk.LEFT, padx=2)
        
        # Data table
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview for experimental data
        self.exp_data_tree = ttk.Treeview(table_frame,
                                         yscrollcommand=vsb.set,
                                         xscrollcommand=hsb.set,
                                         selectmode='extended')
        
        vsb.config(command=self.exp_data_tree.yview)
        hsb.config(command=self.exp_data_tree.xview)
        
        # Define columns
        columns = ('Material', 'W_f', 'V_f', 'V_m', 'V_p', 'E_c (GPa)', 'ρ_c (g/cm³)', 'Notes')
        self.exp_data_tree['columns'] = columns
        
        # Format columns
        self.exp_data_tree.column('#0', width=0, stretch=tk.NO)
        self.exp_data_tree.column('Material', anchor=tk.W, width=120)
        self.exp_data_tree.column('W_f', anchor=tk.CENTER, width=80)
        self.exp_data_tree.column('V_f', anchor=tk.CENTER, width=80)
        self.exp_data_tree.column('V_m', anchor=tk.CENTER, width=80)
        self.exp_data_tree.column('V_p', anchor=tk.CENTER, width=80)
        self.exp_data_tree.column('E_c (GPa)', anchor=tk.CENTER, width=100)
        self.exp_data_tree.column('ρ_c (g/cm³)', anchor=tk.CENTER, width=120)
        self.exp_data_tree.column('Notes', anchor=tk.W, width=200)
        
        for col in columns:
            self.exp_data_tree.heading(col, text=col, anchor=tk.CENTER)
        
        # Grid layout
        self.exp_data_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.E, tk.W))
        
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Bind double-click for inline editing
        self.exp_data_tree.bind('<Double-1>', self.on_cell_double_click)
        
        # Bind keyboard shortcuts
        self.exp_data_tree.bind('<Delete>', lambda e: self.delete_experimental_point())
        self.exp_data_tree.bind('<Control-d>', lambda e: self.duplicate_selected_rows())
        self.exp_data_tree.bind('<Control-a>', lambda e: self.select_all_rows())
        self.exp_data_tree.bind('<Control-c>', lambda e: self.copy_selected_rows())
        self.exp_data_tree.bind('<Control-v>', lambda e: self.paste_rows())
        
        # Bind right-click context menu
        self.exp_data_tree.bind('<Button-3>', self.show_context_menu)
        
        # Store reference to editing entry widget
        self.editing_entry = None
        self.editing_item = None
        self.editing_column = None
        self.clipboard_data = []
        
        # Info label
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.exp_data_count_label = ttk.Label(info_frame, 
                                              text="No experimental data points",
                                              font=('Arial', 9), foreground='gray')
        self.exp_data_count_label.pack(side=tk.LEFT)
        
        # Initial load
        self.update_experimental_data_table()
    
    def create_help_tab(self, parent):
        """Create a help tab with program documentation"""
        # Create scrollable frame
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        help_frame = ttk.Frame(canvas)
        
        help_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=help_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel scrolling only when mouse is over canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Help content with styling
        content_frame = ttk.Frame(help_frame, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(content_frame, text="Composite Material Analysis Tool - Help Guide", 
                        font=('Arial', 16, 'bold'), fg='#2c3e50')
        title.pack(anchor=tk.W, pady=(0, 15))
        
        # Section 1: Overview
        self.add_help_section(content_frame, "📋 Overview",
            "This tool analyzes fiber-reinforced composite materials by calculating volume fractions, "
            "density, and mechanical properties based on fiber and matrix properties.\n\n"
            "You can compare multiple material configurations side-by-side and export results for further analysis.",
            height=6)
        
        # Section 2: Input Parameters
        self.add_help_section(content_frame, "🔧 Input Parameters",
            "NAMING:\n"
            "• Mix Name: Your composite material name (e.g., 'Carbon-Epoxy-A')\n"
            "• Fiber Name: Type of fiber (e.g., 'Carbon T700')\n"
            "• Matrix Name: Type of matrix (e.g., 'Epoxy 3501-6')\n\n"
            "MATRIX PROPERTIES:\n"
            "• Density (g/cm³): Mass per unit volume (typical: 1.0-1.5)\n"
            "• Porosity Factor (α_pm): Matrix porosity coefficient (typically 0.0)\n"
            "  → Controls void content in matrix phase\n"
            "• Stiffness (GPa): Elastic modulus (typical: 2-5)\n"
            "• Poisson Ratio: Lateral strain ratio (typical: 0.3-0.4)\n\n"
            "FIBER PROPERTIES:\n"
            "• Density (g/cm³): Mass per unit volume (typical: 1.8-2.8)\n"
            "• Porosity Factor (α_pf): Fiber porosity coefficient (typical: 0.0-0.3)\n"
            "  → Accounts for voids between/within fiber bundles\n"
            "  → Can be estimated from experimental data via curve fitting\n"
            "• Stiffness (GPa): Elastic modulus (typical: 70-400)\n"
            "• Orientation Efficiency (η₀): Fiber alignment factor (1.0 = perfect)\n"
            "• Length Efficiency (η₁): Calculated automatically\n"
            "• Fiber Length (mm): Physical length of fibers\n"
            "• Fiber Diameter (mm): Physical diameter of fibers\n\n"
            "COMPOSITE PARAMETERS:\n"
            "• Max Volume Fiber (V_f_max): Maximum fiber packing (typical: 0.5-0.7)\n"
            "• Porosity Exponent (n): Porosity effect power (typical: 2.0)\n"
            "• Test Fiber Weight Fraction (W_f): Target fiber mass fraction to analyze")
        
        # Section 3: Test Fiber Weight Fraction
        self.add_help_section(content_frame, "⚖️ Test Fiber Weight Fraction (W_f)",
            "This is THE KEY PARAMETER you're designing with!\n\n"
            "W_f = (mass of fiber) / (total mass of composite)\n\n"
            "• W_f = 0.40 means 40% fiber, 60% matrix by weight\n"
            "• W_f = 0.60 means 60% fiber, 40% matrix by weight\n\n"
            "WHAT IT DOES:\n"
            "• Sets the specific composition you want to analyze\n"
            "• Determines Case A or Case B behavior\n"
            "• Calculates resulting volume fractions (V_f, V_m, V_p)\n"
            "• Used in single-point results display\n\n"
            "TYPICAL RANGE: 0.20 to 0.70 for practical composites\n\n"
            "NOTE: The plots show how properties vary across ALL W_f values (0 to 1), "
            "but the 'Results' tab shows calculations at YOUR specific W_f test value.",
            height=20)
        
        # Section 4: Case A vs Case B
        self.add_help_section(content_frame, "🔀 Case A vs Case B",
            "The tool automatically determines which case applies:\n\n"
            "CASE A (Low fiber content):\n"
            "• W_f < W_f_transition\n"
            "• Fibers can reach maximum packing\n"
            "• Volume fractions calculated from fiber limit\n\n"
            "CASE B (High fiber content):\n"
            "• W_f ≥ W_f_transition\n"
            "• Matrix cannot fill all spaces\n"
            "• Porosity increases due to lack of matrix\n\n"
            "The transition point is calculated automatically based on material properties.")
        
        # Section 5: Workflow
        self.add_help_section(content_frame, "📝 Workflow",
            "1. NAME your material (Mix, Fiber, Matrix names)\n"
            "2. ENTER material properties in left panel\n"
            "3. SET test fiber weight fraction (W_f)\n"
            "4. Click 'CALCULATE' button\n"
            "5. VIEW results in 'Results' tab\n"
            "6. Click 'GENERATE PLOTS' for visualizations\n"
            "7. ADD more materials with '+ Add Material' button\n"
            "8. COMPARE all materials in 'Comparison Table' tab\n"
            "9. EXPORT results using export buttons")
        
        # Section 6: Multi-Material Comparison
        self.add_help_section(content_frame, "🔄 Multi-Material Comparison",
            "• Use dropdown at top to switch between materials\n"
            "• '+ Add Material' creates a new configuration\n"
            "• '🗑️ Delete' removes current material (must have at least 1)\n"
            "• Each material has its own properties and test W_f\n"
            "• 'Calculate All' runs calculations for all materials\n"
            "• '📊 Include in plots' checkbox controls plot visibility\n"
            "  → Uncheck to hide a material from comparison plots\n"
            "  → Useful when comparing subset of materials\n"
            "• 'Comparison Table' shows all materials side-by-side\n"
            "• Plots overlay enabled materials with color-coded lines")
        
        # Section 7: Plot Types
        self.add_help_section(content_frame, "📊 Plot Types",
            "After clicking 'Generate Plots', you'll see 4 tabs:\n\n"
            "1. WEIGHT/VOLUME RELATIONS:\n"
            "   Shows V_f, V_m, V_p vs W_f for each material\n"
            "   • Solid line = V_f (fiber volume fraction)\n"
            "   • Dashed line = V_m (matrix volume fraction)\n"
            "   • Dash-dot line = V_p (void/porosity fraction)\n\n"
            "2. DENSITY COMPARISON:\n"
            "   Shows composite density vs W_f\n"
            "   • Solid line = actual density (with porosity)\n"
            "   • Dashed line = theoretical density (no porosity)\n\n"
            "3. STIFFNESS COMPARISON:\n"
            "   Shows composite stiffness (E_c) vs W_f\n\n"
            "4. FIBER EFFICIENCY COMPARISON:\n"
            "   Shows fiber length efficiency factor (η₁) vs W_f")
        
        # Section 8: Color Scheme & Plot Control
        self.add_help_section(content_frame, "🎨 Color Scheme & Plot Control",
            "Each material gets a distinct color using HSV color space:\n"
            "• Different hues for different materials\n"
            "• Solid lines: Theoretical curves calculated from properties\n"
            "• Scatter points: Experimental data (if available)\n"
            "• All curves/points for same material share same color\n\n"
            "PLOT CONTROL:\n"
            "• Use '📊 Include in plots' checkbox to show/hide materials\n"
            "• Comparison Table shows plot status (✓/✗)\n"
            "• Only materials with ✓ appear in generated plots")
        
        # Section 9: Experimental Data Management
        self.add_help_section(content_frame, "🔬 Experimental Data Management",
            "The 'Experimental Data' tab allows you to manage measured data:\n\n"
            "ADDING DATA:\n"
            "• Click '+ Add Data Point' to manually enter measurements\n"
            "• Required: W_f (fiber weight fraction)\n"
            "• Optional: V_f, V_m, V_p, E_c, ρ_c, notes\n"
            "• Double-click cells to edit inline\n\n"
            "IMPORTING/EXPORTING:\n"
            "• 'Import from CSV' loads experimental data from file\n"
            "• CSV format: W_f, V_f, V_m, V_p, E_c, rho_c, Notes\n"
            "• 'Export to CSV' saves experimental data\n\n"
            "CURVE FITTING:\n"
            "• Click '🔧 Fit Parameters' to optimize material properties\n"
            "• Uses scipy L-BFGS-B optimization\n"
            "• Can fit: ρ_m, ρ_f, α_pf, α_pm, V_f_max\n"
            "• Automatically detects fiber saturation point\n"
            "• Choose optimization target: volume fractions or density\n"
            "• Smart initial estimates improve convergence\n\n"
            "VISUALIZATION:\n"
            "• Experimental points appear as scatter markers on plots\n"
            "• Compare theoretical curves vs measured data\n"
            "• Validate model predictions against experiments")
        
        # Section 10: Export Options
        self.add_help_section(content_frame, "💾 Export Options",
            "THREE EXPORT BUTTONS:\n\n"
            "📁 EXPORT CURRENT RESULTS:\n"
            "   Saves results for selected material to text file\n\n"
            "📈 EXPORT SUMMARY CSV:\n"
            "   Exports one row per material with current W_f values\n"
            "   Perfect for comparing materials at their test points\n\n"
            "📊 EXPORT DETAILED CSV:\n"
            "   Opens dialog to specify:\n"
            "   • Number of samples (e.g., 100 points)\n"
            "   • W_f range (e.g., 0.0 to 1.0)\n"
            "   Exports full data set across W_f range\n"
            "   Perfect for plotting in Excel/MATLAB/Python")
        
        # Section 11: Save/Load
        self.add_help_section(content_frame, "💿 Save/Load Configurations",
            "SAVE CONFIGURATION:\n"
            "• Saves all material properties to JSON file\n"
            "• Preserves names, parameters, and settings\n"
            "• Results must be recalculated after loading\n\n"
            "LOAD CONFIGURATION:\n"
            "• Loads previously saved material library\n"
            "• Restores all materials and their properties\n"
            "• Click 'Calculate All' to recompute results")
        
        # Section 12: Key Formulas
        self.add_help_section(content_frame, "📐 Key Formulas",
            "COMPOSITE STIFFNESS:\n"
            "E_c = (η₀ η₁ V_f E_f + V_m E_m)(1 - V_p)ⁿ\n\n"
            "COMPOSITE DENSITY:\n"
            "ρ_c = V_f ρ_f + V_m ρ_m\n\n"
            "MATRIX SHEAR STIFFNESS:\n"
            "G_m = E_m / (2(1 + ν_m))\n\n"
            "FIBER LENGTH EFFICIENCY:\n"
            "η₁ = 1 - tanh(βL/2) / (βL/2)\n"
            "where β depends on fiber geometry and matrix stiffness")
        
        # Section 13: Tips
        self.add_help_section(content_frame, "💡 Tips & Best Practices",
            "• Start with default values to understand behavior\n"
            "• Name your materials descriptively for easy identification\n"
            "• Use 'Calculate All' before generating comparison plots\n"
            "• Check 'Comparison Table' to verify all calculations\n"
            "• Export detailed CSV to analyze trends in Excel\n"
            "• Save configurations to build a material library\n"
            "• W_f between 0.3-0.6 is typical for structural composites\n"
            "• Higher fiber content increases stiffness but may add porosity\n"
            "• Watch for Case B transition where porosity increases sharply\n\n"
            "EXPERIMENTAL DATA TIPS:\n"
            "• Need 3+ unsaturated data points for reliable curve fitting\n"
            "• Volume fractions (V_f, V_m, V_p) more reliable than density alone\n"
            "• Fiber porosity factor (α_pf) should only be fit from unsaturated data\n"
            "• Use 'Include in plots' to hide/show materials during comparison\n"
            "• Import sample data from examples/ folder to see proper format")
    
    def add_help_section(self, parent, title, content, height=None):
        """Helper to add a formatted help section"""
        # Section title
        title_label = tk.Label(parent, text=title, 
                              font=('Arial', 12, 'bold'), 
                              fg='#34495e', anchor=tk.W)
        title_label.pack(fill=tk.X, pady=(15, 5))
        
        # Section content
        if height is None:
            height = len(content.split('\n'))
        
        content_text = tk.Text(parent, wrap=tk.WORD, height=height, 
                              font=('Arial', 10), bg='#f8f9fa', relief=tk.FLAT, 
                              padx=10, pady=10)
        content_text.insert(1.0, content)
        content_text.config(state=tk.DISABLED)  # Read-only
        content_text.pack(fill=tk.X, pady=(0, 5))
    
    def update_material_combo(self):
        """Update the material selection combobox"""
        names = [mat.name for mat in self.materials]
        self.material_combo['values'] = names
        if self.current_material_index < len(names):
            self.material_combo.current(self.current_material_index)
    
    def on_material_selected(self, event=None):
        """Handle material selection from combobox"""
        # Save current material first
        self.save_current_material()
        
        # Load selected material
        selected_index = self.material_combo.current()
        if selected_index >= 0:
            self.load_material(selected_index)
    
    def add_new_material(self):
        """Add a new material configuration via button"""
        # Save current material
        self.save_current_material()
        
        # Add new material
        new_index = self.add_material()
        
        # Update combo and load new material
        self.update_material_combo()
        self.load_material(new_index)
        
        self.show_toast(f"Added new material: {self.materials[new_index].name}")
    
    def delete_material(self):
        """Delete the current material"""
        if len(self.materials) <= 1:
            messagebox.showwarning("Warning", "Cannot delete the last material!")
            return
        
        result = messagebox.askyesno("Confirm Delete", 
                                     f"Delete material '{self.materials[self.current_material_index].name}'?")
        if result:
            self.materials.pop(self.current_material_index)
            self.current_material_index = max(0, self.current_material_index - 1)
            self.update_material_combo()
            self.load_material(self.current_material_index)
            self.update_comparison_table()
    
    def on_plot_enabled_changed(self):
        """Called when plot enabled checkbox is toggled"""
        self.save_current_material()
        status = "enabled" if self.plot_enabled_var.get() else "disabled"
        self.show_toast(f"Plotting {status} for {self.materials[self.current_material_index].name}", 
                       type="info", duration=1500)
    
    def save_current_material(self):
        """Save current form values to the current material configuration"""
        if not self.materials:
            return
        
        mat = self.materials[self.current_material_index]
        
        try:
            # Names
            mat.name = self.mix_name.get()
            mat.fiber_name = self.fiber_name.get()
            mat.matrix_name = self.matrix_name.get()
            
            # Matrix
            mat.matrix_density = float(self.matrix_density.get())
            mat.matrix_porosity = float(self.matrix_porosity.get())
            mat.matrix_stiffness = float(self.matrix_stiffness.get())
            mat.matrix_poisson = float(self.matrix_poisson.get())
            
            # Fiber
            mat.fiber_density = float(self.fiber_density.get())
            mat.fiber_porosity = float(self.fiber_porosity.get())
            mat.fiber_stiffness = float(self.fiber_stiffness.get())
            mat.fiber_eta0 = float(self.fiber_eta0.get())
            mat.fiber_length = float(self.fiber_length.get())
            mat.fiber_diameter = float(self.fiber_diameter.get())
            
            # Composite
            mat.v_f_max = float(self.v_f_max.get())
            mat.porosity_exp = float(self.porosity_exp.get())
            mat.w_f_test = float(self.w_f_test.get())
            
            # Plot control
            mat.plot_enabled = self.plot_enabled_var.get()
            
        except ValueError:
            pass  # Ignore invalid values during editing
    
    def load_material(self, index):
        """Load material configuration into form"""
        if index < 0 or index >= len(self.materials):
            return
        
        self.current_material_index = index
        mat = self.materials[index]
        
        # Names
        self.mix_name.delete(0, tk.END)
        self.mix_name.insert(0, mat.name)
        self.fiber_name.delete(0, tk.END)
        self.fiber_name.insert(0, mat.fiber_name)
        self.matrix_name.delete(0, tk.END)
        self.matrix_name.insert(0, mat.matrix_name)
        
        # Matrix
        self.matrix_density.delete(0, tk.END)
        self.matrix_density.insert(0, str(mat.matrix_density))
        self.matrix_porosity.delete(0, tk.END)
        self.matrix_porosity.insert(0, str(mat.matrix_porosity))
        self.matrix_stiffness.delete(0, tk.END)
        self.matrix_stiffness.insert(0, str(mat.matrix_stiffness))
        self.matrix_poisson.delete(0, tk.END)
        self.matrix_poisson.insert(0, str(mat.matrix_poisson))
        
        # Fiber
        self.fiber_density.delete(0, tk.END)
        self.fiber_density.insert(0, str(mat.fiber_density))
        self.fiber_porosity.delete(0, tk.END)
        self.fiber_porosity.insert(0, str(mat.fiber_porosity))
        self.fiber_stiffness.delete(0, tk.END)
        self.fiber_stiffness.insert(0, str(mat.fiber_stiffness))
        self.fiber_eta0.delete(0, tk.END)
        self.fiber_eta0.insert(0, str(mat.fiber_eta0))
        self.fiber_length.delete(0, tk.END)
        self.fiber_length.insert(0, str(mat.fiber_length))
        self.fiber_diameter.delete(0, tk.END)
        self.fiber_diameter.insert(0, str(mat.fiber_diameter))
        
        # Composite
        self.v_f_max.delete(0, tk.END)
        self.v_f_max.insert(0, str(mat.v_f_max))
        self.porosity_exp.delete(0, tk.END)
        self.porosity_exp.insert(0, str(mat.porosity_exp))
        self.w_f_test.delete(0, tk.END)
        self.w_f_test.insert(0, str(mat.w_f_test))
        
        # Plot control
        self.plot_enabled_var.set(mat.plot_enabled)
        
        # Update combo
        self.update_material_combo()
    
    # ========================================================================
    # CALCULATION METHODS
    # ========================================================================
    
    def reset_defaults(self):
        """Reset current material to default values"""
        mat = self.materials[self.current_material_index]
        default = MaterialConfig(name=mat.name, fiber_name=mat.fiber_name, matrix_name=mat.matrix_name)
        self.materials[self.current_material_index] = default
        self.load_material(self.current_material_index)
    
    def calculate_current(self):
        """Calculate properties for the current material"""
        self.save_current_material()
        mat = self.materials[self.current_material_index]
        
        try:
            results = self.perform_calculation(mat)
            mat.results = results
            mat.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Display results
            self.display_results(mat, results)
            self.update_comparison_table()
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error calculating {mat.name}:\n{str(e)}")
    
    def calculate_all(self):
        """Calculate properties for all materials"""
        self.save_current_material()
        
        success_count = 0
        for mat in self.materials:
            try:
                results = self.perform_calculation(mat)
                mat.results = results
                mat.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                success_count += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to calculate {mat.name}:\n{str(e)}")
        
        # Display current material results
        if self.materials[self.current_material_index].results:
            self.display_results(
                self.materials[self.current_material_index],
                self.materials[self.current_material_index].results
            )
        
        self.update_comparison_table()
        self.show_toast(f"Calculated {success_count} material(s) successfully!")
    
    def perform_calculation(self, mat):
        """Perform calculation for a material configuration"""
        # Create Matrix
        matrix = Matrix(
            density=mat.matrix_density * 1000,  # Convert to kg/m³
            porosity=mat.matrix_porosity,
            stiffness=mat.matrix_stiffness,
            poisson_ratio=mat.matrix_poisson
        )
        
        # Create Fiber
        fiber = Fiber(
            density=mat.fiber_density * 1000,  # Convert to kg/m³
            porosity=mat.fiber_porosity,
            stiffness=mat.fiber_stiffness,
            orientation_efficiency_factor=mat.fiber_eta0,
            length_efficiency_factor=0.95,
            length=mat.fiber_length,
            diameter=mat.fiber_diameter
        )
        
        # Calculate accurate eta1
        G_m = matrix.shear_stiffness()
        fiber.eta1 = fiber.calculate_length_efficiency_factor(G_m)
        
        # Create Composite
        composite = Composite_mix(fiber=fiber, matrix=matrix)
        
        # Calculate transition
        test_case = Composite_case(
            composite_mix=composite,
            max_volume_fiber=mat.v_f_max,
            porosity_efficiency_exponent=mat.porosity_exp
        )
        w_f_trans = test_case.calculate_transition_weight_fiber()
        
        # Calculate for test W_f
        case = Composite_case(
            composite_mix=composite,
            fiber_mass_fraction=mat.w_f_test,
            max_volume_fiber=mat.v_f_max,
            porosity_efficiency_exponent=mat.porosity_exp
        )
        
        case_type = case.determine_case()
        
        if case_type == 'Case A':
            V_f, V_m, V_p = case.calculate_volume_fractions_case_a()
        else:
            V_f, V_m, V_p = case.calculate_volume_fractions_case_b()
        
        rho_c = case.calculate_composite_density()
        E_c = case.calculate_composite_stiffness()
        
        return {
            'matrix': matrix,
            'fiber': fiber,
            'composite': composite,
            'G_m': G_m,
            'w_f_trans': w_f_trans,
            'case_type': case_type,
            'V_f': V_f,
            'V_m': V_m,
            'V_p': V_p,
            'rho_c': rho_c,
            'E_c': E_c
        }
    
    def display_results(self, mat, results):
        """Display calculation results in text area"""
        self.results_text.delete(1.0, tk.END)
        
        output = "=" * 70 + "\n"
        output += f"MATERIAL: {mat.name}\n"
        output += f"Fiber: {mat.fiber_name} | Matrix: {mat.matrix_name}\n"
        output += f"Calculated: {mat.timestamp}\n"
        output += "=" * 70 + "\n\n"
        
        output += "MATRIX PROPERTIES:\n"
        output += f"  Density: {results['matrix'].rho:.2f} kg/m³ ({mat.matrix_density:.2f} g/cm³)\n"
        output += f"  Porosity factor (α_pm): {results['matrix'].alpha_pm:.4f}\n"
        output += f"  Stiffness (E_m): {results['matrix'].E:.2f} GPa\n"
        output += f"  Poisson's ratio (ν_m): {results['matrix'].nu:.2f}\n"
        output += f"  Shear stiffness (G_m): {results['G_m']:.3f} GPa\n\n"
        
        output += "FIBER PROPERTIES:\n"
        output += f"  Density: {results['fiber'].rho:.2f} kg/m³ ({mat.fiber_density:.2f} g/cm³)\n"
        output += f"  Porosity factor (α_pf): {results['fiber'].alpha_pf:.4f}\n"
        output += f"  Stiffness (E_f): {results['fiber'].E:.2f} GPa\n"
        output += f"  Orientation efficiency (η₀): {results['fiber'].eta0:.2f}\n"
        output += f"  Length efficiency (η₁): {results['fiber'].eta1:.6f}\n"
        output += f"  Length (L): {results['fiber'].L:.2f} mm\n"
        output += f"  Diameter (D): {results['fiber'].D:.4f} mm\n"
        output += f"  Aspect ratio (L/D): {results['fiber'].aspect_ratio():.0f}\n\n"
        
        output += "COMPOSITE PARAMETERS:\n"
        output += f"  Max fiber volume fraction (V_f_max): {mat.v_f_max:.2f}\n"
        output += f"  Porosity efficiency exponent (n): {mat.porosity_exp:.0f}\n"
        output += f"  Transition fiber weight fraction (W_f_trans): {results['w_f_trans']:.4f}\n\n"
        
        output += "-" * 70 + "\n"
        output += f"TEST CASE: W_f = {mat.w_f_test:.2f}\n"
        output += "-" * 70 + "\n"
        output += f"Case type: {results['case_type']}\n\n"
        
        output += "VOLUME FRACTIONS:\n"
        output += f"  Fiber volume fraction (V_f): {results['V_f']:.4f}\n"
        output += f"  Matrix volume fraction (V_m): {results['V_m']:.4f}\n"
        output += f"  Porosity (V_p): {results['V_p']:.4f}\n"
        output += f"  Sum check (should be 1.0): {results['V_f'] + results['V_m'] + results['V_p']:.4f}\n\n"
        
        output += "COMPOSITE PROPERTIES:\n"
        output += f"  Composite density (ρ_c): {results['rho_c']:.2f} kg/m³ ({results['rho_c']/1000:.3f} g/cm³)\n"
        output += f"  Composite stiffness (E_c): {results['E_c']:.2f} GPa\n"
        
        output += "\n" + "=" * 70 + "\n"
        
        self.results_text.insert(tk.END, output)
    
    def update_comparison_table(self):
        """Update the comparison table with all materials"""
        # Clear existing items
        for item in self.comparison_tree.get_children():
            self.comparison_tree.delete(item)
        
        # Add materials
        for mat in self.materials:
            plot_status = "✓" if mat.plot_enabled else "✗"
            if mat.results:
                values = (
                    mat.name,
                    mat.fiber_name,
                    mat.matrix_name,
                    f"{mat.w_f_test:.3f}",
                    f"{mat.results['V_f']:.4f}",
                    f"{mat.results['rho_c']/1000:.3f}",
                    f"{mat.results['E_c']:.2f}",
                    mat.results['case_type'],
                    plot_status,
                    "✓ Calculated"
                )
            else:
                values = (
                    mat.name,
                    mat.fiber_name,
                    mat.matrix_name,
                    f"{mat.w_f_test:.3f}",
                    "-",
                    "-",
                    "-",
                    "-",
                    plot_status,
                    "Not calculated"
                )
            self.comparison_tree.insert('', tk.END, values=values)
    
    # ========================================================================
    # FILE I/O - SAVE/LOAD CONFIGURATIONS
    # ========================================================================
    
    def save_configuration(self):
        """Save all material configurations to JSON file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Configuration As"
        )
        
        if file_path:
            try:
                self.save_current_material()
                data = {
                    'version': '1.0',
                    'materials': [mat.to_dict() for mat in self.materials],
                    'current_index': self.current_material_index,
                    'saved_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                
                self.show_toast(f"Configuration saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
    
    def load_configuration(self):
        """Load material configurations from JSON file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Configuration"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Load materials
                self.materials = [MaterialConfig.from_dict(mat_data) 
                                 for mat_data in data['materials']]
                
                # Load current index
                self.current_material_index = data.get('current_index', 0)
                
                # Update UI
                self.update_material_combo()
                self.load_material(self.current_material_index)
                self.update_comparison_table()
                
                self.show_toast(f"Loaded {len(self.materials)} material(s)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration:\n{str(e)}")
    
    def export_results(self):
        """Export current material results to text file"""
        mat = self.materials[self.current_material_index]
        
        if not mat.results:
            messagebox.showwarning("Warning", "No results to export. Calculate first!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"{mat.name.replace(' ', '_')}_results.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Results As"
        )
        
        if file_path:
            try:
                content = self.results_text.get(1.0, tk.END)
                with open(file_path, 'w') as f:
                    f.write(content)
                self.show_toast("Results exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results:\n{str(e)}")
    
    def export_summary_csv(self):
        """Export summary of all materials to CSV"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="composite_summary.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Summary As CSV"
        )
        
        if not file_path:
            return
        
        try:
            self.save_current_material()
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Export summary data
                writer.writerow([
                    'Mix Name', 'Fiber Name', 'Matrix Name',
                    'W_f', 'V_f', 'V_m', 'V_p',
                    'rho_c (g/cm³)', 'E_c (GPa)',
                    'Case Type', 'Timestamp'
                ])
                
                for mat in self.materials:
                    if mat.results:
                        writer.writerow([
                            mat.name, mat.fiber_name, mat.matrix_name,
                            f"{mat.w_f_test:.4f}",
                            f"{mat.results['V_f']:.4f}",
                            f"{mat.results['V_m']:.4f}",
                            f"{mat.results['V_p']:.4f}",
                            f"{mat.results['rho_c']/1000:.4f}",
                            f"{mat.results['E_c']:.2f}",
                            mat.results['case_type'],
                            mat.timestamp or 'N/A'
                        ])
            
            self.show_toast("Summary CSV exported successfully")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export summary:\n{str(e)}")
    
    def export_detailed_csv(self):
        """Export detailed sampled data for all materials to CSV"""
        # Ask for sampling options
        dialog = SamplingDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if not dialog.result:
            return  # User cancelled
        
        num_samples = dialog.result['num_samples']
        w_f_range = dialog.result['w_f_range']
        
        # Get file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="composite_detailed_data.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Detailed Data As CSV"
        )
        
        if not file_path:
            return
        
        try:
            self.save_current_material()
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Export detailed sampling data
                writer.writerow([
                    'Mix Name', 'Fiber Name', 'Matrix Name',
                    'W_f', 'V_f', 'V_m', 'V_p',
                    'rho_c (g/cm³)', 'E_c (GPa)', 'Case Type'
                ])
                
                W_f_array = np.linspace(w_f_range[0], w_f_range[1], num_samples)
                
                for mat in self.materials:
                    if not mat.results:
                        continue
                    
                    for W_f in W_f_array:
                        try:
                            # Calculate for this W_f
                            case = Composite_case(
                                mat.results['composite'],
                                fiber_mass_fraction=W_f,
                                max_volume_fiber=mat.v_f_max,
                                porosity_efficiency_exponent=mat.porosity_exp
                            )
                            
                            case_type = case.determine_case()
                            
                            if case_type == 'Case A':
                                V_f, V_m, V_p = case.calculate_volume_fractions_case_a()
                            else:
                                V_f, V_m, V_p = case.calculate_volume_fractions_case_b()
                            
                            rho_c = case.calculate_composite_density()
                            E_c = case.calculate_composite_stiffness()
                            
                            writer.writerow([
                                mat.name, mat.fiber_name, mat.matrix_name,
                                f"{W_f:.4f}",
                                f"{V_f:.4f}",
                                f"{V_m:.4f}",
                                f"{V_p:.4f}",
                                f"{rho_c/1000:.4f}",
                                f"{E_c:.2f}",
                                case_type
                            ])
                        except:
                            pass  # Skip invalid points
            
            self.show_toast("Detailed CSV exported successfully")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export detailed data:\n{str(e)}")
    
    # ========================================================================
    # EXPERIMENTAL DATA MANAGEMENT
    # ========================================================================
    
    def update_experimental_data_table(self):
        """Update the experimental data table with all materials' data"""
        # Clear existing items
        for item in self.exp_data_tree.get_children():
            self.exp_data_tree.delete(item)
        
        total_points = 0
        
        # Add experimental data for all materials
        for mat in self.materials:
            for pt in mat.experimental_data:
                values = (
                    mat.name,
                    f"{pt.W_f:.4f}",
                    f"{pt.V_f:.4f}" if pt.V_f is not None else "-",
                    f"{pt.V_m:.4f}" if pt.V_m is not None else "-",
                    f"{pt.V_p:.4f}" if pt.V_p is not None else "-",
                    f"{pt.E_c:.2f}" if pt.E_c is not None else "-",
                    f"{pt.rho_c:.4f}" if pt.rho_c is not None else "-",
                    pt.notes[:50] if pt.notes else ""
                )
                self.exp_data_tree.insert('', tk.END, values=values)
                total_points += 1
        
        # Update count label
        if total_points == 0:
            self.exp_data_count_label.config(text="No experimental data points")
        elif total_points == 1:
            self.exp_data_count_label.config(text="1 experimental data point")
        else:
            self.exp_data_count_label.config(text=f"{total_points} experimental data points")
    
    def add_empty_experimental_row(self):
        """Add an empty row to the experimental data table for quick editing"""
        # Create an empty experimental data point with W_f=0
        point = ExperimentalDataPoint(
            W_f=0.0,
            V_f=None,
            V_m=None,
            V_p=None,
            E_c=None,
            rho_c=None,
            notes=""
        )
        
        self.materials[self.current_material_index].experimental_data.append(point)
        self.update_experimental_data_table()
        self.show_toast("Empty row added - double-click cells to edit")
    
    def add_experimental_point_dialog(self):
        """Open dialog to add an experimental data point (legacy method)"""
        dialog = ExperimentalDataDialog(self.root, self.materials[self.current_material_index].name)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # Create experimental data point
            point = ExperimentalDataPoint(
                W_f=dialog.result['W_f'],
                V_f=dialog.result['V_f'],
                V_m=dialog.result['V_m'],
                V_p=dialog.result['V_p'],
                E_c=dialog.result['E_c'],
                rho_c=dialog.result['rho_c'],
                notes=dialog.result['notes']
            )
            
            self.materials[self.current_material_index].experimental_data.append(point)
            self.update_experimental_data_table()
            self.show_toast("Experimental data point added")
    
    def edit_experimental_point(self):
        """Edit selected experimental data point"""
        selection = self.exp_data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a data point to edit")
            return
        
        # Get selected item
        item = selection[0]
        values = self.exp_data_tree.item(item)['values']
        mat_name = values[0]
        
        # Find the material and data point
        mat_idx = None
        pt_idx = None
        for i, mat in enumerate(self.materials):
            if mat.name == mat_name:
                mat_idx = i
                # Find the data point by W_f (assuming it's unique enough)
                W_f = float(values[1])
                for j, pt in enumerate(mat.experimental_data):
                    if abs(pt.W_f - W_f) < 1e-6:
                        pt_idx = j
                        break
                break
        
        if mat_idx is None or pt_idx is None:
            messagebox.showerror("Error", "Could not find data point")
            return
        
        # Open edit dialog
        pt = self.materials[mat_idx].experimental_data[pt_idx]
        dialog = ExperimentalDataDialog(self.root, mat_name, edit_data=pt)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # Update the point
            pt.W_f = dialog.result['W_f']
            pt.V_f = dialog.result['V_f']
            pt.V_m = dialog.result['V_m']
            pt.V_p = dialog.result['V_p']
            pt.E_c = dialog.result['E_c']
            pt.rho_c = dialog.result['rho_c']
            pt.notes = dialog.result['notes']
            
            self.update_experimental_data_table()
            self.show_toast("Experimental data point updated")
    
    def on_cell_double_click(self, event):
        """Handle double-click to edit cell inline"""
        # Close any existing edit
        if self.editing_entry:
            self.finish_editing()
        
        # Get the region clicked
        region = self.exp_data_tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
        
        # Get column and item
        column = self.exp_data_tree.identify_column(event.x)
        item = self.exp_data_tree.identify_row(event.y)
        
        if not item:
            return
        
        # Get column index and name
        col_idx = int(column.replace('#', '')) - 1
        if col_idx < 0:
            return
        
        columns = self.exp_data_tree['columns']
        if col_idx >= len(columns):
            return
        
        col_name = columns[col_idx]
        
        # Don't allow editing Material column
        if col_name == 'Material':
            return
        
        # Get current value
        values = self.exp_data_tree.item(item)['values']
        current_value = values[col_idx]
        if current_value == '-':
            current_value = ''
        
        # Get cell coordinates
        bbox = self.exp_data_tree.bbox(item, column)
        if not bbox:
            return
        
        # Create entry widget for editing
        self.editing_entry = ttk.Entry(self.exp_data_tree)
        self.editing_entry.insert(0, str(current_value))
        self.editing_entry.select_range(0, tk.END)
        self.editing_entry.focus()
        
        # Position entry over cell
        self.editing_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        
        # Store editing info
        self.editing_item = item
        self.editing_column = col_name
        
        # Bind events
        self.editing_entry.bind('<Return>', lambda e: self.finish_editing())
        self.editing_entry.bind('<Escape>', lambda e: self.cancel_editing())
        self.editing_entry.bind('<FocusOut>', lambda e: self.finish_editing())
    
    def finish_editing(self):
        """Finish editing and save the value"""
        if not self.editing_entry or not self.editing_item:
            return
        
        # Get new value
        new_value = self.editing_entry.get().strip()
        
        # Get the item values
        values = self.exp_data_tree.item(self.editing_item)['values']
        mat_name = values[0]
        W_f = float(values[1])
        
        # Find the material and data point
        mat_idx = None
        pt_idx = None
        for i, mat in enumerate(self.materials):
            if mat.name == mat_name:
                mat_idx = i
                for j, pt in enumerate(mat.experimental_data):
                    if abs(pt.W_f - W_f) < 1e-6:
                        pt_idx = j
                        break
                break
        
        if mat_idx is None or pt_idx is None:
            self.cancel_editing()
            return
        
        pt = self.materials[mat_idx].experimental_data[pt_idx]
        
        # Update the appropriate field based on column
        try:
            if self.editing_column == 'W_f':
                pt.W_f = float(new_value) if new_value else 0.0
            elif self.editing_column == 'V_f':
                pt.V_f = float(new_value) if new_value and new_value != '-' else None
            elif self.editing_column == 'V_m':
                pt.V_m = float(new_value) if new_value and new_value != '-' else None
            elif self.editing_column == 'V_p':
                pt.V_p = float(new_value) if new_value and new_value != '-' else None
            elif self.editing_column == 'E_c (GPa)':
                pt.E_c = float(new_value) if new_value and new_value != '-' else None
            elif self.editing_column == 'ρ_c (g/cm³)':
                pt.rho_c = float(new_value) if new_value and new_value != '-' else None
            elif self.editing_column == 'Notes':
                pt.notes = new_value
            
            # Update the table
            self.update_experimental_data_table()
        except ValueError:
            messagebox.showerror("Error", f"Invalid value for {self.editing_column}: {new_value}")
        
        # Clean up
        self.cancel_editing()
    
    def cancel_editing(self):
        """Cancel editing without saving"""
        if self.editing_entry:
            self.editing_entry.destroy()
            self.editing_entry = None
        self.editing_item = None
        self.editing_column = None
    
    def edit_cell(self, item, col_index, col_name, current_value):
        """Create an entry widget for inline cell editing"""
        # Close any existing editing widget
        if self.editing_entry:
            self.editing_entry.destroy()
            self.editing_entry = None
        
        # Get the bounding box of the cell
        bbox = self.exp_data_tree.bbox(item, col_index)
        if not bbox:
            return
        
        x, y, width, height = bbox
        
        # Store editing context
        self.editing_item = item
        self.editing_column = col_index
        
        # Create entry widget
        self.editing_entry = ttk.Entry(self.exp_data_tree)
        
        # Set current value
        if current_value == "-":
            self.editing_entry.insert(0, "")
        else:
            self.editing_entry.insert(0, str(current_value))
        
        self.editing_entry.select_range(0, tk.END)
        self.editing_entry.focus()
        
        # Position the entry widget over the cell
        self.editing_entry.place(x=x, y=y, width=width, height=height)
        
        # Bind events
        self.editing_entry.bind('<Return>', lambda e: self.save_cell_edit())
        self.editing_entry.bind('<Escape>', lambda e: self.cancel_cell_edit())
        self.editing_entry.bind('<FocusOut>', lambda e: self.save_cell_edit())
    
    def save_cell_edit(self):
        """Save the edited cell value"""
        if not self.editing_entry or not self.editing_item:
            return
        
        # Get new value
        new_value = self.editing_entry.get().strip()
        
        # Get item values
        values = list(self.exp_data_tree.item(self.editing_item)['values'])
        mat_name = values[0]
        W_f_str = values[1]
        
        # Find the material and data point
        mat = None
        pt = None
        for m in self.materials:
            if m.name == mat_name:
                mat = m
                W_f = float(W_f_str)
                for p in m.experimental_data:
                    if abs(p.W_f - W_f) < 1e-6:
                        pt = p
                        break
                break
        
        if not mat or not pt:
            self.cancel_cell_edit()
            return
        
        # Get column name
        columns = self.exp_data_tree['columns']
        col_name = columns[self.editing_column]
        
        try:
            # Update the data point based on column
            if col_name == 'W_f':
                if new_value:
                    pt.W_f = float(new_value)
            elif col_name == 'V_f':
                pt.V_f = float(new_value) if new_value else None
            elif col_name == 'V_m':
                pt.V_m = float(new_value) if new_value else None
            elif col_name == 'V_p':
                pt.V_p = float(new_value) if new_value else None
            elif col_name == 'E_c (GPa)':
                pt.E_c = float(new_value) if new_value else None
            elif col_name == 'ρ_c (g/cm³)':
                pt.rho_c = float(new_value) if new_value else None
            elif col_name == 'Notes':
                pt.notes = new_value
            
            # Update the table
            self.update_experimental_data_table()
            self.show_toast(f"Updated {col_name}")
            
        except ValueError as e:
            messagebox.showerror("Invalid Value", 
                               f"Could not parse value '{new_value}' for {col_name}.\n"
                               f"Please enter a valid number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update cell:\n{str(e)}")
        
        finally:
            self.cancel_cell_edit()
    
    def cancel_cell_edit(self):
        """Cancel cell editing"""
        if self.editing_entry:
            self.editing_entry.destroy()
            self.editing_entry = None
        self.editing_item = None
        self.editing_column = None
    
    def delete_experimental_point(self):
        """Delete selected experimental data point(s)"""
        selection = self.exp_data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select data point(s) to delete")
            return
        
        # Confirm deletion
        count = len(selection)
        result = messagebox.askyesno("Confirm Delete", 
                                     f"Delete {count} data point(s)?")
        if not result:
            return
        
        # Collect all points to delete
        points_to_delete = []
        for item in selection:
            values = self.exp_data_tree.item(item)['values']
            mat_name = values[0]
            W_f = float(values[1])
            points_to_delete.append((mat_name, W_f))
        
        # Delete all selected points
        for mat_name, W_f in points_to_delete:
            for mat in self.materials:
                if mat.name == mat_name:
                    for i, pt in enumerate(mat.experimental_data):
                        if abs(pt.W_f - W_f) < 1e-6:
                            mat.experimental_data.pop(i)
                            break
                    break
        
        self.update_experimental_data_table()
        self.show_toast(f"{count} data point(s) deleted")
    
    def duplicate_selected_rows(self):
        """Duplicate selected experimental data rows"""
        selection = self.exp_data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select data point(s) to duplicate")
            return
        
        count = 0
        for item in selection:
            values = self.exp_data_tree.item(item)['values']
            mat_name = values[0]
            W_f = float(values[1])
            
            # Find the original point
            for mat in self.materials:
                if mat.name == mat_name:
                    for pt in mat.experimental_data:
                        if abs(pt.W_f - W_f) < 1e-6:
                            # Create duplicate
                            new_pt = ExperimentalDataPoint(
                                W_f=pt.W_f,
                                V_f=pt.V_f,
                                V_m=pt.V_m,
                                V_p=pt.V_p,
                                E_c=pt.E_c,
                                rho_c=pt.rho_c,
                                notes=pt.notes + " (copy)" if pt.notes else "(copy)"
                            )
                            mat.experimental_data.append(new_pt)
                            count += 1
                            break
                    break
        
        self.update_experimental_data_table()
        self.show_toast(f"{count} data point(s) duplicated")
    
    def select_all_rows(self):
        """Select all rows in experimental data table"""
        all_items = self.exp_data_tree.get_children()
        self.exp_data_tree.selection_set(all_items)
        self.show_toast(f"Selected {len(all_items)} data point(s)")
    
    def copy_selected_rows(self):
        """Copy selected rows to clipboard"""
        selection = self.exp_data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select data point(s) to copy")
            return
        
        self.clipboard_data = []
        for item in selection:
            values = self.exp_data_tree.item(item)['values']
            mat_name = values[0]
            W_f = float(values[1])
            
            # Find and copy the point
            for mat in self.materials:
                if mat.name == mat_name:
                    for pt in mat.experimental_data:
                        if abs(pt.W_f - W_f) < 1e-6:
                            self.clipboard_data.append({
                                'W_f': pt.W_f,
                                'V_f': pt.V_f,
                                'V_m': pt.V_m,
                                'V_p': pt.V_p,
                                'E_c': pt.E_c,
                                'rho_c': pt.rho_c,
                                'notes': pt.notes
                            })
                            break
                    break
        
        self.show_toast(f"Copied {len(self.clipboard_data)} data point(s)")
    
    def paste_rows(self):
        """Paste copied rows to current material"""
        if not self.clipboard_data:
            messagebox.showwarning("Warning", "No data in clipboard")
            return
        
        mat = self.materials[self.current_material_index]
        count = 0
        
        for data in self.clipboard_data:
            new_pt = ExperimentalDataPoint(
                W_f=data['W_f'],
                V_f=data['V_f'],
                V_m=data['V_m'],
                V_p=data['V_p'],
                E_c=data['E_c'],
                rho_c=data['rho_c'],
                notes=data['notes']
            )
            mat.experimental_data.append(new_pt)
            count += 1
        
        self.update_experimental_data_table()
        self.show_toast(f"Pasted {count} data point(s) to {mat.name}")
    
    def show_context_menu(self, event):
        """Show right-click context menu for experimental data"""
        # Select the row under cursor
        item = self.exp_data_tree.identify_row(event.y)
        if item:
            self.exp_data_tree.selection_set(item)
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        
        selection = self.exp_data_tree.selection()
        if selection:
            count = len(selection)
            context_menu.add_command(label=f"✏️ Edit ({count})", command=self.edit_experimental_point)
            context_menu.add_command(label=f"🗑️ Delete ({count})", command=self.delete_experimental_point)
            context_menu.add_command(label=f"📋 Duplicate ({count})", command=self.duplicate_selected_rows)
            context_menu.add_separator()
            context_menu.add_command(label=f"📄 Copy ({count})", command=self.copy_selected_rows)
        
        if self.clipboard_data:
            context_menu.add_command(label=f"📌 Paste ({len(self.clipboard_data)})", command=self.paste_rows)
        
        context_menu.add_separator()
        context_menu.add_command(label="✓ Select All", command=self.select_all_rows)
        context_menu.add_command(label="➕ Add New Row", command=self.add_empty_experimental_row)
        
        # Show menu
        context_menu.tk_popup(event.x_root, event.y_root)
    
    def import_experimental_csv(self):
        """Import experimental data from CSV file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import Experimental Data"
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Parse values
                    W_f = float(row.get('W_f', row.get('Wf', 0)))
                    
                    def parse_optional(key, alt_key=None):
                        val = row.get(key, row.get(alt_key, '') if alt_key else '')
                        if val and val != '-' and val.strip():
                            try:
                                return float(val)
                            except:
                                return None
                        return None
                    
                    V_f = parse_optional('V_f', 'Vf')
                    V_m = parse_optional('V_m', 'Vm')
                    V_p = parse_optional('V_p', 'Vp')
                    E_c = parse_optional('E_c', 'Ec')
                    rho_c = parse_optional('rho_c', 'rhoc')
                    notes = row.get('Notes', row.get('notes', ''))
                    
                    # Create data point
                    point = ExperimentalDataPoint(W_f, V_f, V_m, V_p, E_c, rho_c, notes)
                    self.materials[self.current_material_index].experimental_data.append(point)
                    imported_count += 1
            
            self.update_experimental_data_table()
            self.show_toast(f"Imported {imported_count} data point(s)")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV:\n{str(e)}")
    
    def export_experimental_csv(self):
        """Export experimental data to CSV file"""
        mat = self.materials[self.current_material_index]
        
        if not mat.experimental_data:
            messagebox.showwarning("Warning", "No experimental data to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"{mat.name.replace(' ', '_')}_experimental_data.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Experimental Data"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['W_f', 'V_f', 'V_m', 'V_p', 'E_c', 'rho_c', 'Notes'])
                
                for pt in mat.experimental_data:
                    writer.writerow([
                        f"{pt.W_f:.4f}",
                        f"{pt.V_f:.4f}" if pt.V_f is not None else "",
                        f"{pt.V_m:.4f}" if pt.V_m is not None else "",
                        f"{pt.V_p:.4f}" if pt.V_p is not None else "",
                        f"{pt.E_c:.2f}" if pt.E_c is not None else "",
                        f"{pt.rho_c:.4f}" if pt.rho_c is not None else "",
                        pt.notes
                    ])
            
            self.show_toast("Experimental data exported")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{str(e)}")
    
    def open_curve_fitting_dialog(self):
        """Open curve fitting dialog"""
        mat = self.materials[self.current_material_index]
        
        if not mat.experimental_data:
            messagebox.showwarning("Warning", 
                                 "No experimental data available for curve fitting.\n"
                                 "Please add experimental data points first.")
            return
        
        if not mat.results:
            messagebox.showwarning("Warning",
                                 "Please calculate the material properties first.\n"
                                 "Click 'Calculate' button before fitting.")
            return
        
        dialog = CurveFittingDialog(self.root, mat, self)
        self.root.wait_window(dialog.dialog)
        
        if dialog.fitted_params:
            # Apply fitted parameters
            self.apply_fitted_parameters(dialog.fitted_params)
    
    def apply_fitted_parameters(self, fitted_params):
        """Apply fitted parameters to current material"""
        mat = self.materials[self.current_material_index]
        
        # Update parameters
        if 'matrix_density' in fitted_params:
            mat.matrix_density = fitted_params['matrix_density']
        if 'matrix_porosity' in fitted_params:
            mat.matrix_porosity = fitted_params['matrix_porosity']
        if 'matrix_stiffness' in fitted_params:
            mat.matrix_stiffness = fitted_params['matrix_stiffness']
        if 'matrix_poisson' in fitted_params:
            mat.matrix_poisson = fitted_params['matrix_poisson']
        if 'fiber_density' in fitted_params:
            mat.fiber_density = fitted_params['fiber_density']
        if 'fiber_porosity' in fitted_params:
            mat.fiber_porosity = fitted_params['fiber_porosity']
        if 'fiber_stiffness' in fitted_params:
            mat.fiber_stiffness = fitted_params['fiber_stiffness']
        if 'fiber_eta0' in fitted_params:
            mat.fiber_eta0 = fitted_params['fiber_eta0']
        if 'v_f_max' in fitted_params:
            mat.v_f_max = fitted_params['v_f_max']
        if 'porosity_exp' in fitted_params:
            mat.porosity_exp = fitted_params['porosity_exp']
        
        # Reload the material into the form
        self.load_material(self.current_material_index)
        
        # Recalculate with new parameters
        self.calculate_current()
        
        self.show_toast("Fitted parameters applied successfully!")
    
    # ========================================================================
    # PLOTTING & VISUALIZATION
    # ========================================================================
    
    def generate_plots(self):
        """Generate comparison plots for all calculated materials with plot_enabled=True"""
        # Get materials with results AND plot enabled
        calculated_materials = [mat for mat in self.materials if mat.results and mat.plot_enabled]
        
        if not calculated_materials:
            # Check if there are calculated materials but all disabled
            all_calculated = [mat for mat in self.materials if mat.results]
            if all_calculated:
                messagebox.showwarning("Warning", "All materials are excluded from plotting!\n\n" +
                                     "Enable 'Include in plots' checkbox for at least one material.")
            else:
                messagebox.showwarning("Warning", "No calculated materials to plot!")
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
            
            # Generate plots for each material
            plot_data = {}
            
            for mat in calculated_materials:
                V_f_array = []
                V_m_array = []
                V_p_array = []
                rho_c_array = []
                rho_c_no_porosity_array = []
                E_c_array = []
                eta1_array = []
                
                G_m = mat.results['G_m']
                
                for W_f in W_f_array:
                    try:
                        case = Composite_case(
                            mat.results['composite'],
                            fiber_mass_fraction=W_f,
                            max_volume_fiber=mat.v_f_max,
                            porosity_efficiency_exponent=mat.porosity_exp
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
                        
                        # Calculate density without porosity
                        total = V_f + V_m
                        V_f_norm = V_f / total if total > 0 else 0
                        V_m_norm = V_m / total if total > 0 else 0
                        rho_no_p = V_f_norm * mat.results['fiber'].rho + V_m_norm * mat.results['matrix'].rho
                        rho_c_no_porosity_array.append(rho_no_p)
                        
                        E_c = case.calculate_composite_stiffness()
                        E_c_array.append(E_c)
                        
                        eta1 = mat.results['fiber'].calculate_length_efficiency_factor(G_m)
                        eta1_array.append(eta1)
                    except:
                        V_f_array.append(np.nan)
                        V_m_array.append(np.nan)
                        V_p_array.append(np.nan)
                        rho_c_array.append(np.nan)
                        rho_c_no_porosity_array.append(np.nan)
                        E_c_array.append(np.nan)
                        eta1_array.append(np.nan)
                
                plot_data[mat.name] = {
                    'W_f': W_f_array,
                    'V_f': V_f_array,
                    'V_m': V_m_array,
                    'V_p': V_p_array,
                    'rho_c': rho_c_array,
                    'rho_c_no_porosity': rho_c_no_porosity_array,
                    'E_c': E_c_array,
                    'eta1': eta1_array
                }
            
            # Create all comparison plots
            self.create_weight_volume_comparison_plot(plot_data)
            self.create_comparison_density_plot(plot_data)
            self.create_comparison_stiffness_plot(plot_data)
            self.create_fiber_efficiency_comparison_plot(plot_data)
            
            self.show_toast("All comparison plots generated!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plots:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def get_color_scheme(self, num_materials):
        """Generate color variations within same hue for each material
        Returns a list of (base_color, light, medium, dark) tuples"""
        import colorsys
        
        # Generate base hues evenly distributed around the color wheel
        if num_materials <= 10:
            # Use predefined nice hues for small numbers
            base_hues = [0.0, 0.58, 0.33, 0.08, 0.75, 0.15, 0.5, 0.92, 0.42, 0.67][:num_materials]
        else:
            # Evenly distribute hues for more materials
            base_hues = [i / num_materials for i in range(num_materials)]
        
        color_variations = []
        for hue in base_hues:
            # Create three variations of the same hue
            # Light (high saturation, high value)
            light = colorsys.hsv_to_rgb(hue, 0.5, 1.0)
            # Medium (medium saturation, medium-high value)
            medium = colorsys.hsv_to_rgb(hue, 0.7, 0.85)
            # Dark (high saturation, medium value)
            dark = colorsys.hsv_to_rgb(hue, 0.85, 0.65)
            
            color_variations.append((light, medium, dark))
        
        return color_variations
    
    def create_weight_volume_comparison_plot(self, plot_data):
        """Create comparison plot for weight/volume relations"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Weight/Volume Relations")
        self.plot_tabs["Weight/Volume Relations"] = tab
        
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        colors = self.get_color_scheme(len(plot_data))
        
        # Plot for each material with hue variations
        for idx, (mat_name, data) in enumerate(plot_data.items()):
            light, medium, dark = colors[idx]
            
            # Use different line styles and color variations for V_f, V_m, V_p
            # V_f: solid line with light color
            ax.plot(data['W_f'], data['V_f'], '-', 
                   label=f'{mat_name} - V_f', linewidth=2, color=light)
            # V_m: dashed line with medium color
            ax.plot(data['W_f'], data['V_m'], '--', 
                   label=f'{mat_name} - V_m', linewidth=1.8, color=medium)
            # V_p: dash-dot line with dark color (more readable than dotted)
            ax.plot(data['W_f'], data['V_p'], '-.', 
                   label=f'{mat_name} - V_p', linewidth=1.8, color=dark)
            
            # Add experimental data points
            mat = next((m for m in self.materials if m.name == mat_name), None)
            if mat and mat.experimental_data:
                exp_W_f = [pt.W_f for pt in mat.experimental_data if pt.V_f is not None]
                exp_V_f = [pt.V_f for pt in mat.experimental_data if pt.V_f is not None]
                if exp_W_f:
                    ax.scatter(exp_W_f, exp_V_f, marker='o', s=60, color=light, 
                             edgecolors='black', linewidths=1.5, zorder=5,
                             label=f'{mat_name} - V_f (exp)')
                
                exp_W_f = [pt.W_f for pt in mat.experimental_data if pt.V_m is not None]
                exp_V_m = [pt.V_m for pt in mat.experimental_data if pt.V_m is not None]
                if exp_W_f:
                    ax.scatter(exp_W_f, exp_V_m, marker='s', s=60, color=medium,
                             edgecolors='black', linewidths=1.5, zorder=5,
                             label=f'{mat_name} - V_m (exp)')
                
                exp_W_f = [pt.W_f for pt in mat.experimental_data if pt.V_p is not None]
                exp_V_p = [pt.V_p for pt in mat.experimental_data if pt.V_p is not None]
                if exp_W_f:
                    ax.scatter(exp_W_f, exp_V_p, marker='^', s=60, color=dark,
                             edgecolors='black', linewidths=1.5, zorder=5,
                             label=f'{mat_name} - V_p (exp)')
        
        ax.set_xlabel('Fibre weight fraction', fontsize=10)
        ax.set_ylabel('Volume fractions', fontsize=10)
        ax.set_title('Weight/Volume Relations Comparison', fontsize=12, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        fig.tight_layout()
        self.plot_figures["Weight/Volume Relations"] = fig
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(button_frame, text="Save This Plot", 
                  command=lambda: self.save_plot("Weight/Volume Relations")).pack(side=tk.RIGHT)
    
    def create_comparison_density_plot(self, plot_data):
        """Create comparison plot for density with and without porosity"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Density Comparison")
        self.plot_tabs["Density Comparison"] = tab
        
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        colors = self.get_color_scheme(len(plot_data))
        
        for idx, (mat_name, data) in enumerate(plot_data.items()):
            light, medium, dark = colors[idx]
            rho_c_gcm3 = [rho/1000 for rho in data['rho_c']]
            rho_c_no_p_gcm3 = [rho/1000 for rho in data['rho_c_no_porosity']]
            
            # Solid line with medium color for actual density
            ax.plot(data['W_f'], rho_c_gcm3, '-', 
                   label=f'{mat_name}', linewidth=2, color=medium)
            # Dashed line with light color for no porosity
            ax.plot(data['W_f'], rho_c_no_p_gcm3, '--', 
                   label=f'{mat_name} (no porosity)', linewidth=2, color=light)
            
            # Add experimental data points
            mat = next((m for m in self.materials if m.name == mat_name), None)
            if mat and mat.experimental_data:
                exp_W_f = [pt.W_f for pt in mat.experimental_data if pt.rho_c is not None]
                exp_rho_c = [pt.rho_c for pt in mat.experimental_data if pt.rho_c is not None]
                if exp_W_f:
                    ax.scatter(exp_W_f, exp_rho_c, marker='o', s=80, color=medium,
                             edgecolors='black', linewidths=1.5, zorder=5,
                             label=f'{mat_name} (exp)')
        
        ax.set_xlabel('Fibre weight fraction', fontsize=10)
        ax.set_ylabel('Composite density (g/cm³)', fontsize=10)
        ax.set_title('Composite Density Comparison', fontsize=12, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        
        fig.tight_layout()
        self.plot_figures["Density Comparison"] = fig
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(button_frame, text="Save This Plot", 
                  command=lambda: self.save_plot("Density Comparison")).pack(side=tk.RIGHT)
    
    def create_comparison_stiffness_plot(self, plot_data):
        """Create comparison plot for stiffness"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Stiffness Comparison")
        self.plot_tabs["Stiffness Comparison"] = tab
        
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        colors = self.get_color_scheme(len(plot_data))
        
        for idx, (mat_name, data) in enumerate(plot_data.items()):
            light, medium, dark = colors[idx]
            # Use medium color for stiffness
            ax.plot(data['W_f'], data['E_c'], label=mat_name, linewidth=2, color=medium)
            
            # Add experimental data points
            mat = next((m for m in self.materials if m.name == mat_name), None)
            if mat and mat.experimental_data:
                exp_W_f = [pt.W_f for pt in mat.experimental_data if pt.E_c is not None]
                exp_E_c = [pt.E_c for pt in mat.experimental_data if pt.E_c is not None]
                if exp_W_f:
                    ax.scatter(exp_W_f, exp_E_c, marker='o', s=80, color=medium,
                             edgecolors='black', linewidths=1.5, zorder=5,
                             label=f'{mat_name} (exp)')
        
        ax.set_xlabel('Fibre weight fraction', fontsize=10)
        ax.set_ylabel('Composite stiffness (GPa)', fontsize=10)
        ax.set_title('Composite Stiffness Comparison', fontsize=12, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        
        fig.tight_layout()
        self.plot_figures["Stiffness Comparison"] = fig
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(button_frame, text="Save This Plot", 
                  command=lambda: self.save_plot("Stiffness Comparison")).pack(side=tk.RIGHT)
    
    def create_fiber_efficiency_comparison_plot(self, plot_data):
        """Create comparison plot for fiber length efficiency factor"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Fiber Efficiency Comparison")
        self.plot_tabs["Fiber Efficiency Comparison"] = tab
        
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        colors = self.get_color_scheme(len(plot_data))
        
        for idx, (mat_name, data) in enumerate(plot_data.items()):
            light, medium, dark = colors[idx]
            # Use medium color for fiber efficiency
            ax.plot(data['W_f'], data['eta1'], label=mat_name, linewidth=2, color=medium)
        
        ax.set_xlabel('Fibre weight fraction', fontsize=10)
        ax.set_ylabel('Fibre length efficiency factor (η₁)', fontsize=10)
        ax.set_title('Fibre Length Efficiency Factor Comparison', fontsize=12, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0.9, 1.0)
        
        fig.tight_layout()
        self.plot_figures["Fiber Efficiency Comparison"] = fig
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(button_frame, text="Save This Plot", 
                  command=lambda: self.save_plot("Fiber Efficiency Comparison")).pack(side=tk.RIGHT)
    
    def save_plot(self, tab_name):
        """Save a specific plot"""
        if tab_name not in self.plot_figures:
            messagebox.showwarning("Warning", "No plot available to save.")
            return
        
        default_filename = tab_name.lower().replace(" ", "_") + ".png"
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
                # Create directory if it doesn't exist
                directory = os.path.dirname(file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                
                fig = self.plot_figures[tab_name]
                fig.savefig(file_path, dpi=300, bbox_inches='tight')
                self.show_toast("Plot saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save plot:\n{str(e)}")


# ============================================================================
# DIALOG CLASSES
# ============================================================================

class ExperimentalDataDialog:
    """Dialog for adding/editing experimental data points"""
    def __init__(self, parent, material_name, edit_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Experimental Data Point" if not edit_data else "Edit Experimental Data")
        self.dialog.geometry("500x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create scrollable canvas
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main frame
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text=f"Material: {material_name}", 
                 font=('Arial', 11, 'bold')).pack(pady=(0, 15))
        
        # Input fields
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # W_f (required)
        ttk.Label(input_frame, text="Fiber weight fraction (W_f): *", 
                 font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.w_f_var = tk.StringVar(value=str(edit_data.W_f) if edit_data else "")
        ttk.Entry(input_frame, textvariable=self.w_f_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1
        
        # V_f (optional)
        ttk.Label(input_frame, text="Fiber volume fraction (V_f):").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.v_f_var = tk.StringVar(value=str(edit_data.V_f) if edit_data and edit_data.V_f is not None else "")
        ttk.Entry(input_frame, textvariable=self.v_f_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1
        
        # V_m (optional)
        ttk.Label(input_frame, text="Matrix volume fraction (V_m):").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.v_m_var = tk.StringVar(value=str(edit_data.V_m) if edit_data and edit_data.V_m is not None else "")
        ttk.Entry(input_frame, textvariable=self.v_m_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1
        
        # V_p (optional)
        ttk.Label(input_frame, text="Porosity (V_p):").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.v_p_var = tk.StringVar(value=str(edit_data.V_p) if edit_data and edit_data.V_p is not None else "")
        ttk.Entry(input_frame, textvariable=self.v_p_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1
        
        # E_c (optional)
        ttk.Label(input_frame, text="Composite stiffness (E_c) [GPa]:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.e_c_var = tk.StringVar(value=str(edit_data.E_c) if edit_data and edit_data.E_c is not None else "")
        ttk.Entry(input_frame, textvariable=self.e_c_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1
        
        # rho_c (optional)
        ttk.Label(input_frame, text="Composite density (ρ_c) [g/cm³]:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.rho_c_var = tk.StringVar(value=str(edit_data.rho_c) if edit_data and edit_data.rho_c is not None else "")
        ttk.Entry(input_frame, textvariable=self.rho_c_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1
        
        # Notes
        ttk.Label(input_frame, text="Notes:").grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.notes_text = tk.Text(input_frame, width=40, height=5, font=('Arial', 9))
        self.notes_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        if edit_data and edit_data.notes:
            self.notes_text.insert(1.0, edit_data.notes)
        row += 1
        
        # Info
        ttk.Label(input_frame, text="* Required field. Leave other fields empty if not measured.",
                 font=('Arial', 8), foreground='gray').grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="OK", command=self.ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def ok(self):
        """OK button handler"""
        try:
            W_f = float(self.w_f_var.get())
            
            def parse_optional(var):
                val = var.get().strip()
                if val:
                    return float(val)
                return None
            
            self.result = {
                'W_f': W_f,
                'V_f': parse_optional(self.v_f_var),
                'V_m': parse_optional(self.v_m_var),
                'V_p': parse_optional(self.v_p_var),
                'E_c': parse_optional(self.e_c_var),
                'rho_c': parse_optional(self.rho_c_var),
                'notes': self.notes_text.get(1.0, tk.END).strip()
            }
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "W_f is required and must be a valid number!")
    
    def cancel(self):
        """Cancel button handler"""
        self.result = None
        self.dialog.destroy()


class CurveFittingDialog:
    """Dialog for curve fitting parameters"""
    def __init__(self, parent, material, gui_instance):
        self.material = material
        self.gui_instance = gui_instance
        self.fitted_params = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Curve Fitting")
        self.dialog.geometry("650x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create scrollable canvas
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main frame
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text=f"Curve Fitting for: {material.name}", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        ttk.Label(main_frame, 
                 text=f"Experimental data points: {len(material.experimental_data)}",
                 font=('Arial', 9), foreground='gray').pack(pady=(0, 15))
        
        # Optimization target
        target_frame = ttk.LabelFrame(main_frame, text="Optimization Target", padding="10")
        target_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.target_var = tk.StringVar(value='both')
        ttk.Radiobutton(target_frame, text="Minimize stiffness (E_c) error only", 
                       variable=self.target_var, value='stiffness').pack(anchor=tk.W)
        ttk.Radiobutton(target_frame, text="Minimize density (ρ_c) error only", 
                       variable=self.target_var, value='density').pack(anchor=tk.W)
        ttk.Radiobutton(target_frame, text="Minimize combined error (E_c and ρ_c)", 
                       variable=self.target_var, value='both').pack(anchor=tk.W)
        ttk.Radiobutton(target_frame, text="Minimize volume fraction errors (V_f, V_m, V_p)", 
                       variable=self.target_var, value='volume').pack(anchor=tk.W)
        
        # Parameters to optimize
        params_frame = ttk.LabelFrame(main_frame, text="Parameters to Optimize", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.param_vars = {}
        
        # Matrix parameters
        ttk.Label(params_frame, text="Matrix Properties:", 
                 font=('Arial', 9, 'bold')).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.param_vars['matrix_density'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Matrix density (ρ_m)", 
                       variable=self.param_vars['matrix_density']).grid(
            row=1, column=0, sticky=tk.W, padx=20)
        
        self.param_vars['matrix_porosity'] = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Matrix porosity factor (α_pm) [typically 0]", 
                       variable=self.param_vars['matrix_porosity']).grid(
            row=2, column=0, sticky=tk.W, padx=20)
        
        self.param_vars['matrix_stiffness'] = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Matrix stiffness (E_m)", 
                       variable=self.param_vars['matrix_stiffness']).grid(
            row=3, column=0, sticky=tk.W, padx=20)
        
        self.param_vars['matrix_poisson'] = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Matrix Poisson's ratio (ν_m)", 
                       variable=self.param_vars['matrix_poisson']).grid(
            row=4, column=0, sticky=tk.W, padx=20)
        
        # Fiber parameters
        ttk.Label(params_frame, text="Fiber Properties:", 
                 font=('Arial', 9, 'bold')).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.param_vars['fiber_density'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Fiber density (ρ_f)", 
                       variable=self.param_vars['fiber_density']).grid(
            row=6, column=0, sticky=tk.W, padx=20)
        
        self.param_vars['fiber_porosity'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Fiber porosity factor (α_pf)", 
                       variable=self.param_vars['fiber_porosity']).grid(
            row=7, column=0, sticky=tk.W, padx=20)
        
        self.param_vars['fiber_stiffness'] = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Fiber stiffness (E_f)", 
                       variable=self.param_vars['fiber_stiffness']).grid(
            row=8, column=0, sticky=tk.W, padx=20)
        
        self.param_vars['fiber_eta0'] = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Orientation efficiency (η₀)", 
                       variable=self.param_vars['fiber_eta0']).grid(
            row=9, column=0, sticky=tk.W, padx=20)
        
        # Composite parameters
        ttk.Label(params_frame, text="Composite Parameters:", 
                 font=('Arial', 9, 'bold')).grid(row=10, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.param_vars['v_f_max'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Max fiber volume fraction (V_f_max)", 
                       variable=self.param_vars['v_f_max']).grid(
            row=11, column=0, sticky=tk.W, padx=20)
        
        self.param_vars['porosity_exp'] = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Porosity exponent (n)", 
                       variable=self.param_vars['porosity_exp']).grid(
            row=12, column=0, sticky=tk.W, padx=20)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Fitting Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=10, 
                                    font=('Courier', 9))
        results_text_scroll = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.config(yscrollcommand=results_text_scroll.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 0))
        
        ttk.Button(button_frame, text="▶ Run Fitting", 
                  command=self.run_fitting).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✓ Apply Parameters", 
                  command=self.apply_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def run_fitting(self):
        """Run the curve fitting optimization with improved algorithm"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Analyzing experimental data...\n\n")
        self.dialog.update()
        
        try:
            # Get experimental data with target values
            exp_data = []
            target = self.target_var.get()
            
            for pt in self.material.experimental_data:
                if target == 'stiffness' and pt.E_c is not None:
                    exp_data.append(pt)
                elif target == 'density' and pt.rho_c is not None:
                    exp_data.append(pt)
                elif target == 'both' and (pt.E_c is not None or pt.rho_c is not None):
                    exp_data.append(pt)
                elif target == 'volume' and (pt.V_f is not None or pt.V_m is not None or pt.V_p is not None):
                    exp_data.append(pt)
            
            if not exp_data:
                self.results_text.insert(tk.END, "ERROR: No suitable experimental data for selected target!\n")
                return
            
            # Get parameters to optimize
            params_to_fit = [k for k, v in self.param_vars.items() if v.get()]
            
            if not params_to_fit:
                self.results_text.insert(tk.END, "ERROR: Please select at least one parameter to optimize!\n")
                return
            
            # Detect saturation from volume fraction data - find where V_f plateaus
            vf_data = [pt for pt in exp_data if pt.V_f is not None]
            v_f_saturated = None
            unsaturated_data = exp_data
            
            if len(vf_data) >= 3:
                sorted_vf = sorted(vf_data, key=lambda x: x.W_f)
                v_f_values = [pt.V_f for pt in sorted_vf]
                
                # Find where V_f becomes constant
                for i in range(len(sorted_vf) - 2):
                    remaining_vf = v_f_values[i:]
                    if len(remaining_vf) >= 3:
                        vf_std = np.std(remaining_vf)
                        vf_mean = np.mean(remaining_vf)
                        if vf_std < 0.005 * vf_mean:  # Very small variation (<0.5%)
                            v_f_saturated = vf_mean
                            # Include points up to AND INCLUDING first saturation point
                            # The boundary point is still useful information
                            unsaturated_data = [pt for pt in exp_data if pt.V_f is None or 
                                              (pt.V_f is not None and pt.W_f <= sorted_vf[i].W_f)]
                            break
                
                if v_f_saturated:
                    self.results_text.insert(tk.END, 
                        f"Saturation detected at V_f ≈ {v_f_saturated:.4f}\n")
                    self.results_text.insert(tk.END, 
                        f"Using {len(unsaturated_data)} points (up to saturation) for estimation\n\n")
            
            # Smart initial value estimation
            self.results_text.insert(tk.END, "Estimating initial parameters from data...\n")
            initial_estimates = self._estimate_initial_parameters(exp_data, unsaturated_data, v_f_saturated)
            
            # Initial values with smart estimates
            initial_values = []
            param_names = []
            bounds_list = []
            
            for param in params_to_fit:
                param_names.append(param)
                if param == 'matrix_density':
                    # Estimate from low W_f density
                    initial_val = initial_estimates.get('matrix_density', self.material.matrix_density)
                    initial_values.append(initial_val)
                    bounds_list.append((0.5, 2.5))
                elif param == 'matrix_porosity':
                    initial_values.append(initial_estimates.get('matrix_porosity', self.material.matrix_porosity))
                    bounds_list.append((0.0, 0.05))  # Tight bound - matrix typically non-porous
                elif param == 'matrix_stiffness':
                    initial_values.append(self.material.matrix_stiffness)
                    bounds_list.append((0.5, 10.0))
                elif param == 'matrix_poisson':
                    initial_values.append(self.material.matrix_poisson)
                    bounds_list.append((0.2, 0.5))
                elif param == 'fiber_density':
                    # Estimate from high W_f density
                    initial_val = initial_estimates.get('fiber_density', self.material.fiber_density)
                    initial_values.append(initial_val)
                    bounds_list.append((1.0, 4.0))
                elif param == 'fiber_porosity':
                    # Estimate from V_p / V_f ratio in unsaturated region
                    initial_val = initial_estimates.get('fiber_porosity', self.material.fiber_porosity)
                    initial_values.append(initial_val)
                    bounds_list.append((0.0, 0.5))
                elif param == 'fiber_stiffness':
                    initial_values.append(self.material.fiber_stiffness)
                    bounds_list.append((10.0, 500.0))
                elif param == 'fiber_eta0':
                    initial_values.append(self.material.fiber_eta0)
                    bounds_list.append((0.1, 1.0))
                elif param == 'v_f_max':
                    # Use detected saturation value if available
                    initial_val = v_f_saturated if v_f_saturated else self.material.v_f_max
                    initial_values.append(initial_val)
                    if v_f_saturated:
                        # Narrow bounds around detected value
                        bounds_list.append((v_f_saturated * 0.95, v_f_saturated * 1.05))
                    else:
                        bounds_list.append((0.15, 0.80))
                elif param == 'porosity_exp':
                    initial_values.append(self.material.porosity_exp)
                    bounds_list.append((1.0, 5.0))
            
            self.results_text.insert(tk.END, "\nInitial estimates:\n")
            for i, name in enumerate(param_names):
                self.results_text.insert(tk.END, f"  {name}: {initial_values[i]:.6f}\n")
            self.results_text.insert(tk.END, "\nRunning optimization...\n")
            self.dialog.update()
            
            # Define objective function with improved weighting
            def objective(params):
                # Update material with current parameters
                temp_mat = MaterialConfig()
                for key in vars(self.material):
                    setattr(temp_mat, key, getattr(self.material, key))
                
                for i, param_name in enumerate(param_names):
                    setattr(temp_mat, param_name, params[i])
                
                # Calculate error
                error = 0.0
                count = 0
                
                # Use unsaturated data for fiber porosity sensitive calculations
                data_to_use = unsaturated_data if ('fiber_porosity' in param_names) else exp_data
                
                for pt in data_to_use:
                    try:
                        # Perform calculation
                        results = self.gui_instance.perform_calculation(temp_mat)
                        
                        # Calculate for this W_f
                        case = Composite_case(
                            results['composite'],
                            fiber_mass_fraction=pt.W_f,
                            max_volume_fiber=temp_mat.v_f_max,
                            porosity_efficiency_exponent=temp_mat.porosity_exp
                        )
                        
                        if case.determine_case() == 'Case A':
                            V_f, V_m, V_p = case.calculate_volume_fractions_case_a()
                        else:
                            V_f, V_m, V_p = case.calculate_volume_fractions_case_b()
                        
                        rho_c = case.calculate_composite_density() / 1000  # Convert to g/cm³
                        E_c = case.calculate_composite_stiffness()
                        
                        # Calculate error based on target with proper weighting
                        if target == 'stiffness' and pt.E_c is not None:
                            error += ((E_c - pt.E_c) / pt.E_c) ** 2
                            count += 1
                        elif target == 'density' and pt.rho_c is not None:
                            error += ((rho_c - pt.rho_c) / pt.rho_c) ** 2
                            count += 1
                        elif target == 'both':
                            if pt.E_c is not None:
                                error += ((E_c - pt.E_c) / pt.E_c) ** 2
                                count += 1
                            if pt.rho_c is not None:
                                error += ((rho_c - pt.rho_c) / pt.rho_c) ** 2
                                count += 1
                        elif target == 'volume':
                            # Volume fractions are the most reliable measurements
                            # Weight them equally
                            if pt.V_f is not None:
                                error += (V_f - pt.V_f) ** 2 * 10  # Higher weight
                                count += 1
                            if pt.V_m is not None:
                                error += (V_m - pt.V_m) ** 2 * 10
                                count += 1
                            if pt.V_p is not None:
                                error += (V_p - pt.V_p) ** 2 * 10
                                count += 1
                            # Also include density if available
                            if pt.rho_c is not None:
                                error += ((rho_c - pt.rho_c) / pt.rho_c) ** 2
                                count += 1
                    except Exception as e:
                        # Penalize failed calculations heavily
                        error += 1000
                        count += 1
                
                return error / count if count > 0 else 1000
            
            # Calculate initial error
            initial_error = objective(initial_values)
            self.results_text.insert(tk.END, f"Initial error: {initial_error:.6e}\n\n")
            self.dialog.update()
            
            # Run optimization with L-BFGS-B (local optimizer)
            self.results_text.insert(tk.END, "Optimizing (L-BFGS-B method)...\n")
            self.dialog.update()
            
            result = minimize(objective, initial_values, method='L-BFGS-B', bounds=bounds_list,
                            options={'maxiter': 2000, 'ftol': 1e-12})
            
            # Display results
            self.results_text.insert(tk.END, "OPTIMIZATION COMPLETED\n")
            self.results_text.insert(tk.END, "=" * 50 + "\n\n")
            
            if result.success:
                self.results_text.insert(tk.END, "Status: SUCCESS\n")
                self.results_text.insert(tk.END, f"Final error: {result.fun:.6e}\n")
                self.results_text.insert(tk.END, f"Iterations: {result.nit}\n\n")
                
                self.results_text.insert(tk.END, "FITTED PARAMETERS:\n")
                self.results_text.insert(tk.END, "-" * 50 + "\n")
                
                self.fitted_params = {}
                for i, param_name in enumerate(param_names):
                    original = getattr(self.material, param_name)
                    fitted = result.x[i]
                    
                    # Calculate percentage change (avoid division by zero)
                    if abs(original) > 1e-10:
                        change = ((fitted - original) / original) * 100
                        change_str = f"{change:+.2f}%"
                    else:
                        change_str = f"(from ~0 to {fitted:.6f})"
                    
                    self.fitted_params[param_name] = fitted
                    
                    self.results_text.insert(tk.END, 
                        f"{param_name}:\n"
                        f"  Original: {original:.6f}\n"
                        f"  Fitted:   {fitted:.6f}\n"
                        f"  Change:   {change_str}\n\n")
                
                self.results_text.insert(tk.END, 
                    "\nClick 'Apply Parameters' to use these fitted values.\n")
            else:
                self.results_text.insert(tk.END, f"Status: FAILED\n")
                self.results_text.insert(tk.END, f"Message: {result.message}\n")
                self.fitted_params = None
        
        except Exception as e:
            self.results_text.insert(tk.END, f"\nERROR during optimization:\n{str(e)}\n")
            import traceback
            self.results_text.insert(tk.END, f"\n{traceback.format_exc()}\n")
            self.fitted_params = None
    
    def _estimate_initial_parameters(self, exp_data, unsaturated_data, v_f_saturated):
        """Estimate initial parameter values from experimental data"""
        estimates = {}
        
        # Estimate V_f_max from saturation
        if v_f_saturated:
            estimates['v_f_max'] = v_f_saturated
        
        # Estimate densities using two-point method (solving system of equations)
        density_points = [pt for pt in unsaturated_data if pt.rho_c is not None and pt.V_f is not None and pt.V_m is not None]
        
        if len(density_points) >= 2:
            # Use first two unsaturated points to solve for ρ_f and ρ_m
            # System: ρ_c1 = V_f1*ρ_f + V_m1*ρ_m
            #         ρ_c2 = V_f2*ρ_f + V_m2*ρ_m
            pt1 = density_points[0]
            pt2 = density_points[1]
            
            try:
                A = np.array([[pt1.V_f, pt1.V_m], [pt2.V_f, pt2.V_m]])
                b = np.array([pt1.rho_c, pt2.rho_c])
                rho_f_est, rho_m_est = np.linalg.solve(A, b)
                
                # Sanity check: densities should be positive and reasonable
                if 0.5 < rho_m_est < 2.5 and 1.0 < rho_f_est < 4.0:
                    estimates['fiber_density'] = rho_f_est
                    estimates['matrix_density'] = rho_m_est
                else:
                    # Use defaults if unreasonable
                    estimates['fiber_density'] = 2.1
                    estimates['matrix_density'] = 1.0
            except:
                # If system is singular or fails, use defaults
                estimates['fiber_density'] = 2.1
                estimates['matrix_density'] = 1.0
        else:
            # Not enough data, use reasonable defaults
            estimates['fiber_density'] = 2.1
            estimates['matrix_density'] = 1.0
        
        # Estimate fiber porosity from V_p/V_f ratio in unsaturated region
        if len(unsaturated_data) > 0:
            vf_vp_points = [pt for pt in unsaturated_data 
                           if pt.V_f is not None and pt.V_p is not None and pt.V_f > 0.1]
            if vf_vp_points:
                ratios = [pt.V_p / pt.V_f for pt in vf_vp_points]
                estimates['fiber_porosity'] = np.mean(ratios)
            else:
                estimates['fiber_porosity'] = 0.0
        else:
            estimates['fiber_porosity'] = 0.0
        
        # Matrix porosity - always zero (matrix is non-porous)
        estimates['matrix_porosity'] = 0.0
        
        return estimates
    
    def apply_and_close(self):
        """Apply fitted parameters and close"""
        if not self.fitted_params:
            messagebox.showwarning("Warning", "No fitted parameters available. Run fitting first!")
            return
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel and close"""
        self.fitted_params = None
        self.dialog.destroy()


class SamplingDialog:
    """Dialog for CSV export sampling options"""
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export Options")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="CSV Export Options", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Export mode
        ttk.Label(main_frame, text="Export Mode:").pack(anchor=tk.W, pady=5)
        self.mode_var = tk.StringVar(value='summary')
        ttk.Radiobutton(main_frame, text="Summary (current W_f values only)", 
                       variable=self.mode_var, value='summary').pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(main_frame, text="Detailed (sample across W_f range)", 
                       variable=self.mode_var, value='detailed').pack(anchor=tk.W, padx=20)
        
        # Sampling options (for detailed mode)
        detail_frame = ttk.LabelFrame(main_frame, text="Detailed Mode Options", padding="10")
        detail_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(detail_frame, text="Number of samples:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.num_samples_var = tk.StringVar(value='100')
        ttk.Entry(detail_frame, textvariable=self.num_samples_var, width=10).grid(row=0, column=1, pady=5)
        
        ttk.Label(detail_frame, text="W_f range min:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.w_f_min_var = tk.StringVar(value='0.0')
        ttk.Entry(detail_frame, textvariable=self.w_f_min_var, width=10).grid(row=1, column=1, pady=5)
        
        ttk.Label(detail_frame, text="W_f range max:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.w_f_max_var = tk.StringVar(value='1.0')
        ttk.Entry(detail_frame, textvariable=self.w_f_max_var, width=10).grid(row=2, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Export", command=self.ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def ok(self):
        """OK button handler"""
        try:
            self.result = {
                'mode': self.mode_var.get(),
                'num_samples': int(self.num_samples_var.get()),
                'w_f_range': (float(self.w_f_min_var.get()), float(self.w_f_max_var.get()))
            }
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input values!")
    
    def cancel(self):
        """Cancel button handler"""
        self.result = None
        self.dialog.destroy()


def main():
    """Main function to run the advanced GUI"""
    root = tk.Tk()
    app = CompositeGUIAdvanced(root)
    root.mainloop()


if __name__ == "__main__":
    main()
