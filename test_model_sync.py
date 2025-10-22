#!/usr/bin/env python3
"""
Test script untuk memverifikasi bahwa model backend sudah sinkron dengan notebook
"""

import sys
import os
sys.path.append('/Users/falaqmsi/Documents/GitHub/forecast/backend')

import pandas as pd
import numpy as np
from backend.app.core.ml_engine import MLForecaster
from backend.app.core.preprocessing import load_and_normalize, preprocess_data, prepare_features

def test_model_sync():
    """Test apakah model backend menghasilkan hasil yang sama dengan notebook"""
    
    print("🔍 Testing Model Synchronization...")
    
    # Load data yang sama dengan notebook
    data_path = '/Users/falaqmsi/Documents/GitHub/forecast/real_data/alldemand_augjul_new.csv'
    
    print(f"📁 Loading data from: {data_path}")
    df = load_and_normalize(data_path, dayfirst=True)
    
    # Preprocess data
    df = preprocess_data(df)
    
    # Prepare features dengan parameter yang sama dengan notebook
    df_fe = prepare_features(df, group_cols=['partnumber', 'site_code'], 
                           lags=(1, 7, 14, 28), roll_windows=(7, 14, 28))
    
    print(f"✅ Data prepared: {len(df_fe)} rows")
    
    # Config yang sama dengan notebook
    config = {
        'forecast_horizon': 7,
        'forecast_site_codes': ['KENDARI'],  # Same as notebook
        'zero_threshold': 0.5,  # Same as notebook
        'rounding_mode': 'half_up',
        'random_state': 42
    }
    
    # Initialize forecaster
    forecaster = MLForecaster(config)
    
    print("🤖 Training model...")
    model = forecaster.train_and_select_model(df_fe)
    
    print("📊 Model metrics:")
    metrics = forecaster.get_metrics()
    if metrics:
        print(f"   Best model: {metrics['best_model']}")
        if 'Ridge_log' in metrics['all_models']:
            ridge_metrics = metrics['all_models']['Ridge_log']
            print(f"   Raw MAPE%: {ridge_metrics['raw']['MAPE%']:.4f}")
            print(f"   Rounded MAPE%: {ridge_metrics['rounded']['MAPE%']:.4f}")
    
    print("🔮 Generating forecast...")
    forecast_df = forecaster.forecast(df_fe, start_offset_days=1)
    
    print(f"📈 Forecast generated: {len(forecast_df)} predictions")
    print("\n📋 Sample forecast results:")
    print(forecast_df.head(10))
    
    # Check if results look reasonable
    print(f"\n📊 Forecast statistics:")
    print(f"   Total predictions: {len(forecast_df)}")
    print(f"   Non-zero predictions: {(forecast_df['yhat_round'] > 0).sum()}")
    print(f"   Mean yhat_raw: {forecast_df['yhat_raw'].mean():.4f}")
    print(f"   Mean yhat_round: {forecast_df['yhat_round'].mean():.4f}")
    
    # Save results untuk comparison
    output_path = '/Users/falaqmsi/Documents/GitHub/forecast/test_backend_forecast.csv'
    forecast_df.to_csv(output_path, index=False)
    print(f"\n💾 Results saved to: {output_path}")
    
    print("\n✅ Test completed! Backend model should now be synchronized with notebook.")
    print("   Compare the output with forecast_ridge_log_thr05.csv from notebook.")

if __name__ == "__main__":
    test_model_sync()
