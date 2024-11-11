from aws_config import users_table

def register_user(username, password, user_type):
    """
    Registers a new user in the DynamoDB Users table.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.
        user_type (str): The type of user (Push, Pull, Both).

    Returns:
        bool: True if the user was registered successfully, False otherwise.
    """
    try:
        # Check if the user already exists
        response = users_table.get_item(Key={'username': username})
        
        if 'Item' in response:
            return False  # User already exists
        
        # Add the new user
        users_table.put_item(
            Item={
                'username': username,
                'password': password,
                'user_type': user_type,
            }
        )
        return True  # User registered successfully
    except Exception as e:
        print(f"Error registering user: {e}")
        return False

def authenticate_user(username, password):
    """
    Authenticates a user by checking their credentials.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        dict: User information if authentication is successful, None otherwise.
    """
    try:
        response = users_table.get_item(Key={'username': username})

        # Check if the user exists and password matches
        if 'Item' in response and response['Item']['password'] == password:
            return response['Item']  # Return user data if authenticated
        else:
            return None  # Authentication failed
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None
