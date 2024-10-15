import time

import schedule

from main import main

schedule.every().hour.do(main, ["-petu"])
schedule.every(4).hours.do(main, ["-petub"])
schedule.every().sunday.at("00:05").do(main, ["-ch"])

while True:
    schedule.run_pending()
    time.sleep(1)
