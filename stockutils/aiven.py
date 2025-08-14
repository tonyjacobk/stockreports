import pymysql
from datetime import datetime
import logging
import contvar
logger = logging.getLogger(__name__)
from file_utils import read_first_line
from .create_dic import get_comp_code
timeout = 10

class DBClient:
 def __init__(self):
  self.conns=self.connection()
  self.cursor=self.conns.cursor()
  print("DB Init")

 def connection(self):
  passwd=read_first_line("cntrfiles/aiven.txt").strip()
  print (passwd)
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




 def row_exists(self,broker,company,date):
    query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM {table_name}
            WHERE broker = %s AND company = %s AND report_date = %s
        ) AS row_exists
    """

    self.cursor.execute(query, (broker,company,date))
    result = cursor.fetchone()

 def row_exists_no_comp(self,broker,recom,target):
    found=[]
    query = f"""
            SELECT *
            FROM reports
            WHERE  recommendation = %s AND broker =%s AND target = %s
    """
    self.cursor.execute(query, (recom,broker,target))
    for row in cursor:
     found.append(row)
    return (found)  

 def update_name_and_code(self,old_name,new_name,code):
  print ("In inside aiven",old_name,new_name,code)
  try:
   query = f"""
            UPDATE reports 
            SET company = %s ,NSEKEY = %s
            WHERE  company = %s
    """
   print(old_name)
   self.cursor.execute(query,(new_name,code,old_name))
   print ("Reached")
   self.conns.commit()
  except pymysql.connect.Error as err:
   print(str(err))
   logger.error("Could not add this report %s",data)
   logger.error("Something went wrong: %s",str(err))
 

 def insert_into_database(self,data_list, site):
  """
  Inserts data into a MySQL database.

  Parameters:
  - data_list: A list of dictionaries containing data.
  - site: The site to insert into the database.
  - db_config: A dictionary with MySQL connection settings.

  Returns:
  - None
  """
  if contvar.testrundb==1 :
     logger.info("testrundb=1 .. Will not be saving to DB")
     return
  logger.info("Adding reports from %s into DB",site)
  try:
 # Establish a connection
   mysql_data_str=""  
   for data in data_list:
 # Convert report date to MySQL date format
    report_date_str = data['report-date'].rstrip('.') # Remove trailing dot
# Convert to MySQL date format (YYYY-MM-DD)
    mysql_date_str = datetime.strptime(report_date_str, "%B %d, %Y").strftime("%Y-%m-%d")
    realname,code=get_comp_code( data['Company'])
 # Prepare data for insertion
    insert_data = (
    realname,
    code,
    data['broker'],
    data['link'],
    data['recommendation'],
    data['target'],
    mysql_date_str,
    site
 )
 
 # SQL query
    query = ("INSERT IGNORE INTO reports  (company, NSEKEY, broker, URL, recommendation, target, report_date, site) "
 "VALUES (%s, %s, %s, %s, %s, %s, %s,%s)")

 # Execute the query
    self. cursor.execute(query, insert_data)


 # Make sure data is committed to the database
    self.conns.commit()

    print("Data inserted successfully.")

  except pymysql.connect.Error as err:
   logger.error("Could not add this report %s",insert_data)
   logger.error("Something went wrong: %s",str(err))


 def insert_into_codedb(self,comp_name, code):
  logger.info("Adding reports from %s into DB %s  %s",comp_name,code)
  try:

   query = ("INSERT  INTO codes  (company, code) "
 "VALUES (%s, %s)")

   insert_data=(comp_name,code)
   self.cursor.execute(query, insert_data)
   self.conns.commit()


  except pymysql.connect.Error as err:
   logger.error("Could not add this company  %s",insert_data)
   logger.error("Something went wrong: %s",str(err))




db= DBClient()
