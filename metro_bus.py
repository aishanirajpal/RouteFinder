import csv
from neo4j import GraphDatabase, basic_auth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "hellohello"

# Function to connect metro stations to bus stops
def connect_metro_to_bus(driver, connections_csv_path):
    try:
        with driver.session() as session:
            logger.info("Reading CSV file...")
            # Read the CSV file with connections
            with open(connections_csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                logger.info("Creating interchange relationships between metro stations and bus stops...")
                for row in reader:
                    metro_station = row['Metro Station']
                    bus_stop = row['Bus Stop']
                    distance = float(row['Distance (km)'])
                    time = float(row['Bus Timing (minutes)'])
                    
                    # Logging for debugging
                    logger.info(f"Processing interchange from {metro_station} to {bus_stop}")
                    
                    # Create or update the relationship with service_type as interchange and fare as 0
                    result = session.run("""
                        MATCH (m:Station {name: $metro_station}), (b:Stop {name: $bus_stop})
                        MERGE (m)-[r:interchange {distance: $distance, time: $time, service_type: 'interchange', fare: 0}]->(b)
                        RETURN m, b, r
                    """, metro_station=metro_station, bus_stop=bus_stop, distance=distance, time=time)
                    
                    # Logging the results of the query
                    for record in result:
                        logger.info(f"Created or updated interchange relationship: {record}")

        logger.info("Interchange relationships created successfully.")
    except Exception as e:
        logger.error("Failed to create interchange relationships: %s", e)
        raise

# Attempt to connect to Neo4j Aura
logger.info("Attempting to connect to Neo4j Aura at %s", uri)
try:
    driver = GraphDatabase.driver(uri, auth=basic_auth(username, password))
    logger.info("Successfully connected to Neo4j Aura")

    # Path to the CSV file with connections
    connections_csv_path = "C:\\Users\\aisha\\Desktop\\connect\\metro_bus.csv"
    # Create the connections in the graph database
    connect_metro_to_bus(driver, connections_csv_path)

    # Close the driver connection
    driver.close()
    logger.info("Closed the connection to Neo4j Aura")

except Exception as e:
    logger.error("An error occurred: %s", e)
