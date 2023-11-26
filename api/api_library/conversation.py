import requests
import allure


class Conversation:
    def __init__(self, session):
        self.base_url = "https://api.dev.joompers.com"
        self.session = session

    @allure.step('Get chat list')
    def chat_list(self, request_body):
        response = self.session.get(
            self.base_url + "/api/conversation/chats",
            params=request_body
        )
        status = response.status_code

        if status == 200:
            try:
                response_data = response.json()
            except JSONDecodeError:
                response_data = {"error": "Invalid JSON response"} 
        else:
            response_data = {
                "error": response.text,
                "status_code": status
            }

        return response_data, status

