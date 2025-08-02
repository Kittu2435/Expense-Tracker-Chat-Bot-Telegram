import datetime
import time
from bot import start_bot

def is_active_hours():
    now = datetime.datetime.now().time()
    start_time = datetime.time(10,0)
    end_time = datetime.time(0,0)
    
    return start_time <= now or now < end_time

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