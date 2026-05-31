import os
import json
import openai
from dotenv import load_dotenv
import backoff
import tiktoken
from types import SimpleNamespace

class ApiClient:
    def __init__(self):
        """
        Task: Implement secure initialization.
        - Load environment variables from .env.
        - Securely retrieve the API key, raising a ValueError if not found.
        - Initialize the openai.OpenAI client.
        """
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')    
        if not api_key:
            raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")
        
        self.client = openai.OpenAI(api_key=api_key)

        print("API client initialized successfully.")

    def estimate_cost(
            self,
            text: str, 
            model: str,
            estimated_completion_tokens: int,
            prompt_cost_per_million: float,
            completion_cost_per_million: float       
    ) -> float:
        """
        Task: Implement cost estimation logic.
        - Use tiktoken to get the exact token count for the given text and model.
        - Calculate the cost based on the token count and price per million tokens.
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")  # Fallback encoding

        prompt_tokens = len(encoding.encode(text))
        prompt_cost = (prompt_tokens / 1_000_000) * prompt_cost_per_million
        completion_cost = (estimated_completion_tokens / 1_000_000) * completion_cost_per_million
        total_cost = prompt_cost + completion_cost 
        return total_cost
        

    
    @backoff.on_exception(backoff.expo, openai.RateLimitError, max_tries=5)
    def make_request(self, use_mock: bool = False, **kwargs):
        """
        Task:
        - Wrap the live call in a try...except block to handle errors.
        - Re-raise RateLimitError so the backoff decorator can handle it.
        """
        
        print("--- Making LIVE API request ---")
        try:
            # Assumes use of the modern, stateful Responses API
            response = self.client.responses.create(**kwargs)
            return response
        except openai.RateLimitError as e:
            print(f"Rate limit exceeded. Retrying... Error: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

    
# Example of how to test your class as you build
if __name__ == '__main__':
    try:
        # This will fail until you implement the __init__ method
        client = ApiClient()
        
        # This will fail until you implement estimate_cost
        cost = client.estimate_cost(
        "This is a test prompt",
        "gpt-4.1-mini",
        30.0,
        prompt_cost_per_million=0.03,
        completion_cost_per_million=0.06
        )
        print(f"Estimated cost: ${cost:.8f}")

        # Test live request
        live_response = client.make_request(
            use_mock=False,
            model="gpt-4.1-mini", # Or another suitable model
            input=[{"role": "user", "content": "What is the capital of France?"}]
        )
    
        print("Live Response:", live_response.output[0].content[0].text)

    except Exception as e:
        print(f"An error occurred during testing: {e}")