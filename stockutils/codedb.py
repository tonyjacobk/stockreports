import pymysql
from file_utils import read_first_line
import logging
logger = logging.getLogger(__name__)
timeout = 10
class CodeClient:
 def __init__(self):
  self.conn=self.connect()
  self.cursor=self.conn.cursor()
  print("CodeDB Init")

 def connect(self):
  passwd=read_first_line("cntrfiles/aiven.txt").strip()
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




 def get_comp(self,code):
      query = f"""
            SELECT company
            FROM codes
            WHERE code  = %s
           """
      cursor.execute(query, (code))
      result = cursor.fetchone()
      print(code,result)
 def field_exists(self,var,field):

    query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM codes
            WHERE {field}  = %s
        ) AS row_exists
    """
    cursor.execute(query, (var))
    result = cursor.fetchone()
    return result 
      

 def insert_into_codedb(self,comp_name, code):
  logger.info("Adding codes to  DB %s  %s",comp_name,code)
  try:
 
    query = ("INSERT  INTO codes  (company, code) "
 "VALUES (%s, %s)")

 # Execute the query
    insert_data=(comp_name,code)
    self.cursor.execute(query, insert_data)
    self.conn.commit()


  except pymysql.connect.Error as err:
    logger.error("Could not add this report %s",data)
    logger.error("Something went wrong: %s",str(err))

 def create_dictionary(self):
    data_dict = {}
    self.cursor.execute("SELECT code, company FROM codes")
    rows = self.cursor.fetchall()
    # Populate dictionary
    for row  in rows:
        data_dict[row['code']] = row['company']

    return data_dict


 def check_num(self):
    query = f"SELECT COUNT(*) FROM codes;"
    cursor.execute(query)
    # Fetch the result (which will be a single row containing the count)
    result = cursor.fetchone()
    print(result)
    total_rows = result[0]
    print(total_rows) 

coddb=CodeClient()
