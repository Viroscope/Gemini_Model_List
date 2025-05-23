#!/usr/bin/env python3
"""
Command-line interface for Gemini_Model_List project.
"""
import sys
import json

import click
from google import genai
from main import load_api_key, create_db


@click.group()
def cli():
    """Gemini Model List CLI"""
    pass


@cli.command('list-models')
def list_models():
    """Fetch and display available Gemini models"""
    # Initialize database
    create_db()
    api_key = load_api_key()
    if not api_key:
        click.echo('API key not found in database. Please set it via the GUI or manually.', err=True)
        sys.exit(1)
    try:
        client = genai.Client(api_key=api_key)
        models = client.models.list()
    except Exception as e:
        click.echo(f'Error fetching models: {e}', err=True)
        sys.exit(1)
    # Pretty-print model fields
    models = models or []
    if not models:
        click.echo('No models found.')
        return
    for model in models:
        # model is a google.genai.Model object; convert to dict
        info = {
            'name': model.name,
            'display_name': model.display_name,
            'description': model.description,
            'version': model.version,
            'input_token_limit': model.input_token_limit,
            'output_token_limit': model.output_token_limit,
        }
        click.echo(json.dumps(info, indent=2))


if __name__ == '__main__':
    cli()