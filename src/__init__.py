"""
Composite Material Analysis - Source Package

This package contains the core modules for composite material analysis.
"""

from .Mech_tool_composite import Matrix, Fiber, Composite_mix, Composite_case
from .Mech_tool_composite import (plot_weight_volume_relations, 
                                   plot_composite_density,
                                   plot_mechanical_properties,
                                   plot_fiber_length_efficiency,
                                   plot_all_graphs)

__all__ = [
    'Matrix',
    'Fiber', 
    'Composite_mix',
    'Composite_case',
    'plot_weight_volume_relations',
    'plot_composite_density',
    'plot_mechanical_properties',
    'plot_fiber_length_efficiency',
    'plot_all_graphs'
]

__version__ = '1.0.0'
