-- Create the database
CREATE DATABASE IF NOT EXISTS nasa_asteroids;

-- Use the database
USE nasa_asteroids;

-- Create table for asteroid data
CREATE TABLE IF NOT EXISTS asteroids (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    absolute_magnitude_h FLOAT,
    estimated_diameter_min_km FLOAT,
    estimated_diameter_max_km FLOAT,
    is_potentially_hazardous_asteroid BOOLEAN
);

-- Create table for close approach data
CREATE TABLE IF NOT EXISTS close_approach (
    neo_reference_id INT,
    close_approach_date DATE,
    relative_velocity_kmph FLOAT,
    miss_distance_km FLOAT,
    miss_distance_lunar FLOAT,
    orbiting_body VARCHAR(100),
    FOREIGN KEY (neo_reference_id) REFERENCES asteroids(id)
);