# Claude Desktop Setup for Kleinanzeigen MCP

## Installation

First, install the package using uv:

```bash
cd /path/to/kleinanzeigen-mcp
uv pip install -e .
```

## Configuration

Add the following to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "kleinanzeigen": {
      "command": "uv",
      "args": [
        "run",
        "kleinanzeigen-mcp"
      ],
      "cwd": "/path/to/kleinanzeigen-mcp"
    }
  }
}
```

## How to Add to Claude Desktop

1. Open Claude Desktop
2. Go to Settings → Developer → MCP Servers
3. Add the configuration above to your servers list
4. Restart Claude Desktop

## Available Prompts

Once configured, you can use these prompts:

1. **verify_listing_availability** - Instructions for verifying that listings are still active
2. **kleinanzeigen_assistant** - Complete usage guidelines for all tools

## Testing the Connection

After adding the configuration, you can test it by asking Claude:
- "What tools do you have available from the Kleinanzeigen MCP?"
- "Use the kleinanzeigen_assistant prompt"
- "Search for bikes in Berlin using the Kleinanzeigen tools"

## Troubleshooting

If the server doesn't connect:

1. **Check Python path**: Ensure `python3` is available in your PATH
   ```bash
   which python3
   ```

2. **Check dependencies**: Make sure all dependencies are installed
   ```bash
   cd /path/to/kleinanzeigen-mcp
   pip install mcp httpx pydantic
   ```

3. **Test the server manually**:
   ```bash
   cd /path/to/kleinanzeigen-mcp
   uv run kleinanzeigen-mcp
   ```
   The server should start and wait for input (this is normal).

   You can also run it directly with Python:
   ```bash
   python -m kleinanzeigen_mcp
   ```

4. **Check Claude Desktop logs** for any error messages

## Important Note About Listing Verification

The MCP server includes prompts that instruct AI assistants to verify listing availability. When using the tools:
- Search results may contain inactive listings
- Always use `get_listing_details` to verify a listing is still active
- The prompts automatically guide the AI to do this verification