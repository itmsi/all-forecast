#!/usr/bin/env python3
"""
Script untuk menganalisis data yang digunakan untuk membuat file output yang diharapkan
"""

import pandas as pd
import numpy as np

def analyze_expected_data():
    """Analisis data yang digunakan untuk membuat file output yang diharapkan"""
    
    print("=== ANALISIS DATA UNTUK FILE OUTPUT YANG DIHARAPKAN ===\n")
    
    # Load expected output
    expected_output = pd.read_csv('/app/forecast_ridge_log_thr05.csv')
    expected_output['date'] = pd.to_datetime(expected_output['date'])
    
    print(f"📊 File output yang diharapkan:")
    print(f"   Shape: {expected_output.shape}")
    print(f"   Date range: {expected_output['date'].min()} to {expected_output['date'].max()}")
    print(f"   Unique partnumbers: {expected_output['partnumber'].nunique()}")
    print(f"   Unique site codes: {expected_output['site_code'].nunique()}")
    
    # Check for empty partnumbers
    empty_parts = expected_output[expected_output['partnumber'].isna() | (expected_output['partnumber'] == '')]
    print(f"   Empty partnumbers: {len(empty_parts)}")
    
    # Check partnumber patterns
    partnumbers = expected_output['partnumber'].dropna().unique()
    print(f"   Sample partnumbers: {list(partnumbers[:10])}")
    
    # Check if there are partnumbers with quotes
    quoted_parts = [p for p in partnumbers if str(p).startswith("'")]
    print(f"   Partnumbers with quotes: {len(quoted_parts)}")
    if quoted_parts:
        print(f"   Sample quoted partnumbers: {quoted_parts[:5]}")
    
    # Load our input data
    our_data = pd.read_csv('/app/alldemand_augjul_new.csv')
    our_data['date'] = pd.to_datetime(our_data['date'])
    
    print(f"\n📊 Data input kita:")
    print(f"   Shape: {our_data.shape}")
    print(f"   Date range: {our_data['date'].min()} to {our_data['date'].max()}")
    print(f"   Unique partnumbers: {our_data['partnumber'].nunique()}")
    print(f"   Unique site codes: {our_data['site_code'].unique()}")
    
    # Check KENDARI data specifically
    kendari_data = our_data[our_data['site_code'] == 'KENDARI']
    print(f"\n🏢 KENDARI data:")
    print(f"   Shape: {kendari_data.shape}")
    print(f"   Date range: {kendari_data['date'].min()} to {kendari_data['date'].max()}")
    print(f"   Unique partnumbers: {kendari_data['partnumber'].nunique()}")
    
    # Check if we have the partnumbers from expected output
    expected_parts = set(expected_output['partnumber'].dropna().unique())
    our_parts = set(our_data['partnumber'].unique())
    overlap = expected_parts.intersection(our_parts)
    
    print(f"\n🔍 Partnumber overlap:")
    print(f"   Expected partnumbers: {len(expected_parts)}")
    print(f"   Our partnumbers: {len(our_parts)}")
    print(f"   Overlap: {len(overlap)}")
    
    if overlap:
        print(f"   Sample overlap: {list(overlap)[:10]}")
    
    # Check if we need to filter data to match expected output
    print(f"\n📅 Date analysis:")
    print(f"   Expected forecast starts: {expected_output['date'].min()}")
    print(f"   Our data ends: {our_data['date'].max()}")
    print(f"   Difference: {(expected_output['date'].min() - our_data['date'].max()).days} days")
    
    # Check if we need to use different data
    if (expected_output['date'].min() - our_data['date'].max()).days > 0:
        print(f"   ⚠️  Expected forecast starts AFTER our data ends!")
        print(f"   This suggests the expected output was made from different data")
    
    return {
        'expected_output': expected_output,
        'our_data': our_data,
        'overlap': overlap
    }

if __name__ == "__main__":
    try:
        result = analyze_expected_data()
        print(f"\n✅ Analysis completed!")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
