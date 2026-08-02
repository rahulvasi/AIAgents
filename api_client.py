import os
import json
import openai
import tiktoken
import backoff
from dotenv import load_dotenv
from types import SimpleNamespace

class ApiClient:
    """A production ready generic API client for OpenAI API requests"""

    def __init__(self, mock_responses_path="mock_responses.json"):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")

        self.client = openai.OpenAI(api_key=api_key)

        # Load mock responses for testing
        try:
            with open(mock_responses_path, 'r') as f:
                self.mock_responses = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Mock response file not found at {mock_responses_path}")
            self.mock_responses = {}

        print("API client initialized successfully.")


    def estimate_cost(
        self, 
        prompt: str,
        model: str, 
        estimated_completion_tokens: int, 
        prompt_cost_per_million: float,
        completion_cost_per_million: float
    ) -> float:
        """Estimates the total cost of an API call including prompt and completion."""

        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")  # Fallback encoding

        prompt_tokens = len(encoding.encode(prompt))

        prompt_cost = (prompt_tokens / 1_000_000) * prompt_cost_per_million
        completion_cost = (estimated_completion_tokens / 1_000_000) * completion_cost_per_million

        total_cost = prompt_cost + completion_cost
        return total_cost


    @backoff.on_exception(backoff.expo, openai.RateLimitError, max_tries=5)
    def make_request(self, use_mock: bool = False, **kwargs):
        """
        Makes an API request to OpenAI or returns a mock response based on the use_mock flag.
        - If use_mock is True, return a mock response from the loaded JSON file.
        - If use_mock is False, make a live API request and handle errors gracefully.
        """

        if use_mock:
            print("--- Returning MOCK API response ---")
            mock_data = self.mock_responses.get("success", {})
            return SimpleNamespace(**mock_data)

        print("--- Making LIVE API request ---")
        try:
            response = self.client.responses.create(**kwargs)
            return response
        except openai.RateLimitError as e:
            print("Rate limit error encountered. Retrying...")
            raise # Re-raise to allow backoff to handle it
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise





    
