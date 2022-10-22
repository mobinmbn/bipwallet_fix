""" This is a backwards compatibility shim to show a warning when a user imports two1.lib """
import sys
import logging
# import two1.commands.util.uxstring as uxstring

# Import all of the libs as the package name
import bipwallet.two1.bitcoin as bitcoin
import bipwallet.two1.bitrequests as bitrequests
import bipwallet.two1.bitserv as bitserv
import bipwallet.two1.blockchain as blockchain
import bipwallet.two1.channels as channels
import bipwallet.two1.crypto as crypto
import bipwallet.two1.server as server
import bipwallet.two1.wallet as wallet
from bipwallet.two1.commands.util import uxstring

# Force the lib modules to be importable as the moved libs

sys.modules["{}.{}".format(__name__, "bitcoin")] = bitcoin
sys.modules["{}.{}".format(__name__, "bitrequests")] = bitrequests
sys.modules["{}.{}".format(__name__, "bitserv")] = bitserv
sys.modules["{}.{}".format(__name__, "blockchain")] = blockchain
sys.modules["{}.{}".format(__name__, "channels")] = channels
sys.modules["{}.{}".format(__name__, "crypto")] = crypto
sys.modules["{}.{}".format(__name__, "server")] = server
sys.modules["{}.{}".format(__name__, "wallet")] = wallet

# Warn the users to update their imports
logger = logging.getLogger(__name__)
logger.warn(uxstring.UxString.lib_import_warning)
