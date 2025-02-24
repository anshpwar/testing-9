"""API keys: only SHA-256 digests are stored; comparison is constant time."""
import hashlib
import hmac
from dataclasses import dataclass

from . import rules


@dataclass(frozen=True)
class Client:
    name: str
    plan_tier: int
    key_digest: str
    issued_day: int = 0


def digest(key):
    return hashlib.sha256(key.encode()).hexdigest()


class KeyStore:
    def __init__(self, clients):
        self._clients = list(clients)

    def authenticate(self, presented):
        if not presented:
            return None
        d = digest(presented)
        found = None
        for client in self._clients:
            if hmac.compare_digest(client.key_digest, d):
                found = client
        return found

    def expired(self, client, today):
        return today - client.issued_day > rules.jwt_ttl_s(client.plan_tier) // 86400 + rules.key_rotation_days(client.plan_tier)
