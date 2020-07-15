from apscheduler.schedulers.blocking import BlockingScheduler
import requests

sched = BlockingScheduler()


# @sched.scheduled_job('interval', seconds=10)
# def timed_job():
#    print('This job is run every three minutes.')

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#    print('This job is run every weekday at 5pm.')


@sched.scheduled_job('interval', minutes=20)
def wakeup_job():
    url = "https://line-bot-python-kent.herokuapp.com"
    r = requests.get(url)
    print('call ---> ' + url + ', httpCode=' + str(r.status_code))


@sched.scheduled_job('cron', day_of_week='mon-fri', hour=19)
def scheduled_job():
    print('This job is run every weekday at 7pm.')
    url = "https://line-bot-python-kent.herokuapp.com/sendMsg"
    r = requests.get(url)
    print('call ---> ' + url + ', httpCode=' + str(r.status_code))

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def kent_job():
    print('This job is run every weekday at 5pm.')
    url = "https://line-bot-python-kent.herokuapp.com/jobs"
    r = requests.get(url)
    print('call ---> ' + url + ', httpCode=' + str(r.status_code))


sched.start()
