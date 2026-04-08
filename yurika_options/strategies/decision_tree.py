"""
Strategy recommendation system with decision tree logic.
"""
import pandas as pd
from typing import Dict, List, Tuple, Optional


def strategy_decision_tree(iv_pct: float, iv_rank: float, hv20_pct: float, 
                          dte: int, underlying: str = "SPY") -> Dict:
    """
    Core strategy recommendation logic.
    Returns dict with strategy, rationale, and key metrics.
    """
    iv_hv_ratio = iv_pct / hv20_pct if hv20_pct > 0 else 0
    
    # Strategy selection logic
    if iv_rank <= 40 and iv_hv_ratio <= 1.05:
        # Low IV environment - buy volatility
        if dte >= 30:
            strategy = "Long Straddle"
            rationale = f"Low IV Rank ({iv_rank:.1f}) + Low IV/HV ({iv_hv_ratio:.2f}) = Buy volatility"
        else:
            strategy = "Long Strangle" 
            rationale = f"Low IV + Short DTE = Cheaper strangle entry"
    
    elif iv_rank >= 50 and iv_hv_ratio >= 1.25:
        # High IV environment - sell volatility
        if dte >= 45:
            strategy = "Iron Condor"
            rationale = f"High IV Rank ({iv_rank:.1f}) + High IV/HV ({iv_hv_ratio:.2f}) = Sell premium"
        else:
            strategy = "Iron Butterfly"
            rationale = f"High IV + Short DTE = Quick theta decay"
    
    elif 25 <= dte <= 45:
        # Medium term - calendar spreads
        strategy = "Calendar Spread"
        rationale = f"Medium DTE ({dte}d) + IV/HV neutral = Time spread"
        
    else:
        # Default to directional play
        strategy = "Put Credit Spread"
        rationale = f"Mixed signals - conservative bullish bias"
    
    return {
        "strategy": strategy,
        "rationale": rationale,
        "iv_rank": iv_rank,
        "iv_hv_ratio": iv_hv_ratio,
        "dte": dte,
        "confidence": _calculate_confidence(iv_rank, iv_hv_ratio, dte)
    }


def _calculate_confidence(iv_rank: float, iv_hv_ratio: float, dte: int) -> str:
    """Calculate confidence level for strategy recommendation."""
    score = 0
    
    # IV Rank confidence
    if iv_rank <= 25 or iv_rank >= 75:
        score += 2  # Strong signal
    elif iv_rank <= 40 or iv_rank >= 60:
        score += 1  # Medium signal
    
    # IV/HV ratio confidence  
    if iv_hv_ratio <= 0.9 or iv_hv_ratio >= 1.3:
        score += 2  # Strong signal
    elif iv_hv_ratio <= 1.1 or iv_hv_ratio >= 1.2:
        score += 1  # Medium signal
        
    # DTE confidence
    if 21 <= dte <= 45:
        score += 1  # Optimal range
    
    if score >= 4:
        return "High"
    elif score >= 2:
        return "Medium" 
    else:
        return "Low"


def batch_strategy_analysis(tickers: List[str]) -> pd.DataFrame:
    """Run strategy analysis on multiple tickers."""
    # This would import from vol_core
    from yurika_options.core.vol_core import full_scan
    
    results = []
    
    for ticker in tickers:
        try:
            data = full_scan(ticker)
            strategy_result = strategy_decision_tree(
                iv_pct=data['iv_pct_display'],
                iv_rank=data.get('iv_rank', 50),  # Default if missing
                hv20_pct=data['hv20_pct'],
                dte=data['near_dte'],
                underlying=ticker
            )
            
            results.append({
                'Ticker': ticker,
                'Strategy': strategy_result['strategy'],
                'IV Rank': strategy_result['iv_rank'],
                'IV/HV': strategy_result['iv_hv_ratio'],
                'DTE': strategy_result['dte'],
                'Confidence': strategy_result['confidence'],
                'Rationale': strategy_result['rationale']
            })
            
        except Exception as e:
            results.append({
                'Ticker': ticker,
                'Strategy': 'ERROR',
                'Error': str(e)
            })
    
    return pd.DataFrame(results)
