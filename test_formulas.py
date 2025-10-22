#!/usr/bin/env python3
"""
Simple test untuk memverifikasi perubahan formula
"""

import sys
import os
sys.path.append('/Users/falaqmsi/Documents/GitHub/forecast/backend')

import numpy as np
from backend.app.core.utils import smape, mape, eval_with_rounding

def test_formulas():
    """Test apakah formula sudah sama dengan notebook"""
    
    print("🧪 Testing formula synchronization...")
    
    # Test data
    y_true = np.array([1.0, 2.0, 3.0, 0.0, 5.0])
    y_pred = np.array([1.1, 1.9, 3.2, 0.1, 4.8])
    
    print(f"y_true: {y_true}")
    print(f"y_pred: {y_pred}")
    
    # Test SMAPE
    smape_val = smape(y_true, y_pred)
    print(f"SMAPE: {smape_val:.6f}")
    
    # Test MAPE
    mape_val = mape(y_true, y_pred)
    print(f"MAPE: {mape_val:.6f}")
    
    # Test eval_with_rounding
    rounded_metrics = eval_with_rounding(y_true, y_pred, thr=0.5)
    print(f"Rounded metrics: {rounded_metrics}")
    
    # Test thresholding dan rounding
    x = np.array([0.3, 0.6, 1.2, 0.4, 2.7])
    print(f"\nOriginal values: {x}")
    
    # Apply threshold
    x_thr = np.where(x < 0.5, 0, x)
    print(f"After threshold (0.5): {x_thr}")
    
    # Apply half-up rounding
    x_round = np.floor(x_thr + 0.5).astype(int)
    print(f"After half-up rounding: {x_round}")
    
    print("\n✅ Formula tests completed!")
    print("   All formulas should now match the notebook implementation.")

if __name__ == "__main__":
    test_formulas()
