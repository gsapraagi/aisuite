import os
from typing import List
from tavily import TavilyClient
from aisuite.search_provider import SearchProviderInterface, SearchResult


class TavilySearchProvider(SearchProviderInterface):
    """Tavily implementation of the SearchProviderInterface."""

    def __init__(self, api_key: str = None):
        """
        Initialize the Tavily provider with an API key.

        Args:
            api_key (str, optional): The API key for accessing Tavily API.
                                   If not provided, will try to read from TAVILY_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Tavily API key is required. Either pass it to the constructor or set TAVILY_API_KEY environment variable."
            )
        self.client = TavilyClient(api_key=self.api_key)

    def search(
        self, query: str, specific_function: str = None, **kwargs
    ) -> List[SearchResult]:
        """
        Perform a search using the Tavily API.

        Args:
            query (str): The search query
            specific_function (str, optional): Not used for Tavily
            **kwargs: Additional parameters to pass to the API

        Returns:
            List[SearchResult]: List of search results
        """
        response = self.client.search(query, **kwargs)

        return [
            SearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content", ""),
                source="tavily",
            )
            for result in response.get("results", [])
        ]
