
import allure
import pytest

from api.api_library.profile import Profile
from api.test_data.test_data_profile import ProfileJsonSchemas as schema, ProfileTestData as data

"""
Bug Report: BJT-132

Description:
- The API method 'follow_user' in the Profile API raises a concern. It's unclear if following regular users is intended or a bug.
- Current requirements do not specify that following should be exclusively for content creators.
- However, the Swagger UI description "Follow creator profile" implies it should be limited to creator profiles.
- This issue needs resolution to remove ambiguity.

Bug Report: BJT-133

Description:
- Misnamed remove_folower API method
- misleading error messages.
- Suggest rename to remove_follower and use "Follower not found" for non-existent followers.

Note: 
- Once resolved, tests related to this functionality will be updated accordingly.
"""




@allure.feature("Remove follower")
@allure.severity("Major")
class TestRemoveFollower:

    @pytest.mark.xfail
    def test_remove_follower_sucessfull(self, user_logged_in_session_fixture):
        authenticated_session = user_logged_in_session_fixture[0]
        profile_api = Profile(authenticated_session)
        valid_data = {
            "user_profile_id": data.other_common_user_profile_id
        }
        response_body, status_code = profile_api.remove_follower(valid_data)
        success_message = response_body.get("message")

        assert status_code == 200, f"Failed to remove follower, got {status_code} code"
        assert success_message == "Successfully removed user from followers"

    def test_repeated_remove_same_follower(self, user_logged_in_session_fixture):
        authenticated_session = user_logged_in_session_fixture[0]
        profile_api = Profile(authenticated_session)
        valid_data = {
            "user_profile_id": data.other_common_user_profile_id
        }
        response_body, status_code = profile_api.remove_follower(valid_data)
        error_message = response_body.get("message")

        assert status_code == 400,  f"Expected 400 for repeated remove, got {status_code} instead"
        assert error_message == "You don't follow this user"

    def test_remove_yourself_from_followers(self, user_logged_in_session_fixture):
        authenticated_session = user_logged_in_session_fixture[0]
        profile_api = Profile(authenticated_session)
        current_user_profile_id = user_logged_in_session_fixture[3]
        data_with_current_user_profile_id = {
            "user_profile_id": current_user_profile_id
        }
        response_body, status_code = profile_api.remove_follower(data_with_current_user_profile_id)
        error_message = response_body.get("message")

        assert status_code == 400, f"Expected 422 for removing yourself, got {status_code} instead"
        assert error_message == "You don't follow this user"

    @pytest.mark.parametrize("request_data", [
        {"user_profile_id": ""},
        {"": data.other_common_user_profile_id},
        {"user_profile_id": "abc"},
        {"abc": data.other_common_user_profile_id},
        {"user_profile_id": 123},
        {123: data.other_common_user_profile_id},
    ])
    def test_remove_follower_with_invalid_format_user_profile_id(self, user_logged_in_session_fixture, request_data):
        authenticated_session = user_logged_in_session_fixture[0]
        profile_api = Profile(authenticated_session)
        response_body, status_code = profile_api.unfollow_user(request_data)

        assert status_code == 422, f"Expected 422 invalid values, got {status_code} instead"

    @pytest.mark.parametrize("request_data", [
        {"user_profile_id": None},
        {None: data.other_common_user_profile_id},
        {None: None},
    ])
    def test_remove_follower_with_empty_values_in_request_body(self, user_logged_in_session_fixture, request_data):
        authenticated_session = user_logged_in_session_fixture[0]
        profile_api = Profile(authenticated_session)
        response_body, status_code = profile_api.unfollow_user(request_data)
        error_message = response_body["detail"][0]["msg"]

        assert status_code == 422, f"Expected 422 for empty values, got {status_code} instead"
        assert error_message == "field required"

    def test_remove_follower_with_non_existing_user_profile_id(self, user_logged_in_session_fixture):
        authenticated_session = user_logged_in_session_fixture[0]
        data_non_existing_user_profile_id = {
            "user_profile_id": data.non_existing_user_profile_id
        }
        profile_api = Profile(authenticated_session)
        response_body, status_code = profile_api.remove_follower(data_non_existing_user_profile_id)
        error_message = response_body["message"]

        assert status_code == 400, f"Expected 400 for non existing user_profile_id, got {status_code} instead"
        assert error_message == "You don't follow this user"

    def test_remove_follower_unauthorized(self, user_not_logged_in_session_fixture):
        unauthenticated_session = user_not_logged_in_session_fixture
        profile_api = Profile(unauthenticated_session)
        valid_data = {
            "user_profile_id": data.other_common_user_profile_id
        }
        response_body, status_code = profile_api.remove_follower(valid_data)
        error_message = response_body["detail"]

        assert status_code == 401, f"Expected 401 for unauthorized user, got {status_code} instead"
        assert error_message == "Not authenticated"


















