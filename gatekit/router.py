"""Route table: longest-prefix match with {param} segments."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    pattern: str
    upstream: str
    methods: tuple = ("GET",)
    route_class: int = 1

    def match(self, path):
        want = [p for p in self.pattern.strip("/").split("/") if p]
        got = [p for p in path.split("?")[0].strip("/").split("/") if p]
        if len(want) != len(got):
            return None
        params = {}
        for w, g in zip(want, got):
            if w.startswith("{") and w.endswith("}"):
                params[w[1:-1]] = g
            elif w != g:
                return None
        return params


class Router:
    def __init__(self, routes):
        self.routes = sorted(routes, key=lambda r: (-len(r.pattern.strip("/").split("/")), r.pattern.count("{"), r.pattern))

    def resolve(self, method, path):
        """Return (route, params), or (None, 404/405 status)."""
        allowed = False
        for route in self.routes:
            params = route.match(path)
            if params is None:
                continue
            if method in route.methods:
                return route, params
            allowed = True
        return None, (405 if allowed else 404)
