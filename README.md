# cis6930fa24 -- Project 0 

Name: Arpita Patnaik

# Project Description 
download an incident pdf file from (https://ufdatastudio.com/cis6930fa24/assignments/project0).
Extract each incident records from the pdf file.
Create  a database using sqlite and store the records.
Display the "nature" and their total occurance count from the database on the command-line interface.

# How to install
pipenv install bs4
<br />
pipenv install pypdf


## How to run
pipenv run ...
![video](video)


## Functions
1. fetchincidents(url): Takes the url as argument
    a. Used requests library to fetch response from URL
    b. Used BeautifulSoup to parse response
    c. Used re library to find the "incident" pdf in the html. 
    d. Stored the content in a new pdf file. 
2. extractincidents(incident_data): Takes incident_data as argument
    a. Read data from the pdf file using PdfReader
    b. Single line and multiple line RegEx patterns are used to parse incident data records
    c. Return the list consisting of results tuples
3. createdb():
    a. Dreates a database using sqlite3
4. populatedb(db, incidents): Takes the database and incidents list as arguments
    a. Add the values from incidents tuple to the database using sqlite3
5. status(db): takes the database as an argument
    a. selects all the natures and print nature with its number in "{natuer} | {count}" format.

    

## Database Development
We store the database in /resource/normanpd.db
Used sqlite3 to create a database with columns incident_time, incident_number, incident_location, nature and incident_ori.

## Bugs and Assumptions
1. We will consider the first incident file in the whole website.
2. We use the "https://www.normanok.gov/" infront of the fetched "href" value to find the pdf file link.
3. The Stored PDF file name is "Daily_Incident_Summary.pdf"
4. We have assumed that the date is in appropriate month, date and year range as well as the time.
5. In the incident file 2024-08-01_daily_incident_summary.pdf file, the code expects the text lines only on the begining and end of it. Rest of the information are supposed to be records.
6. Stored the 2024-08-01_daily_incident_summary.pdf from url to the pdf file, for testing our code
