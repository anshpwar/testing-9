# Gateway operations runbook

## When the rate limiter rejects a legitimate client
1. Check the client's plan tier in `config/gateway.ini`.
2. Page to the platform on-call if the tier is right but traffic is still rejected.

## When an upstream circuit stays open
1. Confirm the upstream health endpoint; the breaker reopens after its policy cool-down.
2. Page to the owning team if failures continue past the cool-down.

## Rotating API keys
Keys are stored as SHA-256 digests. Issue a new key, update the digest, and revoke the old one after the overlap window.
