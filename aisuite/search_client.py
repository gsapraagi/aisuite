from .search_provider import SearchProviderFactory


class SearchClient:
    def __init__(self, provider_configs: dict = {}):
        """
        Initialize the search client with provider configurations.
        Use the SearchProviderFactory to create provider instances.

        Args:
            provider_configs (dict): A dictionary containing provider configurations.
                Each key should be a provider string (e.g., "you.com" or "google"),
                and the value should be a dictionary of configuration options for that provider.
                For example:
                {
                    "you.com": {"api_key": "your_youcom_api_key"},
                    "google": {
                        "api_key": "your_google_api_key",
                        "cx": "your_google_cx"
                    }
                }
        """
        self.providers = {}
        self.provider_configs = provider_configs
        self._initialize_providers()

    def _initialize_providers(self):
        """Helper method to initialize or update providers."""
        for provider_key, config in self.provider_configs.items():
            self._validate_provider_key(provider_key)
            self.providers[provider_key] = SearchProviderFactory.create_provider(
                provider_key, config
            )

    def _validate_provider_key(self, provider_key):
        """
        Validate if the provider key corresponds to a supported provider.
        """
        supported_providers = SearchProviderFactory.get_supported_providers()

        if provider_key not in supported_providers:
            raise ValueError(
                f"Invalid provider key '{provider_key}'. Supported providers: {supported_providers}. "
                "Make sure the provider string is formatted correctly as 'provider' or 'provider:function'."
            )

    def configure(self, provider_configs: dict = None):
        """
        Configure the client with provider configurations.
        """
        if provider_configs is None:
            return

        self.provider_configs.update(provider_configs)
        self._initialize_providers()

    def search(self, provider: str, query: str, **kwargs):
        """
        Perform a search using the specified provider and query.

        Args:
            provider (str): The provider to use, can be in format "provider" or "provider:specific_function"
            query (str): The search query string
            **kwargs: Additional arguments to pass to the search provider

        Returns:
            List[SearchResult]: A list of search results from the provider

        Examples:
            >>> client.search("you.com", "who is messi")
            >>> client.search("you.com:get_news", "who is messi")
        """
        provider_key, _, specific_function = provider.partition(":")

        # Validate if the provider is supported
        self._validate_provider_key(provider_key)

        # Initialize provider if not already initialized
        if provider_key not in self.providers:
            config = self.provider_configs.get(provider_key, {})
            self.providers[provider_key] = SearchProviderFactory.create_provider(
                provider_key, config
            )

        provider_instance = self.providers.get(provider_key)
        if not provider_instance:
            raise ValueError(f"Could not load provider for '{provider_key}'.")

        # Perform the search using the provider
        return provider_instance.search(
            query, specific_function=specific_function, **kwargs
        )
