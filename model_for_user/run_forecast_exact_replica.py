#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk menghasilkan forecast yang sama persis dengan notebook
Menggunakan konfigurasi dan preprocessing yang identik
"""

import os
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import timedelta

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import Ridge

# TransformedTargetRegressor (fallback utk sklearn lama)
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

def _rmse(y, yhat): return np.sqrt(mean_squared_error(y, yhat))

def smape(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    diff = np.abs(y_true - y_pred) / np.where(denom==0, 1.0, denom)
    return np.mean(diff)

def mape(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    denom = np.where(np.abs(y_true) < 1e-9, 1.0, np.abs(y_true))
    return np.mean(np.abs(y_true - y_pred) / denom)

def wape(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    denom = np.sum(np.abs(y_true))
    return np.sum(np.abs(y_true - y_pred)) / (denom if denom != 0 else 1.0)

def metrics(y, yhat):
    """Return exactly MAE, RMSE, sMAPE%, MAPE%."""
    return {
        "MAE": mean_absolute_error(y, yhat),
        "RMSE": _rmse(y, yhat),
        "sMAPE%": smape(y, yhat) * 100.0,  # smape 0–2  -> % (0–200)
        "MAPE%":  mape(y, yhat)  * 100.0,  # mape  0–∞  -> %
    }

def eval_with_rounding(y_true, y_pred, thr=0.5):
    """Half-up rounding + threshold, same metric keys."""
    x = np.asarray(y_pred, float)
    x = np.where(x < thr, 0, x)       # threshold -> 0
    x = np.floor(x + 0.5)             # half-up rounding
    return {
        "MAE": mean_absolute_error(y_true, x),
        "RMSE": _rmse(y_true, x),
        "sMAPE%": smape(y_true, x) * 100.0,
        "MAPE%":  mape(y_true, x)  * 100.0,
    }

def safe_save_csv(df, path):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    df.to_csv(tmp, index=False, encoding='utf-8-sig'); os.replace(tmp, p)
    print(f"Saved: {p}")

def make_ohe(dense=False):
    try:    return OneHotEncoder(handle_unknown='ignore', sparse_output=not dense)
    except TypeError: return OneHotEncoder(handle_unknown='ignore', sparse=not dense)

def complete_calendar_daily(df, group_cols=('partnumber','site_code'), target='demand_qty'):
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

def robust_read_table(path):
    if path.lower().endswith(('.xlsx','.xls')):
        return pd.read_excel(path, dtype=str)
    for enc in ('utf-8-sig','cp1252','latin1','iso-8859-1'):
        try:
            df_ = pd.read_csv(path, sep=None, engine='python', dtype=str, encoding=enc)
            print(f"Loaded with encoding={enc}"); return df_
        except Exception: continue
    return pd.read_csv(path, sep=None, engine='python', dtype=str, encoding='latin1', errors='replace')

def main():
    # CONFIG - SAMA PERSIS DENGAN NOTEBOOK
    DATA_PATH = '/Users/falaqmsi/Documents/GitHub/forecast/real_data/alldemand_augjul_new.csv'
    FORECAST_HORIZON = 7
    FORECAST_START_DATE = None           # e.g., '2025-08-01'; None = H+1 after last history
    FORECAST_START_OFFSET_DAYS = 1

    FORECAST_SITE_CODES = ['KENDARI'] # e.g., ['SOFIFI', 'ANGSANA', 'ANGSANA']; None for all
    TRAIN_SITE_CODES    = None           # optional training subset filter

    ZERO_THR = 0.5                       # predictions < ZERO_THR => 0
    DAYFIRST = True                      # ID-style dates (dd/mm/yyyy)
    RANDOM_STATE = 42

    print("=== FORECAST KENDARI - REPLIKASI NOTEBOOK ===")
    print(f"Data path: {DATA_PATH}")
    print(f"Site codes: {FORECAST_SITE_CODES}")
    print(f"Forecast horizon: {FORECAST_HORIZON} hari")
    print(f"Random state: {RANDOM_STATE}")
    print()

    # Set random seed untuk reproducibility
    np.random.seed(RANDOM_STATE)

    # LOAD & NORMALIZE - SAMA PERSIS DENGAN NOTEBOOK
    print("1. Loading data...")
    df = robust_read_table(DATA_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    req = {'demand_qty','date','partnumber','site_code'}
    miss = req - set(df.columns)
    if miss: raise ValueError(f"Kolom wajib hilang: {miss}. Header: {list(df.columns)}")

    df['partnumber'] = df['partnumber'].astype(str).str.strip()
    df['site_code']  = df['site_code'].astype(str).str.strip()
    d = pd.to_datetime(df['date'], dayfirst=DAYFIRST, errors='coerce')
    if d.isna().mean() > 0.2:
        d = pd.to_datetime(df['date'], dayfirst=not DAYFIRST, errors='coerce')
    df['date'] = d
    if df['date'].isna().any():
        raise ValueError("Ada tanggal gagal parse. Cek format kolom 'date'.")

    df['demand_qty'] = pd.to_numeric(df['demand_qty'], errors='coerce').fillna(0)
    df = df.sort_values(['partnumber','site_code','date']).reset_index(drop=True)

    # Aggregate daily, complete calendar, clip outliers per series (p99)
    df = (df.groupby(['partnumber','site_code','date'], as_index=False)
            .agg(demand_qty=('demand_qty','sum')))
    df = complete_calendar_daily(df, group_cols=('partnumber','site_code'), target='demand_qty')
    p99 = df.groupby(['partnumber','site_code'])['demand_qty'].transform(lambda s: s.quantile(0.99))
    df['demand_qty'] = df['demand_qty'].clip(lower=0, upper=p99)
    
    print(f"Data loaded: {len(df)} rows")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Unique partnumbers: {df['partnumber'].nunique()}")
    print(f"Unique site codes: {df['site_code'].unique()}")
    print()

    # FEATURE ENGINEERING & SPLIT - SAMA PERSIS DENGAN NOTEBOOK
    print("2. Feature engineering...")
    group_cols = ['partnumber','site_code']
    df_model = df if TRAIN_SITE_CODES is None else df[df['site_code'].isin(TRAIN_SITE_CODES)].copy()
    if df_model.empty: raise ValueError("TRAIN_SITE_CODES filter produced empty data.")

    df_fe = add_calendar_features(df_model)
    df_fe = add_group_lags_rolls(df_fe, group_cols, target_col='demand_qty',
                                 lags=(1,7,14,28), roll_windows=(7,14,28))
    need = [c for c in df_fe.columns if c.startswith('lag_') or c.startswith('rollmean_')]
    df_fe = df_fe[df_fe[need].notnull().all(axis=1)].reset_index(drop=True)

    feature_cols_cat = ['partnumber','site_code']
    feature_cols_num = ['year','month','day','dayofweek','weekofyear','is_month_start','is_month_end'] + need

    cutoff = df_fe['date'].max() - pd.Timedelta(days=max(28, 2*FORECAST_HORIZON))
    train = df_fe[df_fe['date'] <= cutoff].copy()
    valid = df_fe[df_fe['date'] >  cutoff].copy()
    X_train = pd.concat([train[feature_cols_cat], train[feature_cols_num]], axis=1)
    X_valid = pd.concat([valid[feature_cols_cat], valid[feature_cols_num]], axis=1)
    y_train = train['demand_qty'].astype(float).values
    y_valid = valid['demand_qty'].astype(float).values

    print("Baseline: Naive t-1 (raw)")
    print(metrics(y_valid, valid.get('lag_1', 0).fillna(0).values))

    print("\nBaseline: Naive t-7 (raw)")
    print(metrics(y_valid, valid.get('lag_7', 0).fillna(0).values))
    print()

    # MODEL = Ridge_log ONLY - SAMA PERSIS DENGAN NOTEBOOK
    print("3. Training Ridge_log model...")
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

    # Evaluate (raw & rounded thr=0.5)
    m_raw = metrics(y_valid, y_pred)                       # <— tanpa as_percent
    m_rnd = eval_with_rounding(y_valid, y_pred, thr=ZERO_THR)

    eval_df = pd.DataFrame([
        {"model": "Ridge_log", "eval": "raw", **m_raw},
        {"model": "Ridge_log", "eval": f"rounded(thr={ZERO_THR})", **m_rnd},
    ])[["model","eval","MAE","RMSE","sMAPE%","MAPE%"]]     # tampilkan 4 metrik saja

    print("Model evaluation:")
    print(eval_df)
    print()

    # FORECAST LOOP (fixed model + outputs) - SAMA PERSIS DENGAN NOTEBOOK
    print("4. Generating forecasts...")
    best_est = ridge_log  # fixed

    # subset sites for output
    df_sites = df if FORECAST_SITE_CODES is None else df[df['site_code'].isin(FORECAST_SITE_CODES)].copy()
    if df_sites.empty: raise ValueError("FORECAST_SITE_CODES tidak ditemukan di data.")

    def one_day_forecast(history_df, fdate):
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

    start_date = pd.to_datetime(FORECAST_START_DATE) if FORECAST_START_DATE else (df['date'].max() + pd.Timedelta(days=FORECAST_START_OFFSET_DAYS))
    forecasts = []
    hist_all = df.copy()

    for h in range(FORECAST_HORIZON):
        fdate = start_date + pd.Timedelta(days=h)
        day_fc = one_day_forecast(hist_all, fdate)
        forecasts.append(day_fc)
        # append rounded predictions back as history for iterative features
        add_back = day_fc.rename(columns={'yhat_round':'demand_qty'})[['partnumber','site_code','date','demand_qty']].copy()
        hist_all = pd.concat([hist_all, add_back], ignore_index=True)

    forecast_df = (pd.concat(forecasts, ignore_index=True)
                     .sort_values(['partnumber','site_code','date'])
                     .reset_index(drop=True))

    print("Sample forecast:")
    print(forecast_df.head(10))
    print()

    # Save output
    output_path = "/Users/falaqmsi/Documents/GitHub/forecast/model_for_user/forecast_kendari_exact_replica.csv"
    safe_save_csv(forecast_df, output_path)
    
    print(f"=== FORECAST SELESAI ===")
    print(f"Output tersimpan di: {output_path}")
    print(f"Total forecast: {len(forecast_df)} rows")
    print(f"Unique partnumbers: {forecast_df['partnumber'].nunique()}")
    print(f"Date range: {forecast_df['date'].min()} to {forecast_df['date'].max()}")

if __name__ == "__main__":
    main()
