import requests, mysql.connector
from datetime import datetime, timedelta

API_KEY = "Fs6p4ma7RDrCS8o38mqtLSPy0LRbiSKq7ZtRf0Cv"


# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="darnish@666666",
    database="nasa_asteroids"
)
cursor = conn.cursor()

# Set date range
start_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
total_records = 0
target = 10000

while total_records < target:
    end_date = start_date + timedelta(days=7)
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}&api_key={API_KEY}"
    data = requests.get(url).json()['near_earth_objects']

    for date in data:
        for a in data[date]:
            id = a['id']
            name = a['name']
            mag = a['absolute_magnitude_h']
            dia_min = a['estimated_diameter']['kilometers']['estimated_diameter_min']
            dia_max = a['estimated_diameter']['kilometers']['estimated_diameter_max']
            haz = a['is_potentially_hazardous_asteroid']

            cursor.execute("""
                INSERT IGNORE INTO asteroids (id, name, absolute_magnitude_h, estimated_diameter_min_km, estimated_diameter_max_km, is_potentially_hazardous_asteroid)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id, name, mag, dia_min, dia_max, haz))

            for approach in a['close_approach_data']:
                date = approach['close_approach_date']
                vel = float(approach['relative_velocity']['kilometers_per_hour'])
                miss_km = float(approach['miss_distance']['kilometers'])
                miss_lunar = float(approach['miss_distance']['lunar'])
                body = approach['orbiting_body']

                cursor.execute("""
                    INSERT INTO close_approach (neo_reference_id, close_approach_date, relative_velocity_kmph, miss_distance_km, miss_distance_lunar, orbiting_body)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id, date, vel, miss_km, miss_lunar, body))

            total_records += 1

    print(f"{total_records} records inserted...")
    start_date = end_date

# Finalize
conn.commit()
cursor.close()
conn.close()
print("Data inserted into MySQL!")