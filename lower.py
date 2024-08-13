from neo4j import GraphDatabase

# Replace these with your actual database credentials
uri = "bolt://localhost:7687"
username = "neo4j"
password = "hellohello"

# Function to convert node names to lower case
def convert_node_names_to_lowercase(uri, username, password):
    driver = GraphDatabase.driver(uri, auth=(username, password))

    with driver.session() as session:
        # Retrieve all nodes with their names
        result = session.run("MATCH (n) RETURN n")

        for record in result:
            node = record["n"]
            if "name" in node:
                # Convert the node name to lower case
                lower_case_name = node["name"].lower()
                node_id = node.id
                # Update the node name in the database
                session.run("MATCH (n) WHERE id(n) = $id SET n.name = $name", id=node_id, name=lower_case_name)
    
    driver.close() 

# Call the function
convert_node_names_to_lowercase(uri, username, password)
