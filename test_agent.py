#!/usr/bin/env python3
"""
Mistral Test Case Generator - Local Ollama Edition
Single file agent. Save as test_agent.py and run with: python test_agent.py generate your_prd.md
"""

import os
import json
import sys
import requests
from typing import Dict, List
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "mistral"

SYSTEM_PROMPT = """You are an expert QA engineer. Generate comprehensive test cases from PRDs.

Output ONLY valid JSON in this exact format:
{
  "test_suite": {
    "name": "string",
    "description": "string",
    "requirements": [{"id": "req_001", "text": "string", "type": "functional", "priority": "high"}],
    "test_cases": [{
      "id": "TC_001",
      "title": "string",
      "description": "string",
      "type": "functional|integration|edge_case|security|performance|negative",
      "priority": "high|medium|low",
      "requirement_id": "req_001",
      "preconditions": ["string"],
      "steps": [{"number": 1, "action": "string", "expected_result": "string"}],
      "expected_result": "string",
      "tags": ["string"]
    }]
  }
}

Rules:
1. Extract ALL requirements from PRD
2. Generate 2-4 test cases per requirement
3. Include positive, negative, and edge cases
4. Be specific and detailed
5. Use clear, actionable language"""


def check_ollama():
    try:
        return requests.get("http://localhost:11434/api/tags", timeout=5).ok
    except:
        return False


def list_models():
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=10)
        return [m["name"] for m in resp.json().get("models", [])]
    except:
        return []


def generate(prd_text, model=DEFAULT_MODEL, temperature=0.7, max_tokens=4000):
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"PRD:\n{prd_text}"}
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
        "format": "json"
    }
    resp = requests.post(OLLAMA_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    content = resp.json()["message"]["content"]
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:].strip()
    if content.startswith("```"):
        content = content[3:].strip()
    if content.endswith("```"):
        content = content[:-3].strip()
    return json.loads(content)


def format_markdown(data):
    ts = data.get("test_suite", {})
    md = f"# {ts.get('name', 'Test Suite')}\n\n{ts.get('description', '')}\n\n"
    md += f"**Test Cases:** {len(ts.get('test_cases', []))}\n\n---\n\n"
    for tc in ts.get("test_cases", []):
        md += f"### {tc.get('id')}: {tc.get('title')}\n\n"
        md += f"**Type:** {tc.get('type')} | **Priority:** {tc.get('priority')} | **Req:** {tc.get('requirement_id')}\n\n"
        md += f"**Description:** {tc.get('description')}\n\n"
        if tc.get("preconditions"):
            md += "**Preconditions:**\n" + "\n".join(f"- {p}" for p in tc["preconditions"]) + "\n\n"
        if tc.get("steps"):
            md += "**Steps:**\n" + "\n".join(f"{s['number']}. {s['action']}\n   → {s['expected_result']}" for s in tc["steps"]) + "\n\n"
        md += f"**Expected:** {tc.get('expected_result')}\n\n"
        if tc.get("tags"):
            md += f"**Tags:** {', '.join(tc['tags'])}\n\n"
        md += "---\n\n"
    return md


def format_csv(data):
    import csv
    import io
    ts = data.get("test_suite", {})
    tc = ts.get("test_cases", [])
    if not tc:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "title", "type", "priority", "requirement_id", "description", "preconditions", "steps", "expected_result", "tags"])
    writer.writeheader()
    for t in tc:
        writer.writerow({
            "id": t.get("id"), "title": t.get("title"), "type": t.get("type"),
            "priority": t.get("priority"), "requirement_id": t.get("requirement_id"),
            "description": t.get("description"),
            "preconditions": "; ".join(t.get("preconditions", [])),
            "steps": "; ".join(f"{s['number']}. {s['action']}" for s in t.get("steps", [])),
            "expected_result": t.get("expected_result"),
            "tags": "; ".join(t.get("tags", []))
        })
    return output.getvalue()


@click.group()
def cli():
    pass


@cli.command()
@click.argument('prd_file', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='Output file')
@click.option('--model', '-m', default=DEFAULT_MODEL, help='Model to use')
@click.option('--temperature', '-t', default=0.7, help='Creativity (0-1)')
@click.option('--format', '-f', type=click.Choice(['json', 'markdown', 'csv']), default='json')
def generate_cmd(prd_file, output, model, temperature, format):
    try:
        if not check_ollama():
            console.print("[red]Error: Ollama not running. Start with: ollama serve[/red]")
            sys.exit(1)
        
        with open(prd_file, 'r') as f:
            prd_text = f.read()
        
        console.print(Panel.fit(f"[cyan]Generating from {os.path.basename(prd_file)}[/cyan]"))
        
        with console.status("[green]Generating..."):
            result = generate(prd_text, model, temperature)
        
        if format == 'markdown':
            output_text = format_markdown(result)
        elif format == 'csv':
            output_text = format_csv(result)
        else:
            output_text = json.dumps(result, indent=2)
        
        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            console.print(f"[green]Saved to {output}[/green]")
        else:
            console.print(output_text)
        
        tc = result.get("test_suite", {}).get("test_cases", [])
        console.print(f"\n[green]✓ Generated {len(tc)} test cases[/green]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def models():
    if not check_ollama():
        console.print("[red]Ollama not running[/red]")
        return
    models = list_models()
    if models:
        table = Table(title="Available Models")
        table.add_column("Model", style="cyan")
        for m in models:
            table.add_row(m)
        console.print(table)
    else:
        console.print("[yellow]No models found. Run: ollama pull mistral[/yellow]")


@cli.command()
def setup():
    console.print(Panel.fit("[bold]Mistral Test Agent - Setup[/bold]"))
    console.print("\n1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
    console.print("2. Pull model: ollama pull mistral")
    console.print("3. Start server: ollama serve")
    console.print("4. Run: python test_agent.py generate prd.md --output test_cases.json")


if __name__ == "__main__":
    cli()
