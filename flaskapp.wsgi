#!/var/www/webserver/drogsok/public_html/venv/bin/python
import sys
import site

# Add the site-packages of the virtual environment
site.addsitedir('/var/www/webserver/drogsok/public_html/venv/lib/python3.10/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.insert(0, '/var/www/webserver/drogsok/public_html')

from flaskapp import app as application
