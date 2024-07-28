# Norwegian Actual Budget utils (WIP)

> NOTE: Work in progress.

Some Norway based utilities for Actual for my personal use.

TODO:

- [ ] Docker image that runs the script periodically, instead of relying on cron

## What it does (for now)

- **Car Value** - Queries regnr.no to get an estimated median value of a car based on the license plate _via selenium_
  The difference is posted to the Actual budget as a transaction based on the last known value (LKV). Only updates the
  assets estimated value (You can still add/track debt yourself in the same account).

- **Hjemla** - Queries hjemla.no to get an estimated median value of a house based on the URL _via selenium_. The
  difference is posted to the Actual budget as a transaction based on the last known value (LKV). Only updates the
  assets estimated value (You can still add/track debt yourself in the same account).

## Usage

Simply run the script periodically to update the values in your Actual budget. There's no reason to run it more than
once per week or even per month, as the values are not likely to change that often.

Environment variables are used to specify the license plates and hjemla URLs to use. See the `.env.example` file for
details.

## Modules

### Car Value

Gets the value of a car based on the registration number via `https://regnr.no/[REGISTRATION_NUMBER]`

### Hjemla

Gets the value of a house based on the hjemla URL where the house price is listed ("Se mer" modal).

Example URL: `https://www.hjemla.no/boligkart?search=lat_lon_addresse-1_1234_Postnummer&z=16&showPanel=true&unit=H1234`