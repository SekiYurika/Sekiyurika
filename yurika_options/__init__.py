"""
Yurika's Professional Options Trading Toolkit
Version 1.0 - Comprehensive volatility analysis and strategy tools
"""

__version__ = "1.0.0" 
__author__ = "Yurika Seki"

# Core volatility functions
from .core.vol_core import full_scan, calc_hv, get_atm_iv, fetch_history

# Strategy tools
from .strategies.decision_tree import strategy_decision_tree, batch_strategy_analysis
from .strategies.calendar_optimizer import calendar_analysis_summary, scan_calendar_opportunities

# Analysis tools  
from .analysis.iv_hv_scanner import iv_hv_scanner, quick_scan
from .analysis.dix_gex_analyzer import dix_gex_summary, plot_dix_gex_analysis

# Make key functions easily accessible
__all__ = [
    # Core functions
    "full_scan",
    "calc_hv",
    "get_atm_iv", 
    "fetch_history",
    
    # Strategy functions
    "strategy_decision_tree",
    "batch_strategy_analysis",
    "calendar_analysis_summary",
    "scan_calendar_opportunities",
    
    # Analysis functions
    "iv_hv_scanner",
    "quick_scan",
    "dix_gex_summary", 
    "plot_dix_gex_analysis",
]
