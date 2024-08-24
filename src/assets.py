import datetime
import re
from logging import getLogger

from actual.queries import create_transaction

logging = getLogger(__name__)


def _get_generated_transactions(transactions):
    """A small hack to make sure we only get the transactions we've generated"""
    return [t for t in transactions if t.notes and "[Automated]" in t.notes and "LKV" in t.notes]


def _get_last_known_value(name, transactions):
    """Get the last known value of an entity with the given name in the given account"""
    for t in _get_generated_transactions(transactions):
        if name in t.notes:
            return int(re.search(r"LKV: (\d+)", t.notes).group(1))
    return 0


def update_asset_value(name, value, account, payee, actual, transactions):
    """
    Updates the last known values for assets in the given account (house, car, etc.)
    by posting the difference in value as a transaction
    """
    diff = value - _get_last_known_value(name, transactions)
    if diff == 0:
        logging.info(f"No difference in value for {name}")
        return
    logging.info(f"Posting difference of {diff} for {name}")
    create_transaction(
        actual.session,
        datetime.date.today(),
        account,
        payee,
        notes=f"[Automated] {name} - LKV: {value}",
        amount=diff,
    )
