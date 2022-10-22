"""This module implements the server side of payment channels."""
import codecs
import contextlib
import os
import threading
import time

from ...two1 import TWO1_CHANNELS_FEE
from ...two1 import TWO1_CHANNELS_MIN_DURATION
from ...two1.bitcoin import Hash
from ...two1.bitcoin import PublicKey
from ...two1.bitcoin import Script
from ...two1.bitcoin import Signature
from ...two1.bitcoin import Transaction
from ...two1.bitcoin.utils import pack_compact_int
from ...two1.bitcoin.utils import pack_u32
from ...two1.channels.blockchain import TwentyOneBlockchain
from ...two1.channels.statemachine import PaymentChannelRedeemScript
from ...two1.channels.walletwrapper import Two1WalletWrapper

from .models import Channel
from .models import ChannelSQLite3
from .models import DatabaseSQLite3


class PaymentServerError(Exception):
    """Generic exception for payment channel processing errors."""
    pass


class RedeemPaymentError(PaymentServerError):
    """Raised when the payment server fails to redeem a payment."""
    pass


class ChannelClosedError(PaymentServerError):
    """Raised when attempting to access a channel that has been closed."""
    pass


class PaymentChannelNotFoundError(PaymentServerError):
    """Raised when attempting to access a channel that does not exist."""
    pass


class BadTransactionError(PaymentServerError):
    """Raised when an incorrect or malformed transaction is provided by a client."""
    pass


class TransactionVerificationError(PaymentServerError):
    """Raised when the server fails to verify the validity of a transaction."""
    pass


class Lock(contextlib.ContextDecorator):
    """An inter-thread lock decorator."""

    def __init__(self):
        """Return a new Lock instance."""
        self.tlock = threading.Lock()

    def __enter__(self):
        self.tlock.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.tlock.release()


class PaymentServer:
    """Payment channel handling.

    This class handles the server-side implementation of payment channels from
    handshake to channel close. It also implements the ability for an API
    server to redeem micropayments made within the channel.
    """

    DEFAULT_TWENTYONE_BLOCKCHAIN_URL = os.environ.get(
        "TWO1_PROVIDER_HOST", "https://blockchain.21.co") + "/blockchain/bitcoin"
    """Default mainnet blockchain URL."""

    DEFAULT_TWENTYONE_TESTNET_BLOCKCHAIN_URL = os.environ.get(
        "TWO1_PROVIDER_HOST", "https://blockchain.21.co") + "/blockchain/testnet3"
    """Default testnet blockchain URL."""

    MIN_TX_FEE = TWO1_CHANNELS_FEE
    """Minimum transaction fee for payment channel deposit/payment."""

    DUST_LIMIT = 3000
    """Minimum payment amount (dust limit) for any transaction output."""

    MIN_EXP_TIME = TWO1_CHANNELS_MIN_DURATION
    """Minimum expiration time (in sec) for a payment channel refund."""

    # Three days is the maximum length of time an unconfirmed
    # transaction will stay in a Bitcoin Core node's mempool
    EXP_TIME_BUFFER = 3 * 24 * 3600
    """Buffer time before expiration (in sec) in which to broadcast payment."""

    PROTOCOL_VERSION = 2
    """Payment channel protocol version."""

    lock = Lock()
    """Thread and process lock for database access."""

    def __init__(self, wallet, db=None, blockchain=None, zeroconf=False,
                 sync_period=600, db_dir=None):
        """Initialize the payment server.

        Args:
            wallet (two1.wallet.Wallet): wallet instance.
            db (.models.ChannelDataManager): a database wrapper to manage the
                payment channel server's interface with a persistent store of
                data.
            blockchain (two1.blockchain.provider): a blockchain data
                provider capable of broadcasting raw transactions.
            zeroconf (boolean): whether or not to use a payment channel before
                the deposit transaction has been confirmed by the network.
            sync_period (integer): how often to sync channel status (in sec).
        """
        if blockchain is None:
            url = PaymentServer.DEFAULT_TWENTYONE_BLOCKCHAIN_URL
            if wallet.testnet:
                url = PaymentServer.DEFAULT_TWENTYONE_TESTNET_BLOCKCHAIN_URL
            blockchain = TwentyOneBlockchain(url)

        self.zeroconf = zeroconf

        self._wallet = Two1WalletWrapper(wallet, blockchain)
        self._blockchain = blockchain
        self._db = db
        if db is None:
            self._db = DatabaseSQLite3(db_dir=db_dir)

        self._sync_stop = threading.Event()
        self._sync_thread = threading.Thread(
            target=self._auto_sync,
            args=(sync_period, self._sync_stop),
            daemon=True)
        self._sync_thread.start()

    def identify(self):
        """Query the payment server information.

        Returns:
            (dict): a key-value store that contains the merchant's public key
                and other custom config.
        """
        public_key = self._wallet.get_payout_public_key().compressed_bytes
        return dict(
            public_key=codecs.encode(public_key, 'hex_codec').decode(),
            version=self.PROTOCOL_VERSION,
            zeroconf=self.zeroconf,
        )

    @lock
    def open(self, deposit_tx, redeem_script):
        """Open a payment channel.

        Args:
            deposit_tx (string): signed deposit transaction which pays to a
                2 of 2 multisig script hash.
            redeem_script (string): the redeem script that comprises the script
                hash so that the merchant can verify.

        Returns:
            (string): deposit transaction id
        """
        # Parse payment channel `open` parameters
        deposit_tx = Transaction.from_hex(deposit_tx)
        redeem_script = PaymentChannelRedeemScript.from_bytes(codecs.decode(redeem_script, 'hex_codec'))

        # Verify that the deposit pays to the redeem script
        output_index = deposit_tx.output_index_for_address(redeem_script.hash160())
        if output_index is None:
            raise BadTransactionError('Deposit does not pay to the provided script hash.')

        # Parse payment channel data for open
        deposit_txid = str(deposit_tx.hash)
        merchant_public_key = codecs.encode(redeem_script.merchant_public_key.compressed_bytes, 'hex_codec').decode()
        amount = deposit_tx.outputs[output_index].value

        # Verify that one of the public keys belongs to the merchant
        valid_merchant_public_key = self._wallet.validate_public_key(redeem_script.merchant_public_key)
        if not valid_merchant_public_key:
            raise BadTransactionError('Public key does not belong to the merchant.')

        # Verify that the deposit is not already part of a payment channel
        if self._db.pc.lookup(deposit_txid):
            raise BadTransactionError('That deposit has already been used to create a channel.')

        # Verify that the lock time is an allowable amount in the future
        minimum_locktime = int(time.time()) + self.MIN_EXP_TIME - 1
        if redeem_script.expiration_time < minimum_locktime:
            raise TransactionVerificationError('Transaction locktime must be further in the future.')

        # Open and save the payment channel
        self._db.pc.create(deposit_tx, merchant_public_key, amount, redeem_script.expiration_time)

        # Set the channel to `ready` if zeroconf is enabled
        if self.zeroconf:
            self._db.pc.update_state(deposit_txid, ChannelSQLite3.READY)

        return str(deposit_tx.hash)

    @lock
    def receive_payment(self, deposit_txid, payment_tx):
        """Receive and process a payment within the channel.

        The customer makes a payment in the channel by sending the merchant a
        half-signed payment transaction. The merchant signs the other half of
        the transaction and saves it in its records (but does not broadcast it
        or send it to the customer). The merchant responds with 200 to verify
        that the payment was handled successfully.

        Args:
            deposit_txid (string): string representation of the deposit
                transaction hash. This is used to look up the payment channel.
            payment_tx (string): half-signed payment transaction from a
                customer.
        Returns:
            (string): payment transaction id
        """
        # Parse payment channel `payment` parameters
        payment_tx = Transaction.from_hex(payment_tx)

        # Get channel and addresses related to the deposit
        channel = self._db.pc.lookup(deposit_txid)

        if not channel:
            raise PaymentChannelNotFoundError('Related channel not found.')

        # Get merchant public key information from payment channel
        merchant_public_key = PublicKey.from_hex(channel.merchant_pubkey)

        # Verify that redeem script contains the merchant public key
        redeem_script = PaymentChannelRedeemScript.from_bytes(payment_tx.inputs[0].script[-1])
        if redeem_script.merchant_public_key.to_hex() != merchant_public_key.to_hex():
            raise BadTransactionError('Invalid merchant pubkey.')

        # Verify that the payment has a valid signature from the customer
        txn_copy = payment_tx._copy_for_sig(0, Transaction.SIG_HASH_ALL, redeem_script)
        msg_to_sign = bytes(Hash.dhash(bytes(txn_copy) + pack_u32(Transaction.SIG_HASH_ALL)))
        sig = Signature.from_der(payment_tx.inputs[0].script[0][:-1])
        if not redeem_script.customer_public_key.verify(msg_to_sign, sig, False):
            raise BadTransactionError('Invalid payment signature.')

        # Verify the length of the script is what we expect
        if len(payment_tx.inputs[0].script) != 3:
            raise BadTransactionError('Invalid payment channel transaction structure.')

        # Verify the script template is valid for accepting a merchant signature
        if (not Script.validate_template(payment_tx.inputs[0].script, [bytes, 'OP_1', bytes]) and
                not Script.validate_template(payment_tx.inputs[0].script, [bytes, 'OP_TRUE', bytes])):
            raise BadTransactionError('Invalid payment channel transaction structure.')

        # Verify that the payment channel is ready
        if channel.state == ChannelSQLite3.CONFIRMING:
            confirmed = self._blockchain.check_confirmed(channel.deposit_txid)
            if confirmed:
                self._db.pc.update_state(channel.deposit_txid, ChannelSQLite3.READY)
            else:
                raise ChannelClosedError('Payment channel not ready.')
        elif channel.state == ChannelSQLite3.CLOSED:
            raise ChannelClosedError('Payment channel closed.')

        # Verify that payment is made to the merchant public key
        index = payment_tx.output_index_for_address(merchant_public_key.hash160())
        if index is None:
            raise BadTransactionError('Payment must pay to merchant pubkey.')

        # Verify that both payments are not below the dust limit
        for output_index, output in enumerate(payment_tx.outputs):
            if output.value < PaymentServer.DUST_LIMIT:
                # Payment to merchant is less than dust limit
                if output_index == index:
                    raise BadTransactionError(
                        'Initial payment must be greater than {}.'.format(PaymentServer.DUST_LIMIT))
                # Payment to customer is less than dust limit
                else:
                    raise BadTransactionError(
                        'Payment channel balance is not large enough to make payment.')

        # Validate that the payment is more than the last one
        new_pmt_amt = payment_tx.outputs[index].value
        if new_pmt_amt <= channel.last_payment_amount:
            raise BadTransactionError('Payment must be greater than 0.')

        # Verify that the transaction has adequate fees
        net_pmt_amount = sum([d.value for d in payment_tx.outputs])
        deposit_amount = channel.amount
        fee = deposit_amount - net_pmt_amount
        if fee < PaymentServer.MIN_TX_FEE:
            raise BadTransactionError('Payment must have adequate fees.')

        # Recreate redeem script from merchant side
        redeem_script_copy = PaymentChannelRedeemScript(
            merchant_public_key,
            redeem_script.customer_public_key,
            channel.expires_at)
        if redeem_script.to_hex() != redeem_script_copy.to_hex():
            raise BadTransactionError('Invalid redeem script.')

        # Recreate customer payment from merchant side
        payment_tx_copy = self._wallet.create_unsigned_payment_tx(
            channel.deposit_tx, redeem_script, new_pmt_amt, fee)

        # Recreate signed input script using signature from customer
        hash_type = pack_compact_int(Transaction.SIG_HASH_ALL)
        signed_input_script = Script(
            [sig.to_der() + hash_type, "OP_1", bytes(redeem_script)])
        payment_tx_copy.inputs[0].script = signed_input_script

        if payment_tx.to_hex() != payment_tx_copy.to_hex():
            raise BadTransactionError('Invalid payment channel transaction structure.')

        # Update the current payment transaction
        self._db.pc.update_payment(deposit_txid, payment_tx_copy, new_pmt_amt)
        self._db.pmt.create(deposit_txid, payment_tx_copy, new_pmt_amt - channel.last_payment_amount)

        return str(payment_tx_copy.hash)

    def status(self, deposit_txid):
        """Get a payment channel's current status.

        Args:
            deposit_txid (string): string representation of the deposit
                transaction hash. This is used to look up the payment channel.
        """
        channel = self._db.pc.lookup(deposit_txid)

        if not channel:
            raise PaymentChannelNotFoundError('Related channel not found.')

        return dict(status=channel.state,
                    balance=channel.last_payment_amount,
                    time_left=channel.expires_at)

    @lock
    def close(self, deposit_txid, deposit_txid_signature):
        """Close a payment channel.

        Args:
            deposit_txid (string): string representation of the deposit
                transaction hash. This is used to look up the payment channel.
            deposit_txid_signature (two1.bitcoin.Signature): a signature
                consisting solely of the deposit_txid to verify the
                authenticity of the close request.
        """
        channel = self._db.pc.lookup(deposit_txid)

        # Verify that the requested channel exists
        if not channel:
            raise PaymentChannelNotFoundError('Related channel not found.')

        # Parse payment channel `close` parameters
        try:
            signature_der = codecs.decode(deposit_txid_signature, 'hex_codec')
            deposit_txid_signature = Signature.from_der(signature_der)
        except TypeError:
            raise TransactionVerificationError('Invalid signature provided.')

        # Verify that there is a valid payment to close
        if not channel.payment_tx:
            raise BadTransactionError('No payments made in channel.')

        # Verify that the user is authorized to close the channel
        payment_tx = channel.payment_tx
        redeem_script = PaymentChannelRedeemScript.from_bytes(payment_tx.inputs[0].script[-1])
        sig_valid = redeem_script.customer_public_key.verify(
            deposit_txid.encode(), deposit_txid_signature)
        if not sig_valid:
            raise TransactionVerificationError('Invalid signature.')

        # Sign the final transaction
        self._wallet.sign_half_signed_payment(payment_tx, redeem_script)

        # Broadcast payment transaction to the blockchain
        self._blockchain.broadcast_tx(payment_tx.to_hex())

        # Record the broadcast in the database
        self._db.pc.update_state(deposit_txid, ChannelSQLite3.CLOSED)

        return str(payment_tx.hash)

    @lock
    def redeem(self, payment_txid):
        """Determine the validity and amount of a payment.

        Args:
            payment_txid (string): the hash in hexadecimal of the payment
                transaction, often referred to as the transaction id.

        Returns:
            pmt_amount (int): value in satoshis of the incremental payment.

        Raises:
            PaymentError: reason why payment is not redeemable.
        """
        # Verify that we have this payment transaction saved
        payment = self._db.pmt.lookup(payment_txid)
        if not payment:
            raise PaymentChannelNotFoundError('Payment not found.')

        # Verify that this payment exists within a channel
        channel = self._db.pc.lookup(payment.deposit_txid)
        if not channel:
            raise PaymentChannelNotFoundError('Channel not found.')

        # Verify that the payment channel is ready
        if channel.state == ChannelSQLite3.CONFIRMING:
            raise ChannelClosedError('Payment channel not ready.')
        elif channel.state == ChannelSQLite3.CLOSED:
            raise ChannelClosedError('Payment channel closed.')

        # Calculate and redeem the current payment
        redeem_success = self._db.pmt.redeem(payment_txid)

        # Verify that the payment has not already been redeemed
        if not redeem_success:
            raise RedeemPaymentError('Payment already redeemed.')
        return payment.amount

    @lock
    def sync(self):
        """Sync the state of all payment channels."""
        # Look up all channels
        channel_query = self._db.pc.lookup()

        # Check whether the return result is a single Channel or list
        if isinstance(channel_query, Channel):
            payment_channels = [channel_query]
        else:
            payment_channels = channel_query

        # Return if there are no payment channels to sync
        if not payment_channels:
            return

        for pc in payment_channels:

            # Skip sync if channel is closed
            if pc.state == ChannelSQLite3.CLOSED:
                continue

            # Check for deposit confirmation
            if pc.state == ChannelSQLite3.CONFIRMING and self._blockchain.check_confirmed(pc.deposit_txid):
                self._db.pc.update_state(pc.deposit_txid, ChannelSQLite3.READY)

            # Check if channel got closed
            if pc.state in (ChannelSQLite3.CONFIRMING, ChannelSQLite3.READY) and pc.payment_tx:
                redeem_script = PaymentChannelRedeemScript.from_bytes(pc.payment_tx.inputs[0].script[-1])
                deposit_tx_utxo_index = pc.deposit_tx.output_index_for_address(redeem_script.hash160())
                spend_txid = self._blockchain.lookup_spend_txid(pc.deposit_txid, deposit_tx_utxo_index)
                if spend_txid:
                    self._db.pc.update_state(pc.deposit_txid, ChannelSQLite3.CLOSED)

            # Check for channel expiration
            if pc.state != ChannelSQLite3.CLOSED:
                if time.time() + PaymentServer.EXP_TIME_BUFFER > pc.expires_at and pc.payment_tx:
                    redeem_script = PaymentChannelRedeemScript.from_bytes(pc.payment_tx.inputs[0].script[-1])
                    self._wallet.sign_half_signed_payment(pc.payment_tx, redeem_script)
                    self._blockchain.broadcast_tx(pc.payment_tx.to_hex())
                    self._db.pc.update_payment(pc.deposit_txid, pc.payment_tx, pc.last_payment_amount)
                    self._db.pc.update_state(pc.deposit_txid, ChannelSQLite3.CLOSED)

    def _auto_sync(self, timeout, stop_event):
        """Lightweight thread for automatic channel syncs."""
        while not stop_event.is_set():
            stop_event.wait(timeout)
            self.sync()
