import logging

from actual.database import Transactions, Payees


def find_pairs(transactions: list[Transactions]) -> list[tuple[Transactions, Transactions]]:
    """Find pairs of transactions that are transfers."""
    pairs = []
    for transaction in transactions:
        for other in transactions:
            # Skip empty transactions, identical transactions, and transactions without payees
            if any([not transaction.amount, not other.amount, transaction.acct == other.acct,
                    not transaction.payee, not other.payee]):
                continue
            # Append if the amount is the same, they are not already paired and they are not transfers
            # TODO: Be more lenient with the date? I.e. processing time for interbank transfers
            if all([transaction.date == other.date, transaction.amount == -other.amount,
                    not transaction.payee.transfer_acct, not other.payee.transfer_acct]):
                pairs.append((transaction, other))
    return pairs


transfer_payee_cache = {}


def get_transfer_payee(from_account_id: str, payees: list[Payees]) -> Payees:
    """Get the transfer payee based on the transfer account ID."""
    if from_account_id in transfer_payee_cache:
        logging.debug(f'Cache hit for {from_account_id}')
        return transfer_payee_cache[from_account_id]
    for payee in payees:
        logging.debug(f'{payee.transfer_acct} == {from_account_id}')
        if payee.transfer_acct == from_account_id:
            logging.debug(f'Found payee: {payee.name} ({payee.account})')
            transfer_payee_cache[from_account_id] = payee
            return payee


def recognize_and_merge_transfers(transactions: list[Transactions], payees: list[Payees]):
    """Recognize transfers and merge them into transfer transactions."""
    pairs = find_pairs(transactions)

    for t1, t2 in pairs:
        logging.info(
            f'Merging transaction into transfer: {t1.account.name} ({t1.amount}) <-> {t2.account.name}')
        logging.debug(f'Transfer pair: {t1.acct} -> {t2.acct}')
        # Update the payee IDs
        t1.payee_id = get_transfer_payee(t2.acct, payees).id
        t2.payee_id = get_transfer_payee(t1.acct, payees).id
