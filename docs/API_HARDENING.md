# API Hardening

This document defines the production-style API safeguards implemented for the credit risk scoring service.

## Goals

The scoring API should:

- validate request payloads before scoring
- reject oversized batch requests
- return structured error responses
- include request IDs for traceability
- expose artifact health information
- preserve predictable response contracts for downstream systems

## Request IDs

Every API response includes an `X-Request-ID` header. Clients may send their own request ID with the same header. If no request ID is provided, the service generates one.

This supports:

- traceability across logs
- incident review
- batch workflow debugging
- downstream system correlation

## Batch Limits

The `/batch_predict` endpoint enforces a maximum batch size to prevent accidental oversized requests from overloading the scoring service.

Default limit:

```text
100 applicants per request
```

Larger portfolio scoring workloads should use the batch scoring CLI.

## Structured Errors

Errors are returned with a consistent shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "request_id": "..."
  }
}
```

## Artifact Health

The `/health` endpoint reports whether model, metadata, and feature schema artifacts are available. This helps separate service availability from model readiness.
