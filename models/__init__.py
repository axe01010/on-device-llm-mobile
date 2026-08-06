"""Model catalog & tooling for on-device LLM inference.

This package holds the curated GGUF model registry (``catalog``) kept in sync
with the rest of the project so that chat, download and memory-estimation share
one source of truth about which models exist and how heavy they are.
"""

from .catalog import MODEL_CATALOG, ALIASES, resolve, list_models  # noqa: F401

__all__ = ["MODEL_CATALOG", "ALIASES", "resolve", "list_models"]
__version__ = "0.2.0"