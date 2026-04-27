# Population-genetics-heatmap
This project was developed by Xintian Liu during and after the course **BINP29 at Lund University,** with guidance from Eran Elhaik and Chandrashekar C.R. 

It provides an interactive web-based tool for visualizing population genetics data through heatmaps and animations. The application integrates multiple analysis scripts into a single interface, allowing users to explore genetic distance patterns across space and time.

All genetic distances are calculated relative to Icelandic Vikings (CultureID = 1000).

## Features 
* Generate a single modern genetic heatmap
* Generate multiple ancient genetic heatmaps across time bins
* Create animated heatmaps showing genetic changes over time
* Choose among different modeling algorithms for the animation

## Data
Currently, the tool uses internally provide test datasets for all the genetic distance calculations and geographical information. 

Future versions may support user-uploaded datasets and customized reference populations (alternative CultureIDs)

## Project Structure
The project consists of multiple scripts, where one main script (app.py) coordinates the execution of all others to generate the final outputs.

## Installation
Clone the repository and set up the environment using **uv:** 
```bash
git clone https://github.com/XintianL8347/Population-genetics-heatmap.git

cd Population-genetics-heatmap/
uv sync
```

## Usage 
Run the application with:
```bash
uv run streamlit run Scripts/app.py
```
This will start a local web server and output a URL. Open the URL in your browser ro access the interface. 

## Web Interface
All interactions are performed through the web application.
### Algorithms
Three algorithms can be selected for generating animations: 

* ***3D-RBF:*** Applies a 3D radial basis function (RBF) interpolation across both space and time. This method estimates missing data in time bins with sparse samples.

* ***Site Turnover:*** Assumes that individuals remain at a location until replaced. Each geographic location is assigned a site ID, and the model tracks when new individuals appear at each site over time. 

* ***Linear Migration:*** Assumes active migration. Populations are tracked by CultureID, and individuals are replaced when new individuals with the same CultureID appear in subsequent time bins.

### Parameters
Time range, window size, and step size for the animation can be specified in the web interface via slider and input fields. 

## Notes
This tool was developed for exploratory and educational purposes, so the accuracy wan not the top priority. 