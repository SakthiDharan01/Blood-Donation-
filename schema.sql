-- Use the database
USE blood_donation;

-- Create Donors table
CREATE TABLE IF NOT EXISTS donors (
    donor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 18 AND age <= 65),
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    contact_number VARCHAR(15) NOT NULL,
    email VARCHAR(100) UNIQUE,
    address TEXT NOT NULL,
    last_donation_date DATE,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Blood Banks table
CREATE TABLE IF NOT EXISTS blood_banks (
    bank_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    contact_number VARCHAR(15) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Blood Inventory table
CREATE TABLE IF NOT EXISTS blood_inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    bank_id INT,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    UNIQUE KEY unique_bank_blood_group (bank_id, blood_group)
);

-- Create Recipients table
CREATE TABLE IF NOT EXISTS recipients (
    recipient_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 0 AND age <= 120),
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    contact_number VARCHAR(15) NOT NULL,
    hospital_name VARCHAR(100) NOT NULL,
    hospital_address TEXT NOT NULL,
    urgency_level ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL,
    units_needed INT NOT NULL,
    status ENUM('PENDING', 'FULFILLED', 'CANCELLED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    donor_id INT,
    recipient_id INT,
    bank_id INT,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units INT NOT NULL,
    transaction_type ENUM('DONATION', 'DISTRIBUTION') NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE SET NULL,
    FOREIGN KEY (recipient_id) REFERENCES recipients(recipient_id) ON DELETE SET NULL,
    FOREIGN KEY (bank_id) REFERENCES blood_banks(bank_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_donor_blood_group ON donors(blood_group);
CREATE INDEX idx_donor_location ON donors(address(100));
CREATE INDEX idx_recipient_blood_group ON recipients(blood_group);
CREATE INDEX idx_recipient_urgency ON recipients(urgency_level);
CREATE INDEX idx_inventory_blood_group ON blood_inventory(blood_group);

-- Create view for available blood types at each location
CREATE OR REPLACE VIEW blood_bank_inventory_view AS
SELECT 
    bb.name AS bank_name,
    bb.address AS bank_address,
    bi.blood_group,
    bi.quantity,
    bi.last_updated
FROM blood_banks bb
JOIN blood_inventory bi ON bb.bank_id = bi.bank_id
WHERE bi.quantity > 0;

-- Create trigger to update inventory after donation
DELIMITER //
CREATE TRIGGER after_donation
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    IF NEW.transaction_type = 'DONATION' THEN
        UPDATE blood_inventory
        SET quantity = quantity + NEW.units
        WHERE bank_id = NEW.bank_id AND blood_group = NEW.blood_group;
    ELSEIF NEW.transaction_type = 'DISTRIBUTION' THEN
        UPDATE blood_inventory
        SET quantity = quantity - NEW.units
        WHERE bank_id = NEW.bank_id AND blood_group = NEW.blood_group;
    END IF;
END //
DELIMITER ; 