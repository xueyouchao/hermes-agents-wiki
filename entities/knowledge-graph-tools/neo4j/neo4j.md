---
title: Neo4j
description: Graph database platform with LLM integration for knowledge graph RAG pipelines
type: entity
created: 2026-04-17
updated: 2026-04-17
tags: [graph-database, rag, knowledge-graph, production, scalable]
sources: [https://github.com/neo4j/neo4j, https://neo4j.com/]
---

# Neo4j

## Overview
Neo4j is the world's leading high-performance graph database, featuring a flexible network structure (nodes/relationships), Cypher query language, and full ACID transactions. It is widely used as a backend for knowledge graph storage and RAG pipelines.

## Key Features
- **Graph database**: Native graph storage optimized for relationship-heavy data
- **Cypher query language**: Expressive graph querying language
- **RAG integration**: Neo4j LLM Knowledge Graph Builder and GraphRAG for RAG workflows
- **Scalability**: Scales horizontally for large knowledge graphs
- **ACID compliance**: Strong consistency guarantees
- **Rich tooling**: Desktop, browser UI, and extensive ecosystem

## Use Cases
- Production knowledge graph storage
- RAG backends for LLM applications
- Graph analytics and pattern discovery
- Recommendation systems
- Network analysis

## Architecture
- JVM-based (Java/Scala) with multiple storage and query engines
- Supports both embedded and server modes
- Enterprise edition includes advanced features and support
- Cloud and on-premise deployment options

## Comparison with Graphify
- **Neo4j**: Storage and querying backend, production-ready, requires separate extraction pipeline
- **Graphify**: Knowledge extraction and graph building tool, optimized for token efficiency and multimodal content, creates the graph structure that can be stored in Neo4j

## Integration Pattern
Use Graphify to build the knowledge graph from source materials, then export the graph structure for storage in Neo4j for production querying at scale.

## References
- https://github.com/neo4j/neo4j
- https://neo4j.com/