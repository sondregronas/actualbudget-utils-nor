import re
from logging import getLogger

import yaml
from actual.queries import get_or_create_payee, get_payee

logging = getLogger()


def add_regex_boundaries(entry: str):
    """Add regex word boundaries to the entry if they are not already there"""
    entry = f'\\b{entry}' if not entry.startswith('\\b') else entry
    entry = f'{entry}\\b' if not entry.endswith('\\b') else entry
    return entry


def read_payee_aggregate() -> dict[str, str]:
    """Read the payee aggregate configuration from a YAML file and return it as a dictionary"""
    with open('payee_aggregate.yaml', 'r', encoding='utf8') as f:
        # Convert lists to (|)-separated, if it is a list, otherwise return the value as is
        payee_aggregates = {}
        for k, v in yaml.safe_load(f).items():
            if isinstance(v, list):
                entries = [add_regex_boundaries(str(entry)) for entry in v]
                payee_aggregates[k] = f"({'|'.join(entries)})"
                continue
            payee_aggregates[k] = add_regex_boundaries(str(v))
        return payee_aggregates


def _aggregate(transaction, payee_aggregates):
    """Aggregate the payee of a transaction based on the payee aggregates configuration"""
    for payee, regex in payee_aggregates.items():
        if not transaction.payee:
            return transaction.payee, False
        if re.search(regex, transaction.payee.name, re.IGNORECASE):
            return payee, True
    return transaction.payee, False


def aggregate_all_payees(actual, transactions):
    """Aggregate all payees based on the payee aggregates configuration"""
    payee_aggregates = read_payee_aggregate()
    logging.debug(f'Payee aggregates: {payee_aggregates}')
    merged_payees = {}
    for transaction in transactions:
        # Find payee aggregate for the transaction
        new_payee, to_be_aggregated = _aggregate(transaction, payee_aggregates)
        if not to_be_aggregated or transaction.payee.name == new_payee:
            continue
        logging.info(f'Aggregated payee: {transaction.payee.name} -> {new_payee}')

        # Construct the new payee (if it doesn't already exist)
        p = get_or_create_payee(actual.session, new_payee)
        if not p.category:
            p.category = transaction.payee.category
        if not p.tombstone:
            p.tombstone = transaction.payee.tombstone

        # Keep track of which payees are merged to which new payee, so we can merge them later
        if new_payee not in merged_payees:
            merged_payees[new_payee] = []
        if transaction.payee.id not in merged_payees[new_payee]:
            merged_payees[new_payee].append((transaction.payee.id, transaction.payee.name))

        # Update the transaction to use the new payee
        transaction.payee_id = p.id

    # Merge the payees (delete the old ones)
    aggregation_count = 0
    for _, payees in merged_payees.items():
        for id, name in payees:
            p = get_payee(actual.session, name)
            if not p:
                continue
            p.delete()
            aggregation_count += 1
            logging.info(f'Merged payee: ({name})')
            logging.debug(f'Payee ID: ({id})')

    # Fin
    if merged_payees:
        logging.info(f'Aggregated {aggregation_count} payees')
        logging.debug(f'Aggregated payees: {merged_payees}')
    else:
        logging.info('No payees to aggregate')
