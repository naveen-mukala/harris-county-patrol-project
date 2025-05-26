#!/usr/bin/env python3
"""
Modeling Script for Harris County Law Enforcement Resource Allocation Project

This script builds predictive and analytical models for the Harris County Law Enforcement 
Resource Allocation and Service Equity Analysis project.

The modeling includes:
1. Spatial optimization for resource allocation
2. Service area analysis
3. Equity assessment metrics
4. Visualization of model outputs

Author: Naveen Mukala
Date: May 26, 2025
"""

import os
import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from shapely.geometry import Point, LineString
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import random

# Set paths
DATA_DIR = '/home/ubuntu/harris_county_project/data'
EDA_DIR = '/home/ubuntu/harris_county_project/data/eda'
OUTPUT_DIR = '/home/ubuntu/harris_county_project/data/models'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load datasets
def load_datasets():
    datasets = {
        'constable_precincts': os.path.join(DATA_DIR, 'constable_precincts.geojson'),
        'commissioner_precincts': os.path.join(DATA_DIR, 'commissioner_precincts.geojson'),
        'harris_county_zipcodes': os.path.join(DATA_DIR, 'harris_county_zipcodes.geojson')
    }
    
    loaded_data = {}
    for name, path in datasets.items():
        try:
            gdf = gpd.read_file(path)
            loaded_data[name] = gdf
            print(f"Loaded {name} with {len(gdf)} features")
        except Exception as e:
            print(f"Error loading {name}: {e}")
    
    # Load EDA results
    try:
        with open(os.path.join(EDA_DIR, 'eda_summary.json'), 'r') as f:
            eda_summary = json.load(f)
        loaded_data['eda_summary'] = eda_summary
        print("Loaded EDA summary")
    except Exception as e:
        print(f"Error loading EDA summary: {e}")
    
    return loaded_data

# Calculate area in square kilometers for each dataset if not already present
def calculate_areas(data_dict):
    """
    Calculate area in square kilometers for each dataset if not already present
    """
    for name, gdf in data_dict.items():
        if isinstance(gdf, gpd.GeoDataFrame) and 'area_sq_km' not in gdf.columns:
            print(f"Calculating area for {name}...")
            # Create a copy with projected coordinates for accurate area calculation
            gdf_projected = gdf.to_crs(epsg=3857)  # Web Mercator projection
            
            # Calculate area in square kilometers
            data_dict[name]['area_sq_km'] = gdf_projected.geometry.area / 10**6
    
    return data_dict

# Generate synthetic patrol points for modeling
def generate_patrol_points(constable_precincts, num_points=100):
    """
    Generate synthetic patrol points for each constable precinct
    based on precinct area and shape.
    """
    all_points = []
    
    for idx, precinct in constable_precincts.iterrows():
        # Calculate number of points proportional to area
        area_proportion = precinct['area_sq_km'] / constable_precincts['area_sq_km'].sum()
        precinct_points = max(5, int(num_points * area_proportion))
        
        # Generate random points within the precinct boundary
        minx, miny, maxx, maxy = precinct.geometry.bounds
        points = []
        
        while len(points) < precinct_points:
            x = random.uniform(minx, maxx)
            y = random.uniform(miny, maxy)
            point = Point(x, y)
            
            if precinct.geometry.contains(point):
                points.append({
                    'geometry': point,
                    'precinct': int(precinct['PCT_NUM']),
                    'patrol_id': f"P{int(precinct['PCT_NUM'])}_{len(points) + 1}"
                })
        
        all_points.extend(points)
    
    # Create GeoDataFrame from points
    patrol_points = gpd.GeoDataFrame(all_points, crs=constable_precincts.crs)
    
    return patrol_points

# Perform K-means clustering for optimal patrol station locations
def optimize_patrol_stations(patrol_points, constable_precincts, num_stations_per_precinct=3):
    """
    Use K-means clustering to identify optimal patrol station locations
    within each constable precinct.
    """
    optimal_stations = []
    
    for precinct_num in constable_precincts['PCT_NUM'].unique():
        # Filter points for this precinct
        precinct_points = patrol_points[patrol_points['precinct'] == precinct_num]
        
        if len(precinct_points) < num_stations_per_precinct:
            print(f"Not enough points in Precinct {precinct_num} for clustering")
            continue
        
        # Extract coordinates for clustering
        coords = np.array([(p.x, p.y) for p in precinct_points.geometry])
        
        # Scale coordinates for better clustering
        scaler = StandardScaler()
        coords_scaled = scaler.fit_transform(coords)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=num_stations_per_precinct, random_state=42)
        clusters = kmeans.fit_predict(coords_scaled)
        
        # Get cluster centers and transform back to original scale
        centers_scaled = kmeans.cluster_centers_
        centers = scaler.inverse_transform(centers_scaled)
        
        # Create station points
        for i, center in enumerate(centers):
            optimal_stations.append({
                'geometry': Point(center),
                'precinct': int(precinct_num),
                'station_id': f"S{int(precinct_num)}_{i + 1}",
                'cluster_size': np.sum(clusters == i)
            })
    
    # Create GeoDataFrame from optimal stations
    stations_gdf = gpd.GeoDataFrame(optimal_stations, crs=constable_precincts.crs)
    
    return stations_gdf

# Calculate service areas and coverage metrics
def analyze_service_coverage(patrol_stations, constable_precincts, zipcodes):
    """
    Analyze service coverage by calculating distances and service areas
    for each patrol station.
    """
    # Create Voronoi-like service areas by assigning each zipcode to nearest station
    zipcode_centroids = zipcodes.copy()
    
    # Use to_crs to project to a projected CRS before calculating centroids
    zipcode_centroids_projected = zipcode_centroids.to_crs(epsg=3857)  # Web Mercator projection
    zipcode_centroids['centroid'] = zipcode_centroids_projected.geometry.centroid
    zipcode_centroids = zipcode_centroids.set_geometry('centroid')
    
    # Project patrol stations to the same CRS for distance calculations
    patrol_stations_projected = patrol_stations.to_crs(epsg=3857)
    
    # Calculate distances from each zipcode centroid to each station
    distances = {}
    assignments = {}
    station_precincts = {}
    
    # Create a mapping of station_id to precinct
    for _, station in patrol_stations.iterrows():
        station_precincts[station['station_id']] = station['precinct']
    
    for idx, zipcode in zipcode_centroids.iterrows():
        min_dist = float('inf')
        nearest_station = None
        
        for _, station in patrol_stations_projected.iterrows():
            dist = zipcode.centroid.distance(station.geometry)
            
            if dist < min_dist:
                min_dist = dist
                nearest_station = station['station_id']
        
        # Convert distance to kilometers
        min_dist_km = min_dist / 1000  # Convert meters to kilometers
        
        distances[zipcode['ZIP']] = min_dist_km
        assignments[zipcode['ZIP']] = nearest_station
    
    # Add distance and assignment information to zipcodes
    zipcodes['nearest_station'] = zipcodes['ZIP'].map(assignments)
    zipcodes['distance_km'] = zipcodes['ZIP'].map(distances)
    
    # Add precinct information based on the assigned station
    zipcodes['precinct'] = zipcodes['nearest_station'].map(station_precincts)
    
    # Calculate service area statistics
    service_areas = zipcodes.groupby('nearest_station').agg({
        'area_sq_km': 'sum',
        'distance_km': 'mean',
        'ZIP': 'count'
    }).reset_index()
    
    service_areas.columns = ['station_id', 'service_area_sq_km', 'avg_distance_km', 'zipcode_count']
    
    # Merge service area info back to stations
    patrol_stations = patrol_stations.merge(
        service_areas, 
        left_on='station_id', 
        right_on='station_id',
        how='left'
    )
    
    # Fill any NaN values
    patrol_stations['service_area_sq_km'] = patrol_stations['service_area_sq_km'].fillna(0)
    patrol_stations['avg_distance_km'] = patrol_stations['avg_distance_km'].fillna(0)
    patrol_stations['zipcode_count'] = patrol_stations['zipcode_count'].fillna(0)
    
    return patrol_stations, zipcodes

# Calculate equity metrics
def calculate_equity_metrics(zipcodes, patrol_stations, constable_precincts):
    """
    Calculate equity metrics to assess service distribution fairness.
    """
    # Calculate average distance by precinct
    precinct_avg_distance = zipcodes.groupby('precinct').agg({
        'distance_km': ['mean', 'max', 'min', 'std'],
        'ZIP': 'count'
    }).reset_index()
    
    # Flatten the multi-level column names
    precinct_avg_distance.columns = [
        'precinct', 'avg_distance_km', 'max_distance_km', 
        'min_distance_km', 'std_distance_km', 'zipcode_count'
    ]
    
    # Calculate Gini-like coefficient for service equity
    distances = np.array(zipcodes['distance_km'])
    distances = distances[~np.isnan(distances)]  # Remove NaN values
    distances = np.sort(distances)
    
    n = len(distances)
    index = np.arange(1, n + 1)
    gini = (np.sum((2 * index - n - 1) * distances)) / (n * np.sum(distances))
    
    # Calculate coverage ratio (% of area within X km of a station)
    threshold_distance = 10  # km
    covered_zipcodes = zipcodes[zipcodes['distance_km'] <= threshold_distance]
    coverage_ratio = covered_zipcodes['area_sq_km'].sum() / zipcodes['area_sq_km'].sum()
    
    # Compile equity metrics
    equity_metrics = {
        'gini_coefficient': float(gini),
        'coverage_ratio': float(coverage_ratio),
        'threshold_distance_km': threshold_distance,
        'precinct_metrics': precinct_avg_distance.to_dict('records')
    }
    
    return equity_metrics

# Visualize model results
def visualize_model_results(constable_precincts, patrol_points, patrol_stations, zipcodes, equity_metrics):
    """
    Create visualizations of the modeling results.
    """
    # 1. Patrol points and optimal station locations
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot precincts
    constable_precincts.plot(
        ax=ax,
        edgecolor='black',
        alpha=0.5,
        column='PCT_NUM',
        cmap='tab10'
    )
    
    # Plot patrol points
    patrol_points.plot(
        ax=ax,
        color='blue',
        markersize=10,
        alpha=0.5
    )
    
    # Plot optimal stations
    patrol_stations.plot(
        ax=ax,
        color='red',
        markersize=50,
        marker='*',
        edgecolor='black'
    )
    
    # Add station labels
    for idx, station in patrol_stations.iterrows():
        ax.text(
            station.geometry.x, 
            station.geometry.y, 
            station['station_id'],
            fontsize=8,
            ha='center',
            va='center',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
        )
    
    ax.set_title('Optimal Patrol Station Locations')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'optimal_station_locations.png'), dpi=300)
    plt.close()
    
    # 2. Service area map
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create a colormap for service areas
    station_ids = zipcodes['nearest_station'].unique()
    n_stations = len(station_ids)
    cmap = plt.cm.get_cmap('tab20', n_stations)
    
    # Create a color dictionary
    color_dict = {station_id: mcolors.rgb2hex(cmap(i)) 
                 for i, station_id in enumerate(station_ids)}
    
    # Plot zipcodes colored by nearest station
    for station_id in station_ids:
        station_zipcodes = zipcodes[zipcodes['nearest_station'] == station_id]
        station_zipcodes.plot(
            ax=ax,
            color=color_dict[station_id],
            edgecolor='black',
            linewidth=0.2,
            alpha=0.7
        )
    
    # Plot constable precinct boundaries
    constable_precincts.boundary.plot(
        ax=ax,
        color='black',
        linewidth=1.5
    )
    
    # Plot stations
    patrol_stations.plot(
        ax=ax,
        color='red',
        markersize=50,
        marker='*',
        edgecolor='black'
    )
    
    # Add station labels
    for idx, station in patrol_stations.iterrows():
        ax.text(
            station.geometry.x, 
            station.geometry.y, 
            station['station_id'],
            fontsize=8,
            ha='center',
            va='center',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
        )
    
    ax.set_title('Service Areas by Nearest Station')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'service_areas.png'), dpi=300)
    plt.close()
    
    # 3. Distance heatmap
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create a custom colormap for distances
    distance_cmap = LinearSegmentedColormap.from_list(
        'distance_cmap', 
        ['green', 'yellow', 'red']
    )
    
    # Plot zipcodes colored by distance to nearest station
    zipcodes.plot(
        column='distance_km',
        ax=ax,
        cmap=distance_cmap,
        edgecolor='black',
        linewidth=0.2,
        alpha=0.7,
        legend=True
    )
    
    # Plot constable precinct boundaries
    constable_precincts.boundary.plot(
        ax=ax,
        color='black',
        linewidth=1.5
    )
    
    # Plot stations
    patrol_stations.plot(
        ax=ax,
        color='blue',
        markersize=50,
        marker='*',
        edgecolor='black'
    )
    
    ax.set_title('Distance to Nearest Patrol Station (km)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'distance_heatmap.png'), dpi=300)
    plt.close()
    
    # 4. Equity metrics visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    
    precinct_metrics = pd.DataFrame(equity_metrics['precinct_metrics'])
    
    # Sort by precinct number
    precinct_metrics = precinct_metrics.sort_values('precinct')
    
    # Create bar chart of average distances by precinct
    sns.barplot(
        x='precinct',
        y='avg_distance_km',
        data=precinct_metrics,
        ax=ax
    )
    
    # Add error bars for standard deviation
    for i, row in enumerate(precinct_metrics.itertuples()):
        ax.errorbar(
            i, 
            row.avg_distance_km, 
            yerr=row.std_distance_km,
            fmt='none', 
            color='black', 
            capsize=5
        )
    
    ax.set_title('Average Distance to Nearest Station by Precinct')
    ax.set_xlabel('Constable Precinct')
    ax.set_ylabel('Average Distance (km)')
    
    # Add text with equity metrics
    fig.text(
        0.5, 
        0.01, 
        f"Gini Coefficient: {equity_metrics['gini_coefficient']:.3f} | " +
        f"Coverage Ratio ({equity_metrics['threshold_distance_km']} km): {equity_metrics['coverage_ratio']:.1%}",
        ha='center',
        fontsize=12
    )
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(os.path.join(OUTPUT_DIR, 'equity_metrics.png'), dpi=300)
    plt.close()
    
    # 5. Service load visualization
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sort stations by precinct and ID
    patrol_stations_sorted = patrol_stations.sort_values(['precinct', 'station_id'])
    
    # Create bar chart of service areas
    sns.barplot(
        x='station_id',
        y='service_area_sq_km',
        data=patrol_stations_sorted,
        ax=ax
    )
    
    ax.set_title('Service Area Size by Station')
    ax.set_xlabel('Station ID')
    ax.set_ylabel('Service Area (sq km)')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'service_load.png'), dpi=300)
    plt.close()

# Main execution
def main():
    print("Starting modeling for Law Enforcement Resource Allocation...")
    
    # Load datasets
    data_dict = load_datasets()
    
    # Calculate areas if not already present
    data_dict = calculate_areas(data_dict)
    
    # Generate synthetic patrol points
    print("Generating synthetic patrol points...")
    patrol_points = generate_patrol_points(data_dict['constable_precincts'], num_points=200)
    
    # Save patrol points
    patrol_points.to_file(os.path.join(OUTPUT_DIR, 'patrol_points.geojson'), driver='GeoJSON')
    
    # Optimize patrol station locations
    print("Optimizing patrol station locations...")
    patrol_stations = optimize_patrol_stations(
        patrol_points, 
        data_dict['constable_precincts'],
        num_stations_per_precinct=3
    )
    
    # Save optimal stations
    patrol_stations.to_file(os.path.join(OUTPUT_DIR, 'optimal_stations.geojson'), driver='GeoJSON')
    
    # Analyze service coverage
    print("Analyzing service coverage...")
    patrol_stations, zipcodes_with_service = analyze_service_coverage(
        patrol_stations,
        data_dict['constable_precincts'],
        data_dict['harris_county_zipcodes']
    )
    
    # Save service coverage results
    patrol_stations.to_file(os.path.join(OUTPUT_DIR, 'stations_with_metrics.geojson'), driver='GeoJSON')
    zipcodes_with_service.to_file(os.path.join(OUTPUT_DIR, 'zipcodes_with_service.geojson'), driver='GeoJSON')
    
    # Calculate equity metrics
    print("Calculating equity metrics...")
    equity_metrics = calculate_equity_metrics(
        zipcodes_with_service,
        patrol_stations,
        data_dict['constable_precincts']
    )
    
    # Save equity metrics
    with open(os.path.join(OUTPUT_DIR, 'equity_metrics.json'), 'w') as f:
        json.dump(equity_metrics, f, indent=2)
    
    # Visualize results
    print("Visualizing model results...")
    visualize_model_results(
        data_dict['constable_precincts'],
        patrol_points,
        patrol_stations,
        zipcodes_with_service,
        equity_metrics
    )
    
    # Create summary report
    model_summary = {
        "model_type": "Spatial Optimization and Service Equity Analysis",
        "input_datasets": list(data_dict.keys()),
        "synthetic_points_generated": len(patrol_points),
        "optimal_stations_identified": len(patrol_stations),
        "equity_metrics": equity_metrics,
        "service_coverage": {
            "total_area_covered_sq_km": float(patrol_stations['service_area_sq_km'].sum()),
            "average_distance_km": float(zipcodes_with_service['distance_km'].mean()),
            "max_distance_km": float(zipcodes_with_service['distance_km'].max())
        }
    }
    
    with open(os.path.join(OUTPUT_DIR, 'model_summary.json'), 'w') as f:
        json.dump(model_summary, f, indent=2)
    
    print("Modeling complete!")
    print(f"Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
