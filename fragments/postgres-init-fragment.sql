-- Create llc_geo database
CREATE DATABASE llc_geo;

--Create user for llc_geo DB
CREATE ROLE llc_geo_user with LOGIN password 'llc_geo_password';

\c llc_geo;
CREATE EXTENSION postgis;