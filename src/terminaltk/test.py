"""
from threading import Thread
from time import sleep

def f() -> None:
    while True:
        sleep(0.4)
        print("Thread is running.")

thread = Thread(target=f, daemon=True)
thread.start()

try:
    sleep(10)
    # thread.join()
except KeyboardInterrupt:
    print("Caught KeyboardInterrupt")

sleep(0.8)
print(f"thread._is_stopped = {thread._is_stopped}")
print(f"thread.is_alive() = {thread.is_alive()}")
sleep(0.8)
"""

import tkinter as tk

root = tk.Tk()
root.geometry("100x100")

widget = tk.Label(root, bg="red", width=10)
frame = tk.Frame(root, bg="blue", width=90, height=30)
frame.grid_propagate(False)
frame.grid(row=1, column=1)

widget.grid(row=1, column=1, in_=frame, sticky="news")
frame.grid_columnconfigure(1, weight=1)

# Note that at this point the frame is on top of the widget.
# So we need to call:
widget.lift()
