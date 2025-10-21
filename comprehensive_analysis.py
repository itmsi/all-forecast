#!/usr/bin/env python3
"""
Analisis komprehensif perbedaan antara output yang dihasilkan dan yang diharapkan
"""

import pandas as pd
import numpy as np

def comprehensive_analysis():
    """Analisis komprehensif perbedaan output"""
    
    print("=== ANALISIS KOMPREHENSIF PERBEDAAN OUTPUT ===\n")
    
    # Load files
    our_output = pd.read_csv('test_forecast_permissive.csv')
    expected_output = pd.read_csv('/app/forecast_ridge_log_thr05.csv')
    
    print(f"📊 Perbandingan Output:")
    print(f"   Output kita: {len(our_output)} rows")
    print(f"   Output yang diharapkan: {len(expected_output)} rows")
    print(f"   Perbedaan: {len(expected_output) - len(our_output)} rows")
    
    # Analyze KENDARI specifically
    our_kendari = our_output[our_output['site_code'] == 'KENDARI']
    expected_kendari = expected_output[expected_output['site_code'] == 'KENDARI']
    
    print(f"\n🏢 KENDARI Analysis:")
    print(f"   Output kita: {len(our_kendari)} rows")
    print(f"   Output yang diharapkan: {len(expected_kendari)} rows")
    print(f"   Perbedaan: {len(expected_kendari) - len(our_kendari)} rows")
    
    print(f"   Unique partnumbers kita: {our_kendari['partnumber'].nunique()}")
    print(f"   Unique partnumbers yang diharapkan: {expected_kendari['partnumber'].nunique()}")
    
    # Check partnumber overlap
    our_parts = set(our_kendari['partnumber'].unique())
    expected_parts = set(expected_kendari['partnumber'].unique())
    
    overlap = our_parts.intersection(expected_parts)
    only_our = our_parts - expected_parts
    only_expected = expected_parts - our_parts
    
    print(f"\n🔍 Partnumber Analysis:")
    print(f"   Overlap: {len(overlap)} partnumbers")
    print(f"   Hanya di output kita: {len(only_our)} partnumbers")
    print(f"   Hanya di output yang diharapkan: {len(only_expected)} partnumbers")
    
    if overlap:
        print(f"   Contoh overlap: {list(overlap)[:5]}")
    if only_our:
        print(f"   Contoh hanya di output kita: {list(only_our)[:5]}")
    if only_expected:
        print(f"   Contoh hanya di output yang diharapkan: {list(only_expected)[:5]}")
    
    # Check date range
    print(f"\n📅 Date Range Analysis:")
    print(f"   Output kita: {our_output['date'].min()} to {our_output['date'].max()}")
    print(f"   Output yang diharapkan: {expected_output['date'].min()} to {expected_output['date'].max()}")
    
    # Check if expected output has more days
    our_dates = set(our_output['date'].unique())
    expected_dates = set(expected_output['date'].unique())
    
    print(f"   Unique dates kita: {len(our_dates)}")
    print(f"   Unique dates yang diharapkan: {len(expected_dates)}")
    
    # Check value ranges
    print(f"\n📈 Value Range Analysis:")
    print(f"   Output kita yhat_raw: {our_output['yhat_raw'].min():.6f} to {our_output['yhat_raw'].max():.6f}")
    print(f"   Output yang diharapkan yhat_raw: {expected_output['yhat_raw'].min():.6f} to {expected_output['yhat_raw'].max():.6f}")
    
    print(f"   Output kita yhat_thr: {our_output['yhat_thr'].min():.6f} to {our_output['yhat_thr'].max():.6f}")
    print(f"   Output yang diharapkan yhat_thr: {expected_output['yhat_thr'].min():.6f} to {expected_output['yhat_thr'].max():.6f}")
    
    # Check for zero values
    our_zeros = (our_output['yhat_thr'] == 0).sum()
    expected_zeros = (expected_output['yhat_thr'] == 0).sum()
    
    print(f"\n🔢 Zero Values Analysis:")
    print(f"   Output kita zeros: {our_zeros}/{len(our_output)} ({our_zeros/len(our_output)*100:.1f}%)")
    print(f"   Output yang diharapkan zeros: {expected_zeros}/{len(expected_output)} ({expected_zeros/len(expected_output)*100:.1f}%)")
    
    # Check if expected output has more comprehensive coverage
    print(f"\n🎯 Coverage Analysis:")
    print(f"   Output kita: {len(our_output)} forecasts untuk {our_output['partnumber'].nunique()} partnumbers")
    print(f"   Output yang diharapkan: {len(expected_output)} forecasts untuk {expected_output['partnumber'].nunique()} partnumbers")
    
    # Calculate expected partnumbers based on 7-day forecast
    expected_partnums_calc = len(expected_output) // 7
    our_partnums_calc = len(our_output) // 7
    
    print(f"   Perhitungan partnumbers (÷7):")
    print(f"     Output kita: {our_partnums_calc}")
    print(f"     Output yang diharapkan: {expected_partnums_calc}")
    
    return {
        'our_output': our_output,
        'expected_output': expected_output,
        'our_kendari': our_kendari,
        'expected_kendari': expected_kendari,
        'overlap': overlap,
        'only_our': only_our,
        'only_expected': only_expected
    }

if __name__ == "__main__":
    try:
        result = comprehensive_analysis()
        print(f"\n✅ Analysis completed!")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
