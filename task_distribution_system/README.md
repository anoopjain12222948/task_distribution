# Task Distribution System

This project is a Django-based application designed to manage and distribute tasks efficiently.

## Prerequisites

- Python 3.8
- pip (Python package installer)
- PostgreSQL

## Setup

task_distribution_system/scripts/1_init_db.sh

### 1. Create a Python 3.8 virtual environment

```bash
python3.8 -m venv venv3.8
```

### 2. Activate the virtual environment and install dependencies

```
source venv3.8/bin/activate
pip install -r requirements.txt
```

### 3. Initialize the Database

Run the following shell script to create the PostgreSQL database and grant necessary permissions:

```bash
bash task_distribution_system/scripts/1_init_db.sh
```

### 4. Run Django migrations

```bash
python manage.py migrate
```

### 5. Start Django development server

```bash
python manage.py runserver
```

### 6. Please find api collection in following path

task_distribution_system/jsons/task_distribution_app.postman_collection.json