from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import mysql.connector
from mysql.connector import Error
from openpyxl import Workbook
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def connect_to_database():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='Brandy 123!',
            database='combineddb'
        )
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/fetch_data', methods=['GET', 'POST'])
def fetch_data():
    connection = connect_to_database()
    if connection is None:
        flash("Database connection failed.")
        return redirect(url_for('home'))

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM finaltodatabase")
    results = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]

    cursor.close()
    connection.close()
    return render_template('data_view.html', results=results, column_names=column_names)

@app.route('/search', methods=['POST'])
def search():
    name = request.form.get('name')
    surname = request.form.get('surname')
    cert_no = request.form.get('certNO')

    connection = connect_to_database()
    if connection is None:
        flash("Database connection failed.")
        return redirect(url_for('home'))

    cursor = connection.cursor()
    query = "SELECT * FROM finaltodatabase WHERE 1=1"
    params = []
    if name:
        query += " AND name LIKE %s"
        params.append(f"%{name}%")
    if surname:
        query += " AND surname LIKE %s"
        params.append(f"%{surname}%")
    if cert_no:
        query += " AND certNO = %s"
        params.append(cert_no)

    cursor.execute(query, params)
    results = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]

    cursor.close()
    connection.close()
    return render_template('data_view.html', results=results, column_names=column_names)

@app.route('/delete_record/<int:recordID>', methods=['POST'])
def delete_record(recordID):
    connection = connect_to_database()
    if connection is None:
        flash("Database connection failed.")
        return redirect(url_for('home'))

    cursor = connection.cursor()
    cursor.execute("DELETE FROM finaltodatabase WHERE recordID = %s", (recordID,))
    connection.commit()

    cursor.close()
    connection.close()
    return redirect(url_for('fetch_data'))

@app.route('/update_record/<int:recordID>', methods=['GET', 'POST'])
def update_record(recordID):
    connection = connect_to_database()
    if connection is None:
        flash("Database connection failed.")
        return redirect(url_for('home'))

    cursor = connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        counter = request.form['counter']
        cert_no = int(request.form['certNO'])  # Ensure this is an integer
        shares = request.form['shares']
        new_cert_no = int(request.form['newCertNO'])  # Ensure this is an integer
        new_quantity = request.form['newQuantity']
        price = float(request.form['price'])  # Ensure this is a float
        value = float(request.form['value'])  # Change to float
        sector = request.form['sector']
        security = request.form['security']
        remarks = request.form['remarks']
        csd_acc_no = request.form['csdAccNo']
        currency = request.form['currency']
        status = request.form['status']

        cursor.execute("""
            UPDATE finaltodatabase 
            SET name = %s, surname = %s, counter = %s, certNO = %s, shares = %s, 
                newCertNO = %s, newQuantity = %s, price = %s, value = %s, 
                sector = %s, security = %s, remarks = %s, csdAccNo = %s, 
                currency = %s, status = %s 
            WHERE recordID = %s
        """, (name, surname, counter, cert_no, shares, new_cert_no, new_quantity, price, value, 
              sector, security, remarks, csd_acc_no, currency, status, recordID))
        
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('fetch_data'))

    cursor.execute("SELECT * FROM finaltodatabase WHERE recordID = %s", (recordID,))
    record = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('update_record.html', record=record)
@app.route('/toggle_verification/<int:recordID>', methods=['POST'])
def toggle_verification(recordID):
    connection = connect_to_database()
    if connection is None:
        flash("Database connection failed.")
        return redirect(url_for('fetch_data'))

    cursor = connection.cursor()
    cursor.execute("SELECT status FROM finaltodatabase WHERE recordID = %s", (recordID,))
    current_status = cursor.fetchone()[0]

    new_status = 'verified' if current_status != 'verified' else 'unverified'
    cursor.execute("UPDATE finaltodatabase SET status = %s WHERE recordID = %s", (new_status, recordID))
    connection.commit()

    cursor.close()
    connection.close()
    return redirect(url_for('fetch_data'))

@app.route('/fetch_verified', methods=['GET'])
def fetch_verified():
    connection = connect_to_database()
    if connection is None:
        flash("Database connection failed.")
        return redirect(url_for('home'))

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM finaltodatabase WHERE status = 'verified'")
    results = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]

    cursor.close()
    connection.close()
    return render_template('data_view.html', results=results, column_names=column_names)

@app.route('/download_verified', methods=['GET'])
def download_verified():
    connection = connect_to_database()
    if connection is None:
        flash("Database connection failed.")
        return redirect(url_for('home'))

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM finaltodatabase WHERE status = 'verified'")
    results = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]

    # Create an Excel workbook and add a worksheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Verified Records"

    # Add column headers
    sheet.append(column_names)

    # Add data rows
    for row in results:
        sheet.append(row)

    # Save the workbook to a bytes buffer
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)

    # Close the database connection
    cursor.close()
    connection.close()

    return send_file(output, as_attachment=True, download_name="verified_records.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)