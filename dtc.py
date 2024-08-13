import csv
from neo4j import GraphDatabase, basic_auth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the DTC fare rate function
def calculate_dtc_fare(distance):
    if distance <= 4:
        return 5  # Minimum fare for up to 4 km
    elif distance <= 10:
        return 10  # Fare for 4 to 10 km
    elif distance <= 16:
        return 15  # Fare for 10 to 16 km
    elif distance <= 28:
        return 20  # Fare for 16 to 28 km
    elif distance <= 40:
        return 25  # Fare for 28 to 40 km
    elif distance <= 60:
        return 30  # Fare for 40 to 60 km
    elif distance <= 80:
        return 40  # Fare for 60 to 80 km
    elif distance <= 100:
        return 50  # Fare for 80 to 100 km
    else:
        return 60  # Maximum fare for distances over 100 km

# Estimate bus frequency (buses per hour)
def estimate_frequency():
    # Assuming an average bus frequency of 15 minutes between buses
    return 4  # 60 minutes / 15 minutes per bus

# Connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "hellohello"

# Function to create bus stops and relationships
def create_graph(driver, csv_path):
    try:
        with driver.session() as session:
            logger.info("Reading CSV file...")
            # Read the CSV file
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Create nodes for bus stops with "type" attribute
                logger.info("Creating bus stop nodes...")
                stops = set()
                for row in reader:
                    stops.add(row['From'])
                    stops.add(row['To'])
                
                for stop in stops:
                    session.run("MERGE (s:Stop {name: $name, type: 'Stop'})", name=stop)
                
                # Reset the reader to read the CSV again
                csvfile.seek(0)
                next(reader)  # Skip the header

                # Create relationships with additional properties
                logger.info("Creating relationships...")
                for row in reader:
                    from_stop = row['From']
                    to_stop = row['To']
                    distance = float(row['Distance (km)'])
                    time = float(row['Time (minutes)'])
                    fare = calculate_dtc_fare(distance)
                    frequency = estimate_frequency()
                    
                    session.run("""
                        MATCH (a:Stop {name: $from_stop}), (b:Stop {name: $to_stop})
                        MERGE (a)-[r:CONNECTED {distance: $distance, time: $time, fare: $fare, service_type: 'DTC', frequency: $frequency}]->(b)
                    """, from_stop=from_stop, to_stop=to_stop, distance=distance, time=time, fare=fare, frequency=frequency)
        
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
    csv_path = "C:\\Users\\aisha\\Desktop\\connect\\bus_connections.csv"
    
    # Create the graph database
    create_graph(driver, csv_path)

    # Close the driver connection
    driver.close()
    logger.info("Closed the connection to Neo4j Aura")

except Exception as e:
    logger.error("An error occurred: %s", e)
