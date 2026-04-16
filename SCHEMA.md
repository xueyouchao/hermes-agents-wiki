# Wiki Schema

## Domain
Knowledge base covering:
1. Temporal and durable execution ecosystem
2. Andrej Karpathy's AI/ML repositories (LLM training, tokenization, neural network implementations)
3. General ML/AI concepts

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `temporal-sdks.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
---
```

## Tag Taxonomy
- Platform: temporal, temporal-cloud, self-hosted
- SDKs: python, go, typescript, java, csharp, ruby, php
- Repositories: karpathy, nanogpt, llm-c, mingpt, minbpe, micrograd, char-rnn
- Cloud: aws, ec2, lambda, s3, rds, dynamodb, vpc, cloudfront, iam, route53, sns, sqs, ecs, eks, sagemaker
- Concepts: durable-execution, workflow, activity,-signal, timer,-replay, compensation
- Patterns: saga,-cqrs,-event-sourcing, outbox-pattern
- Infrastructure: cluster, namespace, task-queue, persistence
- Use-cases: ai-agents, fintech, media, ecommerce, infrastructure
- People/Orgs: company, person
- Meta: comparison, tutorial, reference, controversy

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index

## Entity Pages
One page per notable entity. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other entities ([[wikilinks]])
- Source references

## Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

## Comparison Pages
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in the lint report