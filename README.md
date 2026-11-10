# Mistral Ollama Test Case Generator

A single-file Python agent that uses **local Mistral models via Ollama** to generate comprehensive test cases from Product Requirements Documents (PRD).

## Features

- ✅ Uses local Mistral models (no API key required)
- ✅ Generates functional, integration, edge case, security, and performance tests
- ✅ Outputs in JSON, Markdown, or CSV format
- ✅ Works offline once models are downloaded
- ✅ Single Python file - easy to use and deploy
- ✅ Rich CLI with progress indicators

## Requirements

- Python 3.8+
- Ollama installed and running
- Mistral model downloaded (e.g., `mistral`, `mistral:7b`, `mixtral:8x7b`)

## Quick Start

### 1. Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [https://ollama.com](https://ollama.com)

### 2. Pull a Mistral Model

```bash
ollama pull mistral
# or for better quality:
ollama pull mistral:7b
# or for more advanced:
ollama pull mixtral:8x7b
```

### 3. Start Ollama Server

```bash
ollama serve
```
*Keep this running in a separate terminal*

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Generator

```bash
# Generate test cases from PRD file
python test_agent.py generate example_prd.md --output test_cases.json

# Generate in Markdown format
python test_agent.py generate example_prd.md --format markdown

# List available models
python test_agent.py models

# Show setup instructions
python test_agent.py setup
```

## Usage Examples

```bash
# Basic generation (JSON output to stdout)
python test_agent.py generate prd.md

# Save to file
python test_agent.py generate prd.md --output test_cases.json

# Markdown format
python test_agent.py generate prd.md --format markdown --output test_cases.md

# CSV format
python test_agent.py generate prd.md --format csv --output test_cases.csv

# Use different model
python test_agent.py generate prd.md --model mixtral:8x7b --output test_cases.json

# Adjust creativity
python test_agent.py generate prd.md --temperature 0.9 --output test_cases.json
```

## Output Formats

### JSON
Structured JSON with full test case details, requirements, and metadata.

### Markdown
Human-readable documentation with:
- Statistics
- Requirements list
- Detailed test cases with steps
- Formatted for easy reading

### CSV
Spreadsheet-compatible format for import into test management tools.

## Example Output

When you run:
```bash
python test_agent.py generate example_prd.md --format markdown
```

You'll get output like:

```markdown
# User Authentication System

**Test Cases:** 25

---

### TC_001: Verify user registration with valid credentials

**Type:** functional | **Priority:** high | **Req:** req_001

**Description:** Test that users can successfully register with valid email and password

**Preconditions:**
- User is on registration page
- Email and password meet requirements

**Steps:**
1. Enter valid email address
   → Email field accepts input
2. Enter valid password
   → Password field accepts input
3. Click register button
   → Account is created and user is redirected to login page

**Expected:** User account is successfully created

**Tags:** registration, authentication, positive

---
```

## Customization

### Change Model
Use any Ollama-supported model:
```bash
python test_agent.py generate prd.md --model mixtral:8x7b
```

### Adjust Creativity
Higher temperature = more creative but less deterministic:
```bash
python test_agent.py generate prd.md --temperature 0.9
```

## Troubleshooting

### Ollama not running
```bash
ollama serve
```
Make sure Ollama is running in a separate terminal.

### Model not found
```bash
ollama pull mistral
```
Download the model first.

### Connection error
Check that Ollama is running on `http://localhost:11434`

### Slow generation
- Use a smaller model (e.g., `mistral:7b` instead of `mixtral:8x7b`)
- Reduce `--max-tokens` value (default is 4000)
- Lower `--temperature`

## VSCode Integration

1. Open the folder in VSCode
2. Create a `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Generate Test Cases",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "args": ["generate", "prd.md", "--output", "test_cases.json"],
      "console": "integratedTerminal"
    }
  ]
}
```
3. Press F5 to run

## License

MIT License
