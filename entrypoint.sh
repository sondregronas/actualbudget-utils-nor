# Run everything but car/house/bank sync every hour
echo "0 * * * * /usr/local/bin/python /app/main.py -petu" > /etc/cron.d/entrypoint
# Same as above + Bank sync every 4 hours on weekdays (might not work as expected) - 5 min later
echo "5 */4 * * 1-5 /usr/local/bin/python /app/main.py -petub" >> /etc/cron.d/entrypoint
# House and car sync every sunday
echo "5 0 * * 0 /usr/local/bin/python /app/main.py -ch" >> /etc/cron.d/entrypoint

# Apply cron job
crontab /etc/cron.d/entrypoint
echo "Cron job has been set"
cron -f