# Product Brief — request-nest

## Problem
When integrating webhooks or debugging HTTP clients, you often need a quick way to:
- receive requests from external systems,
- see exactly what was sent (headers/body/query),
- iterate without writing a "real" receiver first.

Most teams either:
- add temporary logging to the real service (slow + risky),
- use a 3rd-party hosted tool (privacy + access concerns),
- run ad-hoc scripts (no UI/history).

## Solution
A self-hosted "request bin" service that provides disposable endpoints and a UI to inspect incoming HTTP requests.

## Why it should exist (value)
- **Faster debugging**: see payloads instantly, no code changes
- **Safer**: avoid sending customer/prod data to random SaaS tools
- **Repeatable**: consistent UI/history for troubleshooting and demos
- **Homelab-friendly**: easy deploy, low resource use, minimal config

## Target users
- Engineers building integrations (webhooks, callbacks, API clients)
- DevOps/SRE debugging network behavior
- Anyone testing HTTP clients and automation tools

## Non-goals (for now)
- Full replay/editing pipeline
- Multi-tenant RBAC
- High-scale ingestion / streaming analytics
