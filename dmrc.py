import csv
from neo4j import GraphDatabase, basic_auth
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the DMRC fare rate function
def calculate_fare(distance):
    if distance <= 2:
        return 10
    elif distance <= 5:
        return 20
    elif distance <= 12:
        return 30
    elif distance <= 21:
        return 40
    elif distance <= 32:
        return 50
    else:
        return 60

# Estimate travel time between stations (in minutes)
def estimate_time(distance):
    # Assuming an average speed of 35 km/h and converting to minutes
    return round(distance / 35 * 60, 2)

# Estimate metro frequency (trains per hour)
def estimate_frequency():
    # Assuming an average metro frequency of 5 minutes between trains
    return 12  # 60 minutes / 5 minutes per train

# Connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "hellohello"

# Function to create stations and relationships
def create_graph(driver, csv_path):
    try:
        with driver.session() as session:
            logger.info("Reading CSV file...")

            # Read the CSV file using pandas
            df = pd.read_csv(csv_path)

            # Extract the start stations (first column) and end stations (first row)
            start_stations = df.iloc[:, 0]
            end_stations = df.columns[1:]

            # Create nodes for stations with "type" attribute
            logger.info("Creating station nodes...")
            for station in start_stations:
                session.run("MERGE (s:Station {name: $name, type: 'Station'})", name=station)

            # Create relationships with additional properties
            logger.info("Creating relationships...")
            for i, start_station in enumerate(start_stations):
                for end_station in end_stations:
                    distance = df.iloc[i, df.columns.get_loc(end_station)]
                    if pd.notna(distance):
                        distance_value = float(distance)
                        fare = calculate_fare(distance_value)
                        time = estimate_time(distance_value)
                        frequency = estimate_frequency()

                        session.run("""
                            MATCH (a:Station {name: $start_station}), (b:Station {name: $end_station})
                            MERGE (a)-[r:CONNECTS_TO {distance: $distance, fare: $fare, time: $time, service_type: 'DMRC', frequency: $frequency}]->(b)
                        """, start_station=start_station, end_station=end_station, distance=distance_value, fare=fare, time=time, frequency=frequency)
            logger.info("Graph created successfully.")
    except Exception as e:
        logger.error("Failed to create graph: %s", e)
        raise

# Attempt to connect to Neo4j Aura
logger.info("Attempting to connect to Neo4j Aura at %s", uri)
try:
    driver = GraphDatabase.driver(uri, auth=basic_auth(username, password))
    logger.info("Successfully connected to Neo4j Aura")

    # Path to the CSV file
    csv_path = "C:\\Users\\aisha\\Desktop\\connect\\dmrc.csv"
    # Create the graph database
    create_graph(driver, csv_path)

    # Close the driver connection
    driver.close()
    logger.info("Closed the connection to Neo4j Aura")

except Exception as e:
    logger.error("An error occurred: %s", e)
