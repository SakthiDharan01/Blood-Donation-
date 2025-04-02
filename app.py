from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')


db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'blood_donation')
}


class DonorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=18, max=65)])
    blood_group = SelectField('Blood Group', choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Address', validators=[DataRequired()])
    submit = SubmitField('Add Donor')

class RecipientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=120)])
    blood_group = SelectField('Blood Group', choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Address', validators=[DataRequired()])
    hospital_name = StringField('Hospital Name', validators=[DataRequired(), Length(min=2, max=100)])
    hospital_address = TextAreaField('Hospital Address', validators=[DataRequired()])
    urgency_level = SelectField('Urgency Level', choices=[
        ('CRITICAL', 'Critical'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low')
    ])
    units_needed = IntegerField('Units Needed', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Add Recipient')

class InventoryForm(FlaskForm):
    bank_id = SelectField('Blood Bank', coerce=int, validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Blood Units')

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    cursor.execute("SELECT COUNT(*) as total FROM donors")
    total_donors = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM recipients")
    total_recipients = cursor.fetchone()['total']
    
    cursor.execute("SELECT SUM(quantity) as total FROM blood_inventory")
    total_blood_units = cursor.fetchone()['total'] or 0
    
    cursor.execute("SELECT COUNT(*) as total FROM recipients WHERE status = 'PENDING'")
    pending_requests = cursor.fetchone()['total']
    
   
    cursor.execute("""
        SELECT bb.name as blood_bank_name, bi.blood_group, bi.quantity, bi.last_updated
        FROM blood_inventory bi
        JOIN blood_banks bb ON bi.bank_id = bb.bank_id
        ORDER BY bi.last_updated DESC
    """)
    inventory = cursor.fetchall()
    
    
    cursor.execute("""
        SELECT name, blood_group, hospital_name as hospital, urgency_level, units_needed
        FROM recipients
        WHERE status = 'PENDING'
        ORDER BY 
            CASE urgency_level
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                ELSE 4
            END,
            created_at DESC
        LIMIT 5
    """)
    emergency_requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('index.html',
                         total_donors=total_donors,
                         total_recipients=total_recipients,
                         total_blood_units=total_blood_units,
                         pending_requests=pending_requests,
                         inventory=inventory,
                         emergency_requests=emergency_requests)

@app.route('/donors', methods=['GET', 'POST'])
def donors():
    form = DonorForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO donors (name, age, blood_group, contact_number, email, address, is_available)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                form.name.data,
                form.age.data,
                form.blood_group.data,
                form.contact_number.data,
                form.email.data,
                form.address.data,
                True
            ))
            conn.commit()
            flash('Donor added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding donor: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('donors'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM donors ORDER BY created_at DESC")
    donors = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('donors.html', form=form, donors=donors)

@app.route('/recipients', methods=['GET', 'POST'])
def recipients():
    form = RecipientForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO recipients (name, age, blood_group, contact_number, email, address, 
                                     hospital_name, hospital_address, urgency_level, units_needed, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                form.name.data,
                form.age.data,
                form.blood_group.data,
                form.contact_number.data,
                form.email.data,
                form.address.data,
                form.hospital_name.data,
                form.hospital_address.data,
                form.urgency_level.data,
                form.units_needed.data,
                'PENDING'
            ))
            conn.commit()
            flash('Recipient added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding recipient: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('recipients'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recipients ORDER BY created_at DESC")
    recipients = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('recipients.html', form=form, recipients=recipients)

@app.route('/inventory')
def inventory():
    form = InventoryForm()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get blood group filter
    blood_group = request.args.get('blood_group')
    
    # Build query
    query = """
        SELECT bi.*, bb.name as blood_bank_name
        FROM blood_inventory bi
        JOIN blood_banks bb ON bi.bank_id = bb.bank_id
    """
    params = []
    
    if blood_group:
        query += " WHERE bi.blood_group = %s"
        params.append(blood_group)
    
    query += " ORDER BY bi.last_updated DESC"
    
    cursor.execute(query, params)
    inventory = cursor.fetchall()
    
   
    cursor.execute("SELECT * FROM blood_banks")
    blood_banks = cursor.fetchall()
    
    
    form.bank_id.choices = [(bank['bank_id'], bank['name']) for bank in blood_banks]
    
    cursor.close()
    conn.close()
    
    return render_template('inventory.html', form=form, inventory=inventory, blood_banks=blood_banks)

@app.route('/inventory/add', methods=['POST'])
def add_inventory():
    if request.method == 'POST':
        bank_id = request.form.get('bank_id')
        blood_group = request.form.get('blood_group')
        quantity = request.form.get('quantity')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO blood_inventory (bank_id, blood_group, quantity, last_updated)
                VALUES (%s, %s, %s, NOW())
            """, (bank_id, blood_group, quantity))
            conn.commit()
            flash('Blood units added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding blood units: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('inventory'))

@app.route('/inventory/<int:id>/edit', methods=['POST'])
def edit_inventory(id):
    if request.method == 'POST':
        bank_id = request.form.get('bank_id')
        blood_group = request.form.get('blood_group')
        quantity = request.form.get('quantity')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE blood_inventory
                SET bank_id = %s, blood_group = %s, quantity = %s, last_updated = NOW()
                WHERE inventory_id = %s
            """, (bank_id, blood_group, quantity, id))
            conn.commit()
            flash('Blood units updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating blood units: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('inventory'))

@app.route('/inventory/<int:id>/delete', methods=['POST'])
def delete_inventory(id):
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM blood_inventory WHERE inventory_id = %s", (id,))
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
        finally:
            cursor.close()
            conn.close()

@app.route('/api/inventory/<int:id>')
def get_inventory(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM blood_inventory WHERE inventory_id = %s", (id,))
        inventory = cursor.fetchone()
        return jsonify(inventory)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/reports')
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as total FROM donors")
    stats = {
        'total_donors': cursor.fetchone()['total']
    }
    
    cursor.execute("SELECT COUNT(*) as total FROM recipients")
    stats['total_recipients'] = cursor.fetchone()['total']
    
    cursor.execute("SELECT SUM(quantity) as total FROM blood_inventory")
    stats['total_blood_units'] = cursor.fetchone()['total'] or 0
    
    cursor.execute("SELECT COUNT(*) as total FROM recipients WHERE status = 'PENDING'")
    stats['pending_requests'] = cursor.fetchone()['total']
    
   
    cursor.execute("""
        SELECT blood_group, COUNT(*) as count
        FROM donors
        GROUP BY blood_group
    """)
    blood_group_data = cursor.fetchall()
    
    cursor.execute("""
        SELECT DATE_FORMAT(transaction_date, '%Y-%m') as month, COUNT(*) as count
        FROM transactions
        WHERE transaction_type = 'DONATION'
        GROUP BY DATE_FORMAT(transaction_date, '%Y-%m')
        ORDER BY month DESC
        LIMIT 12
    """)
    monthly_donations = cursor.fetchall()
    
    
    cursor.execute("""
        SELECT t.*, bb.name as blood_bank_name
        FROM transactions t
        JOIN blood_banks bb ON t.bank_id = bb.bank_id
        ORDER BY t.transaction_date DESC
        LIMIT 10
    """)
    recent_transactions = cursor.fetchall()
    
    
    cursor.execute("""
        SELECT 
            bb.name,
            SUM(bi.quantity) as total_units,
            SUM(CASE WHEN bi.quantity > 0 THEN bi.quantity ELSE 0 END) as available_units,
            COUNT(CASE WHEN t.transaction_type = 'DONATION' AND DATE_FORMAT(t.transaction_date, '%Y-%m') = DATE_FORMAT(NOW(), '%Y-%m') THEN 1 END) as donations_this_month,
            COUNT(CASE WHEN t.transaction_type = 'DISTRIBUTION' AND DATE_FORMAT(t.transaction_date, '%Y-%m') = DATE_FORMAT(NOW(), '%Y-%m') THEN 1 END) as distributions_this_month
        FROM blood_banks bb
        LEFT JOIN blood_inventory bi ON bb.bank_id = bi.bank_id
        LEFT JOIN transactions t ON bb.bank_id = t.bank_id
        GROUP BY bb.bank_id, bb.name
    """)
    blood_bank_stats = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('reports.html',
                         stats=stats,
                         blood_group_labels=[item['blood_group'] for item in blood_group_data],
                         blood_group_data=[item['count'] for item in blood_group_data],
                         monthly_labels=[item['month'] for item in monthly_donations],
                         monthly_donations=[item['count'] for item in monthly_donations],
                         recent_transactions=recent_transactions,
                         blood_bank_stats=blood_bank_stats)

if __name__ == '__main__':
    app.run(debug=True) 
