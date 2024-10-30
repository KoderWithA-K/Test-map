import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import numpy as np
import pickle
import os

# Initialize session state for grid colors
if 'grid_colors' not in st.session_state:
    st.session_state.grid_colors = {}

# Set page title
st.title("Singapore Interactive Grid Map")

# Sidebar controls
st.sidebar.header("Grid Settings")
grid_size = 0.6
color_option = st.sidebar.selectbox("Select Color", ["blue", "gold"])

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
            grid_id = f"{lat:.4f}_{lon:.4f}"
            grid_cells.append({
                'id': grid_id,
                'bounds': [[lat, lon], [lat + grid_size_deg, lon + grid_size_deg]]
            })
            # Initialize grid color to blue
            if grid_id not in st.session_state.grid_colors:
                st.session_state.grid_colors[grid_id] = 'blue'
    
    return grid_cells

# Create grid cells
grid_cells = create_grid(grid_size)

# Set specific grid cells to gold
gold_grids = [
    "1.2689_103.8216", "1.2689_103.8162", "1.2689_103.8108", "1.2689_103.8054", "1.2689_103.8000",
    "1.2743_103.8000", "1.2743_103.8054", "1.2743_103.8108", "1.2743_103.8162", "1.2797_103.8054",
    "1.2797_103.8000", "1.2797_103.7946", "1.2797_103.7892", "1.2797_103.7838", "1.2851_103.7838",
    "1.2851_103.7784", "1.2851_103.7892", "1.2851_103.8108", "1.2905_103.8108", "1.2959_103.8054",
    "1.2959_103.8000", "1.2743_103.8486", "1.2797_103.8486", "1.2797_103.8432", "1.2797_103.8378", "1.2797_103.8486", "1.2797_103.8541", "1.2797_103.8595",
    "1.2743_103.8595", "1.2797_103.8703", "1.2797_103.8649", "1.2851_103.8541", "1.2851_103.8595", "1.2905_103.8541", "1.2905_103.8595", "1.2905_103.8649", "1.2905_103.8703", "1.2851_103.8703", "1.2851_103.8432", "1.2851_103.8378", "1.2905_103.8432", "1.2959_103.8432",
    "1.2959_103.8378", "1.2959_103.8324", "1.2905_103.8324", "1.2959_103.8270", "1.2905_103.8270", "1.2959_103.8703", "1.2959_103.8757", "1.2959_103.8811", "1.2959_103.8865", "1.2959_103.8919", "1.3014_103.8919", "1.3014_103.8973", "1.3014_103.8865", "1.3014_103.8811",
    "1.3014_103.8486", "1.3014_103.8595", "1.3014_103.8649", "1.3014_103.8703", "1.3068_103.8757", "1.3068_103.8703", "1.3068_103.8649", "1.3068_103.8595", "1.3068_103.8541", "1.3068_103.8486", "1.3068_103.8432", "1.3122_103.8757", "1.3176_103.8757", "1.3230_103.8757",
    "1.3068_103.8919", "1.3122_103.8865", "1.3122_103.8919", "1.3122_103.8973", "1.3122_103.9027", "1.3176_103.9027", "1.3176_103.8973", "1.3176_103.8919", "1.2959_103.9027", "1.2959_103.9081", "1.3014_103.9135", "1.3068_103.9189", "1.3068_103.9135", "1.3068_103.9081", "1.3068_103.9027", "1.3122_103.9189",
    



]

for grid_id in gold_grids:
    st.session_state.grid_colors[grid_id] = 'gold'

# Create select box for grid cell selection
grid_ids = [cell['id'] for cell in grid_cells]
selected_grid = st.selectbox("Select grid cell to color", grid_ids)

# Button to apply color
if st.button(f"Color selected grid {color_option}"):
    st.session_state.grid_colors[selected_grid] = color_option
    st.experimental_rerun()

# Draw grid cells on map
for cell in grid_cells:
    fill_color = st.session_state.grid_colors.get(cell['id'], 'transparent')
    folium.Rectangle(
        bounds=cell['bounds'],
        color="black",
        weight=1,
        fill=True,
        fill_color=fill_color,
        fill_opacity=0.3,
        popup=f"Grid ID: {cell['id']}"
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

# Save/Load/Clear buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Save Grid Colors"):
        try:
            with open('grid_colors.pkl', 'wb') as f:
                pickle.dump(st.session_state.grid_colors, f)
            st.success("Grid colors saved successfully!")
        except Exception as e:
            st.error(f"Error saving grid colors: {str(e)}")

with col2:
    if st.button("Load Saved Grid Colors"):
        try:
            if os.path.exists('grid_colors.pkl'):
                with open('grid_colors.pkl', 'rb') as f:
                    st.session_state.grid_colors = pickle.load(f)
                st.success("Grid colors loaded successfully!")
                st.experimental_rerun()
            else:
                st.warning("No saved grid colors found!")
        except Exception as e:
            st.error(f"Error loading grid colors: {str(e)}")

with col3:
    if st.button("Clear All Colors"):
        st.session_state.grid_colors = {}
        st.experimental_rerun()
