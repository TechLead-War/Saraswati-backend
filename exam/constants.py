USER_ALREADY_EXISTS = "users already exists."
USER_CREATED_SUCCESSFULLY = "users created successfully."
EXAM_PREFIX_NOT_FOUND = "Exam prefix not found!"
MISSING_REQUIRED_FIELD = '{} is required'
ALREADY_LOGGED_IN = 'Already logged in'
INVALID_CREDENTIALS = 'Invalid credentials'


class CustomRedisException(Exception):
    def __init__(self):
        pass
