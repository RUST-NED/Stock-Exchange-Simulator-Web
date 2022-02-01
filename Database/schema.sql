--@block
CREATE DATABASE IF NOT EXISTS stockexchangesimulator;

--@block
CREATE TABLE Users (
username VARCHAR(30) PRIMARY KEY,
password_hash VARCHAR(255) NOT NULL,
API_KEY VARCHAR(255) NOT NULL,
cash NUMERIC NOT NULL
);


--@block
CREATE TABLE Transactions (
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    username VARCHAR(30) NOT NULL,
    stock_symbol VARCHAR(30) NOT NULL,
    num_shares NUMERIC NOT NULL,
    price NUMERIC NOT NULL,
    FOREIGN KEY (username) REFERENCES Users(username)
);


