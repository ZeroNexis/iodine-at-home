# 第三方库
import re
import time
import acme
import acme.errors
import httpx
import josepy
import asyncio
import datetime
import cryptography
import acme.challenges
import acme.crypto_util
import cryptography.utils
import cryptography.x509
from josepy.jwk import JWKRSA
from acme import client, messages
from acme import client as acme_client
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

# 本地库
import core.const as const
from core.config import config


class CloudFlareAPI:
    def __init__(self, email: str, api_token: str, zone_id: str):
        self.email = email
        self.api_token = api_token
        self.zone_id = zone_id
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": const.user_agent,
            "Authorization": f"Bearer {self.api_token}",
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def get_all_records(self):
        async with httpx.AsyncClient() as client:
            data = await client.get(
                f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records",
                headers=self.headers,
            )
        if data.status_code == 200:
            result = list(data.json()["result"])
            return result
        else:
            return None

    async def create_record(
        self, name: str, type: str, content: str, ttl: int = 60, proxied=False
    ):
        async with httpx.AsyncClient() as client:
            data = await client.post(
                f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records",
                headers=self.headers,
                json={
                    "type": type,
                    "name": name,
                    "content": content,
                    "ttl": ttl,
                    "proxied": proxied,
                },
            )
        if data.status_code == 200:
            return data.json()
        else:
            return None

    async def delete_record(self, record_id: str):
        async with httpx.AsyncClient() as client:
            data = await client.delete(
                f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/{record_id}",
                headers=self.headers,
            )
        if data.status_code == 200:
            return data.json()
        else:
            return None

    async def update_record(
        self,
        record_id: str,
        name: str,
        type: str,
        content: str,
        ttl: int = 60,
        proxied=False,
    ):
        async with httpx.AsyncClient() as client:
            data = await client.patch(
                f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/{record_id}"
            )
        if data.status_code == 200:
            return data.json()
        else:
            return None

    async def get_certificate(self, domain: str):
        key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096
        )  # 生成一个 RSA 密钥对

        ssl_key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096
        )  # 生成一个 RSA 密钥对

        private_key_pem = ssl_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )  # 将私钥转换为 PEM 格式

        account_key = JWKRSA(key=key)  # 创建一个 ACME 账户密钥对

        net = acme_client.ClientNetwork(
            account_key
        )  # 创建一个网络对象，用于与 ACME 服务器通信

        # 获取 ACME 目录
        directory = messages.Directory.from_json(
            net.get("https://acme-v02.api.letsencrypt.org/directory").json()
        )

        client = acme_client.ClientV2(directory, net)  # 创建一个 ACME 客户端

        # 注册账号
        registration = client.new_account(
            messages.NewRegistration.from_data(
                email=config.get("cluster-certificate.email"),
                terms_of_service_agreed=True,
            )
        )

        csr_pem = acme.crypto_util.make_csr(private_key_pem, [domain])  # 创建 CSR

        order = client.new_order(csr_pem)  # 创建新订单
        order_authorizations = order.authorizations  # 获取订单的授权列表
        for authorizations in order_authorizations:
            challenges_list = authorizations.body.challenges
            for challenge in challenges_list:
                if isinstance(challenge.chall, acme.challenges.DNS01):
                    dns_challenge = challenge
                    dns_challenge_chall = challenge.chall
                    break

            validation = dns_challenge_chall.validation(account_key)
            create_result = await self.create_record(
                f"_acme-challenge.{domain}", "TXT", validation
            )
            id = create_result["result"]["id"]

            # 等待一段时间让DNS记录传播
            time.sleep(30)  # 可能需要更长的时间，取决于 DNS 提供商

            # 使用ACME客户端回答DNS-01挑战
            response = dns_challenge_chall.response(account_key)
            client.answer_challenge(dns_challenge, response)
            deadline = datetime.datetime.now() + datetime.timedelta(seconds=60)
            try:
                finalize_order = client.poll_and_finalize(order, deadline)

            except acme.errors.ValidationError:
                finalize_order = None
            await self.delete_record(record_id=id)
            break
        if finalize_order is None:
            return None, None
        else:
            return finalize_order.fullchain_pem, private_key_pem.decode()


cf_client = CloudFlareAPI(
    config.get("cloudflare.email"),
    config.get("cloudflare.api-token"),
    config.get("cloudflare.zone-id"),
)