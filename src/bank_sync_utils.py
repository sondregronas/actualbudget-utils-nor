import logging

from actual.database import Transactions


def remove_uncleared_from_bank_synced(transactions: list[Transactions]):
    for t in transactions:
        if t.account.bank_id:
            if not t.cleared:
                t.delete()
                logging.info(f"Deleted uncleared transaction: {t=}")
