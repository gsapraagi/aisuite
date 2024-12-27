import os
from typing import List
from serpapi import (
    GoogleSearch,
)  # Despite the name, this handles multiple search engines
from aisuite.search_provider import SearchProviderInterface, SearchResult


class SerpSearchProvider(SearchProviderInterface):
    """SerpAPI implementation of the SearchProviderInterface supporting Google, Bing, YouTube and other search engines."""

    def __init__(self, api_key: str = None):
        """
        Initialize the SerpAPI provider with an API key.

        Args:
            api_key (str, optional): The API key for accessing SerpAPI.
                                   If not provided, will try to read from SERPAPI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("SERP_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SerpAPI key is required. Either pass it to the constructor or set SERP_API_KEY environment variable."
            )

    def youtube_search(self, query: str, **kwargs) -> List[SearchResult]:
        """
        Perform a YouTube search using the SerpAPI.

        Args:
            query (str): The search query
            **kwargs: Additional parameters specific to YouTube search (e.g., type='video')

        Returns:
            List[SearchResult]: List of search results
        """
        params = {"q": query, "api_key": self.api_key, "engine": "youtube", **kwargs}

        search = GoogleSearch(params)
        results = search.get_dict()

        # Handle YouTube video results
        video_results = results.get("video_results", [])

        return [
            SearchResult(
                title=result.get("title", ""),
                url=result.get("link", ""),
                content=f"Duration: {result.get('duration', 'N/A')} | "
                f"Views: {result.get('views', 'N/A')} | "
                f"Channel: {result.get('channel', {}).get('name', 'N/A')} | "
                f"Description: {result.get('description', '')}",
                source="serpapi:youtube",
            )
            for result in video_results
        ]

    def search(
        self, query: str, specific_function: str = None, **kwargs
    ) -> List[SearchResult]:
        """
        Perform a search using the SerpAPI.
        Note: Although we use GoogleSearch class, it supports multiple engines including Google, Bing,
        Baidu, Yahoo, YouTube and others through the 'engine' parameter.

        Args:
            query (str): The search query
            specific_function (str, optional): Search engine to use ('google', 'bing', 'youtube', etc.).
                                             Defaults to Google.
            **kwargs: Additional parameters to pass to the API (e.g., num=10, location="Austin, TX")

        Returns:
            List[SearchResult]: List of search results
        """
        print(
            f"Calling SerpSearchProvider.search with query: {query}, specific_function: {specific_function}, kwargs: {kwargs}"
        )
        # Handle YouTube searches separately due to different result structure
        if specific_function == "youtube":
            return self.youtube_search(query, **kwargs)

        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",  # Default to Google search
            **kwargs,
        }

        # Override engine if specific_function is provided
        if specific_function:
            params["engine"] = specific_function

        # Perform the search (GoogleSearch class handles all engine types)
        search = GoogleSearch(params)
        results = search.get_dict()

        # Handle organic search results
        organic_results = results.get("organic_results", [])

        return [
            SearchResult(
                title=result.get("title", ""),
                url=result.get("link", ""),
                content=result.get("snippet", ""),
                source=f"serpapi:{params['engine']}",
            )
            for result in organic_results
        ]
