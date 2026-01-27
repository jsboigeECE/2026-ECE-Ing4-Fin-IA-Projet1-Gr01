import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicates and handle missing values.
    """
    if df is None or df.empty:
        return df
        
    df = df.drop_duplicates()
    # Sort by date just in case
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
    return df

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Level 1 Feature Engineering: Create relative and advanced metrics.
    """
    df = df.copy()
    
    # Ensure return_1d exists
    if 'return_1d' not in df.columns and 'close' in df.columns:
        df['return_1d'] = df.groupby('ticker')['close'].pct_change()
    
    # 1. Volatility Measures (Rolling)
    # 20d Rolling Volatility of returns
    if 'return_1d' in df.columns:
        df['volatility_20d'] = df.groupby('ticker')['return_1d'].transform(lambda x: x.rolling(20).std())
    
    # 2. Distance to Moving Averages
    if 'close' in df.columns:
        df['ma_50'] = df.groupby('ticker')['close'].transform(lambda x: x.rolling(50).mean())
        df['dist_ma_50'] = (df['close'] - df['ma_50']) / df['ma_50']
    
    # 3. RSI Lags / interaction
    if 'rsi_14' in df.columns:
        df['rsi_dist_50'] = df['rsi_14'] - 50  # Centered RSI
        
    return df

def merge_data(prices: pd.DataFrame, technicals: pd.DataFrame, macro: pd.DataFrame = None, fundamentals: pd.DataFrame = None) -> pd.DataFrame:
    """
    Merge Prices, Technicals (on ticker, date) and Macro (on date).
    """
    print("Merging data...")
    # Base is prices
    df = prices.copy()
    
    # Merge Technicals
    if technicals is not None and not technicals.empty:
        # Ensure dates are datetime
        technicals['date'] = pd.to_datetime(technicals['date'])
        # Drop duplicates in technicals just in case
        technicals = technicals.drop_duplicates(subset=['ticker', 'date'])
    
    # 1. Merge Prices & Technicals
    # Ensure dates are datetime for merging
    prices['date'] = pd.to_datetime(prices['date'])
    technicals['date'] = pd.to_datetime(technicals['date'])
    df = pd.merge(prices, technicals, on=['date', 'ticker'], how='left')
    
    # 2. Engineer Advanced Features (Level 1)
    df = engineer_features(df)
    
    # 3. Merge Fundamentals (Level 2) - backward fill (latest available fundamental)
    if fundamentals is not None and not fundamentals.empty:
        print("Merging Fundamentals (asof)...")
        # Ensure dates are datetime for merging
        fundamentals['date'] = pd.to_datetime(fundamentals['date'])
        
        df = df.sort_values('date') # merge_asof requires sorted 'on' key
        fundamentals = fundamentals.sort_values('date') # merge_asof requires sorted 'on' key
        
        df = pd.merge_asof(
            df, 
            fundamentals, 
            on='date', 
            by='ticker', 
            direction='backward',
            suffixes=('', '_fund')
        )
    
    # 4. Merge Macro (Broadcast to all tickers)
    # Pivot macro to wide format (date, indicator -> value columns)
    if macro is not None and not macro.empty:
        print("Merging Macro data...")
        macro['date'] = pd.to_datetime(macro['date'])
        # We assume 'name' or 'series_id' identifies the feature
        pivot_col = 'name' if 'name' in macro.columns else 'series_id'
        
        # Remove duplicates
        macro = macro.drop_duplicates(subset=['date', pivot_col])
        
        macro_wide = macro.pivot(index='date', columns=pivot_col, values='value')
        
        # Rename common columns for easier access
        rename_map = {
            '10-Year Treasury Yield': 'treasury_10y',
            '2-Year Treasury Yield': 'treasury_2y',
            'CBOE Volatility Index (VIX)': 'vix',
            'Federal Funds Rate': 'fed_rate',
            'Unemployment Rate (US)': 'unemployment_rate',
            'Consumer Price Index (US)': 'cpi',
            'Real GDP (US)': 'gdp'
        }
        # Only rename columns that exist
        cols_to_rename = {k: v for k, v in rename_map.items() if k in macro_wide.columns}
        macro_wide = macro_wide.rename(columns=cols_to_rename)
        
        # Handle weekends/holidays in macro by forward filling
        macro_wide = macro_wide.sort_index().ffill() 
        
        # Calculate Term Spread (Yield Curve)
        if 'treasury_10y' in macro_wide.columns and 'treasury_2y' in macro_wide.columns:
            macro_wide['term_spread'] = macro_wide['treasury_10y'] - macro_wide['treasury_2y']
            
        # Reset index to make 'date' a column again for merge
        macro_wide = macro_wide.reset_index()
        
        df = pd.merge(df, macro_wide, on='date', how='left')
        
    # 5. Calculate Sample Weights (Exponential Decay)
    # Give less weight to old data.
    # Weight = decay_rate ^ (years_ago)
    # Decay 0.94 per year => 1970 is ~50 years ago => 0.94^50 = 0.045 (~5% weight)
    print("Calculating Sample Weights...")
    max_date = df['date'].max()
    # Convert timedelta to years (approx)
    years_ago = (max_date - df['date']).dt.days / 365.25
    df['sample_weight'] = 0.94 ** years_ago
        
    return df

def create_target(df: pd.DataFrame, horizon: int = 20) -> pd.DataFrame:
    """
    Create binary target: 1 if Return(t+horizon) > 0, else 0.
    """
    if df.empty:
        return df
        
    # Ensure sorted
    df = df.sort_values(['ticker', 'date'])
    
    # Calculate forward return
    # shift(-horizon) gets the price at t+horizon
    df['close_future'] = df.groupby('ticker')['close'].shift(-horizon)
    
    df['fwd_return'] = (df['close_future'] / df['close']) - 1
    df['target'] = (df['fwd_return'] > 0).astype(int)
    
    # Drop rows where target cannot be calculated (unknown future)
    valid_df = df.dropna(subset=['close_future'])
    
    return valid_df

def temporal_split(df: pd.DataFrame, train_ratio: float = 0.7, val_ratio: float = 0.15):
    """
    Strict temporal split: Train < Val < Test
    """
    if df.empty:
        return df, df, df
        
    dates = df['date'].sort_values().unique()
    n = len(dates)
    
    train_end = dates[int(n * train_ratio)]
    val_end = dates[int(n * (train_ratio + val_ratio))]
    
    train = df[df['date'] <= train_end]
    val = df[(df['date'] > train_end) & (df['date'] <= val_end)]
    test = df[df['date'] > val_end]
    
    print(f"Split details:")
    print(f"Train: {train['date'].min()} -> {train['date'].max()} ({len(train)} rows)")
    print(f"Val:   {val['date'].min()}   -> {val['date'].max()}   ({len(val)} rows)")
    print(f"Test:  {test['date'].min()}  -> {test['date'].max()}  ({len(test)} rows)")
    
    return train, val, test
