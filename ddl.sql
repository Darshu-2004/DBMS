CREATE DATABASE transport_system;
USE transport_system;

-- USER
CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    user_type ENUM('passenger','admin','operator')
);

-- USER_PHONE (multi-valued)
CREATE TABLE User_Phone (
    user_id INT,
    phone_number VARCHAR(15),
    PRIMARY KEY(user_id, phone_number),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

-- STATION
CREATE TABLE Station (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(255),
    type ENUM('bus','train','metro','airport')
);

-- ROUTE
CREATE TABLE Route (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    mode ENUM('bus','train','metro','flight'),
    origin_station_id INT,
    destination_station_id INT,
    distance_km FLOAT,
    FOREIGN KEY (origin_station_id) REFERENCES Station(station_id),
    FOREIGN KEY (destination_station_id) REFERENCES Station(station_id)
);

-- VEHICLE
CREATE TABLE Vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT,
    type ENUM('bus','train','metro','plane'),
    capacity INT,
    registration_number VARCHAR(50) UNIQUE,
    status ENUM('active','maintenance','decommissioned'),
    FOREIGN KEY (route_id) REFERENCES Route(route_id)
);

-- OPERATOR
CREATE TABLE Operator (
    operator_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    contact_info VARCHAR(100),
    type ENUM('government','private')
);

-- VEHICLE_ASSIGNMENT
CREATE TABLE Vehicle_Assignment (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT,
    operator_id INT,
    assignment_start DATETIME,
    assignment_end DATETIME,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
    FOREIGN KEY (operator_id) REFERENCES Operator(operator_id)
);

-- SCHEDULE
CREATE TABLE Schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT,
    departure_time DATETIME,
    arrival_time DATETIME,
    frequency ENUM('daily','weekly','monthly'),
    FOREIGN KEY (route_id) REFERENCES Route(route_id)
);

-- TRIP
CREATE TABLE Trip (
    trip_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT,
    route_id INT,
    schedule_id INT,
    departure_time DATETIME,
    arrival_time DATETIME,
    status ENUM('scheduled','ongoing','completed','cancelled'),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
    FOREIGN KEY (route_id) REFERENCES Route(route_id),
    FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id)
);

-- TICKET
CREATE TABLE Ticket (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    trip_id INT,
    purchase_time DATETIME,
    seat_number VARCHAR(10),
    status ENUM('booked','cancelled','checked_in'),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (trip_id) REFERENCES Trip(trip_id)
);

-- PAYMENT
CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT UNIQUE,
    amount DECIMAL(10,2),
    payment_time DATETIME,
    method ENUM('credit_card','debit_card','wallet','cash'),
    status ENUM('success','failed','refunded'),
    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id)
);

-- INTERCHANGE
CREATE TABLE Interchange (
    station_id INT,
    connects_to_station_id INT,
    mode_from ENUM('bus','train','metro','flight'),
    mode_to ENUM('bus','train','metro','flight'),
    PRIMARY KEY(station_id, connects_to_station_id),
    FOREIGN KEY (station_id) REFERENCES Station(station_id),
    FOREIGN KEY (connects_to_station_id) REFERENCES Station(station_id)
);

-- ANNOUNCEMENT
CREATE TABLE Announcement (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT,
    message TEXT,
    announcement_time DATETIME,
    type ENUM('info','alert','emergency'),
    FOREIGN KEY (station_id) REFERENCES Station(station_id)
);
