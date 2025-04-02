# Blood Donation Management System

A comprehensive web-based system for managing blood donation and distribution processes. Built with Flask and MySQL.

## Features

- Donor Management
  - Register and track donors
  - Monitor donor availability
  - Track donation history

- Recipient Management
  - Register blood recipients
  - Track hospital information
  - Manage urgency levels
  - Monitor units needed

- Blood Inventory
  - Track blood units by blood group
  - Monitor inventory levels
  - Set alerts for low inventory
  - Record last updated timestamps

- Transaction System
  - Record blood donations
  - Track blood distributions
  - Maintain transaction history
  - Link transactions to specific blood banks

- Reporting System
  - Blood group distribution statistics
  - Monthly donation trends
  - Blood bank performance metrics
  - Emergency request tracking
  - Inventory status reports

## Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/blood-donation-system.git
   cd blood-donation-system
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env with your database credentials and secret key
   ```

5. Set up the database:
   ```bash
   # Create MySQL database
   mysql -u root -p
   CREATE DATABASE blood_donation;
   exit;

   # Run the database setup script
   python setup_database.py
   ```

## Running the Application

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Project Structure

```
blood-donation-system/
├── app.py                 # Main Flask application
├── setup_database.py      # Database setup script
├── schema.sql            # Database schema
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in git)
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
└── templates/           # HTML templates
    ├── base.html
    ├── index.html
    ├── donors.html
    ├── recipients.html
    ├── inventory.html
    └── reports.html
```

## Database Schema

The system uses the following tables:
- `donors`: Stores donor information
- `blood_banks`: Manages blood bank details
- `blood_inventory`: Tracks blood units
- `recipients`: Stores recipient information
- `transactions`: Records all blood-related transactions

## Contributing

1. Fork the repository
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Commit your changes:
   ```bash
   git commit -m "Add your feature description"
   ```
5. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask web framework
- MySQL database
- Bootstrap for UI components
- WTForms for form handling 