from mega import Mega
import logging
logger = logging.getLogger(__name__)
class MegaManager:
    def __init__(self, email=None, password=None):
        """Initialize the MegaManager and log in (optionally with credentials)."""
        self.mega = Mega()
        self.email = email
        self.password = password
        self.user = None

        if email and password:
            self.login(email, password)
        else:
            self.login_anonymous()

    def login(self, email, password):
        """Login to a MEGA account using email and password."""
        try:
            self.user = self.mega.login(email, password)
            print(f"✅ Logged in as {email}")
        except Exception as e:
            print(f"❌ Login failed: {e}")

    def login_anonymous(self):
        """Login to MEGA anonymously (no credentials)."""
        try:
            self.user = self.mega.login()
            print("✅ Logged in anonymously")
        except Exception as e:
            print(f"❌ Anonymous login failed: {e}")

    def upload_file(self, file_path):
        """Upload a file to MEGA and return the public link."""
        try:
            fpath="/tmp/comp.pdf"
            file = self.mega.upload(fpath,dest_filename=file_path)
            link = self.mega.get_upload_link(file)
            print(f"✅ File uploaded successfully!\n🔗 Link: {link}")
            return link
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None

    def download_file(self, file, destination_path=None):
        """Download a file from MEGA (by handle or path)."""
        try:
            self.mega.download(file, dest_filename=destination_path)
            print(f"✅ File downloaded to {destination_path or 'current directory'}")
        except Exception as e:
            print(f"❌ Download failed: {e}")
    def upload_sector_file(self,file_path):
     try:
            fpath="/tmp/comp.pdf"
            file = self.mega.upload(fpath,dest_filename="sector:"+file_path)
            link = self.mega.get_upload_link(file)
            print(f"✅ File uploaded successfully!\n🔗 Link: {link}")
            return link
     except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None

    def list_files(self):
        """List all files in your MEGA root directory."""
        try:
            files = self.mega.get_files()
            for file_id, file_info in files.items():
                print(file_info['a']['n'])  # File name
            return files
        except Exception as e:
            print(f"❌ Failed to list files: {e}")
            return None
    def get_a_link(self,node):
        return self.mega.get_link(node)

    def delete_Name(self,fileName):
      file=self.mega.find(fileName)
      file_id=None
      if not file:
        print ("File details about '{fileName}' could not be found")
        logger.info("Could not get file Object for %s",fileName)
        return -1
      file_id,filed = file
      if not file_id:
        print ("File ID for   '{fileName}' could not be found ")
        logger.info("Could not get file_id for %s from file Object",fileName)
        return -1

      p= self.mega.delete(file_id)
      if p==0:
       print(f"File '{fileName}' deleted successfully.")
       logger.info("FileName %s deleted Successfully",fileName)
       return 1
      return -1

    def delete_url(self,myurl):
     name=self.get_file_Name_from_url(myurl.strip())

     if name:
        logger.info("Got fileName: %s from URL: %s",name,myurl)
        c=self.delete_Name(name)
        return c
     else:
          print("Could not find file Name from this URL ",myurl)
          logger.info("Could not get fileName for URL %s:",myurl)
          return -2

    def get_file_Name_from_url(self,URL):
     try:
      p= self.mega.get_public_url_info(URL)
      return(p['name'])
     except Exception as E:
      print("Could not find file from this URL %s",URL)
      return None

    def empty_trash(self):
     try:
       print("Emptying trash...")
       self.mega.empty_trash()
       print("Trash emptied successfully!")
       return 1
     except Exception as e:
       print(f"An error occurred: {e}")
       return -1
MegaMan=MegaManager("tonyjacobk@gmail.com","Seemu@2002")
