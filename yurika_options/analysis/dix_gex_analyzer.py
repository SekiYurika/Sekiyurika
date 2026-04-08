"""
DIX/GEX Market Structure Analysis
Dark Index and Gamma Exposure analysis for market positioning.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta


def load_squeeze_data(file_path: str) -> pd.DataFrame:
    """
    Load and clean SqueezeMetrics DIX/GEX data.
    Expected columns: date, dix, gex
    """
    try:
        # Try different date formats and separators
        for sep in [',', '\t', ';']:
            try:
                df = pd.read_csv(file_path, sep=sep)
                break
            except:
                continue
        else:
            raise ValueError("Could not parse CSV with common separators")
        
        # Standardize column names (case insensitive)
        df.columns = df.columns.str.lower().str.strip()
        
        # Convert date column
        date_cols = ['date', 'timestamp', 'time']
        date_col = None
        
        for col in date_cols:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            raise ValueError(f"No date column found. Available: {list(df.columns)}")
        
        # Parse dates
        df['date'] = pd.to_datetime(df[date_col])
        df = df.sort_values('date').reset_index(drop=True)
        
        # Validate required columns
        required = ['dix', 'gex']
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        
        # Convert to numeric
        df['dix'] = pd.to_numeric(df['dix'], errors='coerce')
        df['gex'] = pd.to_numeric(df['gex'], errors='coerce')
        
        # Remove rows with missing data
        df = df.dropna(subset=['date', 'dix', 'gex'])
        
        if len(df) == 0:
            raise ValueError("No valid data rows after cleaning")
        
        return df[['date', 'dix', 'gex']]
        
    except Exception as e:
        raise ValueError(f"Failed to load data: {str(e)}")


def calculate_derivatives(series: pd.Series, window: int = 5) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate smoothed 1st and 2nd derivatives of a time series.
    
    Returns:
        first_derivative: Rate of change (velocity)
        second_derivative: Acceleration
    """
    # Smooth the data first
    smoothed = series.rolling(window=window, center=True, min_periods=1).mean()
    
    # Calculate derivatives
    first_deriv = smoothed.diff()
    second_deriv = first_deriv.diff()
    
    return first_deriv, second_deriv


def analyze_trend_momentum(values: pd.Series, derivatives_1: pd.Series, 
                          derivatives_2: pd.Series) -> Dict:
    """
    Analyze trend and momentum characteristics of a time series.
    """
    current_val = values.iloc[-1]
    recent_vals = values.tail(10)
    
    # Trend analysis
    if recent_vals.iloc[-1] > recent_vals.iloc[0]:
        trend = "Uptrend"
    elif recent_vals.iloc[-1] < recent_vals.iloc[0]:  
        trend = "Downtrend"
    else:
        trend = "Sideways"
    
    # Momentum analysis
    recent_deriv1 = derivatives_1.tail(5).mean()
    recent_deriv2 = derivatives_2.tail(5).mean()
    
    if recent_deriv1 > 0 and recent_deriv2 > 0:
        momentum = "Accelerating Up"
    elif recent_deriv1 > 0 and recent_deriv2 < 0:
        momentum = "Decelerating Up"
    elif recent_deriv1 < 0 and recent_deriv2 < 0:
        momentum = "Accelerating Down"
    elif recent_deriv1 < 0 and recent_deriv2 > 0:
        momentum = "Decelerating Down"
    else:
        momentum = "Neutral"
    
    return {
        'current_value': current_val,
        'trend': trend,
        'momentum': momentum,
        'deriv1_current': derivatives_1.iloc[-1] if not pd.isna(derivatives_1.iloc[-1]) else 0,
        'deriv2_current': derivatives_2.iloc[-1] if not pd.isna(derivatives_2.iloc[-1]) else 0,
        'volatility': values.tail(20).std()
    }


def plot_dix_gex_analysis(df: pd.DataFrame, days_back: int = 200, 
                         smooth_window: int = 5) -> Dict:
    """
    Create comprehensive DIX/GEX analysis plots.
    
    Returns:
        dict: Analysis results with market interpretation
    """
    # Filter data
    cutoff_date = df['date'].max() - timedelta(days=days_back)
    recent_df = df[df['date'] >= cutoff_date].copy()
    
    if len(recent_df) < 10:
        raise ValueError(f"Insufficient data: only {len(recent_df)} rows")
    
    # Calculate derivatives
    dix_deriv1, dix_deriv2 = calculate_derivatives(recent_df['dix'], smooth_window)
    gex_deriv1, gex_deriv2 = calculate_derivatives(recent_df['gex'], smooth_window)
    
    # Analysis
    dix_analysis = analyze_trend_momentum(recent_df['dix'], dix_deriv1, dix_deriv2)
    gex_analysis = analyze_trend_momentum(recent_df['gex'], gex_deriv1, gex_deriv2)
    
    # Plotting
    dates = recent_df['date']
    
    # Set up the plot style
    plt.style.use('dark_background')
    colors = {
        'dix': '#00e5ff',
        'gex': '#ff4444', 
        'deriv1': '#ffaa00',
        'deriv2': '#aa55ff',
        'grid': '#333333',
        'text': '#ffffff'
    }
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], hspace=0.3, wspace=0.2)
    
    # Main DIX/GEX plots
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(dates, recent_df['dix'], color=colors['dix'], linewidth=2, label='DIX')
    ax1.axhline(y=0.45, color='red', linestyle='--', alpha=0.7, label='Bearish Threshold')
    ax1.axhline(y=0.50, color='green', linestyle='--', alpha=0.7, label='Bullish Threshold')
    ax1.set_title('DIX (Dark Index)', fontsize=14, color=colors['text'])
    ax1.set_ylabel('DIX Value', color=colors['text'])
    ax1.grid(True, alpha=0.3, color=colors['grid'])
    ax1.legend()
    
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(dates, recent_df['gex'], color=colors['gex'], linewidth=2, label='GEX')
    ax2.axhline(y=0, color='white', linestyle='-', alpha=0.5)
    ax2.axhline(y=5, color='green', linestyle='--', alpha=0.7, label='Positive Gamma')
    ax2.axhline(y=-5, color='red', linestyle='--', alpha=0.7, label='Negative Gamma')
    ax2.set_title('GEX (Gamma Exposure)', fontsize=14, color=colors['text'])
    ax2.set_ylabel('GEX (Billions)', color=colors['text'])
    ax2.grid(True, alpha=0.3, color=colors['grid'])
    ax2.legend()
    
    # Derivative plots
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(dates, dix_deriv1, color=colors['deriv1'], linewidth=1.5, label='1st Derivative')
    ax3.axhline(y=0, color=colors['grid'], linestyle='-', alpha=0.5)
    ax3.set_title('DIX - Rate of Change', fontsize=12, color=colors['text'])
    ax3.set_ylabel('Rate', color=colors['text'])
    ax3.grid(True, alpha=0.3, color=colors['grid'])
    ax3.legend()
    
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.plot(dates, dix_deriv2, color=colors['deriv2'], linewidth=1.5, label='2nd Derivative')
    ax4.axhline(y=0, color=colors['grid'], linestyle='-', alpha=0.5)
    ax4.set_title('DIX - Acceleration', fontsize=12, color=colors['text'])
    ax4.set_ylabel('Acceleration', color=colors['text'])
    ax4.set_xlabel('Date', color=colors['text'])
    ax4.grid(True, alpha=0.3, color=colors['grid'])
    ax4.legend()
    
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(dates, gex_deriv1, color=colors['deriv1'], linewidth=1.5, label='1st Derivative')
    ax5.axhline(y=0, color=colors['grid'], linestyle='-', alpha=0.5)
    ax5.set_title('GEX - Rate of Change', fontsize=12, color=colors['text'])
    ax5.set_ylabel('Rate', color=colors['text'])
    ax5.grid(True, alpha=0.3, color=colors['grid'])
    ax5.legend()
    
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.plot(dates, gex_deriv2, color=colors['deriv2'], linewidth=1.5, label='2nd Derivative')
    ax6.axhline(y=0, color=colors['grid'], linestyle='-', alpha=0.5)
    ax6.set_title('GEX - Acceleration', fontsize=12, color=colors['text'])
    ax6.set_ylabel('Acceleration', color=colors['text'])
    ax6.set_xlabel('Date', color=colors['text'])
    ax6.grid(True, alpha=0.3, color=colors['grid'])
    ax6.legend()
    
    # Format dates
    for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
        ax.tick_params(colors=colors['text'])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    # Market structure interpretation
    dix_val = dix_analysis['current_value']
    gex_val = gex_analysis['current_value']
    
    if dix_val >= 0.50 and gex_val > 5:
        market_regime = "🟢 BULLISH STRUCTURE: Institutions buying dips + strong gamma support"
    elif dix_val >= 0.50 and gex_val < -5:
        market_regime = "🟡 BULLISH BUT VOLATILE: Institutions bullish but negative gamma"
    elif dix_val < 0.45 and gex_val > 5:
        market_regime = "🟡 BEARISH BUT RANGE-BOUND: Institutions bearish but positive gamma"  
    elif dix_val < 0.45 and gex_val < -5:
        market_regime = "🔴 BEARISH & VOLATILE: Institutions bearish + negative gamma"
    elif -5 <= gex_val <= 5:
        market_regime = "⚪ NEUTRAL GAMMA: Market in transition, watch for breakout"
    else:
        market_regime = "🟡 MIXED SIGNALS: Monitor for clearer directional signals"
    
    return {
        'dix_analysis': dix_analysis,
        'gex_analysis': gex_analysis,
        'market_regime': market_regime,
        'days_analyzed': len(recent_df)
    }


def dix_gex_summary(file_path: str, days_back: int = 200) -> Dict:
    """
    Quick summary analysis without plots.
    """
    df = load_squeeze_data(file_path)
    
    # Filter recent data
    cutoff_date = df['date'].max() - timedelta(days=days_back)
    recent_df = df[df['date'] >= cutoff_date]
    
    current_dix = recent_df['dix'].iloc[-1]
    current_gex = recent_df['gex'].iloc[-1]
    
    # Simple trend analysis
    dix_trend = "Up" if recent_df['dix'].iloc[-1] > recent_df['dix'].iloc[-10] else "Down"
    gex_trend = "Up" if recent_df['gex'].iloc[-1] > recent_df['gex'].iloc[-10] else "Down"
    
    return {
        'current_dix': round(current_dix, 3),
        'current_gex': round(current_gex, 1),
        'dix_trend': dix_trend,
        'gex_trend': gex_trend,
        'data_points': len(recent_df),
        'latest_date': recent_df['date'].max().strftime('%Y-%m-%d')
    }
