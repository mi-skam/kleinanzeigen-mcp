# Claude Desktop Setup for Kleinanzeigen MCP

## Configuration

Add the following to your Claude Desktop configuration file:

### Option 1: Using Python directly

```json
{
  "mcpServers": {
    "kleinanzeigen": {
      "command": "python3",
      "args": [
        "-m",
        "src.kleinanzeigen_mcp.server"
      ],
      "cwd": "/path/to/kleinanzeigen-mcp"
    }
  }
}
```

### Option 2: Using UV (if installed)

```json
{
  "mcpServers": {
    "kleinanzeigen": {
      "command": "uv",
      "args": [
        "run",
        "python3",
        "-m",
        "src.kleinanzeigen_mcp.server"
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
   python3 -m src.kleinanzeigen_mcp.server
   ```
   The server should start and wait for input (this is normal).

4. **Check Claude Desktop logs** for any error messages

## Important Note About Listing Verification

The MCP server includes prompts that instruct AI assistants to verify listing availability. When using the tools:
- Search results may contain inactive listings
- Always use `get_listing_details` to verify a listing is still active
- The prompts automatically guide the AI to do this verification