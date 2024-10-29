import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import numpy as np
import pickle
import os

# Set page title
st.title("Singapore Grid Map")

# Initialize state
if 'golden_grids' not in st.session_state:
    st.session_state.golden_grids = set()  # Only need to track gold cells

# Sidebar controls
st.sidebar.header("Grid Settings")
grid_size = 0.6

# Search functionality
st.sidebar.header("Location Search")
search_query = st.sidebar.text_input("Search location in Singapore")
search_button = st.sidebar.button("Search")

# Create base map
m = folium.Map(
    location=[1.3521, 103.8198],  # Singapore center
    zoom_start=12,
    tiles="cartodbpositron"
)

def create_grid(grid_size):
    # Convert grid size from km to degrees (approximate)
    grid_size_deg = grid_size / 111  # 1 degree ≈ 111 km
    
    # Singapore bounds (approximate)
    bounds = {
        'min_lat': 1.15,
        'max_lat': 1.47,
        'min_lon': 103.6,
        'max_lon': 104.0
    }
    
    grid_cells = []
    for lat in np.arange(bounds['min_lat'], bounds['max_lat'], grid_size_deg):
        for lon in np.arange(bounds['min_lon'], bounds['max_lon'], grid_size_deg):
            cell_id = f"{lat:.4f}_{lon:.4f}"
            grid_cells.append((cell_id, lat, lon))
    
    return grid_cells, bounds

# Create grid cells and get bounds
grid_cells, bounds = create_grid(grid_size)

# Range selection inputs
st.header("Select Range to Mark as Gold")
st.write("First Corner:")
col1, col2 = st.columns(2)
with col1:
    start_lat = st.number_input("Start Latitude", 
                               min_value=bounds['min_lat'],
                               max_value=bounds['max_lat'],
                               value=1.3521,
                               format="%.4f",
                               key="start_lat")
with col2:
    start_lon = st.number_input("Start Longitude", 
                               min_value=bounds['min_lon'],
                               max_value=bounds['max_lon'],
                               value=103.8198,
                               format="%.4f",
                               key="start_lon")

st.write("Second Corner:")
col1, col2 = st.columns(2)
with col1:
    end_lat = st.number_input("End Latitude", 
                             min_value=bounds['min_lat'],
                             max_value=bounds['max_lat'],
                             value=1.3621,
                             format="%.4f",
                             key="end_lat")
with col2:
    end_lon = st.number_input("End Longitude", 
                             min_value=bounds['min_lon'],
                             max_value=bounds['max_lon'],
                             value=103.8298,
                             format="%.4f",
                             key="end_lon")

# Function to find the nearest grid cell
def find_nearest_grid(lat, lon, grid_size):
    grid_size_deg = grid_size / 111
    # Find the nearest grid starting point
    nearest_lat = np.floor((lat - bounds['min_lat']) / grid_size_deg) * grid_size_deg + bounds['min_lat']
    nearest_lon = np.floor((lon - bounds['min_lon']) / grid_size_deg) * grid_size_deg + bounds['min_lon']
    return f"{nearest_lat:.4f}_{nearest_lon:.4f}"

# Function to get all grid cells in a range
def get_grid_cells_in_range(start_lat, start_lon, end_lat, end_lon, grid_size):
    grid_size_deg = grid_size / 111
    
    # Ensure correct order of coordinates
    min_lat = min(start_lat, end_lat)
    max_lat = max(start_lat, end_lat)
    min_lon = min(start_lon, end_lon)
    max_lon = max(start_lon, end_lon)
    
    cells = set()
    current_lat = min_lat
    while current_lat <= max_lat:
        current_lon = min_lon
        while current_lon <= max_lon:
            cell_id = find_nearest_grid(current_lat, current_lon, grid_size)
            cells.add(cell_id)
            current_lon += grid_size_deg
        current_lat += grid_size_deg
    return cells

# Buttons to mark range as gold or blue
col1, col2 = st.columns(2)
with col1:
    if st.button("Mark Range as Gold"):
        range_cells = get_grid_cells_in_range(start_lat, start_lon, end_lat, end_lon, grid_size)
        st.session_state.golden_grids.update(range_cells)
        st.success(f"Marked {len(range_cells)} cells as gold")

with col2:
    if st.button("Mark Range as Blue"):
        range_cells = get_grid_cells_in_range(start_lat, start_lon, end_lat, end_lon, grid_size)
        st.session_state.golden_grids.difference_update(range_cells)
        st.success(f"Marked {len(range_cells)} cells as blue")

# Draw grid cells on map
grid_size_deg = grid_size / 111
for cell_id, lat, lon in grid_cells:
    # Set color - gold if in golden_grids, blue otherwise
    fill_color = 'gold' if cell_id in st.session_state.golden_grids else 'blue'
    
    # Create rectangle for each grid cell
    folium.Rectangle(
        bounds=[[lat, lon], [lat + grid_size_deg, lon + grid_size_deg]],
        color="black",
        weight=1,
        fill=True,
        fill_color=fill_color,
        fill_opacity=0.3,
        popup=f"Coordinates: ({lat:.4f}, {lon:.4f})"
    ).add_to(m)

# Handle location search
if search_button and search_query:
    geolocator = Nominatim(user_agent="singapore_map_app")
    try:
        location = geolocator.geocode(f"{search_query}, Singapore")
        if location:
            folium.Marker(
                [location.latitude, location.longitude],
                popup=location.address,
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            m.location = [location.latitude, location.longitude]
            m.zoom_start = 15
        else:
            st.error("Location not found in Singapore")
    except Exception as e:
        st.error(f"Error searching location: {str(e)}")

# Display map
folium_static(m)

# Save and load functionality
col1, col2 = st.columns(2)

with col1:
    if st.button("Save Gold Markers"):
        try:
            with open('golden_grids.pkl', 'wb') as f:
                pickle.dump(st.session_state.golden_grids, f)
            st.success("Gold markers saved successfully!")
        except Exception as e:
            st.error(f"Error saving: {str(e)}")

with col2:
    if st.button("Load Saved Markers"):
        try:
            if os.path.exists('golden_grids.pkl'):
                with open('golden_grids.pkl', 'rb') as f:
                    st.session_state.golden_grids = pickle.load(f)
                st.success("Gold markers loaded successfully!")
                st.experimental_rerun()
            else:
                st.warning("No saved data found!")
        except Exception as e:
            st.error(f"Error loading: {str(e)}")

# Clear button
if st.button("Clear All Gold Markers"):
    st.session_state.golden_grids = set()
    st.experimental_rerun()

# Display currently golden grids
st.write("Current gold markers:")
for grid_id in st.session_state.golden_grids:
    lat, lon = grid_id.split('_')
    st.write(f"Grid at ({lat}, {lon})")