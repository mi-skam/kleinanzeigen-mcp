#!/bin/bash

#---
# description: "Run linters and formatters with auto-detection and intelligent fixing"
# argument-hint: "[options: --fix --strict --check-only]"
# category: "quality"
# complexity: "simple"
# requires: []
#---

# Run code linters and formatters for the current project
# Auto-detects project type and runs appropriate linting tools with intelligent error reporting and fixing.

set -euo pipefail

# Parse arguments
ARGUMENTS="$*"
FIX_MODE=false
STRICT_MODE=false
CHECK_ONLY=false
STAGED_ONLY=false

for arg in $ARGUMENTS; do
  case $arg in
    --fix)
      FIX_MODE=true
      ;;
    --strict)
      STRICT_MODE=true
      ;;
    --check-only)
      CHECK_ONLY=true
      ;;
    --staged)
      STAGED_ONLY=true
      ;;
    --help|-h)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --fix          Auto-fix issues where possible"
      echo "  --strict       Include style warnings and suggestions"
      echo "  --check-only   Check without fixing (CI mode)"
      echo "  --staged       Only lint staged files"
      exit 0
      ;;
  esac
done

# Auto-detect project languages and linting tools
detected_languages() {
  local tools=()

  # JavaScript/TypeScript
  if [[ -f "package.json" ]]; then
    # ESLint
    if grep -q '"eslint"' package.json 2>/dev/null || compgen -G ".eslintrc.*" > /dev/null 2>&1; then
      tools+=("eslint")
    fi

    # Prettier
    if grep -q '"prettier"' package.json 2>/dev/null || compgen -G ".prettierrc*" > /dev/null 2>&1; then
      tools+=("prettier")
    fi

    # TypeScript
    if [[ -f "tsconfig.json" ]] || grep -q '"typescript"' package.json 2>/dev/null; then
      tools+=("tsc")
    fi
  fi

  # Python
  if [[ -f "pyproject.toml" ]] || [[ -f "requirements.txt" ]] || [[ -f "setup.py" ]]; then
    # Ruff (modern all-in-one)
    if command -v ruff >/dev/null 2>&1; then
      tools+=("ruff")
    fi

    # Black formatter
    if command -v black >/dev/null 2>&1; then
      tools+=("black")
    fi

    # mypy for type checking
    if command -v mypy >/dev/null 2>&1; then
      tools+=("mypy")
    fi

    # flake8 if no ruff
    if [[ ! " ${tools[*]} " =~ " ruff " ]] && command -v flake8 >/dev/null 2>&1; then
      tools+=("flake8")
    fi
  fi

  # Go
  if [[ -f "go.mod" ]]; then
    tools+=("gofmt" "golint" "govet")
  fi

  # Rust
  if [[ -f "Cargo.toml" ]]; then
    tools+=("rustfmt" "clippy")
  fi

  # Ruby
  if [[ -f "Gemfile" ]]; then
    if command -v rubocop >/dev/null 2>&1; then
      tools+=("rubocop")
    fi
  fi

  # Shell scripts
  if compgen -G "*.sh" > /dev/null 2>&1; then
    if command -v shellcheck >/dev/null 2>&1; then
      tools+=("shellcheck")
    fi
  fi

  # Docker files
  if [[ -f "Dockerfile" ]] || [[ -f "dockerfile" ]] || compgen -G "Dockerfile.*" > /dev/null 2>&1; then
    if command -v hadolint >/dev/null 2>&1; then
      tools+=("hadolint")
    fi
  fi

  # Markdown
  if compgen -G "*.md" > /dev/null 2>&1; then
    if command -v markdownlint >/dev/null 2>&1; then
      tools+=("markdownlint")
    elif command -v markdownlint-cli >/dev/null 2>&1; then
      tools+=("markdownlint-cli")
    fi
  fi

  if [[ ${#tools[@]} -gt 0 ]]; then
    echo "${tools[@]}"
  else
    echo ""
  fi
}

# Tool-specific linting functions
run_eslint() {
  local cmd="npx eslint"

  # Add file patterns
  if [[ $STAGED_ONLY == true ]]; then
    local staged_js_files=$(git diff --staged --name-only --diff-filter=ACM | grep -E '\.(js|jsx|ts|tsx)$' | tr '\n' ' ')
    [[ -z "$staged_js_files" ]] && return 0
    cmd="$cmd $staged_js_files"
  else
    cmd="$cmd ."
  fi

  # Add options
  [[ $FIX_MODE == true ]] && cmd="$cmd --fix"
  [[ $CHECK_ONLY == true ]] && cmd="$cmd --max-warnings 0"

  echo "🔍 Running ESLint..."
  echo "Command: $cmd"
  eval $cmd
  return $?
}

run_prettier() {
  local cmd="npx prettier"

  # Add file patterns
  if [[ $STAGED_ONLY == true ]]; then
    local staged_files=$(git diff --staged --name-only --diff-filter=ACM | grep -E '\.(js|jsx|ts|tsx|json|md|css|scss|yaml|yml)$' | tr '\n' ' ')
    [[ -z "$staged_files" ]] && return 0
    cmd="$cmd $staged_files"
  else
    cmd="$cmd ."
  fi

  if [[ $FIX_MODE == true ]]; then
    cmd="$cmd --write"
  else
    cmd="$cmd --check"
  fi

  echo "✨ Running Prettier..."
  echo "Command: $cmd"
  eval $cmd
  return $?
}

run_typescript() {
  echo "📘 Running TypeScript compiler..."
  if [[ $CHECK_ONLY == true ]]; then
    npx tsc --noEmit
  else
    npx tsc --noEmit --pretty
  fi
  return $?
}

run_ruff() {
  local check_cmd="ruff check"
  local format_cmd="ruff format"

  # Handle staged files
  if [[ $STAGED_ONLY == true ]]; then
    local staged_py_files=$(git diff --staged --name-only --diff-filter=ACM | grep '\.py$' | tr '\n' ' ')
    [[ -z "$staged_py_files" ]] && return 0
    check_cmd="$check_cmd $staged_py_files"
    format_cmd="$format_cmd $staged_py_files"
  else
    check_cmd="$check_cmd ."
    format_cmd="$format_cmd ."
  fi

  echo "⚡ Running Ruff..."

  # Run linting
  if [[ $FIX_MODE == true ]]; then
    echo "Fixing with ruff..."
    eval "$check_cmd --fix"
    ruff_lint_result=$?

    echo "Formatting with ruff..."
    eval "$format_cmd"
    ruff_format_result=$?

    return $((ruff_lint_result || ruff_format_result))
  else
    eval "$check_cmd"
    ruff_lint_result=$?

    eval "$format_cmd --check"
    ruff_format_result=$?

    return $((ruff_lint_result || ruff_format_result))
  fi
}

run_black() {
  local cmd="black"

  if [[ $STAGED_ONLY == true ]]; then
    local staged_py_files=$(git diff --staged --name-only --diff-filter=ACM | grep '\.py$' | tr '\n' ' ')
    [[ -z "$staged_py_files" ]] && return 0
    cmd="$cmd $staged_py_files"
  else
    cmd="$cmd ."
  fi

  if [[ $FIX_MODE == false ]]; then
    cmd="$cmd --check --diff"
  fi

  echo "⚫ Running Black..."
  echo "Command: $cmd"
  eval $cmd
  return $?
}

run_mypy() {
  echo "🐍 Running mypy..."
  if [[ $STAGED_ONLY == true ]]; then
    local staged_py_files=$(git diff --staged --name-only --diff-filter=ACM | grep '\.py$' | tr '\n' ' ')
    [[ -z "$staged_py_files" ]] && return 0
    mypy $staged_py_files
  else
    mypy src/kleinanzeigen_mcp
  fi
  return $?
}

run_go_tools() {
  echo "🐹 Running Go tools..."

  # gofmt
  if [[ $FIX_MODE == true ]]; then
    echo "Formatting Go code..."
    gofmt -w .
  else
    echo "Checking Go formatting..."
    local unformatted=$(gofmt -l .)
    if [[ -n "$unformatted" ]]; then
      echo "❌ Unformatted files:"
      echo "$unformatted"
      return 1
    fi
  fi

  # go vet
  echo "Running go vet..."
  go vet ./...
  local vet_result=$?

  # golint if available
  if command -v golint >/dev/null 2>&1; then
    echo "Running golint..."
    golint ./...
    local lint_result=$?
  else
    local lint_result=0
  fi

  return $((vet_result || lint_result))
}

run_rust_tools() {
  echo "🦀 Running Rust tools..."

  # rustfmt
  if [[ $FIX_MODE == true ]]; then
    echo "Formatting Rust code..."
    cargo fmt
  else
    echo "Checking Rust formatting..."
    cargo fmt -- --check
  fi
  local fmt_result=$?

  # clippy
  echo "Running Clippy..."
  if [[ $STRICT_MODE == true ]]; then
    cargo clippy -- -D warnings
  else
    cargo clippy
  fi
  local clippy_result=$?

  return $((fmt_result || clippy_result))
}

run_shellcheck() {
  echo "🐚 Running ShellCheck..."
  local shell_files

  if [[ $STAGED_ONLY == true ]]; then
    shell_files=$(git diff --staged --name-only --diff-filter=ACM | grep '\.sh$' | tr '\n' ' ')
    [[ -z "$shell_files" ]] && return 0
  else
    shell_files=$(find . -name "*.sh" -not -path "./node_modules/*" -not -path "./.git/*" | tr '\n' ' ')
  fi

  if [[ -n "$shell_files" ]]; then
    local shellcheck_cmd="shellcheck"

    # Add strict options if requested
    if [[ $STRICT_MODE == true ]]; then
      shellcheck_cmd="$shellcheck_cmd -S warning"
    fi

    eval "$shellcheck_cmd $shell_files"
    return $?
  fi
  return 0
}

run_hadolint() {
  echo "🐳 Running Hadolint (Docker linter)..."
  local docker_files

  if [[ $STAGED_ONLY == true ]]; then
    docker_files=$(git diff --staged --name-only --diff-filter=ACM | grep -E '^Dockerfile|\.dockerfile$|Dockerfile\.' | tr '\n' ' ')
    [[ -z "$docker_files" ]] && return 0
  else
    docker_files=$(find . -name "Dockerfile*" -o -name "*.dockerfile" | grep -v node_modules | grep -v .git | tr '\n' ' ')
  fi

  if [[ -n "$docker_files" ]]; then
    local hadolint_cmd="hadolint"

    # Add strict options if requested
    if [[ $STRICT_MODE == true ]]; then
      hadolint_cmd="$hadolint_cmd --failure-threshold warning"
    fi

    eval "$hadolint_cmd $docker_files"
    return $?
  fi
  return 0
}

run_markdownlint() {
  echo "📝 Running Markdown lint..."

  local cmd="markdownlint"
  local md_files

  # Check if markdownlint-cli is available instead
  if command -v markdownlint-cli >/dev/null 2>&1; then
    cmd="markdownlint-cli"
  fi

  if [[ $STAGED_ONLY == true ]]; then
    md_files=$(git diff --staged --name-only --diff-filter=ACM | grep '\.md$' | tr '\n' ' ')
    [[ -z "$md_files" ]] && return 0
    cmd="$cmd $md_files"
  else
    # Find all markdown files, excluding node_modules and .git
    md_files=$(find . -name "*.md" -not -path "./node_modules/*" -not -path "./.git/*" | tr '\n' ' ')
    [[ -z "$md_files" ]] && return 0
    cmd="$cmd $md_files"
  fi

  [[ $FIX_MODE == true ]] && cmd="$cmd --fix"

  eval $cmd
  return $?
}

# Install missing tools
install_missing_tools() {
  echo "🔧 Checking for missing linting tools..."

  # Check Node.js tools
  if [[ -f "package.json" ]]; then
    local missing_node_tools=()

    if [[ ! " ${DETECTED_LANGS[*]} " =~ " eslint " ]] && compgen -G ".eslintrc*" > /dev/null 2>&1; then
      missing_node_tools+=("eslint")
    fi

    if [[ ! " ${DETECTED_LANGS[*]} " =~ " prettier " ]] && compgen -G ".prettierrc*" > /dev/null 2>&1; then
      missing_node_tools+=("prettier")
    fi

    if [[ ${#missing_node_tools[@]} -gt 0 ]]; then
      echo "Installing missing Node.js tools: ${missing_node_tools[*]}"
      npm install --save-dev "${missing_node_tools[@]}"
    fi
  fi

  # Check Python tools
  if [[ -f "pyproject.toml" ]] || [[ -f "requirements.txt" ]]; then
    if [[ ! " ${DETECTED_LANGS[*]} " =~ " ruff " ]] && ! command -v ruff >/dev/null 2>&1; then
      echo "Installing ruff..."
      pip install ruff
    fi
  fi

  # Suggest installation for missing tools
  local suggestions=()

  if compgen -G "*.sh" > /dev/null 2>&1 && ! command -v shellcheck >/dev/null 2>&1; then
    suggestions+=("shellcheck (brew install shellcheck)")
  fi

  if [[ -f "Dockerfile" ]] && ! command -v hadolint >/dev/null 2>&1; then
    suggestions+=("hadolint (brew install hadolint)")
  fi

  if compgen -G "*.md" > /dev/null 2>&1 && ! command -v markdownlint >/dev/null 2>&1 && ! command -v markdownlint-cli >/dev/null 2>&1; then
    suggestions+=("markdownlint-cli (npm install -g markdownlint-cli)")
  fi

  if [[ ${#suggestions[@]} -gt 0 ]]; then
    echo "💡 Suggested tools to install:"
    printf '  %s\n' "${suggestions[@]}"
    echo ""
  fi
}

# Main execution
echo "🔍 CODE LINTING & FORMATTING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Auto-detect available tools
DETECTED_LANGS=($(detected_languages))

if [[ ${#DETECTED_LANGS[@]} -gt 0 ]]; then
  echo "Active language tools: ${DETECTED_LANGS[*]}"
else
  echo "Active language tools: none detected"
fi
[[ $FIX_MODE == true ]] && echo "Mode: Fix issues automatically"
[[ $CHECK_ONLY == true ]] && echo "Mode: Check only (no fixes)"
[[ $STAGED_ONLY == true ]] && echo "Scope: Staged files only"
[[ $STRICT_MODE == true ]] && echo "Level: Strict (warnings as errors)"
echo ""

# Install missing tools if needed
install_missing_tools

# Track results
results_file=$(mktemp)
total_errors=0

# Run each available tool
if [[ ${#DETECTED_LANGS[@]} -gt 0 ]]; then
  for tool in "${DETECTED_LANGS[@]}"; do
  echo "Running $tool..."

  case $tool in
    "eslint")
      run_eslint
      echo "$tool:$?" >> "$results_file"
      ;;
    "prettier")
      run_prettier
      echo "$tool:$?" >> "$results_file"
      ;;
    "tsc")
      run_typescript
      echo "$tool:$?" >> "$results_file"
      ;;
    "ruff")
      run_ruff
      echo "$tool:$?" >> "$results_file"
      ;;
    "black")
      run_black
      echo "$tool:$?" >> "$results_file"
      ;;
    "mypy")
      run_mypy
      echo "$tool:$?" >> "$results_file"
      ;;
    "gofmt"|"golint"|"govet")
      # Run Go tools once
      if ! grep -q "^go:" "$results_file" 2>/dev/null; then
        run_go_tools
        echo "go:$?" >> "$results_file"
      fi
      ;;
    "rustfmt"|"clippy")
      # Run Rust tools once
      if ! grep -q "^rust:" "$results_file" 2>/dev/null; then
        run_rust_tools
        echo "rust:$?" >> "$results_file"
      fi
      ;;
    "shellcheck")
      run_shellcheck
      echo "$tool:$?" >> "$results_file"
      ;;
    "hadolint")
      run_hadolint
      echo "$tool:$?" >> "$results_file"
      ;;
    "markdownlint"|"markdownlint-cli")
      run_markdownlint
      echo "markdownlint:$?" >> "$results_file"
      ;;
  esac

  echo ""
  done
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 LINTING SUMMARY"
echo ""

if [[ -f "$results_file" ]] && [[ -s "$results_file" ]]; then
  while IFS=: read -r tool result; do
    if [[ $result -eq 0 ]]; then
      echo "✅ $tool: passed"
    else
      echo "❌ $tool: failed"
      total_errors=$((total_errors + 1))
    fi
  done < "$results_file"
else
  echo "No linting tools were run."
fi

echo ""
if [[ $total_errors -eq 0 ]]; then
  echo "🎉 All linting checks passed!"

  if [[ $FIX_MODE == true ]]; then
    echo "💡 Files were automatically formatted and fixed."
    echo "Review changes with: git diff"
  fi
else
  echo "⚠️  $total_errors linting tool(s) reported issues."

  if [[ $FIX_MODE == false ]]; then
    echo ""
    echo "💡 To auto-fix issues, run: $0 --fix"
  fi
fi

# Cleanup
rm -f "$results_file"

exit $total_errors