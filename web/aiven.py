import pymysql
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
from math import ceil

timeout = 10

def read_first_line(filename):
    try:
        with open(filename, 'r') as file:
            first_line = file.readline()
        return first_line
    except FileNotFoundError:
        return f"The file {filename} does not exist."
    except Exception as e:
        return f"An error occurred: {e}"

def connect():
 passwd=read_first_line("../cntrfiles/aiven.txt").strip()
 connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="defaultdb",
  host="mysql-debe0f5-tonyjacobk-250a.j.aivencloud.com",
  password=passwd,
  read_timeout=timeout,
  port=19398,
  user="avnadmin",
  write_timeout=timeout,
)
 return connection

def create_db():  
 try:
  connection=connect()
  cursor = connection.cursor()
  cursor.execute("""CREATE TABLE reports (
  company VARCHAR(100),
  broker VARCHAR(100),
  URL VARCHAR(255),
  recommendation VARCHAR(10),
  target DECIMAL(10, 2),
  report_date DATE,
  site VARCHAR(50),
  PRIMARY KEY (company, broker, report_date)
);""")
 finally:
  connection.close()

def row_exists(broker,company,date):
    query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM {table_name}
            WHERE broker = %s AND company = %s AND report_date = %s
        ) AS row_exists
    """

    cursor.execute(query, (broker,company,date))
    result = cursor.fetchone()
def row_exists_no_comp(broker,recom,target):
    found=[]
    query = f"""
            SELECT *
            FROM reports
            WHERE  recommendation = %s AND broker =%s AND target = %s
    """
    connection=connect()
    cursor=connection.cursor()
    cursor.execute(query, (recom,broker,target))
    for row in cursor:
     found.append(row)
    return (found)  
def get_rows(pageNo,per_page):
    mysql=connect()
    cursor=mysql.cursor()
    per_page = 20
    cur = mysql.cursor()
    cur.execute("SELECT COUNT(*) FROM reports")
    total_rows = cur.fetchone()['COUNT(*)']
    total_pages = ceil(total_rows / per_page)
    offset = (pageNo - 1) * per_page
    cur.execute(f"SELECT * FROM reports ORDER BY report_date DESC,broker  LIMIT 20 OFFSET %s", (offset) )
    data = cur.fetchall()
    cursor.close()
    return data,total_pages
def get_broker(pageNo,per_page,broker):
    mysql=connect()
    cursor=mysql.cursor()
    per_page = 20
    cur = mysql.cursor()
    cur.execute("SELECT COUNT(*) FROM reports where broker= %s",(broker))
    total_rows = cur.fetchone()['COUNT(*)']
    total_pages = ceil(total_rows / per_page)
    offset = (pageNo - 1) * per_page
    cur.execute(f"SELECT * FROM reports where broker = %s ORDER BY report_date DESC  LIMIT 20 OFFSET %s", (broker,offset) )
    data = cur.fetchall()
    cursor.close()
    return data,total_pages


def insert_into_database(data_list, site):
 """
 Inserts data into a MySQL database.

 Parameters:
 - data_list: A list of dictionaries containing data.
 - site: The site to insert into the database.
 - db_config: A dictionary with MySQL connection settings.

 Returns:
 - None
 """
 logger.info("Adding reports from %s into DB",site)
 try:
 # Establish a connection
  cnx =connect() 
  cursor = cnx.cursor()
 
  mysql_data_str=""  
  for data in data_list:
 # Convert report date to MySQL date format
   report_date_str = data['report-date'].rstrip('.') # Remove trailing dot
# Convert to MySQL date format (YYYY-MM-DD)
   mysql_date_str = datetime.strptime(report_date_str, "%B %d, %Y").strftime("%Y-%m-%d")

 # Prepare data for insertion
   insert_data = (
   data['Company'],
   data['broker'],
   data['link'],
   data['recommendation'],
   data['target'],
   mysql_date_str,
   site
 )
 
 # SQL query
   query = ("INSERT IGNORE INTO reports  (company, broker, URL, recommendation, target, report_date, site) "
 "VALUES (%s, %s, %s, %s, %s, %s, %s)")

 # Execute the query
   cursor.execute(query, insert_data)

 # Make sure data is committed to the database
   cnx.commit()

   print("Data inserted successfully.")

 except pymysql.connect.Error as err:
   logger.error("Could not add this report %s",data)
   logger.error("Something went wrong: %s",str(err))

 finally:
 # Close the cursor and connection
  if 'cursor' in locals():
   cursor.close()
  if 'cnx' in locals():
   cnx.close()


