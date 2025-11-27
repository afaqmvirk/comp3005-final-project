pip install -r requirements.txt

### Setting up the database

Run the database creation scripts in the database_creation.txt file.

### How to setup and run application:

1. Setup a python virtual environment
2. Activate your virtual environment (source /path/to/venv/activate)
3. Pip install requirements.txt
4. Connect your Postgresql database by setting your environment variables by setting DATABASE_URL='postgres://user:password@host:5432/dbname'" in a .env file
5. cd to /app run python3 main.py

Or run the setup.sh