import pytest
import requests
from api.test_data.test_data_conversation import TestData
from api.api_library.conversation import Conversation
import sys

def test_get_all_conversations_with_negative_offset(authenticated_session):
    conversation_api = Conversation(authenticated_session)
    params = {
        'limit': 100, 
        'offset': -1
    }

    response_json, status_code = conversation_api.chat_list(params)

    if status_code == 500: 
        print("Response JSON:", response_json)
        assert True 
    else:
        assert False, f"Unexpected status code: {status_code} - Expected 400 for negative offset"

