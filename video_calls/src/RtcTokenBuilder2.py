# -*- coding: utf-8 -*-
__copyright__ = "Copyright (c) 2014-2024 Agora.io, Inc."

import hmac
from hashlib import sha256
import base64, zlib
import struct
import random
import time
import sys

# Role definitions
Role_Publisher = 1  # for live broadcaster
Role_Subscriber = 2  # default, for live audience

# Service type
ServiceRtc = 1

# Privilege definitions
PrivilegeJoinChannel = 1
PrivilegePublishAudioStream = 2
PrivilegePublishVideoStream = 3
PrivilegePublishDataStream = 4

VERSION_LENGTH = 3
APP_ID_LENGTH = 32

def get_version():
    return '007'

def pack_uint16(x):
    return struct.pack('<H', int(x))

def pack_uint32(x):
    return struct.pack('<I', int(x))

def pack_int32(x):
    return struct.pack('<i', int(x))

def pack_string(string):
    return pack_uint16(len(string)) + string.encode('utf-8')

def pack_map_uint32(m):
    ret = pack_uint16(len(m))
    for k, v in m.items():
        ret += pack_uint16(k) + pack_uint32(v)
    return ret

def pack_service_type(service_type):
    return pack_uint16(service_type)

def pack_privileges(privileges):
    return pack_map_uint32(privileges)

class Service:
    def __init__(self, service_type):
        self.__type = service_type
        self.__privileges = {}

    def __pack_type(self):
        return pack_service_type(self.__type)

    def add_privilege(self, privilege, expire):
        self.__privileges[privilege] = expire

    def __pack_privileges(self):
        return pack_privileges(self.__privileges)

    def pack(self):
        return self.__pack_type() + self.__pack_privileges()

class ServiceRtc:
    def __init__(self, channel_name='', uid=0):
        self.__channel_name = channel_name
        self.__uid = uid
        self.__privileges = {}

    def __pack_channel_name(self):
        return pack_string(self.__channel_name)

    def __pack_uid(self):
        return pack_uint32(self.__uid)

    def add_privilege(self, privilege, expire):
        self.__privileges[privilege] = expire

    def __pack_privileges(self):
        return pack_privileges(self.__privileges)

    def pack(self):
        return self.__pack_channel_name() + self.__pack_uid() + self.__pack_privileges()

class AccessToken:
    def __init__(self, app_id='', app_certificate='', expire=900):
        random.seed(time.time())
        self.__app_id = app_id
        self.__app_cert = app_certificate
        self.__salt = random.randint(1, 99999999)
        self.__expire = expire
        self.__services = {}
        self.__service_rtc = None

    def __signing(self):
        signing = hmac.new(self.__app_cert.encode('utf-8'), digestmod=sha256)
        signing.update(self.__app_id.encode('utf-8'))
        signing.update(pack_uint32(self.__issue_ts))
        signing.update(pack_uint32(self.__expire))
        signing.update(pack_uint32(self.__salt))
        signing.update(pack_uint16(len(self.__services)))
        for _, service in self.__services.items():
            signing.update(service.pack())
        return signing.digest()

    def __pack_content(self):
        ret = pack_uint32(self.__issue_ts)
        ret += pack_uint32(self.__expire)
        ret += pack_uint32(self.__salt)
        ret += pack_uint16(len(self.__services))
        for _, service in self.__services.items():
            ret += service.pack()
        return ret

    def build(self):
        self.__issue_ts = int(time.time())
        m = self.__signing()
        version = get_version()
        content = self.__pack_content()
        signature = hmac.new(m, content, sha256).digest()
        compressed = zlib.compress(content)
        packed_signature = struct.pack('!I', len(signature)) + signature
        packed_version = version.encode('utf-8')
        return base64.b64encode(packed_version + packed_signature + compressed).decode('utf-8')

    def add_service(self, service):
        self.__services[service.__type] = service

class RtcTokenBuilder:
    @staticmethod
    def build_token_with_uid(app_id, app_certificate, channel_name, uid, role, token_expire, privilege_expire=None):
        """
        Build the RTC token with uid.
        :param app_id: The App ID issued to you by Agora. Apply for a new App ID from Agora Dashboard if it is missing from your kit.
        :param app_certificate: Certificate of the application that you registered in the Agora Dashboard.
        :param channel_name: Unique channel name for the AgoraRTC session in the string format.
        :param uid: User ID. A 32-bit unsigned integer with a value ranging from 1 to (232-1).
        :param role: Role_Publisher = 1: A broadcaster (host) in a live-broadcast profile.
                    Role_Subscriber = 2: (Default) A audience in a live-broadcast profile.
        :param token_expire: represented by the number of seconds elapsed since now. If, for example, you want to access the Agora Service within 10 minutes after the token is generated, set token_expire as 600(seconds).
        :param privilege_expire: represented by the number of seconds elapsed since now. If, for example, you want to enable your privilege for 10 minutes, set privilege_expire as 600(seconds).
        :return: The RTC token.
        """
        if not privilege_expire:
            privilege_expire = token_expire

        token = AccessToken(app_id, app_certificate, token_expire)
        service = ServiceRtc(channel_name, uid)

        service.add_privilege(PrivilegeJoinChannel, privilege_expire)
        service.add_privilege(PrivilegePublishAudioStream, privilege_expire)
        service.add_privilege(PrivilegePublishVideoStream, privilege_expire)
        service.add_privilege(PrivilegePublishDataStream, privilege_expire)

        token.add_service(service)
        return token.build()

    @staticmethod
    def build_token_with_account(app_id, app_certificate, channel_name, account, role, token_expire, privilege_expire=None):
        """
        Build the RTC token with account.
        :param app_id: The App ID issued to you by Agora. Apply for a new App ID from Agora Dashboard if it is missing from your kit.
        :param app_certificate: Certificate of the application that you registered in the Agora Dashboard.
        :param channel_name: Unique channel name for the AgoraRTC session in the string format.
        :param account: The user account.
        :param role: Role_Publisher = 1: A broadcaster (host) in a live-broadcast profile.
                    Role_Subscriber = 2: (Default) A audience in a live-broadcast profile.
        :param token_expire: represented by the number of seconds elapsed since now. If, for example, you want to access the Agora Service within 10 minutes after the token is generated, set token_expire as 600(seconds).
        :param privilege_expire: represented by the number of seconds elapsed since now. If, for example, you want to enable your privilege for 10 minutes, set privilege_expire as 600(seconds).
        :return: The RTC token.
        """
        if not privilege_expire:
            privilege_expire = token_expire

        token = AccessToken(app_id, app_certificate, token_expire)
        service = ServiceRtc(channel_name, 0)

        service.add_privilege(PrivilegeJoinChannel, privilege_expire)
        service.add_privilege(PrivilegePublishAudioStream, privilege_expire)
        service.add_privilege(PrivilegePublishVideoStream, privilege_expire)
        service.add_privilege(PrivilegePublishDataStream, privilege_expire)

        token.add_service(service)
        return token.build() 