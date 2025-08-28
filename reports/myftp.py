import ftplib
import datetime
import sys
def upload_file(src,dest):
 clean=False 
 ftp = None
 try:
    ftp = ftplib.FTP('ftpupload.net')
    ftp.login('if0_39747564', 'Simansy2022')
    ftp.cwd('/') # Change to the directory containing the file
    ftp.encoding = "utf-8" # Optional: force UTF-8 encoding

    with open(src, 'rb') as file:
        ftp.storbinary(f'STOR {dest}', file)
        clean=True 
 except ftplib.all_errors as e:
    print(f"FTP Error: {e}")
 except FileNotFoundError:
    print(f"Error: Local file '{local_file_path}' not found.")
 finally:
    if 'ftp' in locals() and ftp.sock: # Check if ftp object exists and socket is open
        ftp.quit()
    if clean:
        return True
    return False

def upload_log():
 dat=datetime.datetime.now().date()
 fname="log"+str(dat)
 c=upload_file('/tmp/myapp.log',fname)
 if c:
     sys.exit(0)
 else:
     sys.exit(1)
upload_log()
