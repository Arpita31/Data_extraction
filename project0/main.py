# Example main.py
import argparse

import project0 as project

def main(url):
    # Download data
    incidents = None
    incident_data = project.fetchincidents(url)

    # Extract data
    incidents = project.extractincidents(incident_data)
	
    # Create new database
    db = project.createdb()
	
    # Insert data
    project.populatedb(db, incidents)
	
    # Print incident counts
    project.status(db)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary url.")
     
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
