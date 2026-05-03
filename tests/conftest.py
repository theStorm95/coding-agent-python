import os

# Ensure a dummy API key is present so the Anthropic client can be imported
# without a real .env file (e.g. in CI). The client is always mocked in tests.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-placeholder")
