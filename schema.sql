-- =============================================================
-- schema.sql  —  Database schema for the climate tracker
-- =============================================================
-- This file defines the structure of our SQLite database.
-- We run this once to create the table. SQLite stores the
-- entire database in a single file (climate.db).
-- =============================================================

-- CREATE TABLE IF NOT EXISTS:
--   "IF NOT EXISTS" prevents an error if you run this script
--   again. Safe to call on every app startup.
CREATE TABLE IF NOT EXISTS readings (

    -- INTEGER PRIMARY KEY tells SQLite to auto-increment this
    -- column. Each new row gets the next available integer.
    id          INTEGER PRIMARY KEY AUTOINCREMENT,

    -- TEXT columns store strings. NOT NULL means the column
    -- is required — SQLite will reject a row without a value.
    city        TEXT    NOT NULL,

    -- REAL stores decimal numbers (floats). Perfect for temps
    -- like 23.5°C. NOT NULL enforces that a value is required.
    temperature REAL    NOT NULL,

    -- We store the date as TEXT in ISO-8601 format: YYYY-MM-DD
    -- SQLite has no dedicated DATE type, but TEXT works fine and
    -- sorts correctly when the format is consistent.
    -- DEFAULT (DATE('now')) auto-fills today's date if omitted.
    date        TEXT    NOT NULL DEFAULT (DATE('now'))
);