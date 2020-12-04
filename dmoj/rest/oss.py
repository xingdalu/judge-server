import json
import os
import time

from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest
import oss2


class OssService:

    def __init__(self, key: str, secret: str, bucket_name: str, role_arn: str, role_session_name: str,
                 region_id: str = 'cn-hangzhou'):
        self.key = key
        self.secret = secret
        self.bucket_name = bucket_name
        self.region_id = region_id
        self.time = None
        self.duration = 60 * 15
        self.endpoint = 'https://oss-cn-hangzhou.aliyuncs.com'
        self.role_arn = role_arn
        self.role_session_name = role_session_name

    def _check_auth(self):
        if not self.time or self.time + self.duration < time.time() - 5:
            self._auth()
            self.time = time.time()

    def _auth(self):
        token = self.get_token()
        self.auth = oss2.StsAuth(token['AccessKeyId'], token['AccessKeySecret'], token['SecurityToken'])
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)

    def get_token(self):
        clt = client.AcsClient(self.key, self.secret, self.region_id)

        req = AssumeRoleRequest.AssumeRoleRequest()
        req.set_accept_format('json')
        req.set_RoleArn(self.role_arn)
        req.set_RoleSessionName(self.role_session_name)
        req.set_DurationSeconds(self.duration)
        try:
            body = clt.do_action_with_exception(req)
            j = json.loads(body)
        except (ValueError, TypeError):
            raise ValueError('failed init oss client')
        token = j.get('Credentials')
        if not token:
            raise ValueError('failed init oss client')
        return token

    def download(self, object_key: str) -> bytes:
        self._check_auth()
        result = self.bucket.get_object(object_key)
        return result.read()


oss_client = OssService(os.environ.get('OSS_KEY'), os.environ.get('OSS_SECRET'),
                        os.environ.get('OSS_BUCKET_NAME'),
                        os.environ.get('OSS_ROLE_ARN'), 'oj-downloader')
