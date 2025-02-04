import pandas as pd
import heapq
import math

def load_airports(csv_file):
    df = pd.read_csv(csv_file)
    airports = {row['ID']: (row['latitude'], row['longitude']) for _, row in df.iterrows()}
    return airports

def load_connections(csv_file):
    df = pd.read_csv(csv_file, header=None, names=["route"])
    connections = set()
    for _, row in df.iterrows():
        try:
            departure, arrival = row["route"].split(" - ")
            connections.add((departure.strip(), arrival.strip()))
        except ValueError:
            print(f"Erreur de format sur la ligne : {row['route']}")
    return connections

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))