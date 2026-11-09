"""Drop, recreate and seed the web app tables.

Equivalent to ``flask --app app init-db --reset``. Requires ADMIN_PASSWORD.
"""
import sys

import click

from app import app, seed_sample_data

if __name__ == '__main__':
    with app.app_context():
        try:
            seed_sample_data(reset=True)
        except click.ClickException as exc:
            sys.exit(f'Error: {exc.message}')
