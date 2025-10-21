#!/usr/bin/env python3
"""
Script untuk menghasilkan output yang persis sama dengan forecast_ridge_log_thr05.csv
Dengan menggunakan data yang difilter untuk mendapatkan date range yang benar
"""

import pandas as pd
import numpy as np
import sys
sys.path.append('/app')
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder

# TransformedTargetRegressor fallback
try:
    from sklearn.compose import TransformedTargetRegressor as TTR
except Exception:
    class TTR:
        def __init__(self, regressor, func=None, inverse_func=None):
            self.regressor = regressor
            self.func = func if func else (lambda x: x)
            self.inverse_func = inverse_func if inverse_func else (lambda x: x)
        def fit(self, X, y):
            self.regressor.fit(X, self.func(np.asarray(y))); return self
        def predict(self, X):
            return self.inverse_func(self.regressor.predict(X))

def make_ohe(dense=False):
    try:    return OneHotEncoder(handle_unknown='ignore', sparse_output=not dense)
    except TypeError: return OneHotEncoder(handle_unknown='ignore', sparse=not dense)

def complete_calendar_daily(df, group_cols=('partnumber','site_code'), target='demand_qty'):
    """Complete missing dates with zero demand"""
    out = []
    for keys, g in df.groupby(list(group_cols), sort=False):
        gd = (g.groupby('date', as_index=False)[target].sum().sort_values('date'))
        idx = pd.date_range(gd['date'].min(), gd['date'].max(), freq='D')
        gd = gd.set_index('date').reindex(idx).fillna(0.0).rename_axis('date').reset_index()
        for col, val in zip(group_cols, (keys if isinstance(keys, tuple) else (keys,))):
            gd[col] = val
        out.append(gd[[*group_cols, 'date', target]])
    return pd.concat(out, ignore_index=True) if out else df

def add_calendar_features(df):
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
                         lags=(1,7,14,28), roll_windows=(7,14,28)):
    df = df.sort_values(group_cols + ['date']).reset_index(drop=True)
    g = df.groupby(group_cols, group_keys=False)
    for L in lags: df[f'lag_{L}'] = g[target_col].shift(L)
    for W in roll_windows: df[f'rollmean_{W}'] = g[target_col].shift(1).rolling(W).mean()
    return df

def one_day_forecast(history_df, df_sites, fdate, best_est, group_cols, ZERO_THR):
    """Generate forecast for one day"""
    hist = add_calendar_features(history_df)
    hist = add_group_lags_rolls(hist, group_cols, target_col='demand_qty',
                                lags=(1,7,14,28), roll_windows=(7,14,28))
    latest = (hist.sort_values('date')
                .groupby(group_cols, as_index=False)
                .tail(1)[[*group_cols] + [c for c in hist.columns
                                          if c.startswith('lag_') or c.startswith('rollmean_')]])

    combos = df_sites[group_cols].drop_duplicates().reset_index(drop=True)
    combos['date'] = fdate
    combos = add_calendar_features(combos).merge(latest, on=group_cols, how='left')

    lagroll_cols = [c for c in [*latest.columns] if c.startswith('lag_') or c.startswith('rollmean_')]
    for c in lagroll_cols:
        if c in combos: combos[c] = combos[c].fillna(0)

    Xf = pd.concat([combos[['partnumber','site_code']],
                    combos[['year','month','day','dayofweek','weekofyear','is_month_start','is_month_end'] + lagroll_cols]], axis=1)
    raw_model = np.maximum(0, best_est.predict(Xf))              # raw >= 0
    raw_thr   = np.where(raw_model < ZERO_THR, 0, raw_model)     # threshold to zero
    yhat      = np.floor(raw_thr + 0.5).astype(int)             # half-up rounding

    out = combos[[*group_cols]].copy()
    out['date'] = fdate
    out['yhat_raw']   = raw_model
    out['yhat_thr']   = raw_thr
    out['yhat_round'] = yhat
    return out

def generate_exact_forecast_filtered():
    """Generate forecast yang persis sama dengan notebook menggunakan data yang difilter"""
    
    print("=== GENERATE FORECAST PERSIS SAMA DENGAN NOTEBOOK (FILTERED DATA) ===\n")
    
    # CONFIG (sama persis dengan notebook)
    DATA_PATH = '/app/alldemand_augjul_new.csv'
    FORECAST_HORIZON = 7
    FORECAST_START_DATE = '2025-08-01'  # Fixed start date
    FORECAST_START_OFFSET_DAYS = 1
    FORECAST_SITE_CODES = ['KENDARI']  # Hanya KENDARI seperti notebook
    TRAIN_SITE_CODES = None
    ZERO_THR = 0.5
    DAYFIRST = True
    RANDOM_STATE = 42
    
    print(f"📁 Loading data: {DATA_PATH}")
    
    # Load data
    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Normalize data
    df['partnumber'] = df['partnumber'].astype(str).str.strip()
    df['site_code']  = df['site_code'].astype(str).str.strip()
    df['date'] = pd.to_datetime(df['date'], dayfirst=DAYFIRST, errors='coerce')
    df['demand_qty'] = pd.to_numeric(df['demand_qty'], errors='coerce').fillna(0)
    df = df.sort_values(['partnumber','site_code','date']).reset_index(drop=True)
    
    print(f"   Original data shape: {df.shape}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Filter data to end before forecast start date
    forecast_start = pd.to_datetime(FORECAST_START_DATE)
    df = df[df['date'] <= forecast_start - pd.Timedelta(days=1)].copy()
    
    print(f"   Filtered data shape: {df.shape}")
    print(f"   Filtered date range: {df['date'].min()} to {df['date'].max()}")
    
    # Aggregate daily, complete calendar, clip outliers per series (p99)
    print(f"\n🔧 Preprocessing...")
    df = (df.groupby(['partnumber','site_code','date'], as_index=False)
            .agg(demand_qty=('demand_qty','sum')))
    
    print(f"   After aggregation: {df.shape}")
    
    # Complete calendar daily
    df = complete_calendar_daily(df, group_cols=('partnumber','site_code'), target='demand_qty')
    print(f"   After complete calendar: {df.shape}")
    
    # Clip outliers per series (p99)
    p99 = df.groupby(['partnumber','site_code'])['demand_qty'].transform(lambda s: s.quantile(0.99))
    df['demand_qty'] = df['demand_qty'].clip(lower=0, upper=p99)
    print(f"   After outlier clipping: {df.shape}")
    
    # Feature engineering
    print(f"\n⚙️  Feature engineering...")
    group_cols = ['partnumber','site_code']
    df_model = df if TRAIN_SITE_CODES is None else df[df['site_code'].isin(TRAIN_SITE_CODES)].copy()
    
    df_fe = add_calendar_features(df_model)
    df_fe = add_group_lags_rolls(df_fe, group_cols, target_col='demand_qty',
                                 lags=(1,7,14,28), roll_windows=(7,14,28))
    
    need = [c for c in df_fe.columns if c.startswith('lag_') or c.startswith('rollmean_')]
    df_fe = df_fe[df_fe[need].notnull().all(axis=1)].reset_index(drop=True)
    
    print(f"   Features shape: {df_fe.shape}")
    print(f"   Unique partnumbers: {df_fe['partnumber'].nunique()}")
    print(f"   Unique site codes: {df_fe['site_code'].nunique()}")
    
    # Split train/valid
    feature_cols_cat = ['partnumber','site_code']
    feature_cols_num = ['year','month','day','dayofweek','weekofyear','is_month_start','is_month_end'] + need
    
    cutoff = df_fe['date'].max() - pd.Timedelta(days=max(28, 2*FORECAST_HORIZON))
    train = df_fe[df_fe['date'] <= cutoff].copy()
    valid = df_fe[df_fe['date'] >  cutoff].copy()
    
    X_train = pd.concat([train[feature_cols_cat], train[feature_cols_num]], axis=1)
    X_valid = pd.concat([valid[feature_cols_cat], valid[feature_cols_num]], axis=1)
    y_train = train['demand_qty'].astype(float).values
    y_valid = valid['demand_qty'].astype(float).values
    
    print(f"   Train shape: {X_train.shape}")
    print(f"   Valid shape: {X_valid.shape}")
    
    # Train model
    print(f"\n🤖 Training Ridge_log model...")
    preprocess_sparse = ColumnTransformer(
        transformers=[('cat', make_ohe(dense=False), feature_cols_cat)],
        remainder='passthrough'
    )
    
    ridge_log = Pipeline([
        ("prep", preprocess_sparse),
        ("reg", TTR(
            regressor=Ridge(alpha=1.0, random_state=RANDOM_STATE) if 'random_state' in Ridge().get_params() else Ridge(alpha=1.0),
            func=np.log1p, inverse_func=np.expm1
        ))
    ])
    
    ridge_log.fit(X_train, y_train)
    y_pred = ridge_log.predict(X_valid)
    
    print(f"   Model trained successfully")
    
    # Forecast
    print(f"\n📊 Generating forecast...")
    best_est = ridge_log
    
    # subset sites for output
    df_sites = df if FORECAST_SITE_CODES is None else df[df['site_code'].isin(FORECAST_SITE_CODES)].copy()
    print(f"   Forecast sites: {sorted(df_sites['site_code'].unique())}")
    print(f"   Forecast partnumbers: {df_sites['partnumber'].nunique()}")
    
    start_date = pd.to_datetime(FORECAST_START_DATE)
    forecasts = []
    hist_all = df.copy()
    
    for h in range(FORECAST_HORIZON):
        fdate = start_date + pd.Timedelta(days=h)
        print(f"   Forecasting {fdate.date()}...")
        day_fc = one_day_forecast(hist_all, df_sites, fdate, best_est, group_cols, ZERO_THR)
        forecasts.append(day_fc)
        # append rounded predictions back as history for iterative features
        add_back = day_fc.rename(columns={'yhat_round':'demand_qty'})[['partnumber','site_code','date','demand_qty']].copy()
        hist_all = pd.concat([hist_all, add_back], ignore_index=True)
    
    forecast_df = (pd.concat(forecasts, ignore_index=True)
                     .sort_values(['partnumber','site_code','date'])
                     .reset_index(drop=True))
    
    print(f"\n📋 Forecast results:")
    print(f"   Shape: {forecast_df.shape}")
    print(f"   Unique partnumbers: {forecast_df['partnumber'].nunique()}")
    print(f"   Unique site codes: {forecast_df['site_code'].nunique()}")
    print(f"   Date range: {forecast_df['date'].min()} to {forecast_df['date'].max()}")
    
    # Check zero values
    zeros = (forecast_df['yhat_thr'] == 0).sum()
    print(f"   Zero values: {zeros}/{len(forecast_df)} ({zeros/len(forecast_df)*100:.1f}%)")
    
    # Save output
    output_file = "/app/forecast_exact_filtered.csv"
    forecast_df.to_csv(output_file, index=False)
    print(f"   Output saved to: {output_file}")
    
    # Show sample
    print(f"\n📄 Sample output (first 20 rows):")
    print(forecast_df.head(20).to_string(index=False))
    
    return forecast_df

if __name__ == "__main__":
    try:
        result = generate_exact_forecast_filtered()
        print(f"\n✅ Forecast generated successfully!")
    except Exception as e:
        print(f"\n❌ Forecast failed: {e}")
        import traceback
        traceback.print_exc()
