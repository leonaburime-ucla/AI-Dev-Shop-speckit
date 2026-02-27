---
name: api-contracts
version: 1.0.0
last_updated: 2026-02-26
description: Governs API contract design, completeness, versioning, and backward compatibility.
---

# Skill: API Contracts

An API contract is a promise to consumers. Breaking that promise — changing a field type, removing an endpoint, altering error shapes — has the same downstream impact as a production outage. This skill governs how contracts are defined, validated, versioned, and tested for backward compatibility.

## What a Complete API Contract Requires (per endpoint)

- HTTP method and path
- Path parameters, query parameters, request headers (name, type, required/optional, constraints)
- Request body schema (all fields, types, required/optional, validation rules, examples)
- Response schemas for each status code: 200/201, 400, 401, 403, 404, 409, 422, 429, 500 minimum
- Auth requirement (none / API key / Bearer JWT / session)
- Rate limit (requests per window, per what scope: IP / user / API key)
- Idempotency behavior (is POST idempotent? Is it safe to retry? What is the idempotency key?)

## OpenAPI 3.x Generation Rules

- Every endpoint in api.spec.md maps to one OpenAPI path + operation object.
- Request/response schemas use JSON Schema — no `$ref` to undefined schemas.
- Examples are required for all request and response bodies.
- `operationId` must be unique, snake_case, verb-first (e.g. `create_invoice`, `list_invoices`).

## Versioning Strategy

- **URL versioning**: (`/v1/`, `/v2/`) — simple, cache-friendly, explicit.
- **Header versioning**: (`Accept: application/vnd.api+json;version=2`) — cleaner URLs, harder to test in browser.
- Choose one strategy at project start and apply consistently.
- Never change versioning strategy mid-project.

## Breaking vs Non-Breaking Changes

### Non-breaking (additive — no version bump required)
- New optional request field
- New response field
- New endpoint
- New optional query parameter
- New status code on an existing endpoint

### Breaking (requires version bump and migration plan)
- Removing or renaming a field (request or response)
- Changing a field type
- Making an optional field required
- Removing an endpoint
- Changing auth requirement
- Changing error response structure

## Consumer-Driven Contract Testing (Pact)

- Consumer defines expectations (request shape + response shape it needs).
- Provider verifies it can satisfy those expectations.
- Pact broker stores contracts between teams.
- Use when: multiple teams consume your API, or you have a public API with versioned consumers.
