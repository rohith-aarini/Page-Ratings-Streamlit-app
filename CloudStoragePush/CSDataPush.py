from google.cloud import storage
from google.oauth2 import service_account

class DataPush:
    def __init__(self,key_path=""):
        self.KEY_PATH = key_path
    
    def initial_connect(self,key_info:dict):
        # Explicitly create credentials and pass them to the Storage client
        credentials = service_account.Credentials.from_service_account_info(
            # self.KEY_PATH,
            info = key_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        # Initialize a client
        self.client = storage.Client(credentials=credentials)
        # self.client = storage.Client()
    
    def get_bucket(self,bucket_name):
        # Get the specified bucket
        self.bucket = self.client.get_bucket(bucket_name)

    def push_data_to_blob(self,folder_name,file_path):
        """
        folder_name: str = object path. Example = folder/file name with extension
        """
        # Get the specified blob
        target_blob = self.bucket.blob(folder_name)
        target_blob.upload_from_string(file_path,content_type='text/csv')

    def close_client(self):
        self.client.close()