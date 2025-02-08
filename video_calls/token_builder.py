import base64
import hmac
import json
import struct
import time
import zlib
from hashlib import sha256
from django.conf import settings

class AgoraTokenBuilder:
    VERSION_LENGTH = 3
    VERSION = "007"

    @staticmethod
    def _pack_uint16(x):
        return struct.pack('<H', int(x))

    @staticmethod
    def _pack_uint32(x):
        return struct.pack('<I', int(x))

    @staticmethod
    def _pack_string(string):
        return struct.pack('<I', len(string)) + string.encode('utf-8')

    @staticmethod
    def build_token_with_uid(app_id, app_certificate, channel_name, uid, role, privilege_expired_ts):
        """
        Build the token with user id.
        Args:
            app_id: The App ID issued to you by Agora
            app_certificate: The App Certificate issued to you by Agora
            channel_name: The channel name that the token is valid for
            uid: The user id
            role: The user role, 1 for publisher, 2 for subscriber
            privilege_expired_ts: Timestamp when the privilege expires
        Returns:
            The token string
        """
        # Prepare the message
        message = {
            "app_id": app_id,
            "channel_name": channel_name,
            "uid": str(uid),
            "role": role,
            "ts": int(time.time()),
            "salt": int(time.time() * 1000) % 100000,
            "privileges": {
                "join_channel": privilege_expired_ts,
                "publish_audio_stream": privilege_expired_ts,
                "publish_video_stream": privilege_expired_ts,
                "publish_data_stream": privilege_expired_ts,
            }
        }

        # Convert message to bytes
        message_bytes = json.dumps(message, separators=(',', ':')).encode('utf-8')

        # Compress the message
        compressed = zlib.compress(message_bytes)

        # Calculate signature
        signature = hmac.new(
            app_certificate.encode('utf-8'),
            compressed,
            sha256
        ).digest()

        # Combine version, signature length, signature, and compressed message
        packed_msg = (
            AgoraTokenBuilder.VERSION.encode('utf-8') +
            struct.pack('>I', len(signature)) +
            signature +
            compressed
        )

        # Base64 encode
        b64_token = base64.b64encode(packed_msg).decode('utf-8')

        return b64_token

    @staticmethod
    def verify_token(token, app_certificate):
        """
        Verify if a token is valid.
        Args:
            token: The token string
            app_certificate: The App Certificate used to generate the token
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Decode base64
            decoded = base64.b64decode(token)

            # Extract version
            version = decoded[:AgoraTokenBuilder.VERSION_LENGTH].decode('utf-8')
            if version != AgoraTokenBuilder.VERSION:
                return False

            # Extract signature length
            sig_len = struct.unpack('>I', decoded[AgoraTokenBuilder.VERSION_LENGTH:AgoraTokenBuilder.VERSION_LENGTH + 4])[0]

            # Extract signature and message
            signature = decoded[AgoraTokenBuilder.VERSION_LENGTH + 4:AgoraTokenBuilder.VERSION_LENGTH + 4 + sig_len]
            message = decoded[AgoraTokenBuilder.VERSION_LENGTH + 4 + sig_len:]

            # Verify signature
            expected_sig = hmac.new(
                app_certificate.encode('utf-8'),
                message,
                sha256
            ).digest()

            return hmac.compare_digest(signature, expected_sig)

        except Exception:
            return False 