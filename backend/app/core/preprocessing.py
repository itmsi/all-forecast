# backend/app/core/preprocessing.py
"""
Data preprocessing functions
Refactored dari forecast11.ipynb
"""

import pandas as pd
import numpy as np


def add_calendar_features(df):
    """Add calendar-based features"""
    df = df.copy()
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['dayofweek'] = df['date'].dt.dayofweek
    df['weekofyear'] = df['date'].dt.isocalendar().week.astype(int)
    df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
    df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
    return df


def add_group_lags_rolls(df, group_cols, target_col='demand_qty',
                         lags=(1, 7, 14, 28), roll_windows=(7, 14, 28)):
    """Add lag and rolling features per group"""
    df = df.sort_values(group_cols + ['date']).reset_index(drop=True)
    g = df.groupby(group_cols, group_keys=False)
    
    # Lag features
    for L in lags:
        df[f'lag_{L}'] = g[target_col].shift(L)
    
    # Rolling mean features
    for W in roll_windows:
        df[f'rollmean_{W}'] = g[target_col].shift(1).rolling(W).mean()
    
    return df


def complete_calendar_daily(df, group_cols=('partnumber', 'site_code'), target='demand_qty'):
    """Complete missing dates with zero demand"""
    out = []
    for keys, g in df.groupby(list(group_cols), sort=False):
        gd = (g.groupby('date', as_index=False)[target]
              .sum()
              .sort_values('date'))
        
        # Create complete date range
        idx = pd.date_range(gd['date'].min(), gd['date'].max(), freq='D')
        gg = gd.set_index('date').reindex(idx).rename_axis('date').reset_index()
        gg[target] = pd.to_numeric(gg[target], errors='coerce').fillna(0)
        
        # Add group keys back
        if not isinstance(keys, tuple):
            keys = (keys,)
        for c, v in zip(group_cols, keys):
            gg[c] = v
        
        out.append(gg)
    
    return pd.concat(out, ignore_index=True)


def load_and_normalize(file_path, dayfirst=True):
    """
    Load and normalize data from CSV with enhanced date parsing
    
    Handles multiple date formats:
    - 3/3/2025 (no leading zero)
    - 03/03/2025 (with leading zero)
    - 2025-03-03 (ISO format)
    - 3-3-2025 (dash separator)
    """
    from .utils import robust_read_table
    
    # Load
    df = robust_read_table(file_path)
    
    # Normalize columns
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Check required columns
    req = {'demand_qty', 'date', 'partnumber', 'site_code'}
    miss = req - set(df.columns)
    if miss:
        raise ValueError(f"Kolom wajib hilang: {miss}. Header: {list(df.columns)}")
    
    # Normalize data types
    df['partnumber'] = df['partnumber'].astype(str).str.strip()
    df['site_code'] = df['site_code'].astype(str).str.strip()
    
    # Enhanced date parsing dengan multiple strategies
    df['date'] = parse_dates_flexible(df['date'], dayfirst=dayfirst)
    
    if df['date'].isna().any():
        na_count = df['date'].isna().sum()
        raise ValueError(f"Ada {na_count} tanggal gagal parse. Cek format kolom 'date'.")
    
    # Normalize demand_qty
    df['demand_qty'] = pd.to_numeric(df['demand_qty'], errors='coerce').fillna(0)
    df = df.sort_values(['partnumber', 'site_code', 'date']).reset_index(drop=True)
    
    return df


def parse_dates_flexible(date_series, dayfirst=True):
    """
    Flexible date parser yang handle berbagai format
    
    Supports:
    - 3/3/2025, 8/5/2024 (no leading zero)
    - 03/03/2025, 08/05/2024 (with leading zero)
    - 2025-03-03 (ISO)
    - 3-3-2025 (dash)
    - Mixed formats dalam satu column
    
    Args:
        date_series: pandas Series dengan tanggal
        dayfirst: True untuk DD/MM/YYYY, False untuk MM/DD/YYYY
    
    Returns:
        pandas Series dengan datetime objects
    """
    
    # Strategy 1: Standard pandas parsing dengan dayfirst
    try:
        parsed = pd.to_datetime(date_series, dayfirst=dayfirst, errors='coerce')
        
        # Jika success rate > 80%, assume format benar
        if parsed.notna().mean() > 0.8:
            # Fill remaining NaT dengan strategy lain
            if parsed.isna().any():
                mask = parsed.isna()
                parsed[mask] = pd.to_datetime(date_series[mask], dayfirst=not dayfirst, errors='coerce')
            
            return parsed
    except Exception as e:
        print(f"Standard parsing failed: {e}")
    
    # Strategy 2: Try opposite dayfirst
    try:
        parsed = pd.to_datetime(date_series, dayfirst=not dayfirst, errors='coerce')
        if parsed.notna().mean() > 0.8:
            return parsed
    except Exception as e:
        print(f"Opposite dayfirst parsing failed: {e}")
    
    # Strategy 3: Explicit format parsing untuk common formats
    formats_to_try = [
        '%m/%d/%Y',   # 8/5/2024, 3/3/2025
        '%d/%m/%Y',   # 5/8/2024, 3/3/2025
        '%Y-%m-%d',   # 2024-08-05
        '%m-%d-%Y',   # 08-05-2024
        '%d-%m-%Y',   # 05-08-2024
        '%m/%d/%y',   # 8/5/24
        '%d/%m/%y',   # 5/8/24
    ]
    
    for fmt in formats_to_try:
        try:
            parsed = pd.to_datetime(date_series, format=fmt, errors='coerce')
            success_rate = parsed.notna().mean()
            
            if success_rate > 0.8:
                print(f"Date parsing successful with format: {fmt} (success rate: {success_rate:.1%})")
                
                # Try to fill remaining NaT with other formats
                if parsed.isna().any():
                    mask = parsed.isna()
                    for alt_fmt in formats_to_try:
                        if alt_fmt != fmt and mask.any():
                            parsed[mask] = pd.to_datetime(date_series[mask], format=alt_fmt, errors='coerce')
                            mask = parsed.isna()
                
                return parsed
        except Exception:
            continue
    
    # Strategy 4: Infer format (last resort)
    try:
        parsed = pd.to_datetime(date_series, infer_datetime_format=True, errors='coerce')
        if parsed.notna().mean() > 0.5:
            print(f"Date parsing successful with infer_datetime_format")
            return parsed
    except Exception as e:
        print(f"Infer datetime format failed: {e}")
    
    # Final fallback: Return with coerce (akan ada NaT)
    print("WARNING: Using fallback date parsing - some dates may be NaT")
    return pd.to_datetime(date_series, dayfirst=dayfirst, errors='coerce')


def preprocess_data(df, group_cols=('partnumber', 'site_code')):
    """Complete preprocessing pipeline"""
    
    # Aggregate daily
    df = (df.groupby(['partnumber', 'site_code', 'date'], as_index=False)
          .agg(demand_qty=('demand_qty', 'sum')))
    
    # Complete calendar
    df = complete_calendar_daily(df, group_cols=group_cols, target='demand_qty')
    
    # Clamp outliers using P99
    p99 = df.groupby(list(group_cols))['demand_qty'].transform(
        lambda s: s.quantile(0.99)
    )
    df['demand_qty'] = df['demand_qty'].clip(lower=0, upper=p99)
    
    return df


def prepare_features(df, group_cols, lags=(1, 7, 14, 28), roll_windows=(7, 14, 28), auto_adjust=True):
    """
    Prepare all features for modeling
    
    Args:
        auto_adjust: If True, automatically adjust lags based on data availability
    """
    
    # Auto-adjust lags untuk small datasets
    if auto_adjust:
        # Check max days span per group
        max_days = (df.groupby(group_cols)['date']
                   .apply(lambda x: (x.max() - x.min()).days)
                   .max())
        
        print(f"Data span: {max_days} days")
        
        # Adjust lags based on available data
        if max_days < 56:  # Not enough for lag_28 + rollmean_28
            # Use only lags that fit in data
            lags = tuple([l for l in [1, 7, 14, 28] if l < max_days - 7])
            roll_windows = tuple([w for w in [7, 14] if w < max_days - 7])
            
            if not lags:  # Very small dataset
                lags = (1,)
                roll_windows = ()
            
            print(f"⚠️  Small dataset! Adjusted lags: {lags}, windows: {roll_windows}")
    
    # Add calendar features
    df_fe = add_calendar_features(df)
    
    # Add lag and rolling features
    df_fe = add_group_lags_rolls(
        df_fe, 
        group_cols, 
        target_col='demand_qty',
        lags=lags, 
        roll_windows=roll_windows
    )
    
    # Remove rows with null lag/roll features
    need = [c for c in df_fe.columns 
            if c.startswith('lag_') or c.startswith('rollmean_')]
    
    if need:
        df_fe = df_fe[df_fe[need].notnull().all(axis=1)].reset_index(drop=True)
    
    # Validate: Check if we have data left
    if len(df_fe) == 0:
        raise ValueError(
            f"❌ Data terlalu sedikit! Setelah feature engineering tidak ada data valid. "
            f"Minimal butuh {max(lags) + (max(roll_windows) if roll_windows else 0)} hari data. "
            f"Upload data minimal 60 hari untuk hasil optimal."
        )
    
    print(f"✅ Features prepared: {len(df_fe)} rows ready for training")
    
    return df_fe


def get_feature_columns(df_fe=None):
    """
    Get feature column names (dynamic if df provided)
    
    Args:
        df_fe: DataFrame with features (optional). If provided, auto-detect lag/roll columns
    
    Returns:
        tuple: (categorical_cols, numerical_cols)
    """
    feature_cols_cat = ['partnumber', 'site_code']
    
    # Calendar features (always present)
    calendar_features = [
        'year', 'month', 'day', 'dayofweek', 'weekofyear',
        'is_month_start', 'is_month_end'
    ]
    
    # If df provided, detect actual lag/rolling columns
    if df_fe is not None:
        lag_cols = sorted([c for c in df_fe.columns if c.startswith('lag_')])
        roll_cols = sorted([c for c in df_fe.columns if c.startswith('rollmean_')])
        feature_cols_num = calendar_features + lag_cols + roll_cols
        print(f"Dynamic features: {len(lag_cols)} lags, {len(roll_cols)} rolling means")
    else:
        # Default full feature set
        feature_cols_num = calendar_features + [
            'lag_1', 'lag_7', 'lag_14', 'lag_28',
            'rollmean_7', 'rollmean_14', 'rollmean_28'
        ]
    
    return feature_cols_cat, feature_cols_num

