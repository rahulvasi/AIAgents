"""
Policy Documentation Assistant 

This agent uses File Search to answer questions from policy documents.
"""

import sys
sys.path.append('../../../../shared')
from api_client import ApiClient
import os
import time
import json
import logging

# --- Logging Setup ---
logging.basicConfig(
    filename='agent.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)


class PolicyAssistant:
    def __init__(self, vector_store_id: str, model: str = "gpt-4o"):
        """
        Initialize the Policy Assistant.

        Args:
            vector_store_id: The ID of your Vector Store (format: vs_...)
            model: The model to use (default: gpt-4o)
        """
        self.client = ApiClient()
        self.vector_store_id = vector_store_id
        self.conversation_id = None
        self.model = model

        self.instructions = """
        You are a helpful Innovate Logistics Support Assistant. Your persona is professional, efficient, and analytical.

        ### RULES ###
        1. First, think step-by-step to analyze the user's query. Enclose this reasoning in <reasoning></reasoning> tags.
        2. Decide if you need to use the File Search tool to find information from the knowledge base.
        3. After your reasoning, provide a clear, final answer to the user.
        4. If the information is not in the knowledge base, state that clearly.
        5. Do not invent information or use external knowledge.
        """

    def ask(self, user_input: str):
        """
        Ask a single question to the assistant and print the response.

        Args:
            user_input: The question to ask
        """
        print(f"\n--- Querying Agent ---")
        print(f"User Prompt: '{user_input}'")

        interaction_id = f"fs_int_{int(time.time())}"

        log_entry = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "interaction_id": interaction_id,
            "prompt": user_input,
            "tool_used": "file_search",
            "vector_store_id": self.vector_store_id,
            "response_snippet": None,
            "error": None,
            "call_type": "live"
        }
        # <<< STEP 1: IMPLEMENT THE QUERY LOGIC HERE >>>

        try:
            # TODO 1: Construct API arguments (fixed for current SDK)
            api_args = {
                "model": self.model,
                "input": user_input,
                "tools": [
                    {
                        "type": "file_search",
                        "vector_store_ids": [self.vector_store_id]
                    }
                ]
            }

            # TODO: 2. Add logic to handle conversation_id for follow-up questions
            if self.conversation_id:

                api_args["conversation_id"] = self.conversation_id
            else:
                api_args["instructions"] = self.instructions

            # TODO: 3. Call the API

            # Make API request
            response = self.client.make_request(**api_args)

            # TODO: 4. Update conversation_id after first request

            # Save conversation_id after first request
            if not self.conversation_id and hasattr(response, 'conversation_id'):
                self.conversation_id = response.conversation_id

            # TODO: 5. Extract and print the agent's response

            # Extract response text
            assistant_response = response.output_text

            print(f"\n--- Agent Response ---")
            print(assistant_response)
            print("----------------------\n")

            # Log response
            log_entry["response_snippet"] = assistant_response[:100] + "..."

        except Exception as e:
            print(f"An error occurred: {e}")
            log_entry["error"] = str(e)

        logging.info(json.dumps(log_entry))


if __name__ == "__main__":
    # Set the actual Vector Store ID
    VECTOR_STORE_ID = "vs_6a93c63e72348191b7505f6c338cf42e"

    if "xxxxxxxxxxxxxxxxxxxxxxxx" in VECTOR_STORE_ID:
        print("\n" + "="*60)
        print("ERROR: Vector Store ID not configured")
        print("="*60)
        print("\nPlease follow these steps:")
        print("1. Run: python create_policies_kb.py")
        print("2. Copy the Vector Store ID from the output")
        print("3. Paste it into this file, replacing the placeholder")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("Innovate Logistics Policy Assistant")
        print("="*60 + "\n")

        # Create agent instance
        assistant = PolicyAssistant(vector_store_id=VECTOR_STORE_ID)

        # Test 1: In-scope question (HR Policy)
        print("=== Test 1: In-Scope Query ===")
        assistant.ask("What is the company's vacation policy for full-time employees?")

        # Test 2: Out-of-scope question
        print("=== Test 2: Out-of-Scope Query ===")
        assistant.ask("What is the current FedEx service status for Europe?")

        # Test 3: Follow-up question (IT Security Policy)
        print("=== Test 3: Follow-Up Query ===")
        assistant.ask("What are the password requirements in the IT security policy?")

        print("\n" + "="*60)
        print("Testing complete! Check agent.log for details.")
        print("="*60 + "\n")