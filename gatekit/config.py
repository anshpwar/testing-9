"""Gateway configuration from an INI file: [route:NAME] sections and [client:NAME] sections."""
import configparser

from .auth import Client, KeyStore, digest
from .router import Route, Router


class ConfigError(ValueError):
    pass


def load(text):
    cp = configparser.ConfigParser()
    cp.read_string(text)
    routes, clients = [], []
    for section in cp.sections():
        kind, _, name = section.partition(":")
        sec = cp[section]
        if kind == "route":
            if "pattern" not in sec or "upstream" not in sec:
                raise ConfigError(f"{section}: pattern and upstream are required")
            methods = tuple(m.strip().upper() for m in sec.get("methods", "GET").split(",") if m.strip())
            routes.append(Route(sec["pattern"], sec["upstream"], methods, sec.getint("class", 1)))
        elif kind == "client":
            if "key" not in sec:
                raise ConfigError(f"{section}: key is required")
            clients.append(Client(name, sec.getint("tier", 1), digest(sec["key"]), sec.getint("issued_day", 0)))
        else:
            raise ConfigError(f"unknown section {section}")
    return Router(routes), KeyStore(clients)
