from flask import Flask, render_template
from aiven import get_rows,get_broker
import urllib.parse
app = Flask(__name__)
rows_per_page=20
# MySQL configurations
@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    data,total_pages=get_rows(page,20)
    return render_template('index.html', data=data, page=page, total_pages=total_pages)
@app.route('/brk/<brok>')
@app.route('/brk/<brok>/<int:page>')
def search_broker(brok,page=1):
    brok=urllib.parse.unquote(brok)
    print(brok)
    data,total_pages=get_broker(page,rows_per_page,brok)
    return render_template('index.html', data=data, page=page, total_pages=total_pages,broker=brok)
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)


