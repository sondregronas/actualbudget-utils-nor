import time
import os
import schedule

from main import main

AUTO_RUN = os.getenv("AUTO_RUN", "1").lower() in ("1", "true", "yes", "y")

schedule.every().hour.do(main, ["-petu"])
schedule.every(4).hours.do(main, ["-petub"])
schedule.every().sunday.at("00:00").do(main, ["-c"])
schedule.every().sunday.at("00:00").do(main, ["-h"])

while True:
    if AUTO_RUN:
        schedule.run_pending()
    time.sleep(1)
