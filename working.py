import streamlit as st
from neo4j import GraphDatabase
import base64
import requests
import logging

# Neo4j connection details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "hellohello"

# Connect to Neo4j
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def check_location(tx, location):
    query = "MATCH (n) WHERE toLower(n.name) = $name RETURN n"
    result = tx.run(query, name=location.lower())
    return result.single() is not None

def get_shortest_route(tx, start, end):
    query = """
    MATCH (start {name: $start}), (end {name: $end})
    WITH start, end
    OPTIONAL MATCH p = shortestPath((start)-[*]-(end))
    UNWIND relationships(p) AS rel
    RETURN nodes(p) AS nodes, 
           sum(rel.distance) AS total_distance,
           sum(rel.fare) AS total_fare
    LIMIT 1
    """
    result = tx.run(query, start=start.lower(), end=end.lower())
    record = result.single()
    
    if record:
        return {
            "nodes": record["nodes"],
            "total_distance": record["total_distance"],
            "total_fare": record["total_fare"],
        }
    return None

def get_fastest_route(tx, start, end):
    query = """
    MATCH (start {name: $start}), (end {name: $end})
    WITH start, end
    OPTIONAL MATCH p = allShortestPaths((start)-[*]-(end))
    UNWIND relationships(p) AS rel
    RETURN nodes(p) AS nodes,
           sum(rel.time) AS total_time,
           sum(rel.fare) AS total_fare
    LIMIT 1
    """
    result = tx.run(query, start=start.lower(), end=end.lower())
    record = result.single()

    if record:
        return {
            "nodes": record["nodes"],
            "total_time": record["total_time"],
            "total_fare": record["total_fare"],
        }
    return None

def get_least_fare_route(tx, start, end):
    query = """
    MATCH (start {name: $start}), (end {name: $end})
    WITH start, end
    OPTIONAL MATCH p = shortestPath((start)-[*]-(end))
    UNWIND relationships(p) AS rel
    RETURN nodes(p) AS nodes,
           sum(rel.fare) AS total_fare
    LIMIT 1
    """
    result = tx.run(query, start=start.lower(), end=end.lower())
    record = result.single()

    if record:
        return {
            "nodes": record["nodes"],
            "total_fare": record["total_fare"],
        }
    return None

def get_route_description(nodes):
    description = []
    prev_type = None
    has_bus = False
    has_metro = False
    location_first=""
    location_middle=""
    for i, node in enumerate(nodes):
        node_type = "Station" if "Station" in node.labels else "Stop"
        location_name = format_location_name(node['name'])
       
        if i == 0:
            location_first=location_name
        elif i==1:
            if prev_type and prev_type == node_type:
                if node_type == "Station":
                    description.append(f"Take the metro from {location_first} to {location_name}.")
                    # st.warning("You need to walk or take a rickshaw from the Bus Stop to Metro Station.")
                    has_metro = True
                else:
                    description.append(f"Take the bus from {location_first} to {location_name}.")
                    # st.warning("You need to walk or take a rickshaw from the Metro Station to the Bus Stop.")
                    has_bus = True
            else:
                if node_type == "Station":
                    description.append(f"Now go to the Station from {location_first} to {location_name}.")
                    st.warning("You need to walk or take a rickshaw from the Bus Stop to Metro Station.")
                    # has_metro = True
                else:
                    description.append(f"Now go to the Stop from {location_first} to {location_name}.")
                    st.warning("You need to walk or take a rickshaw from the Metro Station to the Bus Stop.")
                    # has_bus = True
                    
                # description.append(location_name)
            # if node_type == "Station":
            #     description.append(f"First, take the metro from {location_name}.")
            #     has_metro = True
            # else:
            #     description.append(f"First, take the bus from {location_name}.")
            #     has_bus = True
        else:
            if prev_type and prev_type != node_type:
                if node_type == "Station":
                    description.append(f"Now go to {location_name}.")
                    st.warning("You need to walk or take a rickshaw from the Bus Stop to Metro Station.")
                    has_metro = True
                else:
                    description.append(f"Now go to {location_name}.")
                    st.warning("You need to walk or take a rickshaw from the Metro Station to the Bus Stop.")
                    has_bus = True
            else:
                if node_type == "Station":
                    description.append(f"Take a metro to {location_name}.")
                    # st.warning("You need to walk or take a rickshaw from the Bus Stop to Metro Station.")
                    has_metro = True
                else:
                    description.append(f"Take a bus to {location_name}.")
                    # st.warning("You need to walk or take a rickshaw from the Metro Station to the Bus Stop.")
                    has_bus = True

        prev_type = node_type

    if has_metro and has_bus:
        description.insert(0, "The route involves both bus and metro.")
    elif has_metro:
        description.insert(0, "The route involves only metro.")
    elif has_bus:
        description.insert(0, "The route involves only bus.")
    return description

def format_location_name(name):
    return name.title()

def get_weather_info(location):
    try:
        api_key = "dbd9924d07a74e31b83419272234035b"  # Replace with your API key
        base_url = f"https://api.weatherbit.io/v2.0/current?city={location}&key={api_key}"
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        try:
            weather_data = response.json()
            temperature = weather_data['data'][0]['temp']
            weather_description = weather_data['data'][0]['weather']['description']
            return temperature, weather_description.capitalize()
        except (ValueError, KeyError) as e:
            logging.error(f"Error processing weather data: {e}")
            return None, None
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
    return None, None

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Define the Streamlit app layout and logic
st.set_page_config(page_title="Route Finder", page_icon="🚉")
add_bg_from_local("C:\\Users\\aisha\\Desktop\\connect\\Untitled.png")

st.markdown("""
    <style>
    .stApp {
        background-color: rgba(255, 255, 255, 0.7);
    }
    * {
        font-family: 'Times New Roman', Times, serif;
    }
    .centered-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        text-align: center;
    }
    .stButton button {
        width: 200px;
        margin-top: 10px;
        border-radius: 5px;
        margin-left:35%;
    }
    .find-route-container .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .transparent-box {
        margin: 20px;
        padding: 20px;
        background-color: rgba(255, 255, 255, 0.6);
        border-radius: 10px;
        border: 1px solid black;
    }
    .spacer {
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

centered_container = st.container()

with centered_container:
    st.markdown('<div class="centered-container">', unsafe_allow_html=True)
    st.title("Route Finder")

    start_location = st.text_input("Enter start location:")
    end_location = st.text_input("Enter end location:")

    route_options = ["Shortest Route", "Fastest Route", "Least Fare Route"]
    selected_route = st.selectbox("Select route type:", route_options)

    st.markdown('<div class="spacer">', unsafe_allow_html=True)

    # Weather information checkbox
    weather_info_checkbox = st.checkbox("Show Weather Information")
    
    if start_location and end_location:
            # Weather info for start location
        if start_location:
            temperature, description = get_weather_info(start_location)
            if temperature is not None and description:
                st.write(f"Weather at {format_location_name(start_location)}: {temperature}°C, {description}")
            else:
                st.write(f"Could not retrieve weather information for {format_location_name(start_location)}.")

            # Weather info for end location
        if end_location:
            temperature, description = get_weather_info(end_location)
            if temperature is not None and description:
                st.write(f"Weather at {format_location_name(end_location)}: {temperature}°C, {description}")
            else:
                st.write(f"Could not retrieve weather information for {format_location_name(end_location)}.")
    else:
        st.error("Please enter both start and end locations.")
     
if st.button("Find Route"):
    with driver.session() as session:
        if not (session.read_transaction(check_location, start_location) and
                session.read_transaction(check_location, end_location)):
            st.write("Start or end location not yet added in our database. Please enter another location.")
        else:
            if selected_route == "Shortest Route":
                result = session.read_transaction(get_shortest_route, start_location, end_location)
            elif selected_route == "Fastest Route":
                result = session.read_transaction(get_fastest_route, start_location, end_location)
            elif selected_route == "Least Fare Route":
                result = session.read_transaction(get_least_fare_route, start_location, end_location)

            if result:
                st.subheader("Route Details")
                st.write("Total Fare:", result["total_fare"], "INR")
                
                if selected_route == "Shortest Route":
                    st.write("Total Distance:", result["total_distance"], "km")
                elif selected_route == "Fastest Route":
                    st.write("Total Time:", result["total_time"], "minutes")
                
                # Display detailed route description
                st.subheader("Route Description")
                route_description = get_route_description(result["nodes"])
                for step in route_description:
                    st.write(step)

    st.markdown('</div>', unsafe_allow_html=True)

# Close the Neo4j driver connection when done
driver.close()

