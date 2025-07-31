# tachi

A simple CLI tool for generating GitHub Actions workflows for Azure Container Apps deployments.

## Usage

Run directly without installation using uvx:

```bash
uvx tachi generate --config tachi.yaml
```

## Development

This project uses `uv` for package management. To set up the development environment:

```bash
uv sync
```

For local development:

```bash
uv pip install -e .
```