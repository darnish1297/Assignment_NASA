import streamlit as st
import mysql.connector
import pandas as pd

# MySQL connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='darnish@666666',
    database='nasa_asteroids'
)
cursor = conn.cursor(dictionary=True)

st.set_page_config(page_title="NASA Asteroid Tracker", layout="wide")
st.title("🚀 NASA Asteroid Tracker")

# Sidebar
st.sidebar.title("Asteroid")
option = st.sidebar.radio("Select", ["Approaches", "Queries"])

if option == "Approaches":
    st.sidebar.subheader("🔍 Filter Criteria")

    # Sliders & Filters
    mag_min, mag_max = st.slider("Min Magnitude", 10.0, 35.0, (13.0, 32.0))
    vel_min, vel_max = st.slider("Relative_velocity_kmph Range", 0.0, 180000.0, (1000.0, 70000.0))
    dia_min, dia_max = st.slider("Min Estimated Diameter (km)", 0.0, 10.0, (0.1, 5.0))
    diax_min, diax_max = st.slider("Max Estimated Diameter (km)", 0.0, 20.0, (0.5, 15.0))
    au_min, au_max = st.slider("Astronomical unit", 0.0, 1.0, (0.01, 0.5))

    hazardous = st.selectbox("Only Show Potentially Hazardous", ["All", "Yes", "No"])
    start_date = st.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
    end_date = st.date_input("End Date", value=pd.to_datetime("2025-04-13"))

    if st.button("Filter"):
        query = f"""
        SELECT a.id, a.name, a.absolute_magnitude_h, a.estimated_diameter_min_km,
               a.estimated_diameter_max_km, a.is_potentially_hazardous_asteroid,
               ca.relative_velocity_kmph, ca.miss_distance_km, ca.miss_distance_lunar,
               ca.close_approach_date
        FROM asteroids a
        JOIN close_approach ca ON a.id = ca.neo_reference_id
        WHERE a.absolute_magnitude_h BETWEEN {mag_min} AND {mag_max}
          AND ca.relative_velocity_kmph BETWEEN {vel_min} AND {vel_max}
          AND a.estimated_diameter_min_km BETWEEN {dia_min} AND {dia_max}
          AND a.estimated_diameter_max_km BETWEEN {diax_min} AND {diax_max}
          AND ca.miss_distance_km BETWEEN {au_min * 149597870.7} AND {au_max * 149597870.7}
          AND ca.close_approach_date BETWEEN '{start_date}' AND '{end_date}'
        """

        if hazardous == "Yes":
            query += " AND a.is_potentially_hazardous_asteroid = TRUE"
        elif hazardous == "No":
            query += " AND a.is_potentially_hazardous_asteroid = FALSE"

        cursor.execute(query)
        data = pd.DataFrame(cursor.fetchall())
        st.subheader("Filtered Asteroids")
        st.dataframe(data)

elif option == "Queries":
    st.sidebar.subheader("📊 Query Insights")
    query_options = {
    "1. Count how many times each asteroid has approached Earth":
        "SELECT neo_reference_id, name, COUNT(*) AS approach_count FROM close_approach GROUP BY neo_reference_id, name",

    "2. Average velocity of each asteroid over multiple approaches":
        "SELECT neo_reference_id, name, AVG(relative_velocity_kmph) AS avg_velocity FROM close_approach GROUP BY neo_reference_id, name",

    "3. Top 10 fastest asteroids":
        "SELECT neo_reference_id, name, MAX(relative_velocity_kmph) AS top_speed FROM close_approach GROUP BY neo_reference_id, name ORDER BY top_speed DESC LIMIT 10",

    "4. Find potentially hazardous asteroids":
        "SELECT id, name, is_potentially_hazardous_asteroid FROM asteroids WHERE is_potentially_hazardous_asteroid = 1",

    "5. Find the month with the most asteroid approaches":
        "SELECT MONTH(close_approach_date) AS month, COUNT(*) AS total FROM close_approach GROUP BY month ORDER BY total DESC",

    "6. Get the asteroid with the fastest ever approach speed":
        "SELECT neo_reference_id, name, relative_velocity_kmph FROM close_approach ORDER BY relative_velocity_kmph DESC LIMIT 1",

    "7. Sort asteroids by maximum estimated diameter (descending)":
        "SELECT id, name, estimated_diameter_max_km FROM asteroids ORDER BY estimated_diameter_max_km DESC",

    "8. An asteroid whose closest approach is getting nearer over time":
        "SELECT neo_reference_id, name, close_approach_date, miss_distance_km FROM close_approach ORDER BY miss_distance_km ASC, close_approach_date DESC LIMIT 1",

    "9. Display the name of each asteroid along with the date and miss distance of its closest approach to Earth":
        "SELECT neo_reference_id, name, close_approach_date, miss_distance_km FROM close_approach",

    "10. List names of asteroids that approached Earth with velocity > 50000 km/h":
        "SELECT neo_reference_id, name, relative_velocity_kmph FROM close_approach WHERE relative_velocity_kmph > 50000",

    "11. Count how many approaches happened per month":
        "SELECT MONTH(close_approach_date) AS month, COUNT(*) AS approach_count FROM close_approach GROUP BY month",

    "12. Find asteroid with the highest brightness (lowest magnitude value)":
        "SELECT id, name, absolute_magnitude_h FROM asteroids ORDER BY absolute_magnitude_h ASC LIMIT 1",

    "13. Get number of hazardous vs non-hazardous asteroids":
        "SELECT is_potentially_hazardous_asteroid, COUNT(*) AS count FROM asteroids GROUP BY is_potentially_hazardous_asteroid",

    "14. Find asteroids that passed closer than the Moon (less than 1 LD)":
        "SELECT neo_reference_id, name, miss_distance_lunar FROM close_approach WHERE miss_distance_lunar < 1",

    "15. Find asteroids that came within 0.05 AU (astronomical distance)":
        "SELECT neo_reference_id, name, miss_distance_au FROM close_approach WHERE miss_distance_au < 0.05"
        
    
        "SELECT MONTH(ca.close_approach_date) AS month, COUNT(*) AS count FROM close_approach ca JOIN asteroids a ON ca.neo_reference_id = a.id WHERE a.is_potentially_hazardous_asteroid = 1 GROUP BY month ORDER BY count DESC"}
    bonus_query_options = {
    "Bonus 1: Asteroids with more than 5 approaches":
        "SELECT neo_reference_id, name, COUNT(*) AS total_approaches FROM close_approach GROUP BY neo_reference_id, name HAVING total_approaches > 5",

    "Bonus 2: Average miss distance of hazardous asteroids":
        "SELECT a.name, AVG(ca.miss_distance_km) AS avg_miss_km FROM close_approach ca JOIN asteroids a ON ca.neo_reference_id = a.id WHERE a.is_potentially_hazardous_asteroid = 1 GROUP BY a.name",

    "Bonus 3: Top 5 asteroids with closest approaches (lowest AU distance)":
        "SELECT neo_reference_id, name, miss_distance_au FROM close_approach ORDER BY miss_distance_au ASC LIMIT 5",

    "Bonus 4: Fastest hazardous asteroids":
        "SELECT a.name, ca.relative_velocity_kmph FROM asteroids a JOIN close_approach ca ON a.id = ca.neo_reference_id WHERE a.is_potentially_hazardous_asteroid = 1 ORDER BY ca.relative_velocity_kmph DESC LIMIT 5",

    "Bonus 5: Month with highest number of hazardous approaches":
        "SELECT MONTH(ca.close_approach_date) AS month, COUNT(*) AS count FROM close_approach ca JOIN asteroids a ON ca.neo_reference_id = a.id WHERE a.is_potentially_hazardous_asteroid = 1 GROUP BY month ORDER BY count DESC"
}
    selected_query = st.selectbox("Choose a Query", list(query_options.keys()))
    if st.button("Run Query"):
        cursor.execute(query_options[selected_query])
        result = pd.DataFrame(cursor.fetchall())
        st.dataframe(result)