import json
import os
import ast
import sys
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
from flask import Flask, render_template, request, redirect, url_for
sys.path.append("..")
from cntrfiles import brokers
from stockutils import create_dic,check_if_present,db,get_last_ndays_data,res

FILE_PATH = '/home/ubuntu/stockreports/pdfanalysis'

app = Flask(__name__)


def initialize_logger ():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',filename='/tmp/testapp.log', level=logging.INFO)

def read_data(file_path):
    """
    Reads a file containing a Python list of dictionaries
    and returns it as a Python object.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return ast.literal_eval(content) if content else []

def save_data(pdftext):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(repr(pdftext))

def delete_files_not_needed(oldlist,new_list):
    lookup=  {
    (d["broker"],  d["Company"]) for d in new_list} 
    for entry in oldlist:
     if (entry['broker'],entry['Company']) not in lookup:
         print (entry['Company'] ," is duplicate")
         res.delete_a_key(entry['link'])

def delete_marked_files(pdftext):
 delete_list=[]
 for  i  in range (len(pdftext)-1,-1,-1):
  row=pdftext[i]
  if row['delete']:
   delete_list.append(i)
 for i in delete_list:
  print(pdftext[i]['link'])
  res.set_a_value(pdftext[i]['link'])
  pdftext.pop(i)

def is_a_good_row(row,rtype):
  print(row)
  mrow=["broker","company","date","recommendation","target_price","link"]
  if rtype=="sector":
    mrow=["broker","date","link"]
  for i in mrow:
      if row[i] =="" or not row[i]:
        return False
  return True

def classifier(pdftext):
   delete_list=[]
   complist=[]
   for  i  in range (len(pdftext)-1,-1,-1):
     row=pdftext[i]
     if row.get('delete'):
       res.set_a_value(pdftext[i]['link'])
       delete_list.append(i)
       continue
     if row.get('sector'):
      if is_a_good_row(row,"sector"):
        row=[{"company":row["text"].split("||")[0],"site":"tel","link":row['link'],"report-date":row['date'],"broker":row['broker']}]
        db.insert_into_sector(row)
        delete_list.append(i)
        continue
     if is_a_good_row(row,"company"):
       mydict={"Company": row['company'],
                    "link": row['link'],
                    "report-date": datetime.strptime(row['date'],'%Y-%m-%d').date(),
                    "broker":row['broker'],
                    "recommendation":row['recommendation'],
                    "target":row['target_price'] }
       complist.append(mydict)
       delete_list.append(i)
   return complist,delete_list


def main_func():
 pdftext=read_data(FILE_PATH)
 complist,dellist=classifier(pdftext)
 new_list=check_if_present(complist,"telgram")
 delete_files_not_needed(complist,new_list) 
 db.insert_into_database(new_list,"tel")
 print ("Deleting ..",len(dellist))
 for i in dellist:
   pdftext.pop(i)
 save_data(pdftext)

def unique_brokers(brokers):
    return list(sorted(dict.fromkeys(d.values())))






@app.route('/')
def index():
    entries = read_data(FILE_PATH)
    return render_template('index.html', entries=entries,brkrs=BRKRS)

@app.route('/process', methods=['POST'])
def save():
    # Retrieve lists of data from the form
    ids = request.form.getlist('id')
    texts = request.form.getlist('text')
    brokers = request.form.getlist('broker')
    companies = request.form.getlist('company')
    dates = request.form.getlist('date')
    recommendations = request.form.getlist('recommendation')
    targets = request.form.getlist('target_price')
    links = request.form.getlist('link')
    updated_data = []
    for i in range(len(ids)):
        current_id =ids[i]
        is_delete_checked = f"delete_{current_id}" in request.form
        is_sector_checked = f"sector_{current_id}" in request.form
        entry = {
            "id": ids[i],
            "text": texts[i],
            "broker": brokers[i],
            "company": companies[i],
            "date": dates[i],
            "recommendation": recommendations[i],
            "target_price": targets[i],
            "link": links[i],
            "delete": is_delete_checked,  # True or False
            "sector": is_sector_checked   # True or False
        }
        updated_data.append(entry)
    action = request.form.get('action')
    print("Action is ",action)
    if action == 'save_file':
        (updated_data)
        print("Successfully saved to /tmp/pdfanalysis", "success")
        save_data(updated_data)
    elif action == 'update_db':
        save_data(updated_data)
        main_func()
        print("Database updated successfully!", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    initialize_logger()
    get_last_ndays_data(20)
    BRKRS= list(dict.fromkeys(brokers.values()))
    app.run(host='0.0.0.0',debug=True,port=5500)
