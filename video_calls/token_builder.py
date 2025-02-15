# -*- coding: utf-8 -*-
__copyright__ = "Copyright (c) 2014-2024 Agora.io, Inc."

import os
import sys
import time
import logging
from django.conf import settings
from agora_token_builder import RtcTokenBuilder as AgoraRtcTokenBuilder

logger = logging.getLogger(__name__)

# Role constants from Agora SDK
Role_Publisher = 1  # Host
Role_Subscriber = 2  # Audience

# Token expiration constants (in seconds)
TOKEN_EXPIRATION_IN_SECONDS = 3600  # 1 hour
JOIN_CHANNEL_PRIVILEGE_EXPIRATION_IN_SECONDS = 3600  # 1 hour
PUB_AUDIO_PRIVILEGE_EXPIRATION_IN_SECONDS = 3600  # 1 hour
PUB_VIDEO_PRIVILEGE_EXPIRATION_IN_SECONDS = 3600  # 1 hour
PUB_DATA_STREAM_PRIVILEGE_EXPIRATION_IN_SECONDS = 3600  # 1 hour

class RtcTokenBuilder:
    # Version length and version number
    VERSION_LENGTH = 3
    VERSION = "007"

    @staticmethod
    def build_token_with_uid(app_id, app_certificate, channel_name, uid, role, token_expiration_in_seconds=TOKEN_EXPIRATION_IN_SECONDS, privilege_expiration_in_seconds=None):
        """
        Build the token with user id.
        Args:
            app_id: The App ID issued to you by Agora
            app_certificate: The App Certificate issued to you by Agora
            channel_name: The channel name that the token is valid for
            uid: The user id
            role: The user role, 1 for publisher, 2 for subscriber
            token_expiration_in_seconds: Token expiration time in seconds
            privilege_expiration_in_seconds: Privilege expiration time in seconds
        Returns:
            The token string
        """
        try:
            if not privilege_expiration_in_seconds:
                privilege_expiration_in_seconds = token_expiration_in_seconds

            # Get current timestamp
            current_timestamp = int(time.time())
            
            # Calculate expiration timestamps
            token_expire = current_timestamp + token_expiration_in_seconds
            privilege_expire = current_timestamp + privilege_expiration_in_seconds

            # Use the installed agora-token-builder package
            token = AgoraRtcTokenBuilder.buildTokenWithUid(
                app_id,
                app_certificate,
                channel_name,
                uid,
                role,
                token_expire
            )

            logger.info(f"Generated Agora token for channel: {channel_name}, uid: {uid}, expiry: {token_expire}")
            return token

        except Exception as e:
            logger.error(f"Failed to build token with uid: {str(e)}")
            raise

    @staticmethod
    def build_token_with_user_account(app_id, app_certificate, channel_name, account, role, token_expiration_in_seconds=TOKEN_EXPIRATION_IN_SECONDS, privilege_expiration_in_seconds=None):
        """
        Build the token with user account.
        Args:
            app_id: The App ID issued to you by Agora
            app_certificate: The App Certificate issued to you by Agora
            channel_name: The channel name that the token is valid for
            account: The user account
            role: The user role, 1 for publisher, 2 for subscriber
            token_expiration_in_seconds: Token expiration time in seconds
            privilege_expiration_in_seconds: Privilege expiration time in seconds
        Returns:
            The token string
        """
        try:
            if not privilege_expiration_in_seconds:
                privilege_expiration_in_seconds = token_expiration_in_seconds

            # Get current timestamp
            current_timestamp = int(time.time())
            
            # Calculate expiration timestamps
            token_expire = current_timestamp + token_expiration_in_seconds
            privilege_expire = current_timestamp + privilege_expiration_in_seconds

            return RtcTokenBuilder.build_token_with_user_account_and_privilege(
                app_id=app_id,
                app_certificate=app_certificate,
                channel_name=channel_name,
                account=account,
                token_expiration_in_seconds=token_expire,
                join_channel_privilege_expiration_in_seconds=privilege_expire,
                pub_audio_privilege_expiration_in_seconds=privilege_expire,
                pub_video_privilege_expiration_in_seconds=privilege_expire,
                pub_data_stream_privilege_expiration_in_seconds=privilege_expire
            )
        except Exception as e:
            logger.error(f"Failed to build token with user account: {str(e)}")
            raise

    @staticmethod
    def build_token_with_uid_and_privilege(app_id, app_certificate, channel_name, uid, token_expiration_in_seconds,
                                         join_channel_privilege_expiration_in_seconds, pub_audio_privilege_expiration_in_seconds,
                                         pub_video_privilege_expiration_in_seconds, pub_data_stream_privilege_expiration_in_seconds):
        """
        Build the token with user id and privilege.
        Args:
            app_id: The App ID issued to you by Agora
            app_certificate: The App Certificate issued to you by Agora
            channel_name: The channel name that the token is valid for
            uid: The user id
            token_expiration_in_seconds: Token expiration time in seconds
            join_channel_privilege_expiration_in_seconds: Join channel privilege expiration time in seconds
            pub_audio_privilege_expiration_in_seconds: Publish audio privilege expiration time in seconds
            pub_video_privilege_expiration_in_seconds: Publish video privilege expiration time in seconds
            pub_data_stream_privilege_expiration_in_seconds: Publish data stream privilege expiration time in seconds
        Returns:
            The token string
        """
        try:
            # Import required modules from RtcTokenBuilder2
            from src.RtcTokenBuilder2 import RtcTokenBuilder as RtcTokenBuilder2
            from src.RtcTokenBuilder2 import Role_Publisher, Role_Subscriber

            return RtcTokenBuilder2.buildTokenWithUid(
                app_id,
                app_certificate,
                channel_name,
                uid,
                Role_Publisher,
                token_expiration_in_seconds,
                token_expiration_in_seconds
            )
        except Exception as e:
            logger.error(f"Failed to build token with uid and privilege: {str(e)}")
            raise

    @staticmethod
    def build_token_with_user_account_and_privilege(app_id, app_certificate, channel_name, account,
                                                  token_expiration_in_seconds, join_channel_privilege_expiration_in_seconds,
                                                  pub_audio_privilege_expiration_in_seconds, pub_video_privilege_expiration_in_seconds,
                                                  pub_data_stream_privilege_expiration_in_seconds):
        """
        Build the token with user account and privilege.
        Args:
            app_id: The App ID issued to you by Agora
            app_certificate: The App Certificate issued to you by Agora
            channel_name: The channel name that the token is valid for
            account: The user account
            token_expiration_in_seconds: Token expiration time in seconds
            join_channel_privilege_expiration_in_seconds: Join channel privilege expiration time in seconds
            pub_audio_privilege_expiration_in_seconds: Publish audio privilege expiration time in seconds
            pub_video_privilege_expiration_in_seconds: Publish video privilege expiration time in seconds
            pub_data_stream_privilege_expiration_in_seconds: Publish data stream privilege expiration time in seconds
        Returns:
            The token string
        """
        try:
            # Import required modules from RtcTokenBuilder2
            from src.RtcTokenBuilder2 import RtcTokenBuilder as RtcTokenBuilder2
            from src.RtcTokenBuilder2 import Role_Publisher, Role_Subscriber

            return RtcTokenBuilder2.buildTokenWithAccount(
                app_id,
                app_certificate,
                channel_name,
                account,
                Role_Publisher,
                token_expiration_in_seconds,
                token_expiration_in_seconds
            )
        except Exception as e:
            logger.error(f"Failed to build token with user account and privilege: {str(e)}")
            raise

    @staticmethod
    def build_token_with_rtm(app_id, app_certificate, channel_name, account, role, token_expiration_in_seconds, privilege_expiration_in_seconds):
        """
        Build the token with RTM.
        Args:
            app_id: The App ID issued to you by Agora
            app_certificate: The App Certificate issued to you by Agora
            channel_name: The channel name that the token is valid for
            account: The user account
            role: The user role, 1 for publisher, 2 for subscriber
            token_expiration_in_seconds: Token expiration time in seconds
            privilege_expiration_in_seconds: Privilege expiration time in seconds
        Returns:
            The token string
        """
        try:
            # Import required modules from RtcTokenBuilder2
            from src.RtcTokenBuilder2 import RtcTokenBuilder as RtcTokenBuilder2
            from src.RtcTokenBuilder2 import Role_Publisher, Role_Subscriber

            return RtcTokenBuilder2.buildTokenWithUid(
                app_id,
                app_certificate,
                channel_name,
                account,
                Role_Publisher,
                token_expiration_in_seconds,
                privilege_expiration_in_seconds
            )
        except Exception as e:
            logger.error(f"Failed to build token with RTM: {str(e)}")
            raise 