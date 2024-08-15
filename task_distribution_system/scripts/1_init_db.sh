#!/bin/bash
# Update the package list
sudo apt update

# Install PostgreSQL and its contrib package
sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql

# Enable PostgreSQL service to start on boot
sudo systemct

# Variables
DB_NAME="task_distribution_system1"
DB_USER="postgres"  # Replace with your PostgreSQL username
DB_PASSWORD="postgres"  # Replace with your PostgreSQL password

# Switch to the postgres user and execute the commands
sudo -i -u postgres psql <<EOF
-- Create the database
CREATE DATABASE $DB_NAME;

-- Create the user (if not exists) and grant privileges
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_catalog.pg_roles
        WHERE rolname = '$DB_USER') THEN
        CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

EOF

echo "Database '$DB_NAME' created and privileges granted to user '$DB_USER'."
