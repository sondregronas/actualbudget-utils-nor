import logging

from actual.database import Transactions
from datetime import datetime

from actual.utils.conversions import date_to_int


def remove_uncleared_from_bank_synced(transactions: list[Transactions]):
    today = date_to_int(datetime.now().date())
    for t in transactions:
        if t.account.bank_id:
            if not t.cleared:
                t.delete()
                logging.info(f"Deleted uncleared transaction: {t=}")
            # If the transaction was made TODAY, it might not have cleared properly yet, so we should also delete it
            elif t.date == today:
                t.delete()
                logging.info(f"Deleted fresh transaction that might not have cleared properly yet: {t=}")