from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector

from datetime import date

# from getStudentID import get_student_id


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Replace these with your MySQL database credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'attendance_system',
}



def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student_login')
def student_login():
    return render_template('student_login.html')


@app.route('/student_signup')
def student_signup():
    print("Reached the signup route")
    return render_template('student_signup.html')


    

@app.route('/login', methods=['POST'])
def login():
    roll_no = request.form['roll_no']
    email = request.form['email']
    password = request.form['password']
    login_type = request.form['login_type']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if login_type == 'student':
        cursor.execute('SELECT * FROM new_students_table WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        session['roll_no'] = roll_no
        session['student_name'] = user['student_name']

    elif login_type == 'teacher':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM teachers_table WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()

    connection.close()

    if login_type == 'student':
        if user:
            flash('Login successful!', 'success')
            return redirect(url_for(f'student_dashboard'))
            
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('index'))
    else:
        if user:
            flash('Login successful!', 'success')
            return redirect(url_for(f'teacher_dashboard'))
            
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('index'))


@app.route('/signup', methods=['POST'])
def signup():
    student_name = request.form['name']
    roll_no = request.form['roll_no']
    gender = request.form['gender']
    college_name = request.form['college_name']
    mobile_number = request.form['mobile_number']
    email = request.form['email']
    password = request.form['password']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute('SELECT * FROM new_students_table WHERE email = %s', (email,))
    existing_user = cursor.fetchone()
    print("Existing user :", existing_user)


    if existing_user:
        flash('Email already exists. Please choose a different one.', 'error')
    else:
        cursor.execute('INSERT INTO new_students_table (roll_no, student_name, gender, college_name, mobile_number, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       (roll_no, student_name, gender, college_name, mobile_number, email, password))
        connection.commit()
        flash('Signup successful! You can now log in.', 'success')

    connection.close()
    return redirect(url_for('index'))

@app.route('/student_dashboard')
def student_dashboard():
    roll_no = session.get('roll_no')
    if roll_no:
        return render_template('student_dashboard.html', roll_no=roll_no)
    else:
        flash('Roll number not provided.', 'error')
        return redirect(url_for('index'))

@app.route('/teacher_dashboard')
def teacher_dashboard():
    # Render teacher dashboard with options to confirm attendance and view student attendance records
    return render_template('teacher_dashboard.html')


@app.route('/give_attendance', methods=['POST'])
def give_attendance():
    roll_no = request.form['roll_no']
    status = request.form['status']
    date = request.form['date']
    student_name  = session.get('student_name')
    reason = request.form.get('reason')


    print(f'Student Roll no: {roll_no}')  # Debug print
    print(f'Status: {status}')  # Debug print
    print(f'date selected : {date}')
    print(f'Student Name : {student_name}')
    print(f'Reason Of Absence : {reason}')


    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('INSERT INTO new_attendance_records2 (roll_no, date, status, reason) VALUES (%s, %s, %s, %s)',
                       (roll_no, date, status, reason))
        connection.commit()
          # Get current date
        # current_date = date.today().strftime("%Y-%m-%d")
        
        # Construct message
        message = f'Your attendance has been marked for {date}'

        connection.close()
        return jsonify({'message': message})
    except Exception as e:
        print(f'Error marking attendance: {str(e)}')
        flash('Failed to mark attendance. Please try again.', 'error')

    connection.close()
    return redirect(url_for('student_dashboard'))


@app.route('/view_attendance')
def view_attendance():
    # Get the logged-in student's roll number
    student_name = session.get('student_name')
    roll_no = session.get('roll_no')
    print(f'Student Name : {student_name}')

    # Fetch the attendance records for the student from the database
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
   
    cursor.execute('SELECT * FROM new_attendance_records2 WHERE roll_no = %s', (roll_no,))
    attendance_records = cursor.fetchall()
    connection.close()
    print(f'attendance records : {attendance_records}')

    #  Calculate the total number of classes and the number of classes attended
    total_classes = len(attendance_records)
    classes_attended = sum(1 for record in attendance_records if record['status'] == 'PRESENT')

    #  Calculate the percentage of attendance
    percentage_attendance = round((classes_attended / total_classes) * 100, 2) if total_classes > 0 else 0

    # Pass the attendance records and attendance percentage to the HTML template
    return render_template('view_attendance.html', student_name=student_name, roll_no=roll_no, attendance_records=attendance_records, 
                           percentage_attendance=percentage_attendance)



@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        # Handle form submission for teacher login
        username = request.form['username']
        password = request.form['password']
      
        # Query the database to check if the username and hashed password match any records
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM teachers_table WHERE username = %s AND password = %s', (username, password))
        teacher = cursor.fetchone()
        connection.close()

        if teacher:
            # If authentication successful, set session variables and redirect to teacher dashboard
            # session['teacher_username'] = teacher['username']
            return redirect('/teacher_dashboard')
        else:
            # If authentication fails, render the login page with an error message
            error_message = "Invalid username or password. Please try again."
            return render_template('teacher_login.html', error_message=error_message)
    else:
        # Render the teacher login page
        return render_template('teacher_login.html')



@app.route('/teacher_view_attendance', methods=['POST'])
def teacher_view_attendance():
    # Establish connection to the database

    selected_date = request.form['date']
    print(f"Date Selected by Teacher :- {selected_date}")    

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Prepare and execute the SQL query
    sql = "SELECT * FROM new_attendance_records2 WHERE date = %s"
    cursor.execute(sql, (selected_date,))
    attendance_records = cursor.fetchall()

    print(f"attendance records :- {attendance_records}")

    # Close the connection
    connection.close()

    return render_template('teacher_view_attendance.html', attendance_records=attendance_records, selected_date=selected_date)



@app.route('/individual_student_attendance', methods=['POST'])
def individual_student_attendance():
    # Establish connection to the database

    roll_no = request.form['roll_no']

    print(f"Teacher selected roll no : {roll_no}")
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Prepare and execute the SQL query
    with connection.cursor() as cursor:
        sql = "SELECT * FROM new_attendance_records2 WHERE roll_no = %s"
        cursor.execute(sql, (roll_no,))
        attendance_records = cursor.fetchall()

    print(f"attendance records for : {roll_no} are {attendance_records}")
    # Close the connection
    connection.close()

    return render_template('individual_student_attendance.html', roll_no=roll_no, attendance_records=attendance_records)



if __name__ == '__main__':
    app.run(debug=True)




#     Instead of it make new table..

# mysql> CREATE TABLE new_students_table (
#         roll_no VARCHAR(20) PRIMARY KEY,
#         student_name VARCHAR(100) NOT NULL,
#          gender VARCHAR(10),
#          college_name VARCHAR(100) NOT NULL,
#          mobile_number VARCHAR(15),
#          email VARCHAR(100) UNIQUE NOT NULL,
#          password VARCHAR(100) NOT NULL
#      );

# And....

# CREATE TABLE new_attendance_records (
  
#     roll_no varchar(20) PRIMARY KEY,
#     date DATE,
#     status ENUM('PRESENT', 'ABSENT'),
#     Reason varchar(100),
#     FOREIGN KEY (roll_no) REFERENCES new_students_table(roll_no)
# );


# Is this correct please check this....


