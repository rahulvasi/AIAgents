from api_client import ApiClient

class QAAgent:

    def __init__(self, vector_store_id):
        self.api_client = ApiClient()
        self.vector_store_id = vector_store_id
        #self.conversation_id = None  # Initialize conversation_id to None
        self.previous_response_id = None  # Initialize previous_response_id to None

        self.instructions = """
        You are a helpful SkillSprint Support Assistant for new users. Your persona is encouraging and clear.

        ### RULES ###
        - Your goal is to answer user questions about applying for projects, getting paid, and using the SkillSprint platform.
        - To answer, you MUST use the File Search tool to search the provided knowledge base.
        - If the answer is not found in the files, you must say: "I'm sorry, I cannot find that information in our knowledge base."
        - Do not invent information or use external knowledge.
        """

    def start_chat(self):
        """
        Starts a new chat session by initializing a conversation ID.
        """
        print("Welcome to SkillSprint! How can I help you get started? (Type 'exit' to end)")

        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Thanks for using SkillSprint Support. Good luck with your projects!")
                break

            try:
                response = self.api_client.make_request(
                    use_mock=False,
                    model="gpt-4o-mini",
                    input=user_input,
                    instructions=self.instructions if not self.previous_response_id else None,
                    previous_response_id=self.previous_response_id if self.previous_response_id else None,
                    tools=[
                        {
                            "type": "file_search",
                            "vector_store_ids": [self.vector_store_id],
                        }
                    ]
                )

                #print(response)

                self.previous_response_id = response.id  # Save the response ID for context in future requests

                print(f"Agent: {response.output_text}")


            except Exception as e:
                print(f"An error occurred while processing your request: {e}")
                print("Please try again or type 'exit' to end the chat.")


if __name__ == "__main__":    
            VECTOR_STORE_ID = "vs_6a6f4a0b53288191995d5eecd493382c"  # Replace with your actual vector store ID
            agent = QAAgent(vector_store_id=VECTOR_STORE_ID)
            agent.start_chat()
