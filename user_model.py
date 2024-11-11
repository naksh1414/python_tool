# user_model.py

class User:
    def __init__(self, user_id, username, password, access_level, upload_limit=None, bucket_access=None, folder_access=None):
        self.user_id = user_id  # Unique ID for the user
        self.username = username  # Username
        self.password = password  # Password (consider hashing)
        self.access_level = access_level  # 'push', 'pull', or 'both'
        self.upload_limit = upload_limit  # Upload limit (optional, e.g., in MB or GB)
        self.bucket_access = bucket_access if bucket_access is not None else []  # List of accessible buckets (optional)
        self.folder_access = folder_access if folder_access is not None else []

    def to_dict(self):
        """Convert the User object to a dictionary for DynamoDB."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,  # Make sure to hash this in a real app
            'access_level': self.access_level,
            'upload_limit': self.upload_limit,
            'bucket_access': self.bucket_access,
            'folder_access': self.folder_access,
        }
