from http import HTTPStatus
from unittest.mock import MagicMock, patch

from allauth.socialaccount.providers.oauth.client import OAuth


def test_query_passes_method_before_url():
    """Regression test: sess.request() must receive method as the first
    positional-or-keyword arg, not url.  Previously url was passed first,
    which caused ``TypeError: Session.request() got multiple values for
    argument 'method'``."""

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK

    mock_session = MagicMock()
    mock_session.request.return_value = mock_response
    mock_session.__enter__ = MagicMock(return_value=mock_session)
    mock_session.__exit__ = MagicMock(return_value=False)

    mock_request = MagicMock()
    mock_request.session = {
        "oauth_api.example.com_access_token": {
            "oauth_token": "tok",
            "oauth_token_secret": "sec",
        }
    }

    oauth = OAuth(
        request=mock_request,
        consumer_key="ck",
        secret_key="cs",
        request_token_url="https://api.example.com/oauth/request_token",
    )

    with patch(
        "allauth.socialaccount.providers.oauth.client.get_adapter"
    ) as mock_get_adapter:
        mock_get_adapter.return_value.get_requests_session.return_value = mock_session
        oauth.query("https://api.example.com/me", method="GET")

    mock_session.request.assert_called_once()
    _, kwargs = mock_session.request.call_args
    assert kwargs["method"] == "get"
    assert kwargs["url"] == "https://api.example.com/me"
