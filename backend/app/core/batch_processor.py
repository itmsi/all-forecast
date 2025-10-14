# backend/app/core/batch_processor.py
"""
Batch processing untuk handle large datasets
Auto-partition data dan run parallel jobs
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np


class BatchProcessor:
    """
    Auto-partition large datasets menjadi multiple jobs
    untuk optimasi dan parallel processing
    """
    
    def __init__(self, 
                 max_rows_per_job: int = 2000,
                 partition_by: str = 'site',
                 max_partitions: int = 20):
        """
        Args:
            max_rows_per_job: Maximum rows per job (optimal: 1000-3000)
            partition_by: 'site' atau 'auto' (by site recommended)
            max_partitions: Maximum number of partitions to create
        """
        self.max_rows_per_job = max_rows_per_job
        self.partition_by = partition_by
        self.max_partitions = max_partitions
    
    def analyze_data(self, df: pd.DataFrame) -> Dict:
        """Analyze data untuk determine partitioning strategy"""
        
        total_rows = len(df)
        unique_sites = df['site_code'].nunique()
        unique_parts = df['partnumber'].nunique()
        
        site_distribution = df['site_code'].value_counts().to_dict()
        
        return {
            'total_rows': total_rows,
            'unique_sites': unique_sites,
            'unique_partnumbers': unique_parts,
            'site_distribution': site_distribution,
            'needs_partitioning': total_rows > self.max_rows_per_job,
            'recommended_partitions': min(
                unique_sites,
                max(1, total_rows // self.max_rows_per_job),
                self.max_partitions
            )
        }
    
    def create_partitions(self, df: pd.DataFrame) -> List[Dict]:
        """
        Create partitions dari dataset
        
        Returns:
            List of dicts with partition info:
            {
                'partition_id': int,
                'data': DataFrame,
                'metadata': {
                    'rows': int,
                    'sites': List[str],
                    'partnumbers_count': int,
                    'date_range': tuple
                }
            }
        """
        analysis = self.analyze_data(df)
        
        # Jika data kecil, tidak perlu partition
        if not analysis['needs_partitioning']:
            return [{
                'partition_id': 0,
                'data': df,
                'metadata': self._get_partition_metadata(df, 0)
            }]
        
        # Partition by site (recommended)
        if self.partition_by == 'site':
            return self._partition_by_site(df, analysis)
        
        # Auto partition (by size)
        return self._partition_by_size(df, analysis)
    
    def _partition_by_site(self, df: pd.DataFrame, analysis: Dict) -> List[Dict]:
        """Partition data by site_code"""
        
        partitions = []
        site_dist = analysis['site_distribution']
        
        # Sort sites by volume (largest first)
        sorted_sites = sorted(site_dist.items(), key=lambda x: x[1], reverse=True)
        
        partition_id = 0
        
        # Strategy 1: One site per partition (if reasonable)
        if analysis['unique_sites'] <= self.max_partitions:
            for site_code, count in sorted_sites:
                site_data = df[df['site_code'] == site_code].copy()
                
                partitions.append({
                    'partition_id': partition_id,
                    'data': site_data,
                    'metadata': self._get_partition_metadata(site_data, partition_id)
                })
                partition_id += 1
        
        # Strategy 2: Group small sites together
        else:
            current_batch = []
            current_rows = 0
            
            for site_code, count in sorted_sites:
                if count > self.max_rows_per_job:
                    # Large site gets its own partition
                    if current_batch:
                        # Save current batch first
                        batch_data = df[df['site_code'].isin(current_batch)].copy()
                        partitions.append({
                            'partition_id': partition_id,
                            'data': batch_data,
                            'metadata': self._get_partition_metadata(batch_data, partition_id)
                        })
                        partition_id += 1
                        current_batch = []
                        current_rows = 0
                    
                    # Large site
                    site_data = df[df['site_code'] == site_code].copy()
                    partitions.append({
                        'partition_id': partition_id,
                        'data': site_data,
                        'metadata': self._get_partition_metadata(site_data, partition_id)
                    })
                    partition_id += 1
                
                elif current_rows + count > self.max_rows_per_job:
                    # Save current batch
                    batch_data = df[df['site_code'].isin(current_batch)].copy()
                    partitions.append({
                        'partition_id': partition_id,
                        'data': batch_data,
                        'metadata': self._get_partition_metadata(batch_data, partition_id)
                    })
                    partition_id += 1
                    current_batch = [site_code]
                    current_rows = count
                
                else:
                    # Add to current batch
                    current_batch.append(site_code)
                    current_rows += count
                
                # Safety: max partitions
                if partition_id >= self.max_partitions:
                    break
            
            # Save remaining batch
            if current_batch:
                batch_data = df[df['site_code'].isin(current_batch)].copy()
                partitions.append({
                    'partition_id': partition_id,
                    'data': batch_data,
                    'metadata': self._get_partition_metadata(batch_data, partition_id)
                })
        
        return partitions
    
    def _partition_by_size(self, df: pd.DataFrame, analysis: Dict) -> List[Dict]:
        """Partition data by chunk size (simple split)"""
        
        partitions = []
        chunk_size = self.max_rows_per_job
        total_rows = len(df)
        
        for i in range(0, total_rows, chunk_size):
            chunk_data = df.iloc[i:i+chunk_size].copy()
            partition_id = i // chunk_size
            
            partitions.append({
                'partition_id': partition_id,
                'data': chunk_data,
                'metadata': self._get_partition_metadata(chunk_data, partition_id)
            })
            
            # Safety: max partitions
            if partition_id >= self.max_partitions:
                break
        
        return partitions
    
    def _get_partition_metadata(self, df: pd.DataFrame, partition_id: int) -> Dict:
        """Extract metadata dari partition"""
        
        return {
            'partition_id': partition_id,
            'rows': len(df),
            'sites': df['site_code'].unique().tolist(),
            'site_count': df['site_code'].nunique(),
            'partnumbers_count': df['partnumber'].nunique(),
            'date_range': (df['date'].min(), df['date'].max()) if 'date' in df.columns else None,
            'demand_sum': df['demand_qty'].sum() if 'demand_qty' in df.columns else 0
        }
    
    def save_partition(self, partition: Dict, output_dir: str) -> str:
        """Save partition to CSV file"""
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        partition_id = partition['partition_id']
        filename = f"partition_{partition_id:03d}.csv"
        filepath = Path(output_dir) / filename
        
        partition['data'].to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return str(filepath)
    
    def estimate_processing_time(self, partitions: List[Dict]) -> Dict:
        """Estimate processing time untuk partitions"""
        
        # Estimasi: ~1-2 detik per 100 rows untuk training
        # + overhead 30 detik untuk feature engineering
        
        estimates = []
        for p in partitions:
            rows = p['metadata']['rows']
            parts = p['metadata']['partnumbers_count']
            
            # Base time
            base_time = 30  # overhead
            
            # Training time (depends on unique partnumbers)
            training_time = (parts / 100) * 5  # 5 seconds per 100 unique parts
            
            # Feature engineering
            feature_time = (rows / 1000) * 10  # 10 seconds per 1000 rows
            
            total_seconds = base_time + training_time + feature_time
            
            estimates.append({
                'partition_id': p['partition_id'],
                'estimated_seconds': int(total_seconds),
                'estimated_minutes': round(total_seconds / 60, 1)
            })
        
        # Parallel execution (all run simultaneously)
        max_time = max(e['estimated_seconds'] for e in estimates)
        
        return {
            'per_partition': estimates,
            'sequential_total_seconds': sum(e['estimated_seconds'] for e in estimates),
            'parallel_total_seconds': max_time,
            'speedup_factor': round(
                sum(e['estimated_seconds'] for e in estimates) / max(1, max_time), 
                2
            )
        }

