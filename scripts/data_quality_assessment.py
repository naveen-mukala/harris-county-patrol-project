#!/usr/bin/env python3
"""
Data Quality Assessment Script for Harris County Law Enforcement Resource Allocation Project

This script performs initial quality assessment on the geospatial datasets acquired for the
Harris County Law Enforcement Resource Allocation and Service Equity Analysis project.

The script checks for:
1. Data completeness (missing values)
2. Geometry validity
3. Coordinate reference system consistency
4. Attribute completeness and consistency
5. Basic statistics on key attributes

Author: Data Science Portfolio Project
Date: May 26, 2025
"""

import os
import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.validation import explain_validity

# Set paths
DATA_DIR = '/home/ubuntu/harris_county_project/data'
OUTPUT_DIR = '/home/ubuntu/harris_county_project/data/assessment'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define datasets to assess
datasets = {
    'constable_precincts': os.path.join(DATA_DIR, 'constable_precincts.geojson'),
    'commissioner_precincts': os.path.join(DATA_DIR, 'commissioner_precincts.geojson'),
    'harris_county_zipcodes': os.path.join(DATA_DIR, 'harris_county_zipcodes.geojson')
}

# Function to assess a GeoJSON dataset
def assess_geojson(file_path, dataset_name):
    print(f"\nAssessing {dataset_name}...")
    
    # Load the dataset
    try:
        gdf = gpd.read_file(file_path)
        print(f"Successfully loaded {dataset_name}")
        print(f"CRS: {gdf.crs}")
        print(f"Number of features: {len(gdf)}")
    except Exception as e:
        print(f"Error loading {dataset_name}: {e}")
        return None
    
    # Create assessment report
    report = {
        "dataset_name": dataset_name,
        "file_path": file_path,
        "feature_count": len(gdf),
        "crs": str(gdf.crs),
        "attributes": list(gdf.columns),
        "geometry_type": str(gdf.geometry.geom_type.unique()),
        "missing_values": {},
        "invalid_geometries": [],
        "attribute_stats": {}
    }
    
    # Check for missing values
    for col in gdf.columns:
        if col != 'geometry':
            missing = gdf[col].isna().sum()
            if missing > 0:
                report["missing_values"][col] = int(missing)
    
    # Check geometry validity
    invalid_count = 0
    invalid_indices = []
    
    for idx, geom in enumerate(gdf.geometry):
        if not geom.is_valid:
            invalid_count += 1
            invalid_indices.append({
                "index": idx,
                "reason": explain_validity(geom)
            })
    
    report["invalid_geometries_count"] = invalid_count
    report["invalid_geometries"] = invalid_indices
    
    # Calculate basic statistics for numeric attributes
    for col in gdf.columns:
        if col != 'geometry' and pd.api.types.is_numeric_dtype(gdf[col]):
            report["attribute_stats"][col] = {
                "min": float(gdf[col].min()),
                "max": float(gdf[col].max()),
                "mean": float(gdf[col].mean()),
                "median": float(gdf[col].median()),
                "std": float(gdf[col].std())
            }
    
    # Save report to JSON
    report_path = os.path.join(OUTPUT_DIR, f"{dataset_name}_assessment.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Create a simple visualization of the dataset
    fig, ax = plt.subplots(1, figsize=(10, 10))
    gdf.plot(ax=ax)
    ax.set_title(f"{dataset_name} - Geometry Overview")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"{dataset_name}_overview.png"))
    plt.close()
    
    # Create a summary dataframe for the report
    summary_df = pd.DataFrame({
        "Attribute": list(gdf.columns),
        "Data Type": [str(gdf[col].dtype) for col in gdf.columns],
        "Missing Values": [gdf[col].isna().sum() if col != 'geometry' else 0 for col in gdf.columns],
        "Unique Values": [gdf[col].nunique() if col != 'geometry' else None for col in gdf.columns]
    })
    
    # Save summary to CSV
    summary_df.to_csv(os.path.join(OUTPUT_DIR, f"{dataset_name}_summary.csv"), index=False)
    
    print(f"Assessment complete for {dataset_name}")
    print(f"Report saved to {report_path}")
    
    return report

# Main execution
def main():
    print("Starting data quality assessment...")
    
    assessment_results = {}
    
    for name, path in datasets.items():
        assessment_results[name] = assess_geojson(path, name)
    
    # Create a combined report
    combined_report = {
        "assessment_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "datasets_assessed": list(datasets.keys()),
        "summary": {
            "total_datasets": len(datasets),
            "datasets_with_issues": sum(1 for r in assessment_results.values() 
                                      if r and (r["invalid_geometries_count"] > 0 or len(r["missing_values"]) > 0))
        },
        "dataset_reports": assessment_results
    }
    
    # Save combined report
    combined_report_path = os.path.join(OUTPUT_DIR, "combined_assessment_report.json")
    with open(combined_report_path, 'w') as f:
        json.dump(combined_report, f, indent=2)
    
    print("\nData quality assessment complete!")
    print(f"Combined report saved to {combined_report_path}")
    print(f"Individual reports and visualizations saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
