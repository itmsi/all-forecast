#!/usr/bin/env python3
"""
Script untuk menganalisis mengapa hanya 643 partnumbers yang dihasilkan dari 1164 partnumbers KENDARI
"""

import pandas as pd
import numpy as np

def analyze_missing_partnumbers():
    """Analisis mengapa banyak partnumbers yang hilang"""
    
    print("=== ANALISIS PARTNUMBERS YANG HILANG ===\n")
    
    # Load data
    df = pd.read_csv('/app/alldemand_augjul_new.csv')
    df.columns = [c.strip().lower() for c in df.columns]
    df['partnumber'] = df['partnumber'].astype(str).str.strip()
    df['site_code'] = df['site_code'].astype(str).str.strip()
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df['demand_qty'] = pd.to_numeric(df['demand_qty'], errors='coerce').fillna(0)
    
    # Filter KENDARI only
    kendari_data = df[df['site_code'] == 'KENDARI'].copy()
    
    print(f"📊 KENDARI Data Analysis:")
    print(f"   Total rows: {len(kendari_data)}")
    print(f"   Unique partnumbers: {kendari_data['partnumber'].nunique()}")
    print(f"   Date range: {kendari_data['date'].min()} to {kendari_data['date'].max()}")
    
    # Analyze data span per partnumber
    part_spans = kendari_data.groupby('partnumber')['date'].apply(lambda x: (x.max() - x.min()).days)
    part_counts = kendari_data.groupby('partnumber').size()
    
    print(f"\n📈 Data Span Analysis:")
    print(f"   Min span: {part_spans.min()} days")
    print(f"   Max span: {part_spans.max()} days")
    print(f"   Mean span: {part_spans.mean():.1f} days")
    print(f"   Median span: {part_spans.median():.1f} days")
    
    print(f"\n📊 Data Count Analysis:")
    print(f"   Min count: {part_counts.min()} records")
    print(f"   Max count: {part_counts.max()} records")
    print(f"   Mean count: {part_counts.mean():.1f} records")
    print(f"   Median count: {part_counts.median():.1f} records")
    
    # Check how many partnumbers have enough data for different lag requirements
    print(f"\n🔍 Lag Requirements Analysis:")
    
    # For lag_1 (need at least 1 day before)
    enough_lag1 = part_spans >= 1
    print(f"   Enough for lag_1 (≥1 day): {enough_lag1.sum()}/{len(part_spans)} ({enough_lag1.sum()/len(part_spans)*100:.1f}%)")
    
    # For lag_7 (need at least 7 days before)
    enough_lag7 = part_spans >= 7
    print(f"   Enough for lag_7 (≥7 days): {enough_lag7.sum()}/{len(part_spans)} ({enough_lag7.sum()/len(part_spans)*100:.1f}%)")
    
    # For lag_14 (need at least 14 days before)
    enough_lag14 = part_spans >= 14
    print(f"   Enough for lag_14 (≥14 days): {enough_lag14.sum()}/{len(part_spans)} ({enough_lag14.sum()/len(part_spans)*100:.1f}%)")
    
    # For lag_28 (need at least 28 days before)
    enough_lag28 = part_spans >= 28
    print(f"   Enough for lag_28 (≥28 days): {enough_lag28.sum()}/{len(part_spans)} ({enough_lag28.sum()/len(part_spans)*100:.1f}%)")
    
    # Show examples of partnumbers with different spans
    print(f"\n📋 Examples by Data Span:")
    
    # Very short span (0-7 days)
    short_span = part_spans[part_spans <= 7]
    print(f"   Short span (0-7 days): {len(short_span)} partnumbers")
    if len(short_span) > 0:
        print(f"     Examples: {list(short_span.head(5).index)}")
    
    # Medium span (8-28 days)
    medium_span = part_spans[(part_spans > 7) & (part_spans <= 28)]
    print(f"   Medium span (8-28 days): {len(medium_span)} partnumbers")
    if len(medium_span) > 0:
        print(f"     Examples: {list(medium_span.head(5).index)}")
    
    # Long span (>28 days)
    long_span = part_spans[part_spans > 28]
    print(f"   Long span (>28 days): {len(long_span)} partnumbers")
    if len(long_span) > 0:
        print(f"     Examples: {list(long_span.head(5).index)}")
    
    # Check if we can use minimal lags to keep more partnumbers
    print(f"\n💡 Recommendations:")
    print(f"   Current approach uses lags (1,7,14,28) which requires ≥28 days")
    print(f"   This eliminates {len(part_spans) - enough_lag28.sum()} partnumbers")
    print(f"   Using only lag_1 would keep {enough_lag1.sum()} partnumbers")
    print(f"   Using lags (1,7) would keep {enough_lag7.sum()} partnumbers")
    
    return {
        'part_spans': part_spans,
        'part_counts': part_counts,
        'enough_lag1': enough_lag1,
        'enough_lag7': enough_lag7,
        'enough_lag14': enough_lag14,
        'enough_lag28': enough_lag28
    }

if __name__ == "__main__":
    try:
        result = analyze_missing_partnumbers()
        print(f"\n✅ Analysis completed!")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
