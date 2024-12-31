import time

import schedule

from main import main

schedule.every().hour.do(main, ["-petu"])
schedule.every(4).hours.do(main, ["-petub"])
schedule.every().sunday.at("00:00").do(main, ["-c"])
schedule.every().sunday.at("00:00").do(main, ["-h"])

while True:
    schedule.run_pending()
    time.sleep(1)
