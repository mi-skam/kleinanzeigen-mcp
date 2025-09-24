{
  description = "Kleinanzeigen MCP - Development environment with uv and comprehensive linting tools";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    devshell.url = "github:numtide/devshell";
  };

  outputs = inputs@{ flake-parts, devshell, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        devshell.flakeModule
      ];
      
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" "x86_64-darwin" ];
      
      perSystem = { config, self', inputs', pkgs, system, ... }: {
        devshells.default = {
          name = "kleinanzeigen-mcp-env";
          
          motd = ''
            🔧 Kleinanzeigen MCP Development Environment (uv-based)
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            Available tools:
            ✅ uv (fast Python package manager)
            ✅ Python 3 with isolated virtual environment
            ✅ ruff, black, mypy (via uv)
            ✅ shellcheck, hadolint, markdownlint
            ✅ Git and development utilities

            🚀 Quick commands:
              setup-env       # Initialize uv virtual environment and install deps
              setup-hooks     # Install pre-commit hooks
              lint            # Check code (dry-run, no changes)
              lint-fix        # Check and fix issues automatically
              mcp-server      # Run the MCP server
              test-client     # Run example client test

            💡 First run 'setup-env' to initialize the environment!
            The lint script auto-detects tools and runs them appropriately.

          '';
          
          packages = with pkgs; [
            # Core tools
            bash
            git
            curl

            # UV - Fast Python package manager
            uv

            # Essential linting tools (system-level)
            shellcheck        # Shell script linting
            hadolint         # Docker linting
            nodePackages.markdownlint-cli  # Markdown linting

            # MCP and HTTP client tools
            httpie           # HTTP client for testing API
            jq               # JSON processor for parsing responses
          ];
          
          commands = [
            {
              name = "setup-env";
              help = "Initialize uv virtual environment and install dependencies";
              command = ''
                echo "🚀 Setting up uv environment..."
                
                # Initialize uv project if not already done
                if [ ! -f "uv.lock" ]; then
                  echo "Initializing uv project..."
                  uv init --no-readme --no-workspace
                fi
                
                # Install dependencies
                echo "Installing dependencies..."
                uv sync --dev
                
                echo "✅ Environment setup complete!"
                echo "💡 Virtual environment is at .venv/"
                echo "💡 Run 'source .venv/bin/activate' to activate manually if needed"
              '';
            }
            {
              name = "lint";
              help = "Run linters in dry-run mode (check only, no modifications)";
              command = ''
                if [ -f ".venv/bin/activate" ]; then
                  source .venv/bin/activate
                fi
                ./scripts/lint.sh --check-only "$@"
              '';
            }
            {
              name = "lint-fix";
              help = "Run linters and auto-fix issues where possible";
              command = ''
                if [ -f ".venv/bin/activate" ]; then
                  source .venv/bin/activate
                fi
                ./scripts/lint.sh --fix "$@"
              '';
            }
            {
              name = "setup-hooks";
              help = "Set up pre-commit hooks for automatic linting";
              command = ''
                echo "Setting up pre-commit hooks..."
                mkdir -p .git/hooks
                cat > .git/hooks/pre-commit << 'EOF'
            #!/bin/sh
            if [ -f ".venv/bin/activate" ]; then
              source .venv/bin/activate
            fi
            ./scripts/lint.sh --staged --check-only
            EOF
                chmod +x .git/hooks/pre-commit
                echo "✅ Pre-commit hook installed!"
              '';
            }
            {
              name = "mcp-server";
              help = "Run the Kleinanzeigen MCP server";
              command = ''
                if [ -f ".venv/bin/activate" ]; then
                  source .venv/bin/activate
                fi
                python -m src.kleinanzeigen_mcp.server
              '';
            }
            {
              name = "test-client";
              help = "Run the example client to test MCP functionality";
              command = ''
                if [ -f ".venv/bin/activate" ]; then
                  source .venv/bin/activate
                fi
                python example_usage.py
              '';
            }
          ];
          
          env = [
            {
              name = "PYTHONPATH";
              value = "./src";
            }
            {
              name = "KLEINANZEIGEN_API_URL";
              value = "https://kleinanzeigen-agent.de";
            }
            {
              name = "LINT_ENV";
              value = "development";
            }
            {
              name = "UV_PYTHON_PREFERENCE";
              value = "system";
            }
          ];
        };
      };
    };
}