import psutil
import time
import rumps
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from datetime import datetime

def get_frontmost_app_name():
    window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
    for window in window_list:
        if window.get('kCGWindowLayer', '') == 0:
            return window.get('kCGWindowOwnerName', None)
    return None

def is_app_running_and_focused(app_name):
    frontmost_app = get_frontmost_app_name()
    return frontmost_app and frontmost_app.lower() == app_name.lower()

def log_daily_usage(app_name, total_time):
    today = datetime.today().strftime('%Y-%m-%d')
    log_file = f"{app_name}_daily_usage.log"
    with open(log_file, "a") as f:
        f.write(f"{today}: {total_time:.1f} seconds\n")

class AppMonitor(rumps.App):
    def __init__(self, app_name, *args, **kwargs):
        super(AppMonitor, self).__init__(app_name, *args, **kwargs)
        self.app_name = app_name
        self.total_time = 0
        self.app_active = False
        self.start_time = None
        self.current_day = datetime.today().day
        self.timer = rumps.Timer(self.update, 1)
        self.timer.start()

    def update(self, _):
        if is_app_running_and_focused(self.app_name):
            if not self.app_active:
                self.app_active = True
                self.start_time = time.time()
            else:
                self.total_time += time.time() - self.start_time
                self.start_time = time.time()
        else:
            if self.app_active:
                self.app_active = False
                self.total_time += time.time() - self.start_time

        # Check if it's a new day
        new_day = datetime.today().day
        if self.current_day != new_day:
            log_daily_usage(self.app_name, self.total_time)
            self.current_day = new_day
            self.total_time = 0

        self.title = f"{self.app_name}: {self.total_time:.1f}s"

if __name__ == "__main__":
    app_name = input("Enter the name of the application you want to monitor: ")
    app = AppMonitor(app_name, title="")
    app.run()
