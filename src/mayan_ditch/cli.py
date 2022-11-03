"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mmayan_ditch` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``mayan_ditch.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``mayan_ditch.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import os

import requests
import typer

app = typer.Typer()

session = requests.Session()
session.auth = os.environ['MAYAN_ADMIN_USER'], os.environ['MAYAN_ADMIN_PASSWORD']
session.headers.update({'Accept': 'application/json'})


@app.command()
def cabinet():
    response = session.get('http://mayan:8001/api/v4/cabinets/')
    print(response.text)
