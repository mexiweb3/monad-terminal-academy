r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Terminal Academy"

# Puertos alternos (4000-4005 estaban ocupados en este host)
TELNET_PORTS = [4100]
WEBSERVER_PORTS = [(4101, 4102)]  # (external, internal)
WEBSOCKET_CLIENT_PORT = 4103
AMP_PORT = 4105

# Cloudflare Quick Tunnel — WS tunnel to port 4103
WEBSOCKET_CLIENT_URL = "wss://administrative-sites-colony-broke.trycloudflare.com"

# Start new characters in the Monad Terminal Academy home room si existe
START_LOCATION = "#3"  # Monad Terminal Academy /home — creado por build_academy


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
