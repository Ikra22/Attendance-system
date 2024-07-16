import mysql.connector

def get_student_id(email):
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'attendance_system',
    }

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute('SELECT student_id FROM students_table WHERE email = %s', (email,))
    student = cursor.fetchone()

    cursor.close()
    connection.close()

    if student:
        print('Student inside function-', student )
        print('Student ID  inside Function -', student['student_id'])
        return student['student_id']
    else:
        return None
