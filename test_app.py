import json
import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
import urllib.request

import app


class TestAppUnit(unittest.TestCase):
    @patch('urllib.request.Request', MagicMock(return_value='mock_request'))
    @patch('app.transform_response', MagicMock())
    def test_make_request_invokes_request_with_expected_endpoint_and_header(self):
        app.make_request('http://www.example.com/api', 'token')
        urllib.request.Request.assert_called_with('http://www.example.com/api', headers= {
            'Circle-Token': 'token',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    @patch('urllib.request.Request', MagicMock(return_value='mock_request'))
    @patch('app.transform_response', MagicMock())
    def test_transform_response_is_invoked_with_expected_request(self):
        app.make_request('http://www.example.com/api', 'token')
        app.transform_response.assert_called_with('mock_request')

    def test_transform_response_invokes_urlopen_with_expected_request(self):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def read(self):
                return json.dumps(self.json_data)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_json_data = {
                'foo': 'bar'
            }
            mock_urlopen.return_value = MockResponse(
                json_data=mock_json_data,
                status_code=200
            )
            app.transform_response('expected_request')
            urllib.request.urlopen.assert_called_with('expected_request')

    def test_transform_returns_expected_json_as_dict(self):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def read(self):
                return json.dumps(self.json_data)

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_json_data = {
                'foo': 'bar'
            }
            mock_urlopen.return_value = MockResponse(
                json_data=mock_json_data,
                status_code=200
            )
            self.assertEqual(app.transform_response('expected_request'), mock_json_data)

    @patch('app.make_request', MagicMock(return_value={'items': 'expected'}))
    def test_pipelines_res_invokes_make_request_with_expected_endpoint(self):
        app.pipelines_res('expected_project_slug', 'expected_circle_token')
        app.make_request.assert_called_with(
            'https://circleci.com/api/v2/project/expected_project_slug/pipeline',
            'expected_circle_token'
        )

    @patch('app.make_request', MagicMock(return_value={'items': 'expected'}))
    def test_pipelines_res_returns_dict_with_items(self):
        self.assertEqual(
            app.pipelines_res('expected_project_slug', 'expected_circle_token'),
            'expected'
        )


class TestAppMain(unittest.TestCase):
    circle_token_envvar = 'circle_token_envvar'
    slack_app_url_env_var = 'slack_app_url_env_var'
    gh_token_env_var = 'gh_token_env_var'
    cancel_msg = 'cancel_msg'
    org = 'org'
    repo = 'repo'
    circle_token = 'circle_token'
    slack_app_url = 'slack_app_url'
    gh_token = 'gh_token'
    threshold_seconds = '30'
    alert_threshold_user = '5'
    alert_threshold_build = '10'

    test_pipeline_fixture_data = [{
            "id": "79501a5a-0225-42e2-a9b0-a1c6941a1bdc",
            "errors": [],
            "project_slug": "gh/annapamma/sandbox",
            "updated_at": "2020-06-05T16:59:35.704Z",
            "number": 431,
            "state": "created",
            "created_at": "2020-06-05T16:59:35.704Z",
            "trigger": {
                "received_at": "2020-06-05T16:59:35.665Z",
                "type": "webhook",
                "actor": {
                    "login": "annapamma",
                    "avatar_url": "https://avatars1.githubusercontent.com/u/22031658?v=4"
                }
            },
            "vcs": {
                "origin_repository_url": "https://github.com/annapamma/sandbox",
                "target_repository_url": "https://github.com/annapamma/sandbox",
                "revision": "65e8dbda23734c6919b90c7e317049342cec6e0c",
                "provider_name": "GitHub",
                "commit": {
                    "body": "",
                    "subject": "test"
                },
                "branch": "test-no-pr"
            }
        }, {
            "id": "4dccabbc-0c85-4e29-b694-dcb3c8ceb62f",
            "errors": [],
            "project_slug": "gh/annapamma/sandbox",
            "updated_at": "2020-06-05T16:58:40.630Z",
            "number": 430,
            "state": "created",
            "created_at": "2020-06-05T16:58:40.630Z",
            "trigger": {
                "received_at": "2020-06-05T16:58:40.588Z",
                "type": "webhook",
                "actor": {
                    "login": "annapamma",
                    "avatar_url": "https://avatars1.githubusercontent.com/u/22031658?v=4"
                }
            },
            "vcs": {
                "origin_repository_url": "https://github.com/annapamma/sandbox",
                "target_repository_url": "https://github.com/annapamma/sandbox",
                "revision": "f1adb7e0c3f6b3bdbd12b274e00f150b304b8095",
                "provider_name": "GitHub",
                "commit": {
                    "body": "",
                    "subject": "test"
                },
                "branch": "test-no-pr"
            }
        }]

    def setUp(self):
        os.environ['SLACK_MONITOR_CIRCLE_TOKEN_ENVVAR'] = self.circle_token_envvar
        os.environ[self.circle_token_envvar] = self.circle_token
        os.environ['SLACK_MONITOR_SLACK_APP_URL_ENVVAR'] = self.slack_app_url_env_var
        os.environ[self.slack_app_url_env_var] = self.slack_app_url
        os.environ['SLACK_MONITOR_GITHUB_TOKEN_ENVVAR'] = self.gh_token_env_var
        os.environ[self.gh_token_env_var] = self.gh_token
        os.environ['CANCEL_MESSAGE'] = self.cancel_msg
        os.environ['SLACK_MONITOR_CIRCLE_PROJECT_ORG'] = self.org
        os.environ['SLACK_MONITOR_CIRCLE_PROJECT_REPONAME'] = self.repo
        os.environ['SLACK_MONITOR_PARAM_THRESHOLD_SECONDS'] = self.threshold_seconds
        os.environ['SLACK_MONITOR_PARAM_THRESHOLD_MAX_BUILDS_PER_USER'] = self.alert_threshold_user
        os.environ['SLACK_MONITOR_PARAM_THRESHOLD_MAX_BUILDS'] = self.alert_threshold_build

    def test_env(self):
        self.assertEqual(os.getenv('SLACK_MONITOR_CIRCLE_TOKEN_ENVVAR'), self.circle_token_envvar)

    @patch('app.pipelines_res', MagicMock(return_value=test_pipeline_fixture_data))
    def test_pipeline_res_in_main_invoked_with_expected_params(self):
        app.main()
        app.pipelines_res.assert_called_with(f'gh/{self.org}/{self.repo}', self.circle_token)

    @patch('app.pipelines_res', MagicMock(return_value=test_pipeline_fixture_data))
    def test_k_actor_v_created_arr_returns_expected_arr(self):
        expected = {
            'annapamma': [
                datetime.fromisoformat('2020-06-05T16:59:35.704'),
                datetime.fromisoformat('2020-06-05T16:58:40.630')
            ]
        }
        self.assertEqual(app.func_k_actor_v_created_arr(app.pipelines_res()), expected)


if __name__ == '__main__':
    unittest.main()

# create one instance of alert status
# create one instance of no alert status
# mock post
