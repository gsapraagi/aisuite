from typing import List, Dict, TypedDict
from abc import ABC, abstractmethod
from pathlib import Path
import importlib
import functools
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Data class to store search results."""

    title: str
    url: str
    content: str
    source: str


class SearchProviderInterface(ABC):
    @abstractmethod
    def search(self, query: str, specific_function: str = None) -> List[SearchResult]:
        """
        Search method that returns a list of search results.

        Args:
            query (str): The search query string
            specific_function (str, optional): Specific search function to use (e.g., 'get_news', 'web_search').
                                             If None, uses the provider's default search function.

        Returns:
            List[SearchResult]: A list of dictionaries containing search results,
                              where each dictionary has 'title', 'content', 'url', and 'source' fields
        """
        pass


class SearchProviderFactory:
    """Factory to dynamically load search provider instances based on naming conventions."""

    PROVIDERS_DIR = Path(__file__).parent / "search_providers"

    @classmethod
    def create_provider(
        cls, provider_key: str, config: Dict
    ) -> SearchProviderInterface:
        """Dynamically load and create an instance of a search provider."""
        # Convert provider_key to the expected module and class names
        provider_class_name = f"{provider_key.capitalize()}SearchProvider"
        provider_module_name = f"{provider_key}_search_provider"

        module_path = f"aisuite.search_providers.{provider_module_name}"

        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(
                f"Could not import module {module_path}: {str(e)}. "
                "Please ensure the search provider is supported by calling SearchProviderFactory.get_supported_providers()"
            )

        # Instantiate the provider class
        provider_class = getattr(module, provider_class_name)
        return provider_class(**config)

    @classmethod
    @functools.cache
    def get_supported_providers(cls) -> set[str]:
        """List all supported search provider names based on files present in the search_providers directory."""
        provider_files = Path(cls.PROVIDERS_DIR).glob("*_search_provider.py")
        return {file.stem.replace("_search_provider", "") for file in provider_files}
