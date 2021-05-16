import os
import click
from app import create_app, db, mail
from app.models import User, Role, Orgpart
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app,db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, mail=mail, Orgpart=Orgpart)

@app.cli.command()
#@click.argument('test_names', nargs=1)
#def test(test_names):
def test():
    """Run the unit tests. """
    import unittest
    #if test_names:
    #tests = unittest.TestLoader().discover('tests')
    #else:
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)