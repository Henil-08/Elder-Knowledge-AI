# Elder-Knowledge-AI

This project introduces a computational framework designed to transform unstructured audio oral histories into a structured, searchable, and semantically meaningful digital archive. Addressing the challenge of inaccessible cultural knowledge locked in audio recordings, our system leverages modern machine learning and large language models to enable deep, context-aware exploration of these narratives.

The core pipeline involves automatic speech recognition (ASR) for accurate transcription, followed by text cleaning, normalization, and semantic tagging. These processed transcripts are then converted into high-dimensional vector embeddings and indexed in a vector database. This architecture facilitates semantic search and retrieval-augmented generation (RAG), allowing users to query oral archives based on conceptual meaning rather than keyword matching. By integrating data science with cultural heritage preservation, this project aims to create a powerful tool for discovering the rich, interconnected stories within our shared oral traditions.

## Quick Start

```bash
# Clone repository
git clone https://github.com/Henil-08/Elder-Knowledge-AI.git
cd Elder-Knowledge-AI

# Install dependencies
uv init
uv pip install -r pyproject.toml
```