#!/usr/bin/env python3
"""
Exploratory Data Analysis Script for Harris County Law Enforcement Resource Allocation Project

This script performs exploratory data analysis on the geospatial datasets for the
Harris County Law Enforcement Resource Allocation and Service Equity Analysis project.

The analysis includes:
1. Spatial distribution of precincts and zipcodes
2. Area and perimeter analysis
3. Spatial relationships between different boundary types
4. Visualization of key attributes

Author: Data Science Portfolio Project
Date: May 26, 2025
"""

import os
import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point
import numpy as np
import matplotlib.colors as mcolors

# Set paths
DATA_DIR = '/home/ubuntu/harris_county_project/data'
OUTPUT_DIR = '/home/ubuntu/harris_county_project/data/eda'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define datasets to analyze
datasets = {
    'constable_precincts': os.path.join(DATA_DIR, 'constable_precincts.geojson'),
    'commissioner_precincts': os.path.join(DATA_DIR, 'commissioner_precincts.geojson'),
    'harris_county_zipcodes': os.path.join(DATA_DIR, 'harris_county_zipcodes.geojson')
}

# Load datasets
def load_datasets():
    loaded_data = {}
    for name, path in datasets.items():
        try:
            gdf = gpd.read_file(path)
            loaded_data[name] = gdf
            print(f"Loaded {name} with {len(gdf)} features")
        except Exception as e:
            print(f"Error loading {name}: {e}")
    return loaded_data

# Basic spatial visualization
def visualize_boundaries(data_dict):
    # Create a figure with multiple subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Plot each dataset
    for i, (name, gdf) in enumerate(data_dict.items()):
        gdf.plot(ax=axes[i], edgecolor='black', alpha=0.7)
        axes[i].set_title(f"{name.replace('_', ' ').title()}")
        axes[i].set_axis_off()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'boundary_comparison.png'), dpi=300)
    plt.close()
    
    # Create a combined visualization
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot in order of largest to smallest for better visibility
    data_dict['commissioner_precincts'].plot(ax=ax, edgecolor='black', alpha=0.5, color='blue')
    data_dict['constable_precincts'].plot(ax=ax, edgecolor='black', alpha=0.5, color='red')
    data_dict['harris_county_zipcodes'].boundary.plot(ax=ax, linewidth=0.5, color='green')
    
    ax.set_title('Combined Boundary Visualization')
    ax.set_axis_off()
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='blue', lw=4, alpha=0.5, label='Commissioner Precincts'),
        Line2D([0], [0], color='red', lw=4, alpha=0.5, label='Constable Precincts'),
        Line2D([0], [0], color='green', lw=2, label='Zipcodes')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'combined_boundaries.png'), dpi=300)
    plt.close()

# Area analysis
def analyze_area_distribution(data_dict):
    # Calculate area in square kilometers for each dataset
    area_stats = {}
    
    for name, gdf in data_dict.items():
        # Create a copy with projected coordinates for accurate area calculation
        gdf_projected = gdf.to_crs(epsg=3857)  # Web Mercator projection
        
        # Calculate area in square kilometers
        gdf_projected['area_sq_km'] = gdf_projected.geometry.area / 10**6
        
        # Store statistics
        area_stats[name] = {
            'min': gdf_projected['area_sq_km'].min(),
            'max': gdf_projected['area_sq_km'].max(),
            'mean': gdf_projected['area_sq_km'].mean(),
            'median': gdf_projected['area_sq_km'].median(),
            'std': gdf_projected['area_sq_km'].std(),
            'total': gdf_projected['area_sq_km'].sum()
        }
        
        # Add the area back to the original dataframe
        data_dict[name]['area_sq_km'] = gdf_projected['area_sq_km']
    
    # Create area distribution visualizations
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for i, (name, gdf) in enumerate(data_dict.items()):
        sns.histplot(gdf['area_sq_km'], ax=axes[i], kde=True)
        axes[i].set_title(f"{name.replace('_', ' ').title()} - Area Distribution")
        axes[i].set_xlabel('Area (sq km)')
        axes[i].set_ylabel('Count')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'area_distribution.png'), dpi=300)
    plt.close()
    
    # Create a comparison bar chart for average areas
    fig, ax = plt.subplots(figsize=(10, 6))
    
    names = [name.replace('_', ' ').title() for name in data_dict.keys()]
    mean_areas = [area_stats[name]['mean'] for name in data_dict.keys()]
    
    sns.barplot(x=names, y=mean_areas, ax=ax)
    ax.set_title('Average Area by Boundary Type')
    ax.set_ylabel('Average Area (sq km)')
    ax.set_xlabel('Boundary Type')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'average_area_comparison.png'), dpi=300)
    plt.close()
    
    # Save area statistics to JSON
    with open(os.path.join(OUTPUT_DIR, 'area_statistics.json'), 'w') as f:
        json.dump(area_stats, f, indent=2)
    
    return area_stats

# Analyze spatial relationships
def analyze_spatial_relationships(data_dict):
    # Create a spatial join between constable precincts and commissioner precincts
    constable_commissioner = gpd.sjoin(
        data_dict['constable_precincts'], 
        data_dict['commissioner_precincts'],
        how="inner", 
        predicate="intersects"
    )
    
    # Count how many constable precincts intersect with each commissioner precinct
    constable_per_commissioner = constable_commissioner.groupby('PCT_NO').size().reset_index(name='constable_count')
    
    # Create a visualization of the relationship
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot commissioner precincts
    data_dict['commissioner_precincts'].plot(
        column='PCT_NO',
        ax=ax,
        alpha=0.5,
        edgecolor='black',
        legend=True,
        cmap='viridis'
    )
    
    # Plot constable precincts
    data_dict['constable_precincts'].plot(
        ax=ax,
        edgecolor='red',
        facecolor='none',
        linewidth=2
    )
    
    # Add labels for constable precincts
    for idx, row in data_dict['constable_precincts'].iterrows():
        centroid = row.geometry.centroid
        ax.text(centroid.x, centroid.y, f"Constable {int(row['PCT_NUM'])}", 
                fontsize=8, ha='center', va='center', 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    ax.set_title('Constable Precincts Overlaid on Commissioner Precincts')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'constable_commissioner_overlay.png'), dpi=300)
    plt.close()
    
    # Create a heatmap of zipcode distribution across constable precincts
    zipcode_constable = gpd.sjoin(
        data_dict['harris_county_zipcodes'], 
        data_dict['constable_precincts'],
        how="inner", 
        predicate="intersects"
    )
    
    # Count zipcodes per constable precinct
    zipcode_counts = zipcode_constable.groupby('PCT_NUM').size().reset_index(name='zipcode_count')
    
    # Create a choropleth map
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Merge the count data back to the constable precincts
    constable_with_counts = data_dict['constable_precincts'].merge(
        zipcode_counts, 
        left_on='PCT_NUM', 
        right_on='PCT_NUM',
        how='left'
    )
    
    # Fill any NaN values with 0
    constable_with_counts['zipcode_count'] = constable_with_counts['zipcode_count'].fillna(0)
    
    # Plot the choropleth without legend_kwds
    constable_with_counts.plot(
        column='zipcode_count',
        ax=ax,
        legend=True,
        cmap='YlOrRd',
        edgecolor='black'
    )
    
    # Add labels for constable precincts
    for idx, row in constable_with_counts.iterrows():
        centroid = row.geometry.centroid
        ax.text(centroid.x, centroid.y, f"Precinct {int(row['PCT_NUM'])}\n({int(row['zipcode_count'])} zipcodes)", 
                fontsize=9, ha='center', va='center', 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    ax.set_title('Number of Zipcodes per Constable Precinct')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'zipcode_distribution_by_constable.png'), dpi=300)
    plt.close()
    
    # Return the relationship data
    return {
        'constable_per_commissioner': constable_per_commissioner.to_dict('records'),
        'zipcode_per_constable': zipcode_counts.to_dict('records')
    }

# Analyze attribute distributions
def analyze_attributes(data_dict):
    # Analyze constable precinct attributes
    if 'constable_precincts' in data_dict:
        constable = data_dict['constable_precincts']
        
        # Create a table of constable information
        constable_info = constable[['PCT_NUM', 'PRECINCT', 'COMMISH', 'CITY', 'PHONE', 'Web']].copy()
        constable_info['area_sq_km'] = constable['area_sq_km']
        
        # Save to CSV
        constable_info.to_csv(os.path.join(OUTPUT_DIR, 'constable_precinct_info.csv'), index=False)
        
        # Create a visualization of constable precincts by area
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort by area
        constable_sorted = constable.sort_values('area_sq_km', ascending=False)
        
        # Create bar chart
        sns.barplot(x='PCT_NUM', y='area_sq_km', data=constable_sorted, ax=ax)
        ax.set_title('Constable Precincts by Area')
        ax.set_xlabel('Precinct Number')
        ax.set_ylabel('Area (sq km)')
        
        # Add data labels
        for i, v in enumerate(constable_sorted['area_sq_km']):
            ax.text(i, v + 5, f"{v:.1f}", ha='center')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'constable_precincts_by_area.png'), dpi=300)
        plt.close()
    
    # Analyze commissioner precinct attributes
    if 'commissioner_precincts' in data_dict:
        commissioner = data_dict['commissioner_precincts']
        
        # Create a table of commissioner information
        commissioner_info = commissioner[['PCT_NO', 'COMMISSION', 'URL']].copy()
        commissioner_info['area_sq_km'] = commissioner['area_sq_km']
        
        # Save to CSV
        commissioner_info.to_csv(os.path.join(OUTPUT_DIR, 'commissioner_precinct_info.csv'), index=False)
        
        # Create a visualization of commissioner precincts
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot with different colors for each precinct
        commissioner.plot(
            column='PCT_NO',
            ax=ax,
            edgecolor='black',
            legend=True,
            cmap='tab10'
        )
        
        # Add labels
        for idx, row in commissioner.iterrows():
            centroid = row.geometry.centroid
            ax.text(centroid.x, centroid.y, 
                    f"Precinct {int(row['PCT_NO'])}\n{row['COMMISSION']}\n{row['area_sq_km']:.1f} sq km", 
                    fontsize=9, ha='center', va='center', 
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        
        ax.set_title('Commissioner Precincts')
        ax.set_axis_off()
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'commissioner_precincts_map.png'), dpi=300)
        plt.close()
    
    # Analyze zipcode attributes
    if 'harris_county_zipcodes' in data_dict:
        zipcodes = data_dict['harris_county_zipcodes']
        
        # Analyze zipcode types
        zipcode_types = zipcodes['ZIP_TYPE'].value_counts().reset_index()
        zipcode_types.columns = ['ZIP_TYPE', 'Count']
        
        # Save to CSV
        zipcode_types.to_csv(os.path.join(OUTPUT_DIR, 'zipcode_types.csv'), index=False)
        
        # Create a pie chart of zipcode types
        fig, ax = plt.subplots(figsize=(10, 8))
        
        ax.pie(zipcode_types['Count'], labels=zipcode_types['ZIP_TYPE'], autopct='%1.1f%%', 
               startangle=90, shadow=True)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        ax.set_title('Distribution of Zipcode Types')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'zipcode_types_pie.png'), dpi=300)
        plt.close()
        
        # Create a simple choropleth of zipcode areas without using scheme
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create a custom colormap for the areas
        vmin = zipcodes['area_sq_km'].min()
        vmax = zipcodes['area_sq_km'].max()
        
        # Simple plot without legend_kwds
        zipcodes.plot(
            column='area_sq_km',
            ax=ax,
            cmap='viridis',
            edgecolor='black',
            linewidth=0.2,
            vmin=vmin,
            vmax=vmax
        )
        
        # Add a colorbar manually
        sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=vmin, vmax=vmax))
        sm._A = []  # Empty array for the data range
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label('Area (sq km)')
        
        ax.set_title('Zipcode Areas')
        ax.set_axis_off()
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'zipcode_areas_map.png'), dpi=300)
        plt.close()

# Main execution
def main():
    print("Starting exploratory data analysis...")
    
    # Load datasets
    data_dict = load_datasets()
    
    # Basic spatial visualization
    print("Creating boundary visualizations...")
    visualize_boundaries(data_dict)
    
    # Area analysis
    print("Analyzing area distributions...")
    area_stats = analyze_area_distribution(data_dict)
    
    # Spatial relationships
    print("Analyzing spatial relationships...")
    relationship_data = analyze_spatial_relationships(data_dict)
    
    # Attribute analysis
    print("Analyzing attribute distributions...")
    analyze_attributes(data_dict)
    
    # Save summary report
    summary = {
        "datasets_analyzed": list(data_dict.keys()),
        "area_statistics": area_stats,
        "spatial_relationships": relationship_data
    }
    
    with open(os.path.join(OUTPUT_DIR, 'eda_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("Exploratory data analysis complete!")
    print(f"Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
