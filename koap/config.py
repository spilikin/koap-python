from typing import Optional
from urllib.parse import urljoin
from pydantic import BaseSettings, SecretStr
from enum import Enum


class AuthMethod(str, Enum):
    basic = 'basic'
    cert = 'cert'


class ConnectorConfig(BaseSettings):
    base_url: str
    mandant_id: str
    client_system_id: str
    workplace_id: str
    user_id: str
    trustchain: Optional[str] = None

    auth_method: AuthMethod | str = 'basic'
    
    auth_basic_username: Optional[str] = None
    auth_basic_password: Optional[SecretStr] = None

    auth_cert_p12_filename: Optional[str] = None
    auth_cert_p12_password: Optional[SecretStr] = None

    # Danger zone
    danger_verify_tls: bool = True

    def construct_url(self, path: str) -> str:
        return urljoin(self.base_url, path)

    class Config:
        env_prefix = 'konnektor_'
