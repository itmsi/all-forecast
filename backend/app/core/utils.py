# backend/app/core/utils.py
"""
Utility functions untuk forecasting system
Refactored dari forecast11.ipynb
"""

import os
import time
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import OneHotEncoder


def _rmse(y, yhat):
    """Calculate RMSE"""
    try:
        return mean_squared_error(y, yhat, squared=False)
    except TypeError:
        return np.sqrt(mean_squared_error(y, yhat))


def smape(y_true, y_pred):
    """Symmetric Mean Absolute Percentage Error - exact same as notebook"""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    diff = np.abs(y_true - y_pred) / np.where(denom==0, 1.0, denom)
    return np.mean(diff)


def mape(y_true, y_pred):
    """Mean Absolute Percentage Error - exact same as notebook"""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    denom = np.where(np.abs(y_true) < 1e-9, 1.0, np.abs(y_true))
    return np.mean(np.abs(y_true - y_pred) / denom)


def wape(y_true, y_pred):
    """Weighted Absolute Percentage Error"""
    y_true = np.asarray(y_true, float)
    y_pred = np.asarray(y_pred, float)
    den = np.sum(np.abs(y_true))
    den = den if den != 0 else 1.0
    return 100 * np.sum(np.abs(y_true - y_pred)) / den


def mase(y_true, y_pred, insample):
    """Mean Absolute Scaled Error"""
    denom = mean_absolute_error(insample[1:], insample[:-1]) if len(insample) > 1 else 1.0
    return mean_absolute_error(y_true, y_pred) / (denom if denom != 0 else 1.0)


def metrics(y, yhat, as_percent=False):
    """Return exactly MAE, RMSE, sMAPE%, MAPE% - exact same as notebook"""
    return {
        "MAE": mean_absolute_error(y, yhat),
        "RMSE": _rmse(y, yhat),
        "sMAPE%": smape(y, yhat) * 100.0,  # smape 0–2  -> % (0–200)
        "MAPE%":  mape(y, yhat)  * 100.0,  # mape  0–∞  -> %
    }


def eval_with_rounding(y_true, y_pred, thr=0.5):
    """Half-up rounding + threshold, same metric keys - exact same as notebook"""
    x = np.asarray(y_pred, float)
    x = np.where(x < thr, 0, x)       # threshold -> 0
    x = np.floor(x + 0.5)             # half-up rounding
    return {
        "MAE": mean_absolute_error(y_true, x),
        "RMSE": _rmse(y_true, x),
        "sMAPE%": smape(y_true, x) * 100.0,
        "MAPE%":  mape(y_true, x)  * 100.0,
    }


def round_series(x, mode='half_up'):
    """Round series dengan berbagai mode"""
    if mode == 'half_up':
        return np.floor(x + 0.5).astype(int)
    if mode == 'round':
        return np.round(x).astype(int)
    if mode == 'ceil':
        return np.ceil(x).astype(int)
    if mode == 'floor':
        return np.floor(x).astype(int)
    return np.round(x).astype(int)


def make_ohe(dense=False):
    """Create OneHotEncoder with compatibility"""
    try:
        return OneHotEncoder(handle_unknown='ignore', sparse_output=not dense)
    except TypeError:
        return OneHotEncoder(handle_unknown='ignore', sparse=not dense)


def robust_read_table(path):
    """Read CSV/Excel dengan auto-detect encoding"""
    if path.lower().endswith(('.xlsx', '.xls')):
        return pd.read_excel(path, dtype=str)
    
    for enc in ('utf-8-sig', 'cp1252', 'latin1', 'iso-8859-1'):
        try:
            df_ = pd.read_csv(path, sep=None, engine='python', dtype=str, encoding=enc)
            print(f"Loaded with encoding={enc}")
            return df_
        except Exception:
            continue
    
    # fallback
    return pd.read_csv(path, sep=None, engine='python', dtype=str, encoding='latin1')


def safe_save_csv(df, path):
    """Save CSV with error handling"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        tmp = p.with_suffix(p.suffix + '.tmp')
        df.to_csv(tmp, index=False, encoding='utf-8-sig')
        os.replace(tmp, p)
        print(f"Saved: {p}")
        return str(p)
    except PermissionError:
        alt = p.with_name(p.stem + f'_{int(time.time())}' + p.suffix)
        df.to_csv(alt, index=False, encoding='utf-8-sig')
        print(f"Target locked. Saved: {alt}")
        return str(alt)

