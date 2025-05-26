# Harris County Law Enforcement Resource Allocation Project

## Project Overview

This repository contains a comprehensive data science portfolio project focused on optimizing law enforcement resource allocation in Harris County, Texas. The project uses open data from the Harris County GIS portal to analyze constable precincts, commissioner precincts, and zipcode boundaries, developing a spatial optimization model for patrol station placement.

## Project Structure

```
harris_county_project/
├── data/                      # Data directory
│   ├── constable_precincts.geojson       # Constable precincts boundary data
│   ├── commissioner_precincts.geojson    # Commissioner precincts boundary data
│   ├── harris_county_zipcodes.geojson    # Zipcode boundary data
│   ├── assessment/            # Data quality assessment outputs
│   ├── eda/                   # Exploratory data analysis outputs
│   └── models/                # Modeling outputs and visualizations
├── scripts/                   # Python scripts
│   ├── data_quality_assessment.py        # Script for data quality assessment
│   ├── exploratory_data_analysis.py      # Script for exploratory data analysis
│   └── modeling.py                       # Script for spatial optimization modeling
├── project_report.md          # Comprehensive project report
├── project_definition.md      # Project definition and objectives
├── data_acquisition_summary.md # Summary of data acquisition process
├── README.md                  # Project overview and instructions
└── todo.md                    # Project task checklist
```

## Key Features

- **Geospatial Data Analysis**: Processing and analysis of boundary data for constable precincts, commissioner precincts, and zipcodes
- **Spatial Optimization**: K-means clustering to identify optimal patrol station locations
- **Service Area Analysis**: Calculation of service areas and coverage metrics
- **Equity Assessment**: Evaluation of service equity across different regions of the county
- **Data Visualization**: Comprehensive visualizations of spatial relationships and model results

## Technical Implementation

This project was implemented using Python with the following key libraries:
- GeoPandas for geospatial data processing
- Scikit-learn for K-means clustering
- Matplotlib and Seaborn for visualization
- NumPy and Pandas for data manipulation

## Key Findings

1. **Optimal Station Placement**: Identified 24 optimal patrol station locations across 8 constable precincts
2. **Service Coverage Analysis**: Revealed significant variations in coverage across different areas
3. **Equity Assessment**: Calculated a Gini coefficient of 0.412, indicating moderate inequality in service distribution
4. **Resource Allocation Recommendations**: Suggested redistribution of resources to improve overall service equity

## Getting Started

### Prerequisites

- Python 3.8+
- Required packages: geopandas, matplotlib, seaborn, scikit-learn, numpy, pandas

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/harris-county-resource-allocation.git
cd harris-county-resource-allocation

# Install required packages
pip install -r requirements.txt
```

### Running the Analysis

```bash
# Run data quality assessment
python scripts/data_quality_assessment.py

# Run exploratory data analysis
python scripts/exploratory_data_analysis.py

# Run spatial optimization modeling
python scripts/modeling.py
```

## Results and Visualizations

The project generates various visualizations and outputs, including:

- Optimal patrol station locations
- Service areas by station
- Distance heatmaps
- Service equity metrics by precinct
- Service load distribution

All visualizations are saved in the `data/models/` directory.

## Project Report

For a comprehensive overview of the project, methodology, findings, and recommendations, please see the [Project Report](project_report.md).

## Data Sources

- Harris County Open Data Portal: https://geo-harriscounty.opendata.arcgis.com/
- Constable Precincts data: https://geo-harriscounty.opendata.arcgis.com/datasets/harriscountygis::constable-precincts/about
- Commissioner Precincts data: https://geo-harriscounty.opendata.arcgis.com/datasets/harriscountygis::commissioner-precincts/about
- Harris County Zipcodes data: https://geo-harriscounty.opendata.arcgis.com/datasets/ead5b50792da443da759f1dd073e49c5_0/explore

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Harris County GIS for providing open data
- The open-source community for the tools and libraries used in this project
