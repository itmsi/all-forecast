#!/usr/bin/env python3
"""
Script untuk test forecast dengan preprocessing yang lebih permisif
"""

import pandas as pd
import numpy as np
import sys
sys.path.append('/app')
from app.core.ml_engine import MLForecaster
from app.core.preprocessing import add_calendar_features, add_group_lags_rolls

def prepare_features_permissive(df, group_cols=['partnumber', 'site_code']):
    """Prepare features dengan pendekatan yang lebih permisif"""
    
    print(f"🔧 Preparing features (permissive approach)...")
    
    # Add calendar features
    df_fe = add_calendar_features(df)
    
    # Use minimal lags untuk mempertahankan lebih banyak data
    lags = (1, 7)  # Hanya lag_1 dan lag_7
    roll_windows = (7,)  # Hanya rollmean_7
    
    # Add lag and rolling features
    df_fe = add_group_lags_rolls(
        df_fe, 
        group_cols, 
        target_col='demand_qty',
        lags=lags, 
        roll_windows=roll_windows
    )
    
    # Remove rows with null lag_7 only (keep lag_1 nulls)
    df_fe = df_fe[df_fe['lag_7'].notnull()].reset_index(drop=True)
    
    print(f"   Features prepared: {len(df_fe)} rows")
    print(f"   Unique partnumbers: {df_fe['partnumber'].nunique()}")
    print(f"   Unique site codes: {df_fe['site_code'].nunique()}")
    
    return df_fe

def test_forecast_permissive():
    """Test forecast dengan preprocessing yang lebih permisif"""
    
    print("=== TEST FORECAST DENGAN PREPROCESSING PERMISIF ===\n")
    
    # 1. Load data input
    input_file = "/app/alldemand_augjul_new.csv"
    print(f"📁 Loading input data: {input_file}")
    
    df = pd.read_csv(input_file)
    df['date'] = pd.to_datetime(df['date'])
    print(f"   Data shape: {df.shape}")
    print(f"   Site codes: {sorted(df['site_code'].unique())}")
    
    # 2. Prepare features dengan pendekatan permisif
    df_fe = prepare_features_permissive(df)
    
    # 3. Configure model
    config = {
        'forecast_horizon': 7,
        'forecast_site_codes': ['KENDARI', 'ANGSANA', 'SOFIFI'],
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
    print(f"   Unique partnumbers: {forecast_df['partnumber'].nunique()}")
    print(f"   Unique site codes: {forecast_df['site_code'].nunique()}")
    
    # 6. Format output
    output_df = forecast_df.copy()
    output_df = output_df.rename(columns={
        'forecast_qty_raw_model': 'yhat_raw',
        'forecast_qty_raw': 'yhat_thr', 
        'forecast_qty': 'yhat_round'
    })
    output_df = output_df[['partnumber', 'site_code', 'date', 'yhat_raw', 'yhat_thr', 'yhat_round']]
    
    # 7. Save output
    output_file = "/app/test_forecast_permissive.csv"
    output_df.to_csv(output_file, index=False)
    print(f"   Output saved to: {output_file}")
    
    # 8. Show sample output
    print(f"\n📄 Sample output (first 20 rows):")
    print(output_df.head(20).to_string(index=False))
    
    # 9. Summary statistics
    print(f"\n📈 Summary statistics:")
    print(f"   Total forecasts: {len(output_df)}")
    print(f"   Unique partnumbers: {output_df['partnumber'].nunique()}")
    print(f"   Unique site codes: {output_df['site_code'].nunique()}")
    print(f"   Date range: {output_df['date'].min()} to {output_df['date'].max()}")
    
    # Check KENDARI specifically
    kendari_output = output_df[output_df['site_code'] == 'KENDARI']
    print(f"   KENDARI forecasts: {len(kendari_output)}")
    print(f"   KENDARI unique partnumbers: {kendari_output['partnumber'].nunique()}")
    
    return output_df

if __name__ == "__main__":
    try:
        result = test_forecast_permissive()
        print(f"\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
