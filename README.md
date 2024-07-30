# Norwegian Actual Budget utils (WIP)

> NOTE: Work in progress.

Some Norway based utilities for Actual for my personal use.

TODO:

- [ ] Docker image that runs the script periodically, instead of relying on cron
- [ ] Automatically update categories using payee aggregation as well? Or update based on other transactions with the
  same payee?

## What it does (for now)

- **Car Value** - Queries regnr.no to get an estimated median value of a car based on the license plate _via selenium_.
  The difference is posted to the Actual budget as a transaction based on the last known value (LKV). Only updates the
  assets estimated value (You can still add/track debt yourself in the same account).

- **Hjemla** - Queries hjemla.no to get an estimated median value of a house based on the URL _via selenium_. The
  difference is posted to the Actual budget as a transaction based on the last known value (LKV). Only updates the
  assets estimated value (You can still add/track debt yourself in the same account).

- **Payee Aggregation** - Modify `payee_aggregate.yaml` with Payee: regex (or list of regexes) to aggregate/merge
  payees. See the example file for more details. This is useful for when you have multiple payees that should be
  aggregated into one, i.e. "Store Name" and "Store Name - Location" could be aggregated into "Store Name".

## Usage

Some environment variables are required to run the script, see the `.env.example` file for more details.

Run `python main.py --help` to see the available options. Docker image coming soon.

## Modules

### Car Value

Gets the value of a car based on the registration number via `https://regnr.no/[REGISTRATION_NUMBER]`

### Hjemla

Gets the value of a house based on the hjemla URL where the house price is listed ("Se mer" modal).

Example URL: `https://www.hjemla.no/boligkart?search=lat_lon_addresse-1_1234_Postnummer&z=16&showPanel=true&unit=H1234`

### Payee Aggregation

Modify `payee_aggregate.yaml` with Payee: regex (or list of regexes) to aggregate/merge payees. See the example file