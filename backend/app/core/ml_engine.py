# backend/app/core/ml_engine.py
"""
Main ML Forecasting Engine
Refactored dari forecast11.ipynb
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from datetime import timedelta
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge

from .preprocessing import (
    add_calendar_features, 
    add_group_lags_rolls,
    prepare_features,
    get_feature_columns
)
from .utils import metrics, eval_with_rounding, round_series, make_ohe

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
            self.regressor.fit(X, self.func(np.asarray(y)))
            return self
        
        def predict(self, X):
            return self.inverse_func(self.regressor.predict(X))


class MLForecaster:
    """Main forecasting engine"""
    
    def __init__(self, config):
        """
        Initialize forecaster with config
        
        Args:
            config: dict with keys:
                - forecast_horizon: int (default 7)
                - forecast_site_codes: list or None
                - zero_threshold: float (default 0.5)
                - rounding_mode: str (default 'half_up')
                - random_state: int (default 42)
        """
        self.config = config
        self.forecast_horizon = config.get('forecast_horizon', 7)
        self.forecast_site_codes = config.get('forecast_site_codes', None)
        self.zero_threshold = config.get('zero_threshold', 0.5)
        self.rounding_mode = config.get('rounding_mode', 'half_up')
        self.random_state = config.get('random_state', 42)
        
        self.group_cols = ['partnumber', 'site_code']
        self.feature_cols_cat, self.feature_cols_num = get_feature_columns()
        
        self.best_model = None
        self.best_model_name = None
        self.metrics_history = {}
    
    def _build_candidate_models(self):
        """Build candidate models - Simplified to Ridge_log only (as per latest notebook)"""
        preprocess_sparse = ColumnTransformer(
            transformers=[('cat', make_ohe(dense=False), self.feature_cols_cat)],
            remainder='passthrough'
        )
        
        candidates = {
            # Using Ridge_log only as per forecast11_ridge_only.ipynb
            "Ridge_log": Pipeline([
                ("prep", preprocess_sparse),
                ("reg", TTR(
                    regressor=Ridge(alpha=1.0, random_state=self.random_state) if 'random_state' in Ridge().get_params() else Ridge(alpha=1.0),
                    func=np.log1p, inverse_func=np.expm1
                ))
            ]),
        }
        
        return candidates
    
    def train_and_select_model(self, df_fe):
        """Train Ridge_log model (simplified from notebook)"""
        
        # Update feature columns dynamically from actual data
        from .preprocessing import get_feature_columns
        self.feature_cols_cat, self.feature_cols_num = get_feature_columns(df_fe)
        
        # Split train/valid dengan cutoff yang sama persis dengan notebook
        cutoff = df_fe['date'].max() - pd.Timedelta(days=max(28, 2 * self.forecast_horizon))
        
        train = df_fe[df_fe['date'] <= cutoff].copy()
        valid = df_fe[df_fe['date'] > cutoff].copy()
        
        # Handle small datasets - use 80/20 split
        if len(train) < 10 or len(valid) < 3:
            print(f"⚠️  Small dataset, using 80/20 split instead")
            split_idx = int(len(df_fe) * 0.8)
            train = df_fe.iloc[:split_idx].copy()
            valid = df_fe.iloc[split_idx:].copy()
        
        if len(train) == 0 or len(valid) == 0:
            raise ValueError("Data terlalu sedikit untuk split train/validation!")
        
        X_train = pd.concat([train[self.feature_cols_cat], train[self.feature_cols_num]], axis=1)
        X_valid = pd.concat([valid[self.feature_cols_cat], valid[self.feature_cols_num]], axis=1)
        y_train = train['demand_qty'].astype(float).values
        y_valid = valid['demand_qty'].astype(float).values
        
        # Build and train Ridge_log model
        candidates = self._build_candidate_models()
        results = {}
        fitted = {}
        
        print("Training Ridge_log model...")
        name = "Ridge_log"
        est = candidates[name]
        
        est.fit(X_train, y_train)
        y_pred = est.predict(X_valid)
        
        # Raw metrics - use same format as notebook
        m_raw = metrics(y_valid, y_pred)                       # <— tanpa as_percent
        
        # Rounded metrics - use exact same formula as notebook
        m_rnd = eval_with_rounding(y_valid, y_pred, thr=self.zero_threshold)
        
        results[name] = {
            'raw': m_raw,
            'rounded': m_rnd
        }
        fitted[name] = est
        
        print(f"    MAPE% (rounded): {m_rnd['MAPE%']:.4f}")
        
        # Set as best model
        self.best_model = fitted[name]
        self.best_model_name = name
        self.metrics_history = results
        
        print(f"\nModel trained: {name}")
        print(f"MAPE% (rounded): {results[name]['rounded']['MAPE%']:.4f}")
        
        return self.best_model
    
    def save_model(self, path='models/best_model.pkl'):
        """Save trained model"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'model': self.best_model,
            'model_name': self.best_model_name,
            'config': self.config,
            'metrics': self.metrics_history
        }, path)
        print(f"Model saved to {path}")
    
    def load_model(self, path='models/best_model.pkl'):
        """Load trained model"""
        if not Path(path).exists():
            raise FileNotFoundError(f"Model not found: {path}")
        
        data = joblib.load(path)
        self.best_model = data['model']
        self.best_model_name = data.get('model_name', 'Unknown')
        self.metrics_history = data.get('metrics', {})
        print(f"Model loaded: {self.best_model_name}")
        return self.best_model
    
    def one_day_forecast(self, history_df, df_sites, fdate):
        """Generate forecast for one day"""
        
        # Detect lags from feature columns (use same as training)
        lag_features = [c for c in self.feature_cols_num if c.startswith('lag_')]
        roll_features = [c for c in self.feature_cols_num if c.startswith('rollmean_')]
        
        # Extract lag numbers
        lags = tuple(sorted([int(c.split('_')[1]) for c in lag_features])) if lag_features else (1,)
        roll_windows = tuple(sorted([int(c.split('_')[1]) for c in roll_features])) if roll_features else ()
        
        # Prepare features from history
        hist = add_calendar_features(history_df)
        hist = add_group_lags_rolls(
            hist, 
            self.group_cols, 
            target_col='demand_qty',
            lags=lags, 
            roll_windows=roll_windows
        )
        
        # Get latest lag/rolling features
        latest = (hist.sort_values('date')
                  .groupby(self.group_cols, as_index=False)
                  .tail(1)[[*self.group_cols] + [c for c in hist.columns
                                                  if c.startswith('lag_') or c.startswith('rollmean_')]])
        
        # Create forecast date combinations
        combos = df_sites[self.group_cols].drop_duplicates().reset_index(drop=True)
        combos['date'] = fdate
        combos = add_calendar_features(combos).merge(latest, on=self.group_cols, how='left')
        
        # Fill NaN lag/rolling features with 0
        lagroll_cols = [c for c in self.feature_cols_num 
                       if c.startswith('lag_') or c.startswith('rollmean_')]
        for c in lagroll_cols:
            if c in combos:
                combos[c] = combos[c].fillna(0)
        
        # Predict - exact same logic as notebook
        Xf = pd.concat([combos[['partnumber','site_code']],
                        combos[['year','month','day','dayofweek','weekofyear','is_month_start','is_month_end'] + lagroll_cols]], axis=1)
        raw_model = np.maximum(0, self.best_model.predict(Xf))              # raw >= 0
        raw_thr   = np.where(raw_model < self.zero_threshold, 0, raw_model)     # threshold to zero
        yhat      = np.floor(raw_thr + 0.5).astype(int)             # half-up rounding
        
        combos['yhat_raw'] = raw_model
        combos['yhat_thr'] = raw_thr
        combos['yhat_round'] = yhat
        combos['date'] = fdate
        
        return combos[['partnumber', 'site_code', 'date',
                      'yhat_raw', 'yhat_thr', 'yhat_round']]
    
    def forecast(self, df_full, start_date=None, start_offset_days=1):
        """
        Generate multi-day forecast
        
        Args:
            df_full: Full historical data
            start_date: Start date for forecast (None = auto from data, or DD/MM/YYYY string)
            start_offset_days: Offset days from last historical date
        
        Returns:
            DataFrame with forecast results
        """
        
        # Filter sites if specified
        df_sites = df_full if self.forecast_site_codes is None else \
                   df_full[df_full['site_code'].isin(self.forecast_site_codes)].copy()
        
        if df_sites.empty:
            raise ValueError("No data for specified forecast_site_codes")
        
        # Determine start date
        max_hist = df_sites['date'].max()
        if start_date is None:
            start_date = max_hist + pd.Timedelta(days=start_offset_days)
        else:
            # Handle DD/MM/YYYY format from frontend
            if isinstance(start_date, str):
                try:
                    # Try DD/MM/YYYY format first
                    start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
                except ValueError:
                    # Fallback to pandas default parsing
                    start_date = pd.to_datetime(start_date)
            else:
                start_date = pd.to_datetime(start_date)
        
        # Initialize history
        history = df_sites[df_sites['date'] <= start_date - pd.Timedelta(days=1)].copy() \
                  if start_date <= max_hist else df_sites.copy()
        
        # Warm-up if there's a gap - use yhat_round like notebook
        gap = history['date'].max() + pd.Timedelta(days=1)
        while gap < start_date:
            tmp = self.one_day_forecast(history, df_sites, gap)
            add_back = tmp.rename(columns={'yhat_round':'demand_qty'})[['partnumber','site_code','date','demand_qty']].copy()
            history = pd.concat([history, add_back], ignore_index=True)
            gap += pd.Timedelta(days=1)
        
        # Main forecast loop
        forecasts = []
        for i in range(self.forecast_horizon):
            d = start_date + pd.Timedelta(days=i)
            print(f"  Forecasting {d.date()}...")
            
            out = self.one_day_forecast(history, df_sites, d)
            forecasts.append(out)
            
            # append rounded predictions back as history for iterative features - exact same as notebook
            add_back = out.rename(columns={'yhat_round':'demand_qty'})[['partnumber','site_code','date','demand_qty']].copy()
            history = pd.concat([history, add_back], ignore_index=True)
        
        forecast_df = (pd.concat(forecasts, ignore_index=True)
                       .sort_values(['partnumber', 'site_code', 'date'])
                       .reset_index(drop=True))
        
        return forecast_df
    
    def get_metrics(self):
        """Get model metrics - JSON serializable"""
        if not self.metrics_history:
            return None
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_to_native(obj):
            """Recursively convert numpy/pandas types to native Python types"""
            if isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_to_native(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif pd.api.types.is_scalar(obj) and pd.isna(obj):
                return None
            return obj
        
        return {
            'best_model': self.best_model_name,
            'all_models': convert_to_native(self.metrics_history)
        }

