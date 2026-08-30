"""
Vector Store Setup Script
Creates a Vector Store and uploads policy documents
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration
VECTOR_STORE_NAME = "Innovate Logistics Policies"
POLICY_DOCS_PATH = [
    "policy_docs/hr_policy.md",
    "policy_docs/it_security.md"
]

def create_vector_store_and_upload():
    """
    Creates a Vector Store and uploads policy documents.

    Returns:
        str: The Vector Store ID
    """
    print(f"Creating vector store '{VECTOR_STORE_NAME}'...")

    try:
        #  UPDATED: removed `.beta`
        vector_store = client.vector_stores.create(
            name=VECTOR_STORE_NAME
        )

        print(f"✓ Vector Store created: {vector_store.id}")
        print(f"\nUploading {len(POLICY_DOCS_PATH)} file(s)...")

        # Open file streams
        file_streams = []
        for path in POLICY_DOCS_PATH:
            if not os.path.exists(path):
                print(f"⚠ Warning: File not found: {path}")
                continue
            file_streams.append(open(path, "rb"))
            print(f"  - {path}")

        if not file_streams:
            raise FileNotFoundError("No valid policy files found to upload!")

        # UPDATED: removed `.beta`
        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=file_streams
        )

        print(f"\n✓ Successfully uploaded {len(file_streams)} file(s)")
        print(f"✓ File batch status: {file_batch.status}")

        # Close file streams
        for stream in file_streams:
            stream.close()

        print("\n" + "="*60)
        print("Knowledge base created successfully!")
        print("="*60)
        print(f"\nVector Store ID: {vector_store.id}")
        print("\nIMPORTANT: Copy this ID and paste it into policy_agent_starter.py")
        print("="*60)

        return vector_store.id

    except Exception as e:
        print(f"\n Error occurred: {e}")

        # Clean up file streams on error
        if 'file_streams' in locals():
            for stream in file_streams:
                try:
                    stream.close()
                except:
                    pass

        return None


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Innovate Logistics Policy Knowledge Base Setup")
    print("="*60 + "\n")

    # Verify API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(" ERROR: OPENAI_API_KEY environment variable not set")
        print("\nPlease:")
        print("1. Create a .env file")
        print("2. Add: OPENAI_API_KEY=your-key-here")
        exit(1)

    # Verify files exist
    print("Checking policy documents...")
    all_exist = True
    for path in POLICY_DOCS_PATH:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✓ {path} ({size:,} bytes)")
        else:
            print(f"   {path} (NOT FOUND)")
            all_exist = False

    if not all_exist:
        print("\n⚠ Warning: Some files not found. Continuing with available files...")

    print()

    # Create vector store
    vector_store_id = create_vector_store_and_upload()

    if vector_store_id:
        print("\n Setup complete! You can now run policy_agent_starter.py")
    else:
        print("\n Setup failed. Please check the errors above.")
