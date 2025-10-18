#!/usr/bin/env python3
"""
Cleanup old data files - keep only last 7 days
"""

import os
import glob
from datetime import datetime, timedelta

def cleanup_old_files(folder_pattern, days_to_keep=7):
    """Remove files older than specified days"""
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    removed_count = 0
    
    files = glob.glob(folder_pattern)
    
    for file_path in files:
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        if file_mtime < cutoff_date:
            try:
                os.remove(file_path)
                print(f"🗑️  Removed old file: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {file_path}: {e}")
    
    return removed_count


def main():
    """Clean up old files from all output folders"""
    print("=" * 80)
    print("CLEANUP OLD FILES - Keep Last 7 Days")
    print("=" * 80)
    
    total_removed = 0
    
    # Clean up data/historical
    print("\n📂 Cleaning data/historical/...")
    total_removed += cleanup_old_files('data/historical/*.csv')
    total_removed += cleanup_old_files('data/historical/*.json')
    
    # Clean up output/charts
    print("\n📂 Cleaning output/charts/...")
    total_removed += cleanup_old_files('output/charts/*.png')
    
    # Clean up output/heatmaps
    print("\n📂 Cleaning output/heatmaps/...")
    total_removed += cleanup_old_files('output/heatmaps/*.png')
    
    # Clean up output/reports
    print("\n📂 Cleaning output/reports/...")
    total_removed += cleanup_old_files('output/reports/*.json')
    total_removed += cleanup_old_files('output/reports/*.txt')
    
    print("\n" + "=" * 80)
    print(f"✅ Cleanup complete! Removed {total_removed} old files.")
    print("=" * 80)


if __name__ == "__main__":
    main()
