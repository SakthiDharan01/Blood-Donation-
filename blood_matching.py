"""
Blood Donation Management System - Blood Matching Module
This module handles blood compatibility rules and donor-recipient matching.
"""

# Blood compatibility rules
BLOOD_COMPATIBILITY = {
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'A-': ['A-', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'B-': ['B-', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    'AB-': ['A-', 'B-', 'AB-', 'O-'],
    'O+': ['O+', 'O-'],
    'O-': ['O-']
}

def get_compatible_blood_groups(blood_group):
    """
    Returns a list of blood groups that are compatible with the given blood group.
    
    Args:
        blood_group (str): The blood group to check compatibility for
        
    Returns:
        list: List of compatible blood groups
    """
    return BLOOD_COMPATIBILITY.get(blood_group, [])

def find_compatible_donors(cursor, recipient_blood_group, recipient_location=None, limit=10):
    """
    Find compatible donors for a given blood group.
    
    Args:
        cursor: MySQL cursor
        recipient_blood_group (str): The blood group needed
        recipient_location (str, optional): Location to prioritize nearby donors
        limit (int): Maximum number of donors to return
        
    Returns:
        list: List of compatible donors
    """
    compatible_groups = get_compatible_blood_groups(recipient_blood_group)
    
    if not compatible_groups:
        return []
    
    # Base query to find compatible donors
    query = """
        SELECT 
            d.donor_id,
            d.name,
            d.blood_group,
            d.contact_number,
            d.email,
            d.address,
            d.last_donation_date,
            d.is_available,
            TIMESTAMPDIFF(DAY, d.last_donation_date, CURDATE()) as days_since_last_donation
        FROM donors d
        WHERE d.blood_group IN ({})
        AND d.is_available = TRUE
    """.format(','.join(['%s'] * len(compatible_groups)))
    
    # Add location-based sorting if location is provided
    if recipient_location:
        query += """
        ORDER BY 
            CASE 
                WHEN d.address LIKE %s THEN 1
                ELSE 2
            END,
            d.last_donation_date IS NULL DESC,
            d.last_donation_date ASC
        """
        params = compatible_groups + [f'%{recipient_location}%']
    else:
        query += """
        ORDER BY 
            d.last_donation_date IS NULL DESC,
            d.last_donation_date ASC
        """
        params = compatible_groups
    
    query += " LIMIT %s"
    params.append(limit)
    
    cursor.execute(query, params)
    return cursor.fetchall()

def find_matching_recipients(cursor, donor_blood_group, donor_location=None, limit=10):
    """
    Find recipients that are compatible with a donor's blood group.
    
    Args:
        cursor: MySQL cursor
        donor_blood_group (str): The donor's blood group
        donor_location (str, optional): Location to prioritize nearby recipients
        limit (int): Maximum number of recipients to return
        
    Returns:
        list: List of compatible recipients
    """
    # Base query to find compatible recipients
    query = """
        SELECT 
            r.recipient_id,
            r.name,
            r.blood_group,
            r.contact_number,
            r.hospital_name,
            r.hospital_address,
            r.units_needed,
            r.urgency_level,
            r.status
        FROM recipients r
        WHERE r.blood_group = %s
        AND r.status = 'PENDING'
    """
    params = [donor_blood_group]
    
    # Add location-based sorting if location is provided
    if donor_location:
        query += """
        ORDER BY 
            CASE 
                WHEN r.hospital_address LIKE %s THEN 1
                ELSE 2
            END,
            CASE r.urgency_level
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                WHEN 'LOW' THEN 4
            END,
            r.created_at ASC
        """
        params.append(f'%{donor_location}%')
    else:
        query += """
        ORDER BY 
            CASE r.urgency_level
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                WHEN 'LOW' THEN 4
            END,
            r.created_at ASC
        """
    
    query += " LIMIT %s"
    params.append(limit)
    
    cursor.execute(query, params)
    return cursor.fetchall()

def check_blood_compatibility(donor_blood_group, recipient_blood_group):
    """
    Check if a donor's blood group is compatible with a recipient's blood group.
    
    Args:
        donor_blood_group (str): The donor's blood group
        recipient_blood_group (str): The recipient's blood group
        
    Returns:
        bool: True if compatible, False otherwise
    """
    compatible_groups = get_compatible_blood_groups(recipient_blood_group)
    return donor_blood_group in compatible_groups 