import time
import multiprocessing

from clockmanager import ClockManager

clock = ClockManager()

clock_ticker = multiprocessing.Process(target=clock.tick)
clock_ticker.start()

time.sleep(5)
print("blyat")
