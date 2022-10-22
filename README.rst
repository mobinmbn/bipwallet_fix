
bipwallet

===========

**Simple BIP32 (HD) wallet creation for: BTC, BTG, BCH, ETH, LTC, DASH, DOGE**

BIP32 (or HD for "hierarchical deterministic") wallets allow you to create
child wallets which can only generate public keys and don't expose a
private key to an insecure server.

This library simplify the process of creating new wallets for the
BTC, BTG, BCH, ETH, LTC, DASH and DOGE cryptocurrencies.

Most of the code here is forked from:

- Steven Buss's `Bitmerchant <https://github.com/sbuss/bitmerchant>`_ (original)
- BlockIo's `multimerchant-python <https://github.com/BlockIo/multimerchant-python>`_ (fork of Bitmerchant)
- Michail Brynard's `Ethereum BIP44 Python <https://github.com/michailbrynard/ethereum-bip44-python>`_

I simply added support for a few more cryptocurrencies (BCH, BTG, DASH), as well as created
methods to simplify the creation of HD wallets and child wallets.

Enjoy!

--------------

Installation
-------------

Install via PiP:

.. code:: bash

   $ sudo pip install bipwallet


Example code:
=============

Create HD Wallet
----------------

The following code creates a new Bitcoin HD wallet:

.. code:: python

    # create_btc_wallet.py

    from bipwallet import wallet

    # generate 12 word mnemonic seed
    seed = wallet.generate_mnemonic()

    # create bitcoin wallet
    w = wallet.create_wallet(network="BTC", seed=seed, children=1)

    print(w)

Output looks like this:

.. code:: bash

    $ python create_btc_wallet.py

    {
        "coin": "BTC", 
        "seed": "vivid area able second bicycle advance demand alpha flip stable drift route", 
        "private_key": "cb85f8925621e5322b7d8ec93a5bccddf708d687a76908c7d8e3b8e558b6d033", 
        "public_key": "049868c6d613c74c4fc57dbf2b4320f8803f76cfe29057f4c87784ea5cf70b7a62d130e04465b8e14b15f41870237351ebd17f02a370c3d92d49e6063540ad9001", 
        "xprivate_key": "xprv9s21ZrQH143K2evfWaJQox8GpyJtiUULREbYkaUJeRwisxbkx5RvoUxtN9vkgKGRs7gKedVkPSTMJvE3BG9UvWYm1ctqn1819izk6BP258y", 
        "xpublic_key": "xpub661MyMwAqRbcF918cbqRB651P19P7wCBnTX9YxsvCmUhkkvuVckBMHHNDSWkf6JaZmiYmMWm34Z8NAFrKieHrceEFfsFhagHkkeX6S9FE7D", 
        "address": "1CattPQcAfDNvTieTWyDBZaw1TeooLnTWM", 
        "wif": "L43LJaWmT2VsDmLwyLCpF3xZfdXQwdYT69cpbAKNh7JYzjGBmdbL", 
        "children": [
            {
                "private_key": "e4de7d62ac9874708e7d7de928264255b0d6a8734600d74c75644ae0d1043c97", 
                "public_key": "046090c6e2dcfdcdde8185506461d0606fba96b9579d82cf35f31dbc6d5aaf69450f2d21ab1dc5530e02573677df1d4f92a53fed6b1f61b612e719147ae7c17229", 
                "xpublic_key": "xpub68pfp8h5CJQ9c2aVErAyuasZx5xDDTGPSwgyA7uT1fRX9p4AWRHjd9PsknRhV46quRnPZ7YBECkovzojxv4cpz76iC9UEuSZ4JuuiGhKnLp", 
                "xprivate_key": "xprv9uqKQdABMvqrPYW28pdyYSvqQ47iozYY5imNMjVqTKtYH1j1xsyV5M5PuWTTPAsSmC2Zr5D7hHjaDaYaDVdPRf2uSfjmP3Ym6ifVXmmki2U", 
                "address": "1AyJWCTVAPbztKCne4MU7zgBLz8sa7gm67", 
                "segwit": "32G3MvzimEftSDQrU9qgWq6k8Qea9nHsVo", 
                "wif": "L4tbu5mM9aabaFLmAJF6SBXA4j77uygkR5Du65JnA7aZtWMERPzf", 
                "path": "m/0", 
                "bip32_path": "m/44'/0'/0'/0", 
                "xpublic_key_prime": "xpub68pfp8h5CJQ9c2aVErAyuasZx5xDDTGPSwgyA7uT1fRX9p4AWRHjd9PsknRhV46quRnPZ7YBECkovzojxv4cpz76iC9UEuSZ4JuuiGhKnLp", 
                "xprivate_key_prime": "xprv9uqKQdABMvqrPYW28pdyYSvqQ47iozYY5imNMjVqTKtYH1j1xsyV5M5PuWTTPAsSmC2Zr5D7hHjaDaYaDVdPRf2uSfjmP3Ym6ifVXmmki2U"
            }
        ], 
        "segwit": "3AzjyuhQbMgyLtHerCSEpTxKLAuv7S8qsn", 
        "xpublic_key_prime": "xpub68pfp8hDXxw7nbMSXdLDSaQ6aCtYSGPwqMRijt1ARoBmvbWC1VgRCoSyerhUPzD3ZNVuMAh2khFiesx2g3Xt79sVyeHBcB6xu2wWXpJgTND", 
        "xprivate_key_prime": "xprv9uqKQdAKhbNpa7GyRboD5STN2B442og6U8W7wVbYsTeo3oB3TxNAf18VoZGhBH14PsizxF3KKQguMBzD8ftit7byNZR4yGqUdF5TCMJHkY5"
    }

Similarly, you can do the same for an Ethereum wallet:

.. code:: python

    # create_eth_wallet.py

    from bipwallet import wallet

    seed = wallet.generate_mnemonic()
    w = wallet.create_wallet(network="ETH", seed=seed, children=1)

    print(w)

Output looks like this (no WIF for Ethereum):

.. code:: bash

    $ python create_eth_wallet.py

    {
        "coin": "ETH", 
        "seed": "laptop choose mom any vault knife tomato fruit enemy sunny shop loud", 
        "private_key": "0488ade4038f32b901800000006ee311c2df99d7562da4e42676ea3f85eb481c7733e5d74bd9fda288d3c70b75005a74a8a99aada2406a23de32dfc0940266e058c4a9146f650893101eb9671035", 
        "public_key": "0488b21e038f32b901800000006ee311c2df99d7562da4e42676ea3f85eb481c7733e5d74bd9fda288d3c70b750208950da5ec3a8630208ec4140f0977104d374bc89944a0ec22ca08bcf95407fe", 
        "xprivate_key": "xprv9yiTrsi4an9SgsRaYZoYuuVG62BsPvahYoe8NzxGXfFEesUWuJqH3jWuYsv3DTHwmMo7WTSv15ZoVXw7RpDYHL1La2oGASPPuaWrU2iYgHn", 
        "xpublic_key": "xpub6ChpGPExR9hjuMW3ebLZH3Rze42MoPJYv2ZjBPMt5znDXfofSr9XbXqPQ8KkJvvWg44MihtYc8nohg9ynTCQN3t2ZjaPHNtNyHffitFSekT", 
        "address": "0x3dcc6705c74d7013db44bedf332721886e60c643", 
        "wif": "", 
        "children": [
            {
                "address": "0x3dcc6705c74d7013db44bedf332721886e60c643", 
                "public_key": "0488b21e038f32b901800000006ee311c2df99d7562da4e42676ea3f85eb481c7733e5d74bd9fda288d3c70b750208950da5ec3a8630208ec4140f0977104d374bc89944a0ec22ca08bcf95407fe", 
                "private_key": "0488b21e05577df33a00000000ff5526669afcf1d925731919027f792b5ea18060bb0bc0ec22e325b664384ac003aa0d91a5737babe46f1892912f090f82b9532cf6a9f94551c97e3d03e12ce558", 
                "xpublic_key": "xpub6G4LbJHtVh8DmkQJaXABS7tpmcGXXcLe6Urk3wbzn5tVBL2tF8V25bgoZBMbSsVqGN9UUeJuwfv2LYArhErgHd21dvGUbf95zy8UkqzHXb3", 
                "xprivate_key": "xpub6G4LbJHtVh8DmkQJaXABS7tpmcGXXcLe6Urk3wbzn5tVBL2tF8V25bgoZBMbSsVqGN9UUeJuwfv2LYArhErgHd21dvGUbf95zy8UkqzHXb3", 
                "path": "m/0", 
                "bip32_path": "m/44'/60'/0'/0"
            }
        ]
    }

\* Valid options for `network` are: BTC, BTG, BCH, LTC, DASH, DOGE

Create Child Wallet
-------------------

You can create child-wallets (BIP32 wallets) from the HD wallet's
**Extended Public Key** to generate new public addresses without
revealing your private key.

Example:

.. code-block:: python

    # create_child_wallet.py

    from bipwallet import wallet

    WALLET_PUBKEY = 'YOUR WALLET XPUB'

    # generate address for specific user (id = 10)
    user_addr = wallet.create_address(network="BTC", xpub=WALLET_PUBKEY, child=10)

    # or generate a random address, based on timestamp
    rand_addr = wallet.create_address(network="BTC", xpub=WALLET_PUBKEY)

    print("User Address\n", user_addr)
    print("Random Address\n", rand_addr)

Output looks like this:

.. code:: bash

    $ python create_child_wallet.py

    User Address
    {
        "path": "m/0/10", 
        "bip32_path": "m/44'/0'/0'/0/10", 
        "address": "14NqySawappLCLwFUH6hEumbaTtojydR6d", 
        "segwit": "3NuvdbBJSzzmaq8wv42EyGQWpRCpx5R9wH", 
        "private_key": "6e7c2458e6380eb241121a26158390ad9a1f99799eed8bd33e3ae425240874c5", 
        "public_key": "048cadc3f6b92029ac1a89ca5b52349063d4426f5ec5b75e4a4f56f93e37284e7725260c7d9570f1f5b82576752f808ea154573b36c4fb349e3fbff6e95b3bd31c", 
        "xpublic_key": "xpub69jDfXiciYbG5Y2wsy8MyjS9b9xxD5EEuVJq1sSRSFYoJmKbMS5RTgygFTsRpSa7eFE8mCJdGvAXTs4oz18hiJwGtzXjQrovAfitXZmEKTV", 
        "xprivate_key": "xprv9vjsG2BitB2xs3xUmwbMcbVR388TocWPYGPEDV2osv1pRxzSotmAutfCQCcN7ey8oXBn8ow6dzGL3epT6tZ7ey1hkqbp1H3ZVhNwacquNef", 
        "wif": "KzvUk6y6A8vYjVkgVmWS6UbDreDGvg3CHJtSM32dHk5M4tXNzck3", 
        "xpublic_key_prime": "xpub69jDfXiciYbG5Y2wsy8MyjS9b9xxD5EEuVJq1sSRSFYoJmKbMS5RTgygFTsRpSa7eFE8mCJdGvAXTs4oz18hiJwGtzXjQrovAfitXZmEKTV", 
        "xprivate_key_prime": "xprv9vjsG2BitB2xs3xUmwbMcbVR388TocWPYGPEDV2osv1pRxzSotmAutfCQCcN7ey8oXBn8ow6dzGL3epT6tZ7ey1hkqbp1H3ZVhNwacquNef"
    }
    Random Address
    {
        "path": "m/0/651778924", 
        "bip32_path": "m/44'/0'/0'/0/651778924", 
        "address": "15452g5FE1UDQbBffuLjMnHjXHKhxaPzHU", 
        "segwit": "39dr9PK3MhTacJE1c226WdRQdoyhGc5X2D", 
        "private_key": "3ee0ddb88c359ee9e25401a6d52837670c2cd440e932495e2e5058497afa81b7", 
        "public_key": "0426701b3ba96dfb1901b724b902c274aa8d0b8317119163b1681612a594af66f7515febf156eb7645132d16cdac27269d5a286513232c89f3283a34a1043d585b", 
        "xpublic_key": "xpub69jDfXifFLmNUc7YUXnQsgz7TGVUREN8JaCA6Npaqv1gjsQRMbYHkx6Hv58cDa6GXeBd19LKBeH2HWhA71S7ZbtJziJxkv9rdiLExfJ1YPW", 
        "xprivate_key": "xprv9vjsG2BmQyD5G835NWFQWZ3NuEez1meGwMGZHzQyHaUhs55Gp4E3D9mp4nLru3F3dhTk4j8jXWEPDFKr9tqfdWtCWo79kKRtQTpJBEWha8C", 
        "wif": "KyKwNVrVWASXL46KBvayQK4guHZC2n8dMuTYX6AqGT3sVeELCucY", 
        "xpublic_key_prime": "xpub69jDfXifFLmNUc7YUXnQsgz7TGVUREN8JaCA6Npaqv1gjsQRMbYHkx6Hv58cDa6GXeBd19LKBeH2HWhA71S7ZbtJziJxkv9rdiLExfJ1YPW", 
        "xprivate_key_prime": "xprv9vjsG2BmQyD5G835NWFQWZ3NuEez1meGwMGZHzQyHaUhs55Gp4E3D9mp4nLru3F3dhTk4j8jXWEPDFKr9tqfdWtCWo79kKRtQTpJBEWha8C"
    }

-----

IMPORTANT
=========

I **highly** recommend that you familiarize yourself with the Blockchain technology and
be aware of security issues.
Reading `Mastering Bitcoin <https://github.com/bitcoinbook/bitcoinbook>`_ and going over
Steven Buss's security notes on the `Bitmerchant repository <https://github.com/sbuss/bitmerchant>`_
is a good start.

Enjoy!
