# log_analyzer_agent.py
# Make sure api_client.py is in the same directory

from api_client import ApiClient
import os
import time
import json
import logging

# --- Logging Setup (Pre-implemented for the analyzer's actions) ---
logging.basicConfig(
    filename="analyzer_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
# --- End Logging Setup ---


class InternalAgentAnalyzer:
    def __init__(self, log_file_path="il_agent.txt", model="gpt-4o"):
        self.client = ApiClient()
        self.log_file_path = log_file_path
        self.model = model
        self.instructions = """
        You are an internal performance analyst agent for Praxis AI, reviewing logs
        for the Innovate Logistics project. Your task is to analyze agent
        diagnostic logs provided as a file (one JSON object per line).
        Use the python tool (code_interpreter) to parse the log data and
        answer questions relevant to a customer service manager.
        Focus on metrics like tool usage frequency, error occurrences,
        and response snippets. Present findings clearly.
        """

    def analyze_logs(self, analysis_prompt, use_mock=False):
        interaction_id = f"analyzer_int_{int(time.time())}"

        # --- Log Entry Init (Pre-implemented) ---
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "interaction_id": interaction_id,
            "analysis_prompt": analysis_prompt,
            "target_log_file": self.log_file_path,
            "result_snippet": None,
            "error": None,
            "call_type": "mock" if use_mock else "live",
        }
        # --- End Log Entry Init ---

        print(f"\n--- Analyzing Logs ({interaction_id}): '{analysis_prompt}' ---")

        # <<< STEP 1: UPLOAD THE LOG FILE >>>
        file_id = None
        try:
            openai_client = self.client.client

            if not os.path.exists(self.log_file_path):
                raise FileNotFoundError(f"{self.log_file_path} does not exist")

            with open(self.log_file_path, "rb") as f:
                uploaded_file = openai_client.files.create(
                    file=f,
                    purpose="assistants",
                )
                file_id = uploaded_file.id

            print(f"Log file uploaded successfully. File ID: {file_id}")

        except FileNotFoundError as e:
            print(f"File error: {e}")
            log_entry["error"] = str(e)
            logging.error(json.dumps(log_entry))
            return
        except Exception as e:
            print(f"Unexpected error during file upload: {e}")
            log_entry["error"] = str(e)
            logging.error(json.dumps(log_entry))
            return

        # <<< STEP 2: DEFINE TOOLS WITH FILE ID >>>
        tools = [
            {
                "type": "code_interpreter",
                "file_ids": [file_id],
            }
        ]

        # <<< STEP 3: CONSTRUCT API ARGS >>>
        api_args = {
            "model": self.model,
            "input": analysis_prompt,
            "instructions": self.instructions,
            "tools": tools,
        }

        try:
            # <<< STEP 4: MAKE THE API CALL >>>
            response = self.client.make_request(
                use_mock=use_mock,
                **api_args,
            )

            print("\n--- Analysis Result ---")

            # <<< STEP 5: SAFELY EXTRACT RESPONSE TEXT >>>
            result_text = None

            if hasattr(response, "output_text"):
                result_text = response.output_text
            elif hasattr(response, "text"):
                result_text = response.text
            elif hasattr(response, "output"):
                try:
                    result_text = response.output[0].content[0].text
                except Exception:
                    result_text = str(response)
            else:
                result_text = str(response)

            # Handle empty mock response
            if result_text.strip() == "namespace()":
                result_text = "(Mock analysis response generated successfully.)"

            print(result_text)
            log_entry["result_snippet"] = result_text[:300]

            print("-----------------------\n")

        except Exception as e:
            print(f"An error occurred during analysis: {e}")
            log_entry["error"] = f"Analysis API call error: {e}"

        # --- Write Log Entry (Pre-implemented) ---
        if log_entry["error"]:
            logging.error(json.dumps(log_entry))
        else:
            logging.info(json.dumps(log_entry))

        print(f"Analysis task log written to analyzer_agent.log for {interaction_id}")
        # --- End Write Log ---


# --- Main Execution Logic ---
if __name__ == "__main__":
    log_file = "il_agent.txt"

    if not os.path.exists(log_file):
        print("\n" + "="*60)
        print(f"ERROR: {log_file} not found.")
        print("\n" + "="*60)
        print(f"ERROR: {log_file} not found.")
        print("="*60)
        print("\nThis activity analyzes logs from the previous activities.")
        print("Please either:")
        print("  1. Run Activities 3.1 and 3.2 first to generate logs")
        print("  2. Use the provided sample il_agent.txt file")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("Innovate Logistics - Internal Log Analyzer")
        print("="*60 + "\n")

        # Initialize the analyzer
        analyzer = InternalAgentAnalyzer(log_file_path=log_file)

        # <<< STEP 6: DEFINE ANALYSIS PROMPTS >>>
        ANALYSIS_PROMPT_TOOL_USAGE = (
            "Analyze the attached log file ('il_agent.txt'). "
            "How many interactions used 'web_search', 'file_search', or 'none'?"
        )

        ANALYSIS_PROMPT_ERRORS = (
            "Analyze the attached log file ('il_agent.txt'). "
            "Were there any errors recorded? "
            "List the interaction IDs for any entries where the 'error' field is not null."
        )

        # <<< STEP 7: RUN ANALYSIS TASKS >>>
        analyzer.analyze_logs(ANALYSIS_PROMPT_TOOL_USAGE, use_mock=True)
        analyzer.analyze_logs(ANALYSIS_PROMPT_ERRORS, use_mock=True)
