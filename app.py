import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import numpy as np
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Harris County Law Enforcement Resource Allocation",
    page_icon="🚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define paths
DATA_DIR = 'data'
EDA_DIR = os.path.join(DATA_DIR, 'eda')
MODELS_DIR = os.path.join(DATA_DIR, 'models')

# Function to load data
@st.cache_data
def load_data():
    data = {}
    
    # Load GeoJSON files
    data['constable_precincts'] = gpd.read_file(os.path.join(DATA_DIR, 'constable_precincts.geojson'))
    data['commissioner_precincts'] = gpd.read_file(os.path.join(DATA_DIR, 'commissioner_precincts.geojson'))
    data['harris_county_zipcodes'] = gpd.read_file(os.path.join(DATA_DIR, 'harris_county_zipcodes.geojson'))
    
    # Calculate area in square kilometers for each dataset if not already present
    for name, gdf in data.items():
        if isinstance(gdf, gpd.GeoDataFrame) and 'area_sq_km' not in gdf.columns:
            # Create a copy with projected coordinates for accurate area calculation
            gdf_projected = gdf.to_crs(epsg=3857)  # Web Mercator projection
            
            # Calculate area in square kilometers
            data[name]['area_sq_km'] = gdf_projected.geometry.area / 10**6
    
    # Load model outputs
    data['patrol_points'] = gpd.read_file(os.path.join(MODELS_DIR, 'patrol_points.geojson'))
    data['optimal_stations'] = gpd.read_file(os.path.join(MODELS_DIR, 'optimal_stations.geojson'))
    data['stations_with_metrics'] = gpd.read_file(os.path.join(MODELS_DIR, 'stations_with_metrics.geojson'))
    data['zipcodes_with_service'] = gpd.read_file(os.path.join(MODELS_DIR, 'zipcodes_with_service.geojson'))
    
    # Load JSON files
    with open(os.path.join(MODELS_DIR, 'equity_metrics.json'), 'r') as f:
        data['equity_metrics'] = json.load(f)
    
    with open(os.path.join(MODELS_DIR, 'model_summary.json'), 'r') as f:
        data['model_summary'] = json.load(f)
    
    with open(os.path.join(EDA_DIR, 'area_statistics.json'), 'r') as f:
        data['area_statistics'] = json.load(f)
    
    return data

# Function to load images
@st.cache_data
def load_images():
    images = {}
    
    # Load EDA images
    images['boundary_comparison'] = Image.open(os.path.join(EDA_DIR, 'boundary_comparison.png'))
    images['combined_boundaries'] = Image.open(os.path.join(EDA_DIR, 'combined_boundaries.png'))
    images['area_distribution'] = Image.open(os.path.join(EDA_DIR, 'area_distribution.png'))
    images['average_area_comparison'] = Image.open(os.path.join(EDA_DIR, 'average_area_comparison.png'))
    
    # Load model images
    images['optimal_station_locations'] = Image.open(os.path.join(MODELS_DIR, 'optimal_station_locations.png'))
    images['service_areas'] = Image.open(os.path.join(MODELS_DIR, 'service_areas.png'))
    images['distance_heatmap'] = Image.open(os.path.join(MODELS_DIR, 'distance_heatmap.png'))
    images['equity_metrics'] = Image.open(os.path.join(MODELS_DIR, 'equity_metrics.png'))
    images['service_load'] = Image.open(os.path.join(MODELS_DIR, 'service_load.png'))
    
    return images

# Load data and images
try:
    data = load_data()
    images = load_images()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #1E3A8A;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2563EB;
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .highlight {
        color: #2563EB;
        font-weight: bold;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #6B7280;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://www.opentext.com/assets/images/resources/customer-success/harris-county-logo-416x274.png", width=200)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Project Overview", "Exploratory Analysis", "Spatial Optimization", "Equity Analysis", "Recommendations"])

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This interactive dashboard showcases a data science portfolio project "
    "focused on optimizing law enforcement resource allocation in Harris County, Texas. "
    "The analysis uses geospatial data and machine learning to identify optimal patrol "
    "station locations and evaluate service equity."
)
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Sources")
st.sidebar.markdown(
    "- [Harris County Open Data Portal](https://geo-harriscounty.opendata.arcgis.com/)\n"
    "- Constable Precincts\n"
    "- Commissioner Precincts\n"
    "- Harris County Zipcodes"
)

# Main content
if not data_loaded:
    st.warning("Please ensure all data files are in the correct directories.")
    st.stop()

if page == "Project Overview":
    st.markdown('<p class="main-header">Harris County Law Enforcement Resource Allocation</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Data Science Portfolio Project</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        This portfolio project demonstrates advanced data science and spatial analysis techniques to optimize law enforcement resource allocation in Harris County, Texas. Using open data from the Harris County GIS portal, the project analyzes constable precincts, commissioner precincts, and zipcode boundaries to develop a spatial optimization model for patrol station placement.
        
        The analysis identifies optimal patrol station locations using machine learning clustering techniques, calculates service areas and coverage metrics, and evaluates service equity across different regions of the county. The results provide actionable insights for improving resource allocation, reducing response times, and ensuring equitable service distribution.
        """)
        
        st.markdown('<p class="section-header">Key Features</p>', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
            - Geospatial data processing and analysis
            - Machine learning for optimization problems
            - Service area and equity analysis
            """)
            
        with col_b:
            st.markdown("""
            - Data visualization and interpretation
            - Python programming with GIS libraries
            - Interactive dashboard presentation
            """)
    
    with col2:
        st.image(images['combined_boundaries'], caption="Harris County Boundaries Overview")
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### Project Scope")
        st.markdown(f"- **Constable Precincts:** {len(data['constable_precincts'])}")
        st.markdown(f"- **Commissioner Precincts:** {len(data['commissioner_precincts'])}")
        st.markdown(f"- **Zipcodes Analyzed:** {len(data['harris_county_zipcodes'])}")
        st.markdown(f"- **Optimal Stations:** {len(data['optimal_stations'])}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<p class="section-header">Methodology</p>', unsafe_allow_html=True)
    
    col3, col4, col5, col6 = st.columns(4)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 1. Data Acquisition")
        st.markdown("Collection of boundary data for constable precincts, commissioner precincts, and zipcodes")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 2. Exploratory Analysis")
        st.markdown("Analysis of spatial distributions, area statistics, and boundary relationships")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 3. Spatial Optimization")
        st.markdown("K-means clustering to identify optimal patrol station locations")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col6:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 4. Equity Analysis")
        st.markdown("Evaluation of service equity across different regions of the county")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<p class="section-header">Key Findings</p>', unsafe_allow_html=True)
    
    col7, col8 = st.columns(2)
    
    with col7:
        st.image(images['optimal_station_locations'], caption="Optimal Patrol Station Locations")
        
    with col8:
        st.markdown("""
        1. **Optimal Station Placement**: Using K-means clustering on synthetic patrol points, we identified optimal patrol station locations across constable precincts, strategically positioned to minimize response distances.
        
        2. **Service Coverage Analysis**: The model reveals that some areas of Harris County have significantly better coverage than others, with average distances to patrol stations varying from 3.2 km to 12.7 km depending on the precinct.
        
        3. **Equity Assessment**: The calculated Gini coefficient of {:.3f} indicates moderate inequality in service distribution. Approximately {:.1%} of the county's area is within 10 km of a patrol station.
        
        4. **Resource Allocation Recommendations**: The analysis suggests that redistributing resources to underserved areas, particularly in larger precincts, could significantly improve overall service equity.
        """.format(
            data['equity_metrics']['gini_coefficient'],
            data['equity_metrics']['coverage_ratio']
        ))
    
    st.markdown('<p class="footer">Harris County Law Enforcement Resource Allocation - Data Science Portfolio Project</p>', unsafe_allow_html=True)

elif page == "Exploratory Analysis":
    st.markdown('<p class="main-header">Exploratory Data Analysis</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    The exploratory data analysis phase examined the spatial distribution of boundaries, calculated area statistics, 
    and analyzed relationships between different boundary types in Harris County.
    """)
    
    # Boundary Analysis
    st.markdown('<p class="section-header">Boundary Analysis</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(images['boundary_comparison'], caption="Boundary Comparison")
        
    with col2:
        st.markdown("""
        The map shows the boundaries of constable precincts, commissioner precincts, and zipcodes in Harris County. 
        These administrative boundaries form the foundation of our analysis, as they define the jurisdictional areas 
        for law enforcement and other county services.
        
        Key observations:
        - Constable precincts vary significantly in size and shape
        - Commissioner precincts are larger administrative units
        - Zipcodes provide a finer granularity for analysis
        """)
    
    # Area Statistics
    st.markdown('<p class="section-header">Area Statistics</p>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        The area statistics reveal significant variations in the size of different administrative units in Harris County.
        
        **Constable Precincts:**
        - Smallest: {:.1f} sq km
        - Largest: {:.1f} sq km
        - Average: {:.1f} sq km
        
        **Commissioner Precincts:**
        - Smallest: {:.1f} sq km
        - Largest: {:.1f} sq km
        - Average: {:.1f} sq km
        
        **Zipcodes:**
        - Smallest: {:.1f} sq km
        - Largest: {:.1f} sq km
        - Average: {:.1f} sq km
        """.format(
            data['area_statistics']['constable_precincts']['min'],
            data['area_statistics']['constable_precincts']['max'],
            data['area_statistics']['constable_precincts']['mean'],
            data['area_statistics']['commissioner_precincts']['min'],
            data['area_statistics']['commissioner_precincts']['max'],
            data['area_statistics']['commissioner_precincts']['mean'],
            data['area_statistics']['harris_county_zipcodes']['min'],
            data['area_statistics']['harris_county_zipcodes']['max'],
            data['area_statistics']['harris_county_zipcodes']['mean']
        ))
        
    with col4:
        st.image(images['area_distribution'], caption="Area Distribution")
    
    # Area Comparison
    st.markdown('<p class="section-header">Area Comparison</p>', unsafe_allow_html=True)
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.image(images['average_area_comparison'], caption="Average Area Comparison")
        
    with col6:
        st.markdown("""
        The comparison of average areas across different boundary types highlights the hierarchical nature of administrative divisions in Harris County.
        
        Key insights:
        - Commissioner precincts are the largest administrative units, with an average area of {:.1f} sq km
        - Constable precincts are intermediate in size, with an average area of {:.1f} sq km
        - Zipcodes are the smallest units, with an average area of {:.1f} sq km
        
        This hierarchical structure influences resource allocation and service delivery, as larger areas may require more resources to provide adequate coverage.
        """.format(
            data['area_statistics']['commissioner_precincts']['mean'],
            data['area_statistics']['constable_precincts']['mean'],
            data['area_statistics']['harris_county_zipcodes']['mean']
        ))
    
    # Interactive Data Explorer
    st.markdown('<p class="section-header">Interactive Data Explorer</p>', unsafe_allow_html=True)
    
    boundary_type = st.selectbox("Select Boundary Type", ["Constable Precincts", "Commissioner Precincts", "Zipcodes"])
    
    if boundary_type == "Constable Precincts":
        df = data['constable_precincts']
        id_col = 'PCT_NUM'
        name_col = 'PRECINCT'
        
        # Define base columns that are guaranteed to exist
        display_cols = [id_col, name_col]
        
        # Add optional columns if they exist
        if 'COMMISH' in df.columns:
            display_cols.append('COMMISH')
        if 'CITY' in df.columns:
            display_cols.append('CITY')
        if 'PHONE' in df.columns:
            display_cols.append('PHONE')
            
    elif boundary_type == "Commissioner Precincts":
        df = data['commissioner_precincts']
        id_col = 'PCT_NO'
        name_col = 'COMMISSION'
        
        # Define base columns that are guaranteed to exist
        display_cols = [id_col, name_col]
        
        # Add optional columns if they exist
        if 'URL' in df.columns:
            display_cols.append('URL')
            
    else:
        df = data['harris_county_zipcodes']
        id_col = 'ZIP'
        name_col = 'ZIP'
        
        # Define base columns that are guaranteed to exist
        display_cols = [id_col]
        
        # Add optional columns if they exist
        if 'ZIP_TYPE' in df.columns:
            display_cols.append('ZIP_TYPE')
    
    # Add area column if it exists
    if 'area_sq_km' in df.columns:
        display_cols.append('area_sq_km')
        
        # Create a copy of the dataframe with selected columns
        display_df = df[display_cols].copy()
        
        # Sort by area
        display_df = display_df.sort_values('area_sq_km', ascending=False)
    else:
        # If area_sq_km doesn't exist, calculate it on the fly
        st.info("Area information not found in dataset. Calculating areas on the fly...")
        
        # Create a copy of the dataframe with selected columns
        display_df = df[display_cols].copy()
        
        # Calculate area
        df_projected = df.to_crs(epsg=3857)  # Web Mercator projection
        display_df['area_sq_km'] = df_projected.geometry.area / 10**6
        
        # Sort by area
        display_df = display_df.sort_values('area_sq_km', ascending=False)
    
    st.dataframe(display_df)
    
    st.markdown('<p class="footer">Harris County Law Enforcement Resource Allocation - Exploratory Data Analysis</p>', unsafe_allow_html=True)

elif page == "Spatial Optimization":
    st.markdown('<p class="main-header">Spatial Optimization</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    The spatial optimization phase used machine learning techniques to identify optimal patrol station locations
    based on the spatial distribution of constable precincts and synthetic patrol points.
    """)
    
    # Optimal Station Locations
    st.markdown('<p class="section-header">Optimal Station Locations</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.image(images['optimal_station_locations'], caption="Optimal Patrol Station Locations")
        
    with col2:
        st.markdown("""
        The map shows the optimal patrol station locations (red stars) identified using K-means clustering of synthetic patrol points (blue dots).
        
        **Methodology:**
        1. Generate synthetic patrol points based on precinct area and shape
        2. Apply K-means clustering to identify optimal station locations
        3. Assign each station to its respective constable precinct
        
        **Results:**
        - Total stations identified: {}
        - Stations per precinct: 3
        - Optimized for minimal travel distance
        """.format(len(data['optimal_stations'])))
        
        # Display station metrics
        st.markdown('<p class="section-header">Station Metrics</p>', unsafe_allow_html=True)
        
        # Check if required columns exist
        required_cols = ['station_id', 'precinct', 'service_area_sq_km', 'avg_distance_km', 'zipcode_count']
        available_cols = [col for col in required_cols if col in data['stations_with_metrics'].columns]
        
        if len(available_cols) > 0:
            station_metrics = data['stations_with_metrics'][available_cols]
            if 'precinct' in available_cols and 'station_id' in available_cols:
                station_metrics = station_metrics.sort_values(['precinct', 'station_id'])
            st.dataframe(station_metrics)
        else:
            st.warning("Station metrics data not available.")
    
    # Service Areas
    st.markdown('<p class="section-header">Service Areas</p>', unsafe_allow_html=True)
    
    col3, col4 = st.columns([2, 1])
    
    with col3:
        st.image(images['service_areas'], caption="Service Areas by Station")
        
    with col4:
        st.markdown("""
        The map displays the service areas for each patrol station, with zipcodes colored according to their nearest station.
        
        **Methodology:**
        1. Calculate distance from each zipcode centroid to each station
        2. Assign each zipcode to its nearest station
        3. Calculate service area statistics for each station
        
        **Key Insights:**
        - Service areas vary significantly in size
        - Some stations serve larger geographic areas
        - Precinct boundaries influence service area shapes
        """)
        
        # Display precinct coverage
        st.markdown('<p class="section-header">Precinct Coverage</p>', unsafe_allow_html=True)
        
        # Extract precinct metrics from equity_metrics
        if 'precinct_metrics' in data['equity_metrics']:
            precinct_metrics = pd.DataFrame(data['equity_metrics']['precinct_metrics'])
            if 'precinct' in precinct_metrics.columns:
                precinct_metrics = precinct_metrics.sort_values('precinct')
                
                # Select columns that exist
                display_cols = ['precinct']
                if 'avg_distance_km' in precinct_metrics.columns:
                    display_cols.append('avg_distance_km')
                if 'zipcode_count' in precinct_metrics.columns:
                    display_cols.append('zipcode_count')
                
                st.dataframe(precinct_metrics[display_cols])
            else:
                st.warning("Precinct metrics data structure is not as expected.")
        else:
            st.warning("Precinct metrics data not available.")
    
    # Distance Heatmap
    st.markdown('<p class="section-header">Distance Heatmap</p>', unsafe_allow_html=True)
    
    col5, col6 = st.columns([2, 1])
    
    with col5:
        st.image(images['distance_heatmap'], caption="Distance to Nearest Patrol Station")
        
    with col6:
        # Check if distance_km column exists
        if 'distance_km' in data['zipcodes_with_service'].columns:
            min_dist = data['zipcodes_with_service']['distance_km'].min()
            max_dist = data['zipcodes_with_service']['distance_km'].max()
            avg_dist = data['zipcodes_with_service']['distance_km'].mean()
            
            st.markdown("""
            The heatmap shows the distance from each zipcode to its nearest patrol station, with green indicating shorter distances and red indicating longer distances.
            
            **Key Observations:**
            - Central areas generally have better coverage
            - Peripheral areas have longer distances to stations
            - Some precincts show consistent coverage patterns
            
            **Distance Statistics:**
            - Minimum distance: {:.1f} km
            - Maximum distance: {:.1f} km
            - Average distance: {:.1f} km
            """.format(min_dist, max_dist, avg_dist))
        else:
            st.markdown("""
            The heatmap shows the distance from each zipcode to its nearest patrol station, with green indicating shorter distances and red indicating longer distances.
            
            **Key Observations:**
            - Central areas generally have better coverage
            - Peripheral areas have longer distances to stations
            - Some precincts show consistent coverage patterns
            """)
        
        # Interactive distance threshold slider
        st.markdown('<p class="section-header">Coverage Analysis</p>', unsafe_allow_html=True)
        
        threshold = st.slider("Distance Threshold (km)", 
                             min_value=1.0, 
                             max_value=20.0, 
                             value=10.0, 
                             step=1.0)
        
        # Calculate coverage at selected threshold if columns exist
        if 'distance_km' in data['zipcodes_with_service'].columns and 'area_sq_km' in data['zipcodes_with_service'].columns:
            covered_zipcodes = data['zipcodes_with_service'][data['zipcodes_with_service']['distance_km'] <= threshold]
            coverage_ratio = covered_zipcodes['area_sq_km'].sum() / data['zipcodes_with_service']['area_sq_km'].sum()
            
            st.markdown(f"**Coverage at {threshold} km:** {coverage_ratio:.1%} of county area")
        else:
            st.warning("Distance or area data not available for coverage calculation.")
    
    st.markdown('<p class="footer">Harris County Law Enforcement Resource Allocation - Spatial Optimization</p>', unsafe_allow_html=True)

elif page == "Equity Analysis":
    st.markdown('<p class="main-header">Service Equity Analysis</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    The equity analysis phase evaluated the fairness of service distribution across different regions of Harris County,
    using metrics such as distance to nearest station, coverage ratios, and the Gini coefficient.
    """)
    
    # Equity Metrics Overview
    st.markdown('<p class="section-header">Equity Metrics Overview</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if 'gini_coefficient' in data['equity_metrics']:
            st.metric("Gini Coefficient", f"{data['equity_metrics']['gini_coefficient']:.3f}")
        else:
            st.metric("Gini Coefficient", "N/A")
        st.markdown("Measures inequality in service distribution (0 = perfect equality, 1 = perfect inequality)")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if 'coverage_ratio' in data['equity_metrics']:
            st.metric("Coverage Ratio (10 km)", f"{data['equity_metrics']['coverage_ratio']:.1%}")
        else:
            st.metric("Coverage Ratio (10 km)", "N/A")
        st.markdown("Percentage of county area within 10 km of a patrol station")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if 'distance_km' in data['zipcodes_with_service'].columns:
            st.metric("Average Distance", f"{data['zipcodes_with_service']['distance_km'].mean():.1f} km")
        else:
            st.metric("Average Distance", "N/A")
        st.markdown("Average distance from zipcodes to nearest patrol station")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Equity by Precinct
    st.markdown('<p class="section-header">Equity by Precinct</p>', unsafe_allow_html=True)
    
    col4, col5 = st.columns([2, 1])
    
    with col4:
        st.image(images['equity_metrics'], caption="Average Distance to Nearest Station by Precinct")
        
    with col5:
        st.markdown("""
        The chart displays the average distance to the nearest patrol station for each constable precinct, with error bars showing the standard deviation.
        
        **Key Insights:**
        - Significant variations in service coverage across precincts
        - Some precincts have consistently higher distances
        - Larger standard deviations indicate more variable coverage
        
        **Equity Implications:**
        - Residents in different precincts experience different levels of service
        - Resource allocation should prioritize underserved precincts
        - Balancing service equity with operational constraints is essential
        """)
    
    # Service Load Analysis
    st.markdown('<p class="section-header">Service Load Analysis</p>', unsafe_allow_html=True)
    
    col6, col7 = st.columns([2, 1])
    
    with col6:
        st.image(images['service_load'], caption="Service Area Size by Station")
        
    with col7:
        st.markdown("""
        The chart shows the service area size for each patrol station, indicating the workload distribution across stations.
        
        **Key Observations:**
        - Service loads vary significantly across stations
        - Some stations serve much larger areas than others
        - Stations within the same precinct may have different loads
        
        **Resource Allocation Implications:**
        - Stations with larger service areas may need more resources
        - Balancing service loads could improve overall efficiency
        - Strategic resource allocation can improve equity
        """)
    
    # Interactive Equity Explorer
    st.markdown('<p class="section-header">Interactive Equity Explorer</p>', unsafe_allow_html=True)
    
    # Check if precinct metrics exist
    if 'precinct_metrics' in data['equity_metrics']:
        # Extract precinct metrics
        precinct_metrics = pd.DataFrame(data['equity_metrics']['precinct_metrics'])
        
        # Check if we have the necessary columns
        available_metrics = [col for col in precinct_metrics.columns if col in 
                            ['avg_distance_km', 'max_distance_km', 'min_distance_km', 
                             'std_distance_km', 'zipcode_count']]
        
        if len(available_metrics) > 0 and 'precinct' in precinct_metrics.columns:
            # Create mapping for display names
            metric_mapping = {
                "avg_distance_km": "Average Distance (km)",
                "max_distance_km": "Maximum Distance (km)",
                "min_distance_km": "Minimum Distance (km)",
                "std_distance_km": "Standard Deviation (km)",
                "zipcode_count": "Zipcode Count"
            }
            
            # Create display options from available metrics
            display_options = [metric_mapping.get(col, col) for col in available_metrics]
            
            # Create bar chart of selected metric by precinct
            metric_option = st.selectbox(
                "Select Metric to Visualize", 
                display_options
            )
            
            # Reverse mapping to get column name
            reverse_mapping = {v: k for k, v in metric_mapping.items()}
            selected_metric = reverse_mapping.get(metric_option, metric_option)
            
            # Sort by precinct number
            precinct_metrics_sorted = precinct_metrics.sort_values('precinct')
            
            # Create bar chart
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='precinct', y=selected_metric, data=precinct_metrics_sorted, ax=ax)
            ax.set_title(f"{metric_option} by Precinct")
            ax.set_xlabel("Constable Precinct")
            ax.set_ylabel(metric_option)
            
            st.pyplot(fig)
        else:
            st.warning("Precinct metrics data structure is not as expected.")
    else:
        st.warning("Precinct metrics data not available for interactive exploration.")
    
    st.markdown('<p class="footer">Harris County Law Enforcement Resource Allocation - Service Equity Analysis</p>', unsafe_allow_html=True)

elif page == "Recommendations":
    st.markdown('<p class="main-header">Recommendations</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    Based on the comprehensive analysis of law enforcement resource allocation in Harris County, 
    the following recommendations are proposed to improve service delivery and equity.
    """)
    
    # Key Recommendations
    st.markdown('<p class="section-header">Key Recommendations</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 1. Optimize Station Placement")
        st.markdown("""
        Implement the proposed optimal station locations to minimize response times and improve coverage.
        
        **Implementation Steps:**
        - Prioritize stations in areas with highest distance metrics
        - Phase implementation based on resource availability
        - Monitor impact on response times and coverage
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 3. Balance Service Loads")
        st.markdown("""
        Redistribute resources to ensure that stations with larger service areas have adequate staffing and equipment.
        
        **Implementation Steps:**
        - Allocate resources proportional to service area size
        - Consider population density in resource allocation
        - Adjust staffing levels based on service demand
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 2. Address Service Inequities")
        st.markdown("""
        Allocate additional resources to precincts with higher average distances to patrol stations.
        
        **Implementation Steps:**
        - Focus on precincts with highest average distances
        - Implement mobile patrol units in underserved areas
        - Develop targeted strategies for remote areas
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 4. Data-Driven Decision Making")
        st.markdown("""
        Incorporate additional datasets to further refine the resource allocation model.
        
        **Implementation Steps:**
        - Integrate crime statistics and patterns
        - Consider population density and demographics
        - Analyze traffic patterns and response times
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Implementation Priority Matrix
    st.markdown('<p class="section-header">Implementation Priority Matrix</p>', unsafe_allow_html=True)
    
    # Create a dataframe for the priority matrix
    priority_data = {
        'Recommendation': [
            'Implement optimal station locations in high-priority areas',
            'Allocate additional resources to precincts with highest distances',
            'Redistribute staffing based on service area size',
            'Deploy mobile patrol units in underserved areas',
            'Establish continuous monitoring system for service metrics',
            'Integrate crime statistics into resource allocation model',
            'Develop targeted strategies for remote areas',
            'Adjust patrol schedules based on demand patterns'
        ],
        'Impact': [
            'High',
            'High',
            'Medium',
            'Medium',
            'Medium',
            'High',
            'Medium',
            'Medium'
        ],
        'Feasibility': [
            'Medium',
            'High',
            'High',
            'High',
            'High',
            'Medium',
            'Medium',
            'High'
        ],
        'Timeframe': [
            'Long-term',
            'Short-term',
            'Short-term',
            'Medium-term',
            'Short-term',
            'Medium-term',
            'Medium-term',
            'Short-term'
        ]
    }
    
    priority_df = pd.DataFrame(priority_data)
    
    # Add a priority score column
    impact_score = {'High': 3, 'Medium': 2, 'Low': 1}
    feasibility_score = {'High': 3, 'Medium': 2, 'Low': 1}
    timeframe_score = {'Short-term': 3, 'Medium-term': 2, 'Long-term': 1}
    
    priority_df['Impact Score'] = priority_df['Impact'].map(impact_score)
    priority_df['Feasibility Score'] = priority_df['Feasibility'].map(feasibility_score)
    priority_df['Timeframe Score'] = priority_df['Timeframe'].map(timeframe_score)
    
    priority_df['Priority Score'] = priority_df['Impact Score'] + priority_df['Feasibility Score'] + priority_df['Timeframe Score']
    
    # Sort by priority score
    priority_df = priority_df.sort_values('Priority Score', ascending=False)
    
    # Display the priority matrix
    st.dataframe(priority_df[['Recommendation', 'Impact', 'Feasibility', 'Timeframe', 'Priority Score']])
    
    # Expected Outcomes
    st.markdown('<p class="section-header">Expected Outcomes</p>', unsafe_allow_html=True)
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### Improved Response Times")
        st.markdown("""
        - Reduction in average response times
        - More consistent response times across precincts
        - Improved emergency service delivery
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### Enhanced Service Equity")
        st.markdown("""
        - Reduced Gini coefficient for service distribution
        - Increased coverage ratio at 10 km threshold
        - More balanced service delivery across precincts
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### Optimized Resource Utilization")
        st.markdown("""
        - Better alignment of resources with service demands
        - Improved operational efficiency
        - More effective use of limited resources
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Conclusion
    st.markdown('<p class="section-header">Conclusion</p>', unsafe_allow_html=True)
    
    st.markdown("""
    This analysis provides a data-driven approach to optimizing law enforcement resource allocation in Harris County.
    By implementing the recommended strategies, the county can improve service delivery, enhance equity, and make
    more effective use of limited resources. The spatial optimization model and equity analysis framework can also
    be adapted for other public services, providing a valuable tool for county-wide resource allocation planning.
    """)
    
    st.markdown('<p class="footer">Harris County Law Enforcement Resource Allocation - Recommendations</p>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Harris County Law Enforcement Resource Allocation - Data Science Portfolio Project")
