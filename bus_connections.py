import pandas as pd
import random

# List of bus stops
bus_stops = [
    "Palika Kendra", "Tolstoy Marg", "Regal", "Scindia House", "Shivaji Stadium", "INA Colony",
    "Safdarjung Terminal", "Kidwai Nagar", "Lodhi Colony", "Town Hall", "St. Stephen's Church",
    "Red Fort", "Old Delhi Railway Station", "ISBT Kashmere Gate", "Mori Gate Terminal",
    "Shakti Nagar", "Tis Hazari Court", "Civil Lines", "New Delhi Railway Station Gate 1",
    "Ajmeri Gate", "JLN Marg", "Kamla Market", "CP New Delhi", "Huda City Centre Terminal",
    "Sector 29", "Sector 44", "Sushant Lok", "Rajendra Place Bus Stop", "Shanker Road",
    "Patel Nagar", "East Patel Nagar", "Pusa Road", "Lajpat Nagar Market", "Lajpat Nagar Bus Terminal",
    "Ring Road", "Moolchand", "Defence Colony", "Karol Bagh Metro Station Bus Stop",
    "Jhandewalan", "Karol Bagh Market", "Saket Metro Station Bus Stop", "Malviya Nagar",
    "Select Citywalk", "Pushp Vihar", "Saket District Centre", "Sikanderpur Metro Station Bus Stop",
    "Guru Dronacharya", "DLF Phase 2", "M G Road", "Arjun Marg", "Noida City Centre Terminal",
    "Sector 34", "Sector 50", "Sector 39", "Noida Stadium", "Botanical Garden Metro Station Bus Stop",
    "Sector 37", "Sector 44", "NTPC", "Amity University", "Vishwavidyalaya Metro Station Bus Stop",
    "University of Delhi", "Guru Tegh Bahadur Nagar", "Kamla Nagar", "Mall Road",
    "Janakpuri West Metro Station Bus Stop", "District Centre", "Uttam Nagar", "Vikas Puri",
    "Anand Vihar ISBT", "Vivek Vihar", "Karkardooma", "Preet Vihar", "Patparganj",
    "Nehru Place Metro Station Bus Stop", "Kalkaji", "CR Park", "GK-2", "East of Kailash",
    "Dwarka Sector 21 Metro Station Bus Stop", "Dwarka Sector 23", "Dwarka Sector 22",
    "Dwarka Sector 8", "Dwarka Sector 10", "Mandi House Metro Station Bus Stop", "Bengali Market",
    "ITO", "Barakhamba Road", "Connaught Place", "Central Secretariat Metro Station Bus Stop",
    "Patel Chowk", "Udyog Bhawan", "Krishi Bhawan", "Rail Bhawan", "Pitampura", "Britannia Chowk",
    "Patparganj", "Noida Sector 34", "Janakpuri District Centre"
]

# Generate dummy data
connections = []
for _ in range(150):  # Generating 150 dummy connections
    from_stop = random.choice(bus_stops)
    to_stop = random.choice(bus_stops)
    while to_stop == from_stop:  # Ensuring 'to' stop is different from 'from' stop
        to_stop = random.choice(bus_stops)
    distance = round(random.uniform(1, 20), 2)  # Random distance between 1 and 20 km
    time = round(distance * random.uniform(1.5, 3), 2)  # Random time based on distance (1.5 to 3 min/km)
    connections.append([from_stop, to_stop, distance, time])

# Creating DataFrame
df = pd.DataFrame(connections, columns=["From", "To", "Distance (km)", "Time (minutes)"])
csv_path = "C:\\Users\\aisha\\Documents\\RouteFinder\\bus_connections.csv"
df.to_csv(csv_path, index=False)

csv_path
