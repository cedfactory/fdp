import multiprocessing
import time

class zed_fdp:
    def __init__(self):
        self.process = None

    def run(self):
        """Starts a new process running the run_candle function."""
        if self.process is None or not self.process.is_alive():
            self.process = multiprocessing.Process(target=self.run_candle)
            self.process.start()
            print("Process started.")
        else:
            print("Process is already running.")

    def run_candle(self):
        """A sample long-running function that could represent your candle task."""
        while True:
            print("Candle running...")
            time.sleep(1)  # simulate ongoing work

    def get_status(self):
        """Returns the status of the process: 'alive', 'dead', or a custom message."""
        if self.process is None:
            return "Not started"
        elif self.process.is_alive():
            return "alive"
        else:
            return "dead"

    def stop(self):
        """Stops the process if it's running."""
        if self.process is not None:
            print("Stopping process...")
            self.process.terminate()
            self.process.join()  # Wait for the process to actually terminate
            print("Process stopped.")
        else:
            print("No process to stop.")

    def restart(self):
        """Restarts the process."""
        print("Restarting process...")
        self.stop()
        self.run()

# Example usage:
if __name__ == '__main__':
    zed = zed_fdp()
    zed.run()                # Start the process
    time.sleep(3)            # Let it run for a bit
    print("Status:", zed.get_status())
    zed.restart()            # Restart the process
    time.sleep(3)            # Let it run again
    print("Status after restart:", zed.get_status())
    zed.stop()               # Finally, stop the process
    print("Final Status:", zed.get_status())
