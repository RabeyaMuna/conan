import time
from datetime import timedelta

import jwt
import pytest
from jwt import DecodeError

from conans.server.crypto.jwt.jwt_credentials_manager import JWTCredentialsManager


def test_jwt_manager():
    # Instance the manager to generate tokens that will be valid for immediate checks
    manager = JWTCredentialsManager(secret="1234asdf", expire_time=timedelta(seconds=5))

    # Encrypt a profile
    token = manager.get_token_for("myuser")

    # Decrypt the profile
    assert "myuser" == manager.get_user(token)
    with pytest.raises(DecodeError):
        manager.get_user("invalid_user")

    # Create a short-lived token to deterministically test expiration
    short_manager = JWTCredentialsManager(
        secret="1234asdf", expire_time=timedelta(seconds=1)
    )
    short_token = short_manager.get_token_for("myuser")

    # Now wait 2 seconds and check that the short-lived token is expired
    time.sleep(2)
    with pytest.raises(jwt.ExpiredSignatureError):
        short_manager.get_user(short_token)
