#!/usr/bin/env python3
"""
Script untuk membersihkan alldemand_augjul.csv
- Remove duplikat
- Aggregate demand untuk kombinasi sama
- Fix BOM character
"""

import pandas as pd
import sys

print("=" * 60)
print("🧹 CLEANING: alldemand_augjul.csv")
print("=" * 60)
print()

# Read CSV
print("📖 Loading file...")
input_file = sys.argv[1] if len(sys.argv) > 1 else 'real_data/alldemand_augjul.csv'
df = pd.read_csv(input_file, encoding='utf-8-sig')  # utf-8-sig removes BOM

print(f"   Original rows: {len(df)}")
print(f"   Columns: {list(df.columns)}")
print()

# Check for duplicates
print("🔍 Checking duplicates...")
dup_mask = df.duplicated(subset=['date', 'partnumber', 'site_code'], keep=False)
dup_count = dup_mask.sum()
print(f"   Found {dup_count} duplicate rows")

if dup_count > 0:
    print()
    print("📊 Contoh duplikat:")
    sample_dups = df[dup_mask].head(10)
    for idx, row in sample_dups.iterrows():
        print(f"   {row['date']} | {row['partnumber']} | {row['site_code']} | demand={row['demand_qty']}")
    print()

# Aggregate duplicates by summing demand_qty
print("🔧 Aggregating duplicates (sum demand_qty)...")
df_clean = df.groupby(['date', 'partnumber', 'site_code'], as_index=False).agg({
    'demand_qty': 'sum'
})

# Reorder columns to match original
df_clean = df_clean[['demand_qty', 'date', 'partnumber', 'site_code']]

print(f"   After aggregation: {len(df_clean)} rows")
print(f"   Removed: {len(df) - len(df_clean)} duplicate rows")
print()

# Check for scientific notation partnumbers
print("🔬 Checking for scientific notation partnumbers...")
sci_notation = df_clean['partnumber'].astype(str).str.contains('E\+', na=False, regex=False)
sci_count = sci_notation.sum()

if sci_count > 0:
    print(f"   ⚠️  Found {sci_count} partnumbers with scientific notation")
    print("   Example partnumbers:")
    unique_sci = df_clean[sci_notation]['partnumber'].unique()[:10]
    for pn in unique_sci:
        print(f"      {pn}")
    print()
    print("   ⚠️  WARNING: Scientific notation tidak bisa di-fix otomatis!")
    print("   📝 SOLUSI: Buka file di Excel, format partnumber kolom as TEXT, lalu save ulang")
    print()
else:
    print("   ✅ No scientific notation found")
    print()

# Save cleaned data
output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.csv', '_CLEAN.csv')
print(f"💾 Saving cleaned data to: {output_file}")
df_clean.to_csv(output_file, index=False, encoding='utf-8')

print()
print("=" * 60)
print("✅ DONE!")
print("=" * 60)
print()
print("📊 Summary:")
print(f"   Original rows: {len(df)}")
print(f"   Cleaned rows: {len(df_clean)}")
print(f"   Duplicates removed: {len(df) - len(df_clean)}")
print(f"   Scientific notation issues: {sci_count}")
print()

if sci_count > 0:
    print("⚠️  NEXT STEPS:")
    print("   1. Buka file ASLI (alldemand_augjul.xlsx) di Excel")
    print("   2. Format kolom 'partnumber' as TEXT (bukan General/Number)")
    print("   3. Save as CSV lagi")
    print("   4. Jalankan script ini lagi untuk remove duplikat")
    print()
    print("   ATAU gunakan file CLEAN ini jika scientific notation tidak masalah")
else:
    print("✅ File siap digunakan untuk batch forecast!")
    print(f"   Use: {output_file}")

print()

