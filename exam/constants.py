USER_ALREADY_EXISTS = "users already exists."
USER_CREATED_SUCCESSFULLY = "users created successfully."
EXAM_PREFIX_NOT_FOUND = "Exam prefix not found!"
MISSING_REQUIRED_FIELD = 'Missing required value {}'
ALREADY_LOGGED_IN = 'Already logged in'
INVALID_CREDENTIALS = 'Invalid credentials'
USERNAME_MISSING = 'Username is missing in payload'
USER_NOT_LOGGED_IN = 'User not logged in / or invalid token'


class CustomRedisException(Exception):
    def __init__(self):
        pass
