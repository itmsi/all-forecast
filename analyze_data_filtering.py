#!/usr/bin/env python3
"""
Script untuk menganalisis mengapa hanya sedikit partnumber yang dihasilkan dalam forecast
"""

import pandas as pd
import numpy as np

def analyze_data_filtering():
    """Analisis mengapa preprocessing menghasilkan sedikit data"""
    
    print("=== ANALISIS DATA FILTERING ===\n")
    
    # Load data
    df = pd.read_csv('/app/alldemand_augjul_new.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"📊 Original data:")
    print(f"   Total rows: {len(df)}")
    print(f"   Unique partnumbers: {df['partnumber'].nunique()}")
    print(f"   Unique site codes: {df['site_code'].nunique()}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Analyze per site
    for site in df['site_code'].unique():
        site_data = df[df['site_code'] == site]
        print(f"\n🏢 {site}:")
        print(f"   Rows: {len(site_data)}")
        print(f"   Unique partnumbers: {site_data['partnumber'].nunique()}")
        print(f"   Date range: {site_data['date'].min()} to {site_data['date'].max()}")
        
        # Check data span per partnumber
        part_spans = site_data.groupby('partnumber')['date'].apply(lambda x: (x.max() - x.min()).days)
        print(f"   Data span per partnumber:")
        print(f"     Min: {part_spans.min()} days")
        print(f"     Max: {part_spans.max()} days")
        print(f"     Mean: {part_spans.mean():.1f} days")
        print(f"     Median: {part_spans.median():.1f} days")
        
        # Check how many partnumbers have enough data for lags
        enough_data = part_spans >= 28  # Need at least 28 days for lag_28
        print(f"   Partnumbers with ≥28 days: {enough_data.sum()}/{len(part_spans)}")
        
        # Show some examples
        print(f"   Examples of partnumbers with enough data:")
        examples = part_spans[enough_data].head(5)
        for part, days in examples.items():
            print(f"     {part}: {days} days")
    
    # Check what happens after lag/roll features
    print(f"\n🔧 Simulating feature engineering...")
    
    # Add calendar features
    df_fe = df.copy()
    df_fe['year'] = df_fe['date'].dt.year
    df_fe['month'] = df_fe['date'].dt.month
    df_fe['day'] = df_fe['date'].dt.day
    df_fe['dayofweek'] = df_fe['date'].dt.dayofweek
    df_fe['weekofyear'] = df_fe['date'].dt.isocalendar().week.astype(int)
    df_fe['is_month_start'] = df_fe['date'].dt.is_month_start.astype(int)
    df_fe['is_month_end'] = df_fe['date'].dt.is_month_end.astype(int)
    
    # Add lag features (simplified)
    df_fe = df_fe.sort_values(['partnumber', 'site_code', 'date']).reset_index(drop=True)
    g = df_fe.groupby(['partnumber', 'site_code'], group_keys=False)
    
    # Add lag_1 and lag_7
    df_fe['lag_1'] = g['demand_qty'].shift(1)
    df_fe['lag_7'] = g['demand_qty'].shift(7)
    
    print(f"   After adding lags: {len(df_fe)} rows")
    
    # Check null values
    null_lag1 = df_fe['lag_1'].isnull().sum()
    null_lag7 = df_fe['lag_7'].isnull().sum()
    print(f"   Null lag_1: {null_lag1}")
    print(f"   Null lag_7: {null_lag7}")
    
    # Remove rows with null lags
    df_fe_clean = df_fe[df_fe[['lag_1', 'lag_7']].notnull().all(axis=1)]
    print(f"   After removing null lags: {len(df_fe_clean)} rows")
    print(f"   Unique partnumbers after cleaning: {df_fe_clean['partnumber'].nunique()}")
    
    # Check per site after cleaning
    for site in df_fe_clean['site_code'].unique():
        site_clean = df_fe_clean[df_fe_clean['site_code'] == site]
        print(f"   {site} after cleaning: {len(site_clean)} rows, {site_clean['partnumber'].nunique()} partnumbers")
    
    return df_fe_clean

if __name__ == "__main__":
    try:
        result = analyze_data_filtering()
        print(f"\n✅ Analysis completed!")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
