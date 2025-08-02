import datetime
import time
from bot import start_bot

def is_active_hours():
    now_utc = datetime.datetime.now().time()
    start_time = datetime.time(19,30)
    end_time = datetime.time(4,0)
    print("now_utc , start time, end time ", now_utc, start_time, end_time)
    
    if start_time <= now_utc or now_utc <= end_time:
        return False
    return True

if __name__ == "__main__":
    while True:
        if is_active_hours():
            print("Active hours - running bot.")
            try:
             start_bot()
            except Exception as e:
                print("Error: ",e)
                time.sleep(60)
                
        else:
            print("Outside active hours, Sleeping....")
            time.sleep(600)