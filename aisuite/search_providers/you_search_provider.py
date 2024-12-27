import os
import httpx
from typing import List
from aisuite.search_provider import SearchProviderInterface, SearchResult


class YouSearchProvider(SearchProviderInterface):
    """You.com implementation of the SearchProviderInterface with support for web search and news."""

    BASE_URL = "https://api.ydc-index.io"

    def __init__(self, api_key: str = None):
        """
        Initialize the You.com provider with an API key.

        Args:
            api_key (str, optional): The API key for accessing You.com API.
                                   If not provided, will try to read from YOU_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("YOU_COM_API_KEY")
        if not self.api_key:
            raise ValueError(
                "You.com API key is required. Either pass it to the constructor or set YOU_COM_API_KEY environment variable."
            )
        self.client = httpx.Client()
        self.headers = {"X-API-Key": self.api_key}

    def get_news(self, query: str, **kwargs) -> List[SearchResult]:
        """
        Perform a news search using the You.com API.
        This is based on the documentation at https://documentation.you.com/news-quickstart.

        Args:
            query (str): The search query
            **kwargs: Additional parameters to pass to the API

        Returns:
            List[SearchResult]: List of news results
        """
        params = {"q": query, **kwargs}
        response = self.client.get(
            f"{self.BASE_URL}/news?q={query}", params=params, headers=self.headers
        )
        response.raise_for_status()
        data = response.json()

        return [
            SearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("description", ""),
                source="you.com:news",
            )
            for result in data.get("news", {}).get("results", [])
        ]

    def search(
        self, query: str, specific_function: str = None, **kwargs
    ) -> List[SearchResult]:
        """
        Perform a search using the You.com API.
        This is based on the documentation at https://documentation.you.com/quickstart.

        Args:
            query (str): The search query
            specific_function (str, optional): Specific search function to use ('get_news' for news search)
            **kwargs: Additional parameters to pass to the API

        Returns:
            List[SearchResult]: List of search results
        """
        if specific_function == "get_news":
            return self.get_news(query, **kwargs)

        params = {"query": query, **kwargs}
        response = self.client.get(
            f"{self.BASE_URL}/search?query={query}", params=params, headers=self.headers
        )
        response.raise_for_status()
        data = response.json()

        return [
            SearchResult(
                title=hit.get("title", ""),
                url=hit.get("url", ""),
                content=hit.get("description", "") or " ".join(hit.get("snippets", [])),
                source="you.com",
            )
            for hit in data.get("hits", [])
        ]

    def __del__(self):
        """Ensure the httpx client is properly closed."""
        self.client.close()
