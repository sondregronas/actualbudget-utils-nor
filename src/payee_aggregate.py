import re
from logging import getLogger
from pathlib import Path

import yaml
from actual.queries import get_or_create_payee, get_payee, get_or_create_category

logging = getLogger()


def add_regex_boundaries(entry: str):
    """Add regex word boundaries to the entry if they are not already there"""
    entry = f'\\b{entry}' if not entry.startswith('\\b') else entry
    entry = f'{entry}\\b' if not entry.endswith('\\b') else entry
    return entry


def parse_payee_aggregate() -> dict:
    """Read the payee aggregate configuration from a YAML file and return it as a dictionary

    Returns: {'payee': {'regex': 'regex', 'category': 'category | None'}}
    """
    DIR = 'payee_aggregates'
    EXTRA_DIR = f'aggregate_groups'
    with open(Path(f'{DIR}/payee_aggregate.yaml'), 'r', encoding='utf8') as f:
        # Convert lists to (|)-separated, if it is a list, otherwise return the value as is
        payee_aggregates = dict()
        values = yaml.safe_load(f).values()

        for value in values:
            c = value.get('category', None)
            # Load external file if it is defined for the payee aggregate group
            f = value.get('file', None)
            if f:
                f = f'{DIR}/{EXTRA_DIR}/{f.strip()}{".yaml" if not f.endswith(".yaml") else ""}'
                value.update(yaml.safe_load(open(Path(f), 'r', encoding='utf8')))
            for k, v in value.items():
                if k in ['category', 'file']:
                    continue
                if isinstance(v, list):
                    entries = [add_regex_boundaries(str(entry)) for entry in v]
                    regex = f"({'|'.join(entries)})"
                else:
                    regex = add_regex_boundaries(str(v))
                payee_aggregates[k] = {'regex': regex, 'category': c}
        return payee_aggregates


def _aggregate(transaction, payee_aggregates):
    """Aggregate the payee of a transaction based on the payee aggregates configuration"""
    for payee, aggregate in payee_aggregates.items():
        if not transaction.payee:
            return transaction.payee, False
        # Note: this can be pretty taxing..
        if re.search(aggregate['regex'], transaction.payee.name, re.IGNORECASE):
            return payee, True
    return transaction.payee, False


def aggregate_all_payees(actual, transactions, update_category=True):
    """Aggregate all payees based on the payee aggregates configuration"""
    # TODO: Split this function into smaller functions for better readability
    payee_aggregates = parse_payee_aggregate()
    logging.debug(f'Payee aggregates: {payee_aggregates}')
    merged_payees = dict()
    for transaction in transactions:
        # Find payee aggregate for the transaction
        new_payee, to_be_aggregated = _aggregate(transaction, payee_aggregates)

        # Skip if the payee is not to be aggregated
        if not to_be_aggregated:
            continue

        # Get the new category for the payee, if it is defined in the payee aggregates configuration
        new_category = payee_aggregates[new_payee].get('category', None)
        if new_category:
            new_category = get_or_create_category(actual.session, new_category)

        # Check if the payee or category should be updated
        should_change_payee = transaction.payee.name != new_payee and transaction.payee.name not in payee_aggregates.keys()
        should_update_category = all([update_category, not transaction.category, new_category])

        # Skip if there is nothing to update
        if not any([should_change_payee, should_update_category]):
            continue

        # Construct the new payee (if it doesn't already exist)
        p = get_or_create_payee(actual.session, new_payee)

        # Copy the category and tombstone from the original payee (TODO: Unnecessary?)
        if not p.category:
            p.category = transaction.payee.category
        if not p.tombstone:
            p.tombstone = transaction.payee.tombstone

        # Keep track of which payees are merged to which new payee, so we can merge them later
        if should_change_payee and new_payee not in merged_payees:
            merged_payees[new_payee] = list()
        if should_change_payee and transaction.payee.id not in merged_payees[new_payee]:
            logging.info(f'Aggregated payee: {transaction.payee.name} -> {new_payee}')
            merged_payees[new_payee].append((transaction.payee.id, transaction.payee.name))

        # Update the transaction to use the new payee
        transaction.payee_id = p.id

        # Update the category of the payee (if it doesn't already have a category)
        if update_category and not transaction.category and new_category:
            logging.info(f'Updated empty category for payee transaction ({new_payee}): None -> {new_category.name}')
            transaction.category_id = new_category.id

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


if __name__ == '__main__':
    print(parse_payee_aggregate())
