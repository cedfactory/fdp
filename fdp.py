import os, sys, platform, subprocess, psutil

g_os_platform = platform.system()
g_python_executable = ""

def get_python_processes():
	current_pid = os.getpid()
	processes = []
	for process in psutil.process_iter(['pid', 'name', 'cmdline']):
		if not 'name' in process.info:
			continue
		try:
			if 'python' in process.info['name']:
				if int(process.info['pid']) != current_pid:
					processes.append({"pid": process.info['pid'],
								"command": ' '.join(process.info['cmdline'])})
		except (psutil.NoSuchProcess, psutil.AccessDenied):
			# Skip processes that may have terminated or where access is restricted
			continue

	return processes


def fdp_start():
	log_file = "fdp.log"
	if g_os_platform == "Windows":
		command = "start /B python fdp_main.py > {}".format(log_file)
		print("command : ", command)
		os.system(command)
	elif g_os_platform == "Linux":
		command = "nohup python fdp_main.py > {} &".format(log_file)
		print("command : ", command)
		subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

def fdp_stop():
	all_processes = get_python_processes()

	# keep only alcorak processes
	processes = [process for process in all_processes if 'fdp_main' in process['command']]

	if len(processes) >= 1:
		p = psutil.Process(processes[0]["pid"])
		p.terminate()
		p.wait()
		print(f"Process terminated.")
	else:
		print(f"No process found.")


if __name__ == "__main__":
	print("# Platform :", g_os_platform)
	g_python_executable = sys.executable
	print("# Python executable :", g_python_executable)
	print("\n")

	print('''Available actions :
	- 'start' to start a strategy
	- 'stop' to stop a running strategy
	- 'quit' to quit''')
	action = input("> ").strip().lower()
	print("\n")

	if action == "start":
		fdp_start()

	elif action == "stop":
		fdp_stop()

	elif action == "quit":
		pass
