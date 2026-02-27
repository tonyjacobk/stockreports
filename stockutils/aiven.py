import pymysql
from datetime import datetime,date,timedelta
import logging
import contvar
import re
logger = logging.getLogger(__name__)
from .file_utils import read_first_line
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


 def broker_company_reports_in_last_few_days(self,days,nsecode,broker,date1):
  start_date = date1 -timedelta(days=days)
  end_date = date1 + timedelta(days=days)
  print("NseCode: "+nsecode+" Broker: "+broker)
  print (date1)
  query = """
        SELECT company, NSEKEY, broker, URL, recommendation, target, report_date, site
        FROM reports
        WHERE NSEKEY = %s
          AND broker = %s
          AND report_date BETWEEN %s AND %s
    """

  self.cursor.execute(query, (nsecode,broker,start_date,end_date)) 
  results=self.cursor.fetchall()
  return results

 def get_last_n_day_data(self,days,date1):
  print("getting N days data",days)
  start_date = date1 -timedelta(days=days)
  end_date = date1 + timedelta(days=days)
  query="""
        SELECT NSEKEY, broker, URL 
        FROM reports
        wHERE report_date BETWEEN %s AND %s
    """
  self.cursor.execute(query, (start_date,end_date))
  results=self.cursor.fetchall()
  return results

 def get_last_ndays_sector_data(self,days,date1):
  start_date = date1 -timedelta(days=days)
  end_date = date1 + timedelta(days=days)
  query="""
        SELECT company 
        FROM gen_reports
        wHERE report_date BETWEEN %s AND %s
    """
  self.cursor.execute(query, (start_date,end_date))
  results=self.cursor.fetchall()
  return results




 def row_exists(self,broker,company,date):
    query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM {table_name}
            WHERE broker = %s AND company = %s AND report_date = %s
        ) AS row_exists
    """

    self.cursor.execute(query, (broker,company,date))
    result = self.cursor.fetchone()

 def row_exists_no_comp(self,broker,recom,target):
    found=[]
    query = f"""
            SELECT *
            FROM reports
            WHERE  recommendation = %s AND broker =%s AND target = %s
    """
    self.cursor.execute(query, (recom,broker,target))
    for row in self.cursor:
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

 def find_no_code(self):
  try:
   query = f"""
     SELECT * FROM reports WHERE NSEKEY is NULL or NSEKEY=''
    """
   self.cursor.execute(query)
   clist =""
   for i in self.cursor:
       clist=clist+i["company"]+","
   return clist
  except pymysql.connect.Error as err:
   print(str(err))
   logger.error("Something went wrong while finding No code list: %s",str(err))
   return ""

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
  print("Data list",data_list)

  try:
 # Establish a connection
   mysql_data_str=""  
   for data in data_list:
 # Convert report date to MySQL date format
    if isinstance(data['report-date'],date):
         mysql_date_str=data['report-date'].strftime("%Y-%m-%d")
    else:
     report_date_str = data['report-date'].rstrip('.') # Remove trailing dot
# Convert to MySQL date format (YYYY-MM-DD)
     mysql_date_str = datetime.strptime(report_date_str, "%B %d, %Y").strftime("%Y-%m-%d")
    if "RR" in data.keys() and not data["RR"]:  ## IDBI has RR true for individual 
     realname=data['Company']
     code="SECTOR"
    else:
     realname=data['Company']
     code=data['code']
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

 def insert_into_sector(self,datalist):
  if contvar.testrundb==1 :
     logger.info("testrundb=1 .. Will not be saving to DB")
     return
  for data in datalist:
   insert_data = (
    data["company"],
    data['broker'],
    data['link'],
    data['report-date'],
    data['site']
 )
   query = ("INSERT IGNORE INTO gen_reports  (company,  broker, URL,report_date, site) "
 "VALUES (%s, %s, %s, %s, %s)")
   self. cursor.execute(query, insert_data)
   self.conns.commit()
   print("Data inserted successfully.")
 
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
