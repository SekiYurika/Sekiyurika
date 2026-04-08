"""
IV/HV Scanner for multiple tickers with comprehensive analysis.
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from ..core.vol_core import full_scan


def iv_hv_scanner(tickers: List[str]) -> pd.DataFrame:
    """
    Scan multiple tickers for IV/HV opportunities.
    Returns DataFrame with all key metrics.
    """
    results = []
    
    for ticker in tickers:
        try:
            data = full_scan(ticker)
            
            # Calculate additional metrics
            iv_hv_ratio = data['iv'] / data['hv20'] if data['hv20'] else np.nan
            
            results.append({
                'Ticker': data['ticker'],
                'Spot': f"${data['spot']:.2f}",
                'IV %': f"{data['iv_pct_display']:.1f}%",
                'HV20 %': f"{data['hv20_pct']:.1f}%" if data['hv20_pct'] else "N/A",
                'IV/HV': f"{iv_hv_ratio:.2f}" if not np.isnan(iv_hv_ratio) else "N/A",
                'Near Exp': data['near_exp'],
                'DTE': data['near_dte'],
                'Status': _classify_opportunity(iv_hv_ratio, data.get('iv_rank', 50))
            })
            
        except Exception as e:
            results.append({
                'Ticker': ticker,
                'Status': f'ERROR: {str(e)[:30]}...',
                'Spot': 'N/A',
                'IV %': 'N/A',
                'HV20 %': 'N/A',
                'IV/HV': 'N/A',
                'Near Exp': 'N/A',
                'DTE': 'N/A'
            })
    
    return pd.DataFrame(results)


def _classify_opportunity(iv_hv_ratio: float, iv_rank: float) -> str:
    """Classify trading opportunity based on IV metrics."""
    if np.isnan(iv_hv_ratio):
        return "⚪ NO DATA"
    
    if iv_hv_ratio <= 0.95 and iv_rank <= 40:
        return "🟢 BUY VOL"
    elif iv_hv_ratio >= 1.3 and iv_rank >= 60:
        return "🔴 SELL VOL" 
    elif 0.95 < iv_hv_ratio < 1.3:
        return "🟡 NEUTRAL"
    else:
        return "⚪ MIXED"


def quick_scan(preset: str = "popular") -> pd.DataFrame:
    """Quick scan with preset ticker lists."""
    presets = {
        "popular": ["SPY", "QQQ", "IWM", "TSLA", "AAPL", "NVDA", "AMZN"],
        "etfs": ["SPY", "QQQ", "IWM", "GLD", "TLT", "XLE", "XLF"],
        "mag7": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"]
    }
    
    tickers = presets.get(preset, presets["popular"])
    return iv_hv_scanner(tickers)
