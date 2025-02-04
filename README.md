# py-testing

Files for automated tests for the Morfbot API using Python and pytest.


# 1. test_py_testing.py

These are thr test cases to verify the functionality of the Morfbot API:

Uploading files of various formats.

Deleting uploaded files.

Checking the status of uploaded files.

Reading file information.

Verifying store menu data.

Initiating and canceling file processing.

# 2. utils.py

This file provides helper functions to interact with the API, including:

delete_api_key(id, headers): Deletes an API key

delete_uploaded_file(file_id, headers): Deletes an uploaded file by its ID.

# 3. conftest.py

This file sets up fixtures for pytest, including:

normal_user_token_headers(): Provides authentication headers for test requests.

 # Requirements

Python 3.xx

pytest

requests


