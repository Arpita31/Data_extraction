import pytest
import urllib.request
import os 
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from project0.project0 import fetchincidents, extractincidents, createdb, populatedb, status
import shutil
import sqlite3
import io


def test_fetchincidents_success():
    # Test if the incident pdf is getting downloaded 
    data = fetchincidents("https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf")
    assert isinstance(data, bytes)


def test_createdb_success():
    # Test creation of database
    # Ensure the resources directory doesn't exist before test
    path = os.path.join(os.getcwd(), 'resources/normanpd.db')
    if os.path.exists(path):
        os.remove(path)

    db_path = createdb()

    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        result = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incidents';")
        assert result.fetchone() is not None


def test_populatedb_success():
    # Test data insertion in database
    # Create a test database
    path = os.path.join(os.getcwd(), 'resources/normanpd.db')
    if os.path.exists(path):
        os.remove(path)
    db_path = createdb()

    # Test data for incidents
    incidents = [
        ['8/1/2024 / 0:04', '2024-00055419', '1345 W LINDSEY ST', 'Traffic Stop', 'OK0140200'],
        ['8/1/2024 / 23:50', '2024-00055698', '2920 CHAUTAUQUA AVE', '911 Call Nature Unknown', 'OK0140200'],
        ['8/1/2024 / 23:38', '2024-00055692', 'W BOYD ST / COLLEGE AVE', 'Traffic Stop', 'OK0140200']    
        ]

    # Call populatedb to insert data
    populatedb(db_path, incidents)

    # Verify that data was inserted correctly
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM incidents")
        results = cur.fetchall()
        assert len(results) == 3
        assert results[0][0] == '8/1/2024 / 0:04'
        assert results[1][3] == '911 Call Nature Unknown'
        assert results[2][2] == 'W BOYD ST / COLLEGE AVE'

def test_status_success(capsys):
    # Test 
    # Create a test database
    path = os.path.join(os.getcwd(), 'resources/normanpd.db')
    if os.path.exists(path):
        os.remove(path)
    db_path = createdb()

    # Test data for incidents
    incidents = [
        ['8/1/2024 / 0:04', '2024-00055419', '1345 W LINDSEY ST', 'Traffic Stop', 'OK0140200'],
        ['8/1/2024 / 23:50', '2024-00055698', '2920 CHAUTAUQUA AVE', '911 Call Nature Unknown', 'OK0140200'],
        ['8/1/2024 / 23:38', '2024-00055692', 'W BOYD ST / COLLEGE AVE', 'Traffic Stop', 'OK0140200']    
        ]

    # Populate the database
    populatedb(db_path, incidents)

    # Call the status function and capture the output
    status(db_path)
    captured = capsys.readouterr()

    # Verify that the correct counts were printed
    assert "Traffic Stop|2" in captured.out
    assert "911 Call Nature Unknown|1" in captured.out


