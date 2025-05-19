#!/usr/bin/env python3
"""
Standalone script to regenerate the database with integer IDs.
"""
import os
import sys
import sqlite3
from datetime import date, timedelta
import random

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the sample_data module directly
from bank_agent.entities.sample_data import populate_database

if __name__ == "__main__":
    print("Regenerating database with integer IDs...")
    populate_database()
    print("Database regeneration complete!")
