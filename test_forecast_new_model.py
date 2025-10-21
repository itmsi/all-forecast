#!/usr/bin/env python3
"""
Test script untuk memverifikasi model terbaru dengan file input alldemand_augjul_new.csv
dan memastikan output sesuai dengan format forecast_ridge_log_thr05.csv
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.core.ml_engine import MLForecaster
from app.core.preprocessing import prepare_features

def test_forecast_with_new_model():
    """Test forecast dengan model terbaru"""
    
    print("=== TEST FORECAST DENGAN MODEL TERBARU ===\n")
    
    # 1. Load data input
    input_file = "/app/alldemand_augjul_new.csv"
    print(f"📁 Loading input data: {input_file}")
    
    df = pd.read_csv(input_file)
    print(f"   Data shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   Site codes: {sorted(df['site_code'].unique())}")
    print(f"   Unique partnumbers: {df['partnumber'].nunique()}")
    
    # 2. Prepare data
    print(f"\n🔧 Preparing features...")
    df['date'] = pd.to_datetime(df['date'])
    df_fe = prepare_features(df, group_cols=['partnumber', 'site_code'])
    print(f"   Features shape: {df_fe.shape}")
    print(f"   Feature columns: {len(df_fe.columns)}")
    
    # 3. Configure model
    config = {
        'forecast_horizon': 7,
        'forecast_site_codes': ['KENDARI', 'ANGSANA', 'SOFIFI'],  # JAKARTA tidak ada dalam data
        'zero_threshold': 0.5,
        'rounding_mode': 'half_up',
        'random_state': 42
    }
    
    print(f"\n⚙️  Model configuration:")
    for k, v in config.items():
        print(f"   {k}: {v}")
    
    # 4. Initialize and train model
    print(f"\n🤖 Training model...")
    forecaster = MLForecaster(config)
    model = forecaster.train_and_select_model(df_fe)
    
    # 5. Generate forecast
    print(f"\n📊 Generating forecast...")
    forecast_df = forecaster.forecast(df_fe)
    
    print(f"   Forecast shape: {forecast_df.shape}")
    print(f"   Forecast columns: {list(forecast_df.columns)}")
    print(f"   Date range: {forecast_df['date'].min()} to {forecast_df['date'].max()}")
    print(f"   Site codes in forecast: {sorted(forecast_df['site_code'].unique())}")
    
    # 6. Format output sesuai dengan yang diharapkan
    print(f"\n📋 Formatting output...")
    
    # Rename columns sesuai format yang diharapkan
    output_df = forecast_df.copy()
    output_df = output_df.rename(columns={
        'forecast_qty_raw_model': 'yhat_raw',
        'forecast_qty_raw': 'yhat_thr', 
        'forecast_qty': 'yhat_round'
    })
    
    # Reorder columns sesuai format yang diharapkan
    output_df = output_df[['partnumber', 'site_code', 'date', 'yhat_raw', 'yhat_thr', 'yhat_round']]
    
    # 7. Save output
    output_file = "/app/test_forecast_output.csv"
    output_df.to_csv(output_file, index=False)
    print(f"   Output saved to: {output_file}")
    
    # 8. Show sample output
    print(f"\n📄 Sample output (first 20 rows):")
    print(output_df.head(20).to_string(index=False))
    
    # 9. Compare dengan format yang diharapkan
    print(f"\n🔍 Comparing dengan format yang diharapkan...")
    expected_file = "/app/forecast_ridge_log_thr05.csv"
    
    if os.path.exists(expected_file):
        expected_df = pd.read_csv(expected_file)
        print(f"   Expected format shape: {expected_df.shape}")
        print(f"   Expected columns: {list(expected_df.columns)}")
        print(f"   Our output shape: {output_df.shape}")
        print(f"   Our output columns: {list(output_df.columns)}")
        
        # Check if columns match
        if set(output_df.columns) == set(expected_df.columns):
            print("   ✅ Column names match!")
        else:
            print("   ❌ Column names don't match!")
            print(f"   Missing: {set(expected_df.columns) - set(output_df.columns)}")
            print(f"   Extra: {set(output_df.columns) - set(expected_df.columns)}")
    
    # 10. Summary statistics
    print(f"\n📈 Summary statistics:")
    print(f"   Total forecasts: {len(output_df)}")
    print(f"   Unique partnumbers: {output_df['partnumber'].nunique()}")
    print(f"   Unique site codes: {output_df['site_code'].nunique()}")
    print(f"   Date range: {output_df['date'].min()} to {output_df['date'].max()}")
    print(f"   yhat_raw range: {output_df['yhat_raw'].min():.6f} to {output_df['yhat_raw'].max():.6f}")
    print(f"   yhat_thr range: {output_df['yhat_thr'].min():.6f} to {output_df['yhat_thr'].max():.6f}")
    print(f"   yhat_round range: {output_df['yhat_round'].min()} to {output_df['yhat_round'].max()}")
    
    return output_df

if __name__ == "__main__":
    try:
        result = test_forecast_with_new_model()
        print(f"\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
