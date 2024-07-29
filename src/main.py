import datetime
import logging
import os
import re

import click
from actual import Actual
from actual.queries import get_transactions, create_transaction
from dotenv import load_dotenv

from carvalue import get_car_median_estimates
from hjemla import get_house_median_estimates
from payee_aggregate import aggregate_all_payees

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

ACTUAL_URL = os.getenv('ACTUAL_URL')
ACTUAL_PWD = os.getenv('ACTUAL_PWD')
ACTUAL_ENCRYPTION_PASSWORD = os.getenv('ACTUAL_ENCRYPTION_PASSWORD') or None
ACTUAL_FILE = os.getenv('ACTUAL_FILE')
ACTUAL_PAYEE = os.getenv('ACTUAL_PAYEE') or 'Autogenerated'
ACTUAL_CAR_ACCOUNT = os.getenv('ACTUAL_CAR_ACCOUNT', None)
ACTUAL_MORTGAGE_ACCOUNT = os.getenv('ACTUAL_MORTGAGE_ACCOUNT', None)


def _get_generated_transactions(account, actual):
    """A small hack to make sure we only get the transactions we've generated"""
    transactions = get_transactions(actual.session, account=account)
    return [t for t in transactions if t.notes and '[Automated]' in t.notes and 'LKV' in t.notes]


def _get_last_known_value(name, account, actual):
    """Get the last known value of an entity with the given name in the given account"""
    transactions = _get_generated_transactions(account, actual)
    for t in transactions:
        if name in t.notes:
            return int(re.search(r'LKV: (\d+)', t.notes).group(1))
    return 0


def update_values(name, value, account, actual):
    """Post the difference between the last known value and the current value to the given account"""
    diff = value - _get_last_known_value(name, account, actual)
    if diff == 0:
        logging.info(f'No difference in value for {name}')
        return
    logging.info(f'Posting difference of {diff} for {name}')
    create_transaction(
        actual.session,
        datetime.date.today(),
        account,
        ACTUAL_PAYEE,
        notes=f'[Automated] {name} - LKV: {value}',
        amount=diff,
    )
    actual.commit()


@click.command()
@click.option('--all', help='Update everything', is_flag=True)
@click.option('--aggregate', help='Aggregate all payees based on the payee aggregates configuration', is_flag=True)
@click.option('--car', help='Update car values', is_flag=True)
@click.option('--house', help='Update house values', is_flag=True)
def main(all, aggregate, car, house):
    license_plates = os.getenv('LICENSE_PLATES', '').split(',')
    houses = os.getenv('HJEMLA_URLS', '').split(',')

    car_values, house_values = {}, {}

    if all:
        aggregate = True
        car = True
        house = True

    logger.info(f'Houses: {house}')
    logger.info(f'Car: {car}')
    logger.info(f'Payee aggregation: {aggregate}')

    if license_plates != [''] and license_plates and car:
        car_values = get_car_median_estimates(license_plates)
    if houses != [''] and houses and house:
        house_values = get_house_median_estimates(houses)

    with Actual(base_url=ACTUAL_URL, password=ACTUAL_PWD, encryption_password=ACTUAL_ENCRYPTION_PASSWORD,
                file=ACTUAL_FILE) as actual:
        if all:
            aggregate = True
            car = True
            house = True

        if car:
            for license_plate, value in car_values.items():
                update_values(license_plate, value, ACTUAL_CAR_ACCOUNT, actual)
        if house:
            for house, value in house_values.items():
                update_values(house, value, ACTUAL_MORTGAGE_ACCOUNT, actual)
        if aggregate:
            aggregate_all_payees(actual)


if __name__ == '__main__':
    main()
