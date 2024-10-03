import argparse

import urllib.request
from bs4 import BeautifulSoup
import re
import os
import pypdf
from pypdf import PdfReader
import sqlite3
import shutil


def fetchincidents(url):
    ''''
        Fetch HTML from URL, parse it, find an incident pdf file and store it in temp directory.
        Args: 
            url: url of the website
        Return:
            file_path: path of the downloaded pdf file
    '''
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"                          
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()
        
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(data, 'html.parser')
        
        # For all hyperlinks 
        links = soup.find_all('a')
        
        # Check for incidents PDF using regular expression and download
        for link in links:
            if link.get('href'):
                if re.search("daily_incident_summary.pdf", link.get('href')):                
                    pdf_url = urllib.parse.urljoin(url, link.get('href'))  # Handle relative URLs
                    response = urllib.request.urlopen(pdf_url)
                    temp = os.path.join(os.getcwd(), 'project0/resources')
                    file_path = os.path.join(temp, "Daily_Incident_Summary.pdf")
                    
                    if not os.path.exists(temp):
                        os.makedirs(temp)
                    
                    with open(file_path, 'wb') as pdf_file:
                        pdf_file.write(response.read())
                    
                    print(f"PDF file downloaded and saved to: {file_path}")
                    return file_path
        
        # If no PDF found
        print("No PDF file found.")
        return None
    except Exception as e:
        print(f"Incidents not found: {e}")
        return None
def extractincidents(incident_data):
    """
        Extracts the data from pdf file using PdfReader. Extracts the data using regular expression match and stores in a list.
        Args:
            incident_data: Path of the pdf file
        Return:
            all_rows: A list containing all the individual incident records
    """
    try:
        if incident_data:
            reader = PdfReader(incident_data)
        else:
            return None
        all_rows = []
        page = reader.pages[0]
        first_page = True
        last_page = len(reader.pages)


        # Pattern for matching records
        pattern = r"""(\d{1,2}/\d{1,2}/\d{4})       # Date (e.g., 8/1/2024)
                        \s+
                        (\d{1,2}:\d{2})             # Time (e.g., 1:19)
                        \s{2,}
                        (\d{4}-\d+)                 # Incident Number (e.g., 2024-00055436)
                        \s{2,}
                        (.+?)\s{2,}                 # Address
                        (.+?)\s{2,}                 # Incident Type (e.g., Traffic Stop)
                        ([A-Z0-9]+)$"""             # Final Code (e.g., OK0140200)

        # Compile the regex pattern with verbose flag for readability
        regex = re.compile(pattern, re.VERBOSE)

        # Shows the extracted text
        for page in reader.pages:
            # To eleminate the header row and extra text 
            if first_page:
                row_contents = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False).splitlines()[3:]
                first_page = False
            elif last_page == 1:
                row_contents = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False).splitlines()[:-1]
            else:
                row_contents = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False).splitlines()
            for index in range(len(row_contents)):
                row_check = regex.match(row_contents[index])
                if row_check:
                    extracted_data = [i.strip() for i  in row_check.groups()]
                    extracted_data[:2] = [' / '.join(extracted_data[:2])] # Merging the "date / time" values
                    all_rows.append(extracted_data)
                else:
                    # Multi row record adding the address
                    all_rows[-1][2] = all_rows[-1][2] + " " + row_contents[index].lstrip()
            last_page -= 1
        return all_rows
    except Exception as e:
        print(f"Incidents not extracted: {e}")
        return None

def createdb():
    """
        Creates a database in the resources directory
        Args:
        Returns:
            db_path: path for the databse.
    """
    # Define the path and database name
    # par_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    # db_directory = os.path.join(par_dir, 'resources')
    db_directory = 'resources'
    db_path = os.path.join(db_directory, 'normanpd.db')
    # Remove the directory if it exists, and recreate it
    if os.path.exists(db_directory):
        shutil.rmtree(db_directory) # Remove the existing directory and its contents

    # Create the directory
    os.makedirs(db_directory)
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE incidents ( \
                        incident_time TEXT, \
                        incident_number TEXT, \
                        incident_location TEXT, \
                        nature TEXT, \
                        incident_ori TEXT \
                    );")
        # To verify if the table ahs been created
        res = cur.execute("SELECT name FROM sqlite_master")
        print(f"Table created '{res.fetchone()[0]}'")
    return db_path

def populatedb(db, incidents):
    """
        Insert all the records into db using multiple insert.
        Args:
            db : databse path
            incidents : list of incident records form pdf file.
        Returns:

    """
    if not incidents:
        print("Incidents are not available.")
        return
    try:
        with sqlite3.connect(db) as con:
            cur = con.cursor()

            res = cur.execute("SELECT name FROM sqlite_master")
            table_name = res.fetchone()[0]

            # Insert values into db
            sql = f"INSERT INTO {table_name} VALUES(?, ?, ?, ?, ?)"
            cur.executemany(sql, incidents)
            con.commit()
    except Exception as e:
        print(f"Error database not populated: {e}")


def status(db):
    """
        Extract and print individual natures from the database and with the total number of it's occurences on the terminal.
        Args:
            db : path to the database.
    """
    try:
        with sqlite3.connect(db) as con:
            cur = con.cursor()
            res = cur.execute("SELECT name FROM sqlite_master")
            table_name = res.fetchone()[0]

            #fetch values from the table
            sql = f"SELECT nature, count(*) FROM {table_name} GROUP BY nature"

            # Execute the query
            cur.execute(sql)

            # Fetch and print the results
            results = cur.fetchall()
            print(f"fetched results = {len(results)}")
            for nature, count in results:
                print(f"{nature}|{count}")
    except Exception as e:
        print(f"Error status not retrived: {e}")

def main(url):
    # Download data
    print(url)
    incidents = None
    incident_data = fetchincidents(url)

    # Extract data
    incidents = extractincidents(incident_data)
	
    # Create new database
    db = createdb()
	
    # Insert data
    populatedb(db, incidents)
	
    # Print incident counts
    status(db)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary url.")
     
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)