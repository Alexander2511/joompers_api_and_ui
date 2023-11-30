import pytest
from api.api_library.user_account import UserAccount
import requests
from api.api_library.conversation import Conversation
from api.test_data.test_data_user_account import TestData
from api.support.temporary_email_generator import EmailAndPasswordGenerator

import pytest
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Loading required variables from the .env file
VALID_EMAIL = os.environ.get("VALID_EMAIL")
VALID_PASSWORD = os.environ.get("VALID_PASSWORD")
# CLIENT_ID = os.environ["CLIENT_ID"]
# CLIENT_SECRET = os.environ["CLIENT_SECRET"]
# SCOPE = os.environ.get("SCOPE", "")

@pytest.fixture(scope="session")
def authenticated_session():
    session = requests.Session()
    # Data preparation for the query
    login_data = {
        "grant_type": "password",
        "username": VALID_EMAIL,
        "password": VALID_PASSWORD,
        # "scope": SCOPE,
        # "client_id": CLIENT_ID,
        # "client_secret": CLIENT_SECRET
    }

    # Executing the login request
    response = session.post(
        "https://api.dev.joompers.com/api/login/oauth",
        data=login_data
    )

    # Checking for a successful response status
    assert response.status_code == 200, f"Failed to log in: {response.text}"

    # Retrieving the access token and adding it to the session headers.
    access_token = response.json().get("access_token")
    session.headers.update({"Authorization": f"Bearer {access_token}"})

    return session

#fixture to get chat_id
@pytest.fixture(scope="session")
def chat_id_session():
    session = requests.Session()
    login_data = {
        "grant_type": "password",
        "username": VALID_EMAIL,
        "password": VALID_PASSWORD,
    }

    response = session.post(
        "https://api.dev.joompers.com/api/login/oauth",
        data=login_data
    )

    assert response.status_code == 200, f"Failed to log in: {response.text}"
    access_token = response.json().get("access_token")
    session.headers.update({"Authorization": f"Bearer {access_token}"})

    return session

@pytest.fixture(scope="session")
def chat_id(chat_id_session):
    conversation_api = Conversation(chat_id_session)
    response_json, status_code = conversation_api.chat_list({"limit": 100, "offset": 0})
    assert status_code == 200, "Failed to retrieve chat list"
    return response_json[0]['chatInfo']['id']

# fixture that returns a session of specific user being authorized (with credentials provided in test_data_user_account.py)
# to use - just mention it as a parameter of test,

# to use it - just mention the fixture as a parameter of test
# and later, inside the test itself, you can run API-calls on this session

# EXAMPLE of how to use fixture in test:
#     def test_user_log_out_positive(self, user_logged_in_session_fixture, test_data):
#         api = UserAccount(user_logged_in_session_fixture)  # create an instance of some class from API-library with session from fixture
#         response_body, status = api.user_logout() # now all requests done in the session of authorized user
@pytest.fixture()
def user_logged_in_session_fixture():
    session = requests.Session()
    api = UserAccount(session)
    response_body, status = api.log_in_with_email(TestData.valid_user_credentials[0]["email"], TestData.valid_user_credentials[0]["password"])
    access_token = response_body.get("access_token")
    session.headers.update({"Authorization": f"Bearer {access_token}"})
    return session


# TODO: not tested yet!
# fixture that returns a session without any user being authorized
@pytest.fixture()
def user_not_logged_in_session_fixture():
    session = requests.Session()
    return session


# TODO: not tested yet!
# fixture that (before executing a test itself!):

# - generates email and password
# - registers a user with the credentials generated before
# - logs into a user account created
# - returns: 1) session of this user being authorized 2) email of the user account 3) password of the user account
# 4) profile ID of the user 5) role of the user in system 6) status of the user 7) access token already used in session

# and (after executing the test!):
# - delete user account
# - delete email that was generated and used to create user account

# to use fixture in test - just mention it as a parameter of test
# to get values that returned by fixture in test - just address to them as regular variables, like that:

# EXAMPLE of how to use fixture in test:
# def test_example(new_user_logged_in_session_fixture):
#     # Obtain values returned by the fixture
#     session, email, password, user_profile_id, user_role, user_status = new_user_logged_in_session_fixture
#
#     # Your test logic here, using the obtained values...
#     # For example:
#     assert user_role == "admin", "User should have admin role"
#     assert user_status == "active", "User should be active"
#
#     # No need to clean up or tear down here; it's handled by the fixture

@pytest.fixture()
def new_user_logged_in_session_and_data_fixture():
    email_and_password_generator = EmailAndPasswordGenerator()
    email, password = email_and_password_generator.generate_email_and_password()

    session = requests.Session()
    user_account_api = UserAccount(session)

    request_create_user = user_account_api.user_registration(email, password)
    response_body, status = request_create_user
    assert status == 201, "Error with request to register user. Try again"

    # request_email_verify = session.post(
    #     "https://api.dev.joompers.com/api/email/request_email_verify",
    #     json={"email": email}
    # )
    # assert request_email_verify.status_code == 200


    token_to_confirm_email_for_registration = email_and_password_generator.get_token_from_confirmation_link_for_registration()
    assert token_to_confirm_email_for_registration is not None
    request_confirm_email_for_registration = session.get(
        f"https://api.dev.joompers.com/api/email/confirm_email/{token_to_confirm_email_for_registration}"
    )  # TODO write a method in API library for that
    assert request_confirm_email_for_registration.status_code == 200, "Error with confirm email for registration. Try again"

    request_log_in_with_email = user_account_api.log_in_with_email(email, password)
    # print(f"Response for request_log_in_with_email: {request_log_in_with_email}")
    response_body, status = request_log_in_with_email
    assert status == 200, "Error with request to log in user. Try again"

    user_profile_id = response_body.get("user_profile_id")
    user_role = response_body.get("user_role")
    user_status = response_body.get("user_status")
    access_token = response_body.get("access_token")

    session.headers.update({"Authorization": f"Bearer {access_token}"})  # by that we update session, so now the user is logged in

    yield session, email, password, user_profile_id, user_role, user_status
    # ALL THE CODE ABOVE will be automatically executed before test itself (where this fixture is used)

    # ALL THE CODE BELOW will be executed after test itself
    request_log_in_with_email = user_account_api.log_in_with_email(email, password)
    response_body, status = request_log_in_with_email
    assert status == 200, "Error with request to log in user. Try again"
    access_token = response_body.get("access_token")
    session.headers.update(
        {"Authorization": f"Bearer {access_token}"})  # by that we update session, so now the user is logged in

    request_delete_user = user_account_api.request_delete_user()
    # print(f"Response for request_delete_user: {request_delete_user}")
    status = request_delete_user[1]
    assert status == 200, "Error with request to start delete user. Try again"
    print(f"User (with email \'{email}\' and password \'{password}\' was successfully deleted")

    confirmation_code_for_delete_user_from_email = email_and_password_generator.get_confirmation_code_for_delete_user()
    assert confirmation_code_for_delete_user_from_email is not None, "Error with getting confirmation code from email to delete user. Try again"
    request_confirm_delete_user = user_account_api.delete_user(confirmation_code_for_delete_user_from_email)
    status = request_confirm_delete_user[1]
    assert status == 200, "Error with request to complete delete user. Try again"

    email_and_password_generator.delete_email_generated()  # assertion for successful deletion of user is done inside




















