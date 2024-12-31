# Norwegian Actual Budget utils (WIP)

> NOTE: Work in progress.

Some Norway based utilities for Actual for my personal use.

TODO:

- [ ] Docker image that runs the script periodically, instead of relying on cron

## What it does (for now)

- **Car Value** - Queries regnr.no to get an estimated median value of a car based on the license plate _via selenium_.
  The difference is posted to the Actual budget as a transaction based on the last known value (LKV). Only updates the
  assets estimated value (You can still add/track debt yourself in the same account).

- **Hjemla** - Queries hjemla.no to get an estimated median value of a house based on the URL _via selenium_. The
  difference is posted to the Actual budget as a transaction based on the last known value (LKV). Only updates the
  assets estimated value (You can still add/track debt yourself in the same account).

- **Payee Aggregation** - Modify `payee_aggregate.yaml` with Payee: regex (or list of regexes) to aggregate/merge
  payees. See the example file for more details. This is useful for when you have multiple payees that should be
  aggregated into one, i.e. "Store Name" and "Store Name - Location" could be aggregated into "Store Name". Can also
  be used to update the transaction category based on the payee aggregate group (i.e. all transactions under the
  "Grocery Stores" group can be set to the "Groceries" category).

- **Payee Cleanser** - Cleans up the payee names based on the `payee_cleanser.txt` file. (Removes the specified regexes
  from the payee name). Also strips any extra whitespace from the payee names. I.e. `\.\w{2,3}\b` will remove any domain
  names from the payee name, `\bpaypal\b` will remove the word "paypal" from the payee name.

- **Transfer Recognition** - Recognizes transfers between accounts and marks them as transfers in Actual. By default
  bank syncs will create two transactions for each transfer, one in each account. This module will change the payee to
  be a proper transfer.

- **Bank Sync** - Triggers a bank sync for all accounts in Actual. This is useful if you want to automate the bank sync
  process. (Might not work, disabled in --all for now).

- **Remove Uncleared** - Removes uncleared transactions from bank sync accounts.

## Usage

Some environment variables are required to run the script, see the `.env.example` file for more details.

Run `python main.py --help` to see the available options. Docker image coming soon.
Run `python main.py --help` to see the available options. Docker image coming soon.

```shell
Options:
  -v, --debug                 Enable debug logging
  --dry-run, --dry            Dry run
  -a, --all                   Update everything
  -p, --aggregate             Aggregate all payees based on the payee
                              aggregates configuration
  -e, --cleanse-payees        Cleanse payee names based on the payee cleanser
                              configuration
  -t, --transfer-recognition  Recognize & set transactions to transfers
  -c, --car                   Update car values
  -h, --house                 Update house values
  -b, --bank-sync             Run bank sync on all accounts
  -u, --remove-uncleared      Removes all uncleared transactions from bank
                              sync accounts
  --help                      Show this message and exit.
  ```

## Modules

### Car Value

Gets the value of a car based on the registration number via `https://regnr.no/[REGISTRATION_NUMBER]`

### Hjemla

Gets the value of a house based using hjemla.no (City=Address=Zip code).

Address pair example: `By=Addresse 12=1234` (:50 for 50%, comma separated for multiple addresses)

### Payee Aggregation

Modify `payee_aggregate.yaml` with Payee: regex (or list of regexes) to aggregate/merge payees. See the example file

## Payee Cleanser

Cleans up the payee names based on the `payee_cleanser.txt` file. (Removes the specified regexes from the payee name).

> **NOTE**: This DELETES the matched regexes from the payee name - while the Payee Aggregation module replaces the payee
> name with the aggregated name. Be careful with the regexes you use.

## Transfer Recognition

Recognizes transfers between accounts and marks them as transfers in Actual. (Matching date, amount, and payee).