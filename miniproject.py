import sqlite3

# ---------------- DATABASE CONNECTION ----------------
def get_connection():
    return sqlite3.connect("employee.db")

# ---------------- CREATE TABLES ----------------
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Departments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Department(
        department_id INTEGER PRIMARY KEY AUTOINCREMENT,
        department_name TEXT,
        location TEXT
    )
    """)

    # Jobs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Job(
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        min_salary REAL,
        max_salary REAL
    )
    """)

    # Employees
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employee(
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone TEXT,
        department_id INTEGER,
        job_id INTEGER,
        salary REAL
    )
    """)

    # Attendance
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Attendance(
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        date TEXT,
        status TEXT
    )
    """)

    # Leave
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS LeaveTable(
        leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        leave_type TEXT,
        start_date TEXT,
        end_date TEXT,
        status TEXT
    )
    """)

    # Payroll
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Payroll(
        payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        month TEXT,
        basic_salary REAL,
        deductions REAL,
        net_salary REAL
    )
    """)

    # Login table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Login(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        employee_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

# ---------------- DEFAULT ADMIN ----------------
def add_default_admin():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Login WHERE role='admin'")
    if cursor.fetchone() is None:
        cursor.execute("""
        INSERT INTO Login (username, password, role)
        VALUES ('admin', 'admin123', 'admin')
        """)
        conn.commit()
    conn.close()

# ---------------- LOGIN ----------------
def login(role_choice):
    conn = get_connection()
    cursor = conn.cursor()

    username = input("Username: ")
    password = input("Password: ")

    cursor.execute("""
    SELECT role, employee_id FROM Login
    WHERE username=? AND password=? AND role=?
    """, (username, password, role_choice))

    user = cursor.fetchone()
    conn.close()

    if user:
        print(f"\n✅ Login successful as {role_choice}!\n")
        return user
    else:
        print("\n❌ Invalid login\n")
        return None

# ---------------- ADMIN MENU ----------------
def admin_menu():
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. Add Employee")
        print("2. View Employees")
        print("3. Add Department")
        print("4. View Departments")
        print("5. Mark Attendance")
        print("6. Add Payroll")
        print("7. View Leaves")
        print("8. Approve/Reject Leave")
        print("9. Logout")

        ch = input("Choice: ")
        if ch == '1': add_employee()
        elif ch == '2': view_employees()
        elif ch == '3': add_department()
        elif ch == '4': view_departments()
        elif ch == '5': mark_attendance()
        elif ch == '6': add_payroll()
        elif ch == '7': view_all_leaves()
        elif ch == '8': approve_reject_leave()
        elif ch == '9': break

# ---------------- EMPLOYEE MENU ----------------
def employee_menu(emp_id):
    while True:
        print("\n--- EMPLOYEE MENU ---")
        print("1. View Profile")
        print("2. View Attendance")
        print("3. Apply Leave")
        print("4. View Leave Status")
        print("5. View Payroll")
        print("6. Logout")

        ch = input("Choice: ")
        conn = get_connection()
        cursor = conn.cursor()

        if ch == '1':
            cursor.execute("SELECT * FROM Employee WHERE employee_id=?", (emp_id,))
            print(cursor.fetchone())
        elif ch == '2':
            cursor.execute("SELECT date,status FROM Attendance WHERE employee_id=?", (emp_id,))
            print(cursor.fetchall())
        elif ch == '3':
            apply_leave(emp_id)
        elif ch == '4':
            view_my_leaves(emp_id)
        elif ch == '5':
            cursor.execute("SELECT month,net_salary FROM Payroll WHERE employee_id=?", (emp_id,))
            print(cursor.fetchall())
        elif ch == '6':
            conn.close()
            break

        conn.close()

# ---------------- OTHER FUNCTIONS ----------------
def add_employee():
    conn = get_connection()
    cursor = conn.cursor()

    fname = input("First Name: ")
    lname = input("Last Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    dept = int(input("Department ID: "))
    job = int(input("Job ID: "))
    salary = float(input("Salary: "))

    cursor.execute("""
    INSERT INTO Employee (first_name,last_name,email,phone,department_id,job_id,salary)
    VALUES (?,?,?,?,?,?,?)
    """, (fname, lname, email, phone, dept, job, salary))

    emp_id = cursor.lastrowid
    username = input("Create username: ")
    password = input("Create password: ")

    cursor.execute("""
    INSERT INTO Login (username,password,role,employee_id)
    VALUES (?,?, 'employee', ?)
    """, (username, password, emp_id))

    conn.commit()
    conn.close()
    print("✅ Employee added successfully")

def view_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Employee")
    for row in cursor.fetchall():
        print(row)
    conn.close()

def add_department():
    conn = get_connection()
    cursor = conn.cursor()
    name = input("Department Name: ")
    loc = input("Location: ")
    cursor.execute("INSERT INTO Department VALUES (NULL,?,?)", (name, loc))
    conn.commit()
    conn.close()
    print("✅ Department added")

def view_departments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Department")
    for row in cursor.fetchall():
        print(row)
    conn.close()

def mark_attendance():
    conn = get_connection()
    cursor = conn.cursor()
    eid = int(input("Employee ID: "))
    date = input("Date (YYYY-MM-DD): ")
    status = input("Present/Absent/Leave: ")
    cursor.execute("INSERT INTO Attendance VALUES (NULL,?,?,?)", (eid, date, status))
    conn.commit()
    conn.close()
    print("✅ Attendance marked")

def add_payroll():
    conn = get_connection()
    cursor = conn.cursor()
    eid = int(input("Employee ID: "))
    month = input("Month: ")
    basic = float(input("Basic Salary: "))
    ded = float(input("Deductions: "))
    net = basic - ded
    cursor.execute("INSERT INTO Payroll VALUES (NULL,?,?,?,?,?)", (eid, month, basic, ded, net))
    conn.commit()
    conn.close()
    print("✅ Payroll added")

def view_all_leaves():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LeaveTable")
    for row in cursor.fetchall():
        print(row)
    conn.close()

def approve_reject_leave():
    conn = get_connection()
    cursor = conn.cursor()
    lid = int(input("Leave ID: "))
    action = input("Approved / Rejected: ").capitalize()
    cursor.execute("UPDATE LeaveTable SET status=? WHERE leave_id=?", (action, lid))
    conn.commit()
    conn.close()
    print("✅ Leave updated")

def apply_leave(emp_id):
    conn = get_connection()
    cursor = conn.cursor()
    ltype = input("Leave Type: ")
    start = input("Start Date: ")
    end = input("End Date: ")
    cursor.execute("INSERT INTO LeaveTable VALUES (NULL,?,?,?,?, 'Pending')", (emp_id, ltype, start, end))
    conn.commit()
    conn.close()
    print("✅ Leave applied")

def view_my_leaves(emp_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT leave_type,start_date,end_date,status FROM LeaveTable WHERE employee_id=?", (emp_id,))
    for row in cursor.fetchall():
        print(row)
    conn.close()

# ---------------- MAIN ----------------
def main():
    create_tables()
    add_default_admin()

    while True:
        print("\n=== WELCOME TO XYZ COMPANY ===")
        print("1. Admin Login")
        print("2. Employee Login")
        print("3. Exit")

        choice = input("Enter choice: ")
        if choice == '1':
            user = login('admin')
            if user:
                admin_menu()
        elif choice == '2':
            user = login('employee')
            if user:
                _, emp_id = user
                employee_menu(emp_id)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice")

main()
