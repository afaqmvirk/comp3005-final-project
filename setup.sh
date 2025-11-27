#!/bin/bash
# Setup script for Health and Fitness Club Management System
# Raymond Liu 101264487
# Afaq Virk 101338854

echo "Health & Fitness Club - Setup"

# Create virtual environment
echo ""
echo "Setting up Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "[SUCCESS] Virtual environment created!"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "[SUCCESS] Dependencies installed!"

# Database setup
echo ""
echo "Setting up PostgreSQL database..."
echo "Please ensure PostgreSQL is running."
echo ""
read -p "Enter PostgreSQL host (default: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Enter PostgreSQL username (default: postgres): " DB_USER
DB_USER=${DB_USER:-postgres}

read -sp "Enter PostgreSQL password: " DB_PASS
echo ""

read -p "Enter database name (default: Final_Project): " DB_NAME
DB_NAME=${DB_NAME:-Final_Project}

# Create database
echo ""
echo "Creating database..."
PGPASSWORD=$DB_PASS psql -U $DB_USER -h $DB_HOST -c "DROP DATABASE IF EXISTS $DB_NAME;"
PGPASSWORD=$DB_PASS psql -U $DB_USER -h $DB_HOST -c "CREATE DATABASE $DB_NAME;"

# Load schema and sample data
echo "Loading schema and sample data..."
PGPASSWORD=$DB_PASS psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f docs/database_creation.txt

echo ""
echo "[SUCCESS] Setup complete!"
echo ""
echo "Update the DATABASE_URL in app/main.py (line 21):"
echo "  DATABASE_URL = \"postgresql://$DB_USER:password@$DB_HOST/$DB_NAME\""
echo ""
echo "To run the application:"
echo "  source venv/bin/activate    # Activate virtual environment"
echo "  cd app"
echo "  python main.py"
echo ""
echo "Sample login credentials:"
echo "  Admin:   lebron.james@fitclub.com / admin123"
echo "  Trainer: t1@fitclub.com / trainer123"
echo ""
echo "Or register a new member from the main menu."
echo ""
echo "Note: The virtual environment has been activated for this session."
echo "      Remember to activate it in new terminal sessions using:"
echo "      source venv/bin/activate"
echo ""
