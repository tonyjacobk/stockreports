pkill -f  -9  uidb_updater.py
cd /home/ubuntu/stockreports
nohup /home/ubuntu/.venv/bin/python3 uidb_updater.py  >> /tmp/webserver_console.txt 2>&1 & 

