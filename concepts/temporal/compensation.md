---
title: Compensation
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [temporal, compensation, saga]
sources: [raw/articles/temporal-io-homepage.md]
---

# Compensation

Compensation is the pattern of undoing or offsetting previously completed work when a later step in a workflow fails. In Temporal, compensation logic is usually modeled explicitly in workflow code rather than hidden in infrastructure.

## Typical Use

- Cancel a reservation after payment fails
- Refund a charge after downstream fulfillment fails
- Reverse multi-step business operations that cannot be rolled back atomically

## Related

- [[activity]] - Compensation usually responds to activity outcomes
- [[workflow]] - Workflows orchestrate compensation logic
- [[durable-execution]] - Durable state makes multi-step recovery practical
