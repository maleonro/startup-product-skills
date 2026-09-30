from .base import Provider, ProviderError
from .mock import MockProvider
from .omni import OmniProvider

REGISTRY = {"omni": OmniProvider, "mock": MockProvider}


def get(name: str) -> Provider:
    try:
        return REGISTRY[name]()
    except KeyError:
        raise ProviderError(f"unknown provider '{name}'. Known: {', '.join(REGISTRY)}")
