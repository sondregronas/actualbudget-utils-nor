"""
Replaces any matching regex in payee_cleanser.txt and strips the payee name.

I.e. strips Paypal* | Klarna* from the payee name.

Not to be confused with payee_aggregate.py that aggregates payees based on regex.
"""
import logging
import re

from actual.queries import get_payees, get_or_create_payee


def load_payee_cleanser():
    with open('payee_cleanser.txt', 'r', encoding='utf8') as f:
        lines = f.read().splitlines()
        # Return the line if it is not empty and does not start with a comment
        return [line for line in lines
                if line.strip() and not line.strip().startswith('#')]


def payee_cleanser(actual):
    """Cleanses the payee name based on the payee_cleans"""
    to_delete = list()
    payee_cleansers = load_payee_cleanser()
    for payee in get_payees(actual.session):
        # Cleanse the payee name
        n = payee.name
        for regex in payee_cleansers:
            # print(regex)
            n = re.sub(regex, '', n, flags=re.IGNORECASE)
            n = re.sub(r'\s+', ' ', n).strip()
        if n == payee.name:
            continue

        # Get or create the new payee
        new_payee = get_or_create_payee(actual.session, n)

        # Keep track of transactions that are not associated with the new payee
        t_ids = set()
        for t in payee.transactions:
            t_ids.add(t.id)
            # Update the payee_id of the transaction
            t.payee_id = new_payee.id
        if payee.id not in t_ids and payee not in to_delete:
            to_delete.append(payee)
        logging.info(f'Payee {payee.name} has been cleansed to {n}')

    # Delete empty payees
    for payee in to_delete:
        logging.info(f'Deleting payee {payee.name} as it has no transactions')
        payee.delete()
