import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import numpy as np
import pickle
import os
import pandas as pd

# Create the data
data = {
    "S/N": ["DH1", "DH2", "DH3", "DH4", "DH5", "DH6", "DH7", "DH8", "DH9", "DH10", 
            "DH11", "DH12", "DH13", "DH14", "DH15", "DH16", "DH17", "DH18", "DH19", "DH20", 
            "DH21", "DH22", "DH23", "DH24", "DH25", "DH26", "DH27", "DH28", "DH29", "DH30", 
            "DH31", "DH32", "DH33", "DH34", "DH35", "DH36", "DH37", "DH38", "DH39", "DH40", 
            "DH41", "DH42", "DH43", "DH44", "DH45", "DH46", "DH47", "DH48", "DH49", "DH50", 
            "DH51", "DH52", "DH53", "DH54", "DH55", "DH56", "DH57", "DH58"],
    "Hint": ["There is something fading away near the coin's hiding spot.",
             "If you see something stopping, you may be less than 300m away from the coin's hiding spot.",
             "Somewhere within the area, you might see an object in the air.",
             "If you spot the number 4, face NNW and the hiding spot might be in that direction.",
             "The area has at least 1 manmade place where humans may become tired.",
             "The coin may be warmer at 9am compared to 5pm.",
             "There is a lamp post within 45 steps of the coin's hiding spot.",
             "Those who are lost may be drawn.",
             "Why is this not fixed?",
             "Sqkii heard that something fierce is in the area's history.",
             "A set: The trigger to sleep can be found within 399m of the coin's spot.",
             "Temper, strength and friends came from the area where the coin will be.",
             "There is something missing within walking distance from the coin's hiding spot.",
             "There is at least 1 place in the area where you can find bound things.",
             "A set: Within 311m of the coin's spot, you can reduce something that connects.",
             "Within 500m of the coin's spot, there is a lack of permanence.",
             "There is a crack near the coin's hiding spot.",
             "The area has at least 2 places where humans want low points.",
             "Look out for something that was manufactured between 2013 and 2018.",
             "A set: If you find the falling things, you might be within 450m of the coin's spot.",
             "A sea of watchful eyes but none the wiser.",
             "The coin is within 600m of a place where something may be subsidised.",
             "Think of a word.",
             "A set: Within 500m of the coin, there's a relative of something that only fits one.",
             "The combination mentioned in an MRT station hint affected humans.",
             "You might find creative humans within 1.2km of the coin.",
             "There is a toilet within 700m of the coin.",
             "Something significant happened near the coin's hiding spot between 2015 – 2019.",
             "If you see an AED, the coin's spot may be within a 10-min walk.",
             "You do not have to look around a bronze lamp post.",
             "Daily Hint #8 is somewhere high overhead.",
             "A human nearby may be afraid.",
             "The things in Daily Hint #12 are part of a larger collection.",
             "The coin will be within 300m of something that is older than 5 years old.",
             "Daily Hint #16 comes with a cost.",
             "See a number placed above average human height? You may be within 200m of the coin's spot.",
             "Look up heritage trees. One of the species can be found near the hiding spot.",
             "The coin will not be hidden at a working public phone.",
             "Hungry humans may become happy within 602m of the coin's hiding spot.",
             "Within 480m of the coin's spot, there is something that can have different insides.",
             "Something seems fun less than 600m away from the coin's spot.",
             "The humans in Daily Hint #26 may go home with something new.",
             "The humans in Daily Hint #18 will be hoping for the best.",
             "If you can see something from the other side, you may be on the right track.",
             "Route A (1/5): From a bus stop, face south and walk until you reach a traffic light.",
             "The human in Daily Hint #32 is not likely to be standing up.",
             "There is something symbolic less than 300m away from the coin's hiding spot.",
             "Route A (2/5): Turn left and walk for approximately 450m.",
             "Remember Daily Hint #25? Think about younger humans.",
             "The coin will not be hidden on a rooftop garden.",
             "Something that is yours but not yet with you – look within 320m of the coin's spot.",
             "Something fragrant may be found within 290m of the coin's spot.",
             "The thing in Daily Hint #2 has windows.",
             "A fitness corner is not where you'll find the coin.",
             "If you choose, the thing in Daily Hint #40 may not have anything in it at all.",
             "You can find fruits of the sea within 600m of the coin's spot.",
             "The coin's spot is within 311m of something that has a fixed lifespan.",
             "If you see a 2D version of something meant for movement, you may be within 705m of the coin's spot."]
}

# Initialize session state for grid colors
if 'grid_colors' not in st.session_state:
    st.session_state.grid_colors = {}

# Set page title
st.title("Singapore Grid Map (Incomplete)")

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

df = pd.DataFrame(data)

html_table = df.to_html(index=False, classes='table table-striped') 
 
# Add custom CSS to make the table responsive and align title to the left 
st.write(""" 
    <style> 
    .table { 
        width: 100%; 
        max-width: 100%; 
        margin-bottom: 1rem; 
        background-color: transparent; 
    } 
    .table th, 
    .table td { 
        padding: 0.75rem; 
        vertical-align: top; 
        border-top: 1px solid #dee2e6; 
        text-align: left; /* Align text to the left */ 
    } 
    .table thead th { 
        vertical-align: bottom; 
        border-bottom: 2px solid #dee2e6; 
    } 
    .table tbody + tbody { 
        border-top: 2px solid #dee2e6; 
    } 
    .table-sm th, 
    .table-sm td { 
        padding: 0.3rem; 
    } 
    .table-bordered { 
        border: 1px solid #dee2e6; 
    } 
    .table-bordered th, 
    .table-bordered td { 
        border: 1px solid #dee2e6; 
    } 
    .table-bordered thead th, 
    .table-bordered thead td { 
        border-bottom-width: 2px; 
    } 
    .table-borderless th, 
    .table-borderless td, 
    .table-borderless thead th, 
    .table-borderless tbody + tbody { 
        border: 0; 
    } 
    .table-hover tbody tr:hover { 
        background-color: rgba(0, 0, 0, 0.075); 
    } 
    @media (max-width: 768px) { 
        .table-responsive { 
            display: block; 
            width: 100%; 
            overflow-x: auto; 
            -webkit-overflow-scrolling: touch; 
        } 
        .table-responsive > .table-bordered { 
            border: 0; 
        } 
    } 
    </style> 
""", unsafe_allow_html=True) 
 
# Display the table 
st.write(html_table, unsafe_allow_html=True)

st.markdown("[![Text hints](https://img.icons8.com/?size=80&id=MhNWGcvOM41M&format=png)](https://docs.google.com/spreadsheets/d/101R97Az6VXjjAlitPbymr5qZFAAHzdQELR6yZtgCcgQ/edit?usp=sharing) [Text hints](https://docs.google.com/spreadsheets/d/101R97Az6VXjjAlitPbymr5qZFAAHzdQELR6yZtgCcgQ/edit?usp=sharing)")
