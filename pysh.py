lazy import os
lazy import re
lazy import shlex
lazy import subprocess
lazy import sys
lazy import time
lazy import tomllib
lazy from pathlib import Path

lazy from termcolor import colored

platform = os.name
system = sys.platform
config_path = Path.home() / ".pysh.toml"
config_py_path = Path.home() / ".pyshrc"


if not config_path.exists():
	print("Hello new user!")
	if system == "linux":
		linux_pack = input("What package manager is compatible with your distro? Type here: ")

	watprompt_color = input("What color do you want your prompt to be? (red, green, yellow, blue, magenta, cyan, white): ")
	use_uv = input("Do you use uv? (y/N): ")
	if use_uv.lower() == "y":
		use_uv = True
		use_uv_publish = input("Do you use uv-publish? (y/N): ")
		use_uv_publish = use_uv_publish.lower() == "y"
	else:
		use_uv = False
		use_uv_publish = False
	autocdyes = input("Do you want to enable AUTOCD? (y/N): ")
	autocdyes = autocdyes.lower() == "y"
	whichentrymessage = input("Do you want to enable the entry message? (on/off/legacy): ")
	whichentrymessage = whichentrymessage.lower()

	config_path.parent.mkdir(parents=True, exist_ok=True)

	if system == "win32":
		config_path.write_text(
			f"""package_manager = "winget"
User = "root"
prompt_color = "{watprompt_color}"
use_uv = {str(use_uv).lower()}
use_uv-publish = {str(use_uv_publish).lower()}
AUTOCD = {str(autocdyes).lower()}
entry_message = "{whichentrymessage}"
[danger_zone]
dont_start = false
dont_read_pyshrc = false
"""
		)

	elif system == "linux":
		config_path.write_text(
			f"""package_manager = "{linux_pack}"
User = "root"
prompt_color = "{watprompt_color}"
use_uv = {str(use_uv).lower()}
use_uv-publish = {str(use_uv_publish).lower()}
AUTOCD = {str(autocdyes).lower()}
entry_message = "{whichentrymessage}"
[danger_zone]
dont_start = false
dont_read_pyshrc = false
"""
		)
	elif system == "darwin":
		config_path.write_text(
			f"""package_manager = "brew"
User = "root"
prompt_color = "{watprompt_color}"
use_uv = {str(use_uv).lower()}
use_uv-publish = {str(use_uv_publish).lower()}
AUTOCD = {str(autocdyes).lower()}
entry_message = "{whichentrymessage}"
[danger_zone]
dont_start = false
dont_read_pyshrc = false
"""
		)

if not config_py_path.exists():
	print("Generating .pyshrc")

	config_py_path.parent.mkdir(parents=True, exist_ok=True)

	config_py_path.write_text("# Put code here, to run once before the main code.")

with config_path.open("rb") as f:
	config = tomllib.load(f)


variables = {"USERPROFILE": Path.home(), "USER": config["User"], "SHELL": sys.executable, "HOME": Path.home()}


def expand_vars(text):
	for name, value in variables.items():
		text = text.replace(f"${name}", str(value))
	return text


if config["danger_zone"]["dont_start"]:
	sys.exit()


def main(argv="noargs"):
	change = False
	while True:
		try:
			if not change:
				temp = colored(f"PT -> {Path.cwd()}> ", config["prompt_color"])
			prompter = temp

			cmd = argv if argv != "noargs" else input(prompter).strip()
			commands = argv if isinstance(cmd, list) else [c.strip() for c in re.split(r"&&|;|&", cmd) if c.strip()]
			has_and = "&&" in commands
			success = True
			for command in commands:
				if command == "exit":
					print("Goodbye!")
					sys.exit()
				elif command == "coolguy38 is sigma":
					print("Yes, im sigma B)")
				elif command == "cd" or command == "pwd":
					print(Path.cwd())

				elif command.startswith("cd "):
					path = command[3:].strip().strip("'\"")

					try:
						os.chdir(expand_vars(path))

					except Exception as e:
						print(colored(f"Pysh: cd Error: {e}", "red"))
						success = False

				elif command.startswith("prompt "):
					temp = command[7:] + " "
					change = True
				elif command.lower() == "reset prompt" or command.lower() == "prompt":
					change = False

				elif command.lower() == "help":
					print(
						"""- help: explains every command
- coolguy38 is sigma: responds
- reset prompt: Resets the prompt
- prompt: Also resets the prompt
- pwd: Prints the current working directory
- pyexe <text>: Runs pyinstaller --onefile for you. If it reaches an error it asks you if you want to download pyinstaller
- pypub <text>: Builds and publishes your library to pypi. If it reaches an error it asks you if you want to download twine and build
- pack get: use this like the package manager you chose. (like pack get install Git.git if using winget)
- os: prints your os
- view <path>: Its basically cat but with syntax highlighting
- prompt <text>: Changes the prompt to <text>
- echo <text>: Prints <text>
- ls/dir: Lists the current directory
- ls <path>/dir <path>: Lists the directory at <path>
- md/mkdir <dir>: Makes a directory called <dir>
- time: Prints the current time
- cls/clear: Clears the terminal
- cd <path>: Changes the current directory to <path>
- cat <file>: Prints the contents of <file>
- <file>.pysh: Runs the .pysh file"""
					)

				elif command.startswith("pyexe "):
					pyn = command[6:].strip()
					pynn = subprocess.run(f"pyinstaller {pyn}", shell=True, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
					if pynn.returncode != 0:
						down = input("Oh no! Pyinstaller failed. Download? (y/N)")
						match down.lower():
							case "y":
								subprocess.run("pip install pyinstaller", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=True)
							case "n":
								print("Ok")
						success = False
				elif command.startswith("pypub "):
					if config["use_uv"]:
						pyb = command[6:].strip()
						if config["use_uv-publish"]:
							pybb = subprocess.run(
								f"uv build && uv-publish && uv pip install --upgrade --system {pyb}",
								stdin=sys.stdin,
								stdout=sys.stdout,
								stderr=sys.stderr,
								shell=True,
							)
						else:
							pybb = subprocess.run(
								f"uv build && uv publish && uv pip install --upgrade --system {pyb}",
								stdin=sys.stdin,
								stdout=sys.stdout,
								stderr=sys.stderr,
								shell=True,
							)
					else:
						pyb = command[6:].strip()
						pybb = subprocess.run(
							f"python -m build && python -m twine check dist/* && python -m twine upload dist/* && pip install --upgrade {pyb}",
							stdin=sys.stdin,
							stdout=sys.stdout,
							stderr=sys.stderr,
							shell=True,
						)
					if pybb.returncode != 0:
						if config["use_uv"]:
							downl = input("Oh no! Something failed! Download uv and uv-publish? (y/N)")
							match downl.lower():
								case "y":
									subprocess.run(
										"pipx install uv && uv tool install uv-publish",
										stdin=sys.stdin,
										stdout=sys.stdout,
										stderr=sys.stderr,
										shell=True,
									)
								case "n":
									print("Ok")

						else:
							downl = input("Oh no! Something failed! Download build and twine? (y/N)")
							match downl.lower():
								case "y":
									subprocess.run("pipx install build twine", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=True)
								case "n":
									print("Ok")
						success = False
				elif command.startswith("pack_get "):
					getd = command[9:].strip()
					subprocess.run(f"{config['package_manager']} {getd}", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=True)
				elif command == "whoami":
					print(f"You are {config['User']}")

				elif command.endswith(")"):
					try:
						exec(command)
					except NameError:
						print(colored(f"Pysh: Error: Python command {command} doesnt exist", "red"))
					success = False
				elif command == "os":
					print(system)

				elif command.startswith("view "):
					viewed = command[5:].strip()

					viewer = subprocess.run(
						f"pygmentize {expand_vars(viewed)}", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=True, text=True
					)
					if viewer.returncode != 0:
						print(colored("Pysh: view Error: Failed to view file", "red"))
						success = False
				elif command.startswith("cat "):
					file = command[4:].strip()

					try:
						print(expand_vars(Path(file).read_text()))
					except FileNotFoundError:
						print(colored(f"Pysh: cat Error: File {file} not found", "red"))
						success = False
				elif command.startswith("echo "):
					echoed = command[5:].strip()
					print(expand_vars(echoed))
				elif command in ["ls", "dir"]:
					path = "."
					try:
						for entry in os.listdir(path):
							print(entry)
					except FileNotFoundError:
						print(colored(f"Pysh: {command} Error: Directory {path} not found", "red"))
						success = False
					except PermissionError:
						print(
							colored(
								f"Pysh: {command} Error: Permission denied to access {path}. Make sure you have permissions to view this directory.",
								"red",
							)
						)
						success = False
				elif command.lower().startswith("ls "):
					pather = command[3:].strip()
					path = expand_vars(pather.strip("'\""))
					try:
						for entry in os.listdir(path):
							print(entry)
					except FileNotFoundError:
						print(colored(f"Pysh: ls Error: Directory {path} not found", "red"))
						success = False
					except PermissionError:
						print(
							colored(
								f"Pysh: ls Error: Permission denied to access {path}. Make sure you have permissions to view this directory.", "red"
							)
						)
						success = False

				elif command.endswith(".pysh") or command.endswith(".py") and not command.startswith("python"):
					try:
						exec(Path(command).read_text())
					except FileNotFoundError:
						print(colored(f"Pysh: Error: File {command} not found", "red"))
						success = False

				elif command.startswith("md "):
					makedir = command[3:].strip().strip("'\"")
					try:
						Path(makedir).mkdir(exist_ok=True, parents=True)
					except PermissionError:
						print(colored(f"Pysh: md Error: You can't make a directory in {Path.cwd()}", "red"))
						success = False
				elif command.startswith("mkdir "):
					makedir = command[6:].strip().strip("'\"")
					try:
						Path(makedir).mkdir(exist_ok=True, parents=True)
					except PermissionError:
						print(colored(f"Pysh: mkdir Error: You can't make a directory in {Path.cwd()}", "red"))
						success = False
				elif command == "time":
					print(time.strftime("%I:%M %p"))
				elif command in ["cls", "clear"]:
					subprocess.run("cls" if platform == "nt" else "clear", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=True)

				else:
					if config["AUTOCD"]:
						try:
							os.chdir(expand_vars(command))
						except Exception:
							args = shlex.split(command)
							subprocess.run(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
					else:
						args = shlex.split(command)
						subprocess.run(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
				if not success and has_and:
					break
				argv = "noargs"

		except KeyboardInterrupt:
			print("^C")
			continue
		except EOFError:
			print("^D")
			print("Goodbye!")
			sys.exit()
		except Exception as e:
			print(colored(f"Pysh: Error: {e}", "red"))


if len(sys.argv) > 1:
	if sys.argv[1] == "-c":
		if config["entry_message"] == "legacy":
			print(colored(f"Welcome to the python terminal, {config['User']}!", config["prompt_color"]))
		elif config["entry_message"] == "on":
			print(colored(f"Welcome to Pysh, {config['User']}!", config["prompt_color"]))
		if not config["danger_zone"]["dont_read_pyshrc"]:
			try:
				exec(config_py_path.read_text())
			except Exception as e:
				print(colored(f"Pysh: Error: Error when executing pyshrc: {e}", "red"))
		tempargs = sys.argv[2:]
		main(tempargs)

	elif sys.argv[1] == "-h":
		main(["help"])
	else:
		if sys.argv[1].startswith("-"):
			print(f"Pysh: Error: Unknown arg {sys.argv[1]}.")
		else:
			try:
				exec(Path(sys.argv[1]).read_text())
			except Exception as e:
				print(colored(f"Pysh: Error: Error while executing file {sys.argv[1]}: {e}", "red"))


else:
	if config["entry_message"] == "legacy":
		print(colored(f"Welcome to the python terminal, {config['User']}!", config["prompt_color"]))
	elif config["entry_message"] == "on":
		print(colored(f"Welcome to Pysh, {config['User']}!", config["prompt_color"]))
	if not config["danger_zone"]["dont_read_pyshrc"]:
		try:
			exec(config_py_path.read_text())
		except Exception as e:
			print(colored(f"Pysh: Error: Error when executing pyshrc: {e}", "red"))
	main()
