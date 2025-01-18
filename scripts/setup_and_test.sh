#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting setup and test process...${NC}"

# Create and activate virtual environment
echo -e "\n${GREEN}Setting up virtual environment...${NC}"
python -m venv venv
source venv/bin/activate

# Install requirements
echo -e "\n${GREEN}Installing requirements...${NC}"
pip install -r requirements.txt

# Run migrations
echo -e "\n${GREEN}Running migrations...${NC}"
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo -e "\n${GREEN}Creating superuser...${NC}"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin@example.com', 'adminpass')" | python manage.py shell

# Run setup script
echo -e "\n${GREEN}Running setup script...${NC}"
python scripts/setup_agora.py

# Start development server
echo -e "\n${GREEN}Starting development server...${NC}"
python manage.py runserver 