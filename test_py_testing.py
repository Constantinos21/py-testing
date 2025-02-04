import requests
import os
from utils import delete_api_key
from utils import delete_uploaded_file


MORFBOT_API_URL = "http://161.97.127.38:90/api/v1"



def test_upload(normal_user_token_headers):
    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json"
    }

    file_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "csv": "text/csv",
        "epub": "application/epub+zip"
    }

    base_path = "C:/Users/User/Downloads/py-testing/py-testing/"

    for ext, mime_type in file_types.items():
        file_path = os.path.join(base_path, f"small_file.{ext}")

        if not os.path.exists(file_path):
            print(f"Skipping {file_path} (file not found)")
            continue
        # Open all small files with the tested extensions
        with open(file_path, "rb") as file:
            files = {"file": (f"small_file.{ext}", file, mime_type)}
            data = {
                "is_menu": "false",
                "is_private": "true",
                "org_id": "abc123",
                "auto_process": "false",
            }
        #upload the files
            response = requests.post(
                f"{MORFBOT_API_URL}/chats/uploadfile/",
                headers=headers,
                files=files,
                data=data
            )

            assert response.status_code == 200, f"Upload failed for {file_path}"

            response_json = response.json()
            assert "file" in response_json
            assert response_json["file"]["org_id"] == "abc123"

            file_id = response_json["file"]["id"]
            delete_uploaded_file(file_id, headers)

#################################################################


def test_delete_upload(normal_user_token_headers): 
    category = "file"  
    file_id = "159b4001-4959-441d-9b39-55e20d65fcd1" 

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json",
    }
    # Check if file exists
    check_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/{file_id}",
        headers=headers
    )
    
    print(f"Check File Response Code: {check_response.status_code}")
    print(f"Check File Response Body: {check_response.text}")

    if check_response.status_code != 200:
        print("Error: File not found, skipping deletion.")
        return  
    # delete response if file exists
    delete_response = requests.delete(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/{file_id}",
        headers=headers
    )

    assert delete_response.status_code == 200, f"Unexpected response: {delete_response.text}"

    verify_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/{file_id}",
        headers=headers
    )


    assert verify_response.status_code == 404, "File was not deleted successfully."

#################################################################

def test_uploaded_files(normal_user_token_headers):

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json"
    }
    params = {
        "org_id": "abc123", 
        "status": "uploaded",  
        "skip": 0,  
        "limit": 5  
    }
    category = "file"

    response = requests.get(
        f"{MORFBOT_API_URL}/chats/uploads/{category}",
        headers=headers,
        params=params
    )
    assert response.status_code == 200

    response_json = response.json()

    assert "data" in response_json
    assert "count" in response_json

    assert len(response_json["data"]) > 0

    first_file = response_json["data"][0]
    assert first_file["status"] == "uploaded"
    assert first_file["org_id"] == "abc123"
    assert first_file["is_private"] is True


################################################################


def test_read_upload_info(normal_user_token_headers):
    category = "file"  
    file_id = "159b4001-4959-441d-9b39-55e20d65fcd1"  

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json",
    }

    list_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}",
        headers=headers
    )

    if list_response.status_code != 200:
        print("Error: File not found in the system.")
        return

    response = requests.get(f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/{file_id}", headers=headers)

    assert response.status_code == 200, f"Unexpected response: {response.text}"

    response_json = response.json()
    assert "filename" in response_json, "Missing 'filename' key in response"
    assert "status" in response_json, "Missing 'status' key in response"
    assert isinstance(response_json["filename"], str), "'filename' should be a string"

##########################################################################

def test_read_store_menu_data(normal_user_token_headers):
    file_id = "2f5f4930-dd43-499d-98a4-5e96fe6f36cf"  

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json",
    }

    list_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/file",
        headers=headers
    )

    if list_response.status_code != 200:
        print("Error: File list could not be retrieved.")
        return

    upload_data = list_response.json()
    file_exists = any(file["id"] == file_id and file.get("is_menu") for file in upload_data)

    if not file_exists:
        print(f"Error: File {file_id} is not marked as a menu file or does not exist.")
        return

    response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/menufile/{file_id}",
        headers=headers
    )

    assert response.status_code == 200, f"Unexpected response: {response.text}"

    response_json = response.json()
    assert "menu" in response_json, "Missing 'menu' key in response"
    assert isinstance(response_json["menu"], list), "Menu data should be a list"

    if response_json["menu"]:  
        menu_item = response_json["menu"][0]
        assert "category_name" in menu_item, "Missing 'category_name' in menu item"
        assert "item_name" in menu_item, "Missing 'item_name' in menu item"
        assert "item_price" in menu_item, "Missing 'item_price' in menu item"

##################################################################

def test_start_processing(normal_user_token_headers):
    category = "file"  
    file_id = "fdc777fd-0fa4-498e-b6dc-040d64c638f2" 

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json",
    }

    check_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/{file_id}",
        headers=headers
    )

    if check_response.status_code != 200:
        print("Error: File not found, cannot start processing.")
        return  

    file_data = check_response.json()
    
    if file_data.get("status") == "processed":
        print(f"File '{file_id}' is already processed, skipping processing.")
        return  

    process_response = requests.post(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/process/{file_id}",
        headers=headers
    )

    assert process_response.status_code == 200, f"Unexpected response: {process_response.text}"

    verify_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/{file_id}",
        headers=headers
    )
    verify_data = verify_response.json()
    
    assert verify_data.get("status") == "processed", "File was not processed successfully."

###############################################################################
def test_cancel_upload(normal_user_token_headers):
    category = "file"  
    store_id = "eef22993-a684-4f73-9ccd-21193d42790d"
    document_name = "vegan menu.pdf"

    headers = {
        "Authorization": f"Bearer {normal_user_token_headers['access_token']}",
        "accept": "application/json",
    }

    check_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}",
        headers=headers
    )

    if check_response.status_code != 200:
        print("Error: Could not retrieve uploads list, skipping cancellation.")
        return  

    upload_data = check_response.json()
    file_exists = any(
        file.get("item_name_ai") == document_name and file.get("org_id") == store_id
        for file in upload_data
    )

    if not file_exists:
        print(f"Error: Document '{document_name}' not found in store '{store_id}', skipping cancellation.")
        return  

    cancel_response = requests.delete(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}/cancel/{store_id}/{document_name}",
        headers=headers
    )

    assert cancel_response.status_code == 200, f"Unexpected response: {cancel_response.text}"

    verify_response = requests.get(
        f"{MORFBOT_API_URL}/api/v1/chats/uploads/{category}",
        headers=headers
    )

    verify_data = verify_response.json()
    still_exists = any(
        file.get("item_name_ai") == document_name and file.get("org_id") == store_id
        for file in verify_data
    )

    assert not still_exists, "File was not canceled successfully."

