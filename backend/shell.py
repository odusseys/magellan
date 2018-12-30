from IPython import start_ipython
from magellan.app import get_app
from magellan.services.database import db
from magellan.models import *
from traitlets.config import Config

c = Config()

# Now we can set options as we would in a config file:
#   c.Class.config_value = value
# For example, we can set the exec_lines option of the InteractiveShellApp
# class to run some code when the IPython REPL starts
c.InteractiveShellApp.exec_lines = [
    '%load_ext autoreload',
    '%autoreload 2',
    'from magellan.app import get_app',
    'app = get_app()',
    'from magellan.models import *'
]

app = get_app()

start_ipython(config=c)
