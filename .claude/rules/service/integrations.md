---
globs: ["**/integrations/**/*.py"]
---

# Integrations

- Protocol + RealClient + MockClient pattern
- Mock clients use fixture data from fixtures/integrations/
- Wrap errors in IntegrationError with context
- Set timeouts on all HTTP clients (30s default)
- Conformance tests verify fixtures match real APIs
