# import subprocess
# import sys
#
#
# def run_command(command):
#     try:
#         """Helper function to run a shell command and check for errors."""
#         result = subprocess.run(command, shell=True, text=True, capture_output=True)
#         if result.returncode != 0:
#             # print(f"Error: {result.stderr}", file=sys.stderr)
#             sys.exit(result.returncode)
#         print(result.stdout)
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#
#
# def main():
#     try:
#         # Create a Python 3.8 virtual environment
#         print("Creating Python 3.8 virtual environment...")
#         run_command("python3.8 -m venv venv3.8")
#
#         # Activate the virtual environment and install dependencies
#         print("Activating virtual environment and installing dependencies...")
#         run_command("source venv3.8/bin/activate && pip install -r requirements.txt")
#
#         # Run Django migrations
#         print("Running Django migrations...")
#         run_command("python manage.py migrate")
#
#         # Start the Django development server
#         print("Starting Django development server...")
#         run_command("python manage.py runserver")
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#
#
# if __name__ == "__main__":
#     main()
import subprocess
import sys


def run_command(command):
    """Helper function to run a shell command and check for errors."""
    result = subprocess.call(command, shell=True)
    if result != 0:
        print(f"Error: Command failed with return code {result}", file=sys.stderr)
        sys.exit(result)


def main():
    # Create a Python 3.8 virtual environment
    print("Creating Python 3.8 virtual environment...")
    run_command("python3.8 -m venv venv3.8")

    # Activate the virtual environment and install dependencies
    print("Activating virtual environment and installing dependencies...")
    run_command("venv3.8/bin/pip install -r requirements.txt")

    # Run Django migrations
    print("Running Django migrations...")
    run_command("venv3.8/bin/python manage.py migrate")

    # Start the Django development server
    print("Starting Django development server...")
    run_command("venv3.8/bin/python manage.py runserver")


if __name__ == "__main__":
    main()
