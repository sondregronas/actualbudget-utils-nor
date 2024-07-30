import logging
import os
from functools import partial

import click
from actual import Actual
from actual.queries import get_transactions
from dotenv import load_dotenv

from assets import update_asset_value
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


@click.command()
@click.option('--debug', '-v', help='Enable debug logging', is_flag=True)
@click.option('--dry-run', '--dry', help='Dry run', is_flag=True)
@click.option('--all', '-a', help='Update everything', is_flag=True)
@click.option('--aggregate', '-p', help='Aggregate all payees based on the payee aggregates configuration',
              is_flag=True)
@click.option('--car', '-c', help='Update car values', is_flag=True)
@click.option('--house', '-h', help='Update house values', is_flag=True)
@click.option('--bank-sync', '-b', help='Run bank sync on all accounts', is_flag=True)
def main(debug, dry_run, all, aggregate, car, house, bank_sync):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('Debug logging enabled')

    if dry_run:
        logging.info('Dry run enabled - no changes will be committed')

    license_plates = os.getenv('LICENSE_PLATES', '').split(',')
    houses = os.getenv('HJEMLA_URLS', '').split(',')

    car_values, house_values = {}, {}

    if all:
        aggregate = True
        car = True
        house = True
        bank_sync = True

    logger.info(f'Starting with the following options:')
    logger.info('-' * 40)
    logger.info(f'Dry run: {dry_run}')
    logger.info(f'Houses: {house}')
    logger.info(f'Car: {car}')
    logger.info(f'Payee aggregation: {aggregate}')
    logger.info(f'Bank sync: {bank_sync}')
    logger.info('-' * 40)

    if license_plates != [''] and license_plates and car:
        car_values = get_car_median_estimates(license_plates)
    if houses != [''] and houses and house:
        house_values = get_house_median_estimates(houses)

    with Actual(base_url=ACTUAL_URL, password=ACTUAL_PWD, encryption_password=ACTUAL_ENCRYPTION_PASSWORD,
                file=ACTUAL_FILE) as actual:

        transactions = get_transactions(actual.session)
        logger.info(f'Found {len(transactions)} transactions')

        new_transactions = []
        if bank_sync:
            new_transactions = actual.run_bank_sync()
            logger.info(f'Imported {len(new_transactions)} new transactions from bank sync')

        all_transactions = list(transactions) + list(new_transactions)

        # Partial function to update assets
        update_asset = partial(update_asset_value,
                               account=ACTUAL_CAR_ACCOUNT,
                               payee=ACTUAL_PAYEE,
                               actual=actual,
                               transactions=all_transactions)

        if car:
            [update_asset(car, value) for car, value in car_values.items()]
        if house:
            [update_asset(house, value) for house, value in house_values.items()]
        if aggregate:
            aggregate_all_payees(actual, all_transactions)

        # Run rules
        actual.run_rules()
        if dry_run:
            logging.info('Dry run concluded - no changes were committed')
            return
        actual.commit()
        logging.info('Completed successfully')


if __name__ == '__main__':
    main()
