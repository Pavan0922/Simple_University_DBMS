from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from datetime import date
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask_user:flask_password@localhost/university'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)

class AdminLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Department(db.Model):
    Department_Name = db.Column(db.String(255), primary_key=True)
    Dept_S_Name = db.Column(db.String(50), nullable=False)

class Sections(db.Model):
    Section_Name = db.Column(db.String(1), primary_key=True)

class Semesters(db.Model):
    Semester_Number = db.Column(db.Integer, primary_key=True)

class DeptSemSection(db.Model):
    __tablename__ = 'DEPT_SEM_SECTION'
    Department_Name = db.Column(db.String(255), db.ForeignKey('department.Department_Name'), primary_key=True)
    Semester_Number = db.Column(db.Integer, db.ForeignKey('semesters.Semester_Number'), primary_key=True)
    Section_Name = db.Column(db.String(1), db.ForeignKey('sections.Section_Name'), primary_key=True)

class Student(db.Model):
    USN = db.Column(db.Integer, primary_key=True, autoincrement=True)
    F_Name = db.Column(db.String(255))
    M_Name = db.Column(db.String(255))
    L_Name = db.Column(db.String(255))
    Gender = db.Column(db.String(1))
    DOB = db.Column(db.Date)
    PHNO = db.Column(db.BigInteger)
    Email = db.Column(db.String(255), unique=True)
    Password = db.Column(db.String(255))
    Department_Name = db.Column(db.String(255), db.ForeignKey('department.Department_Name'))
    Enrollment_Year = db.Column(db.Date)
    Semester_Number = db.Column(db.Integer, db.ForeignKey('semesters.Semester_Number'))
    Section_Name = db.Column(db.String(1), db.ForeignKey('sections.Section_Name'))
    Image = db.Column(db.LargeBinary, nullable=True)

class Teacher(db.Model):
    Teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    F_Name = db.Column(db.String(255))
    M_Name = db.Column(db.String(255))
    L_Name = db.Column(db.String(255))
    Gender = db.Column(db.String(1))
    DOB = db.Column(db.Date)
    PHNO = db.Column(db.BigInteger)
    Email = db.Column(db.String(255), unique=True)
    Password = db.Column(db.String(255))
    Department_Name = db.Column(db.String(255), db.ForeignKey('department.Department_Name'))
    Enrollment_Year = db.Column(db.Date)
    Image = db.Column(db.LargeBinary, nullable=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Department_Name = db.Column(db.String(255), db.ForeignKey('department.Department_Name'), nullable=False)
    Semester_Number = db.Column(db.Integer, db.ForeignKey('semesters.Semester_Number'), nullable=False)
    Course_Name = db.Column(db.String(255), nullable=False)
    Course_Number = db.Column(db.String(50), nullable=False)

class CourseForTeacher(db.Model):
    __tablename__ = 'course_for_teacher'
    Department_Name = db.Column(db.String(50), primary_key=True)
    Course_Name = db.Column(db.String(50), primary_key=True)
    Course_Instructor = db.Column(db.String(50), primary_key=True)
    Semester_Number = db.Column(db.Integer, primary_key=True)
    Section_Name = db.Column(db.String(1), primary_key=True)



class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.Teacher_id'), nullable=False)
    Department_Name = db.Column(db.String(255), db.ForeignKey('department.Department_Name'), nullable=False)
    Semester_Number = db.Column(db.Integer, db.ForeignKey('semesters.Semester_Number'), nullable=False)
    Section_Name = db.Column(db.String(255), db.ForeignKey('sections.Section_Name'), nullable=False)
    Student_USN = db.Column(db.Integer, db.ForeignKey('student.USN'), nullable=False)
    Course_Name = db.Column(db.String(255), nullable=False)
    Date = db.Column(db.Date, nullable=False)
    Attendance_Count = db.Column(db.Integer, default=0)
    F_Internal_Marks = db.Column(db.Integer)
    S_Internal_Marks = db.Column(db.Integer)
    Average_Marks = db.Column(db.Float)




setup_done = False

@app.before_request
def setup():
    global setup_done
    if not setup_done:
        db.create_all()
        setup_done = True

@app.route('/')
def admin_login_page():
    return render_template('admin/login.html')

@app.route('/Admin_login', methods=['POST'])
def login():
    email = request.form['username']
    password = request.form['password']
    admin = AdminLogin.query.filter_by(email=email).first()
    if admin and admin.password == password:
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid Email or Password', 'danger')
        return redirect(url_for('admin_login_page'))

@app.route('/admin_dashboard')
def admin_dashboard():
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    departments = Department.query.all()
    department_data = []
    for department in departments:
        department_name = department.Department_Name
        student_count = Student.query.filter_by(Department_Name=department_name).count()
        teacher_count = Teacher.query.filter_by(Department_Name=department_name).count()
        department_data.append({
            'name': department_name,
            'student_count': student_count,
            'teacher_count': teacher_count
        })
    return render_template('admin/admin_dashboard.html', 
                           total_students=total_students, 
                           total_teachers=total_teachers, 
                           department_data=department_data)

@app.route('/teacher_login', methods=['POST'])
def teacher_login():
    email = request.form['email']
    password = request.form['password']
    teacher = Teacher.query.filter_by(Email=email).first()
    if teacher and teacher.Password == password:
        session['teacher_id'] = teacher.Teacher_id
        session['teacher_name'] = f"{teacher.F_Name} {teacher.L_Name}"
        return redirect(url_for('teacher_profile'))
    else:
        flash('Invalid Email or Password', 'danger')
        return redirect(url_for('login_page'))

@app.route('/student_login', methods=['POST'])
def student_login():
    email = request.form['email']
    password = request.form['password']
    student = Student.query.filter_by(Email=email).first()
    if student and student.Password == password:
        session['student_usn'] = student.USN
        session['student_name'] = f"{student.F_Name} {student.L_Name}"
        return render_template("student/studentProfile.html", student=student)
    else:
        flash('Invalid Email or Password', 'danger')
        return redirect(url_for('login_page'))

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/teacher_profile')
def teacher_profile():
    if 'teacher_id' in session:
        teacher = Teacher.query.filter_by(Teacher_id=session['teacher_id']).first()
        assigned_courses = db.session.query(
            Course.Course_Name, 
            CourseForTeacher.Semester_Number, 
            CourseForTeacher.Section_Name
        ).join(
            CourseForTeacher, Course.Course_Name == CourseForTeacher.Course_Name
        ).filter(
            CourseForTeacher.Course_Instructor == session['teacher_id']
        ).all()
        return render_template('teacher/teachersProfile.html', teacher=teacher, assigned_courses=assigned_courses)
    else:
        flash('You are not logged in', 'danger')
        return redirect(url_for('login_page'))


@app.route('/student_profile')
def student_profile():
    if 'student_usn' in session:
        student = Student.query.filter_by(USN=session['student_usn']).first()
        return render_template('student/studentProfile.html', student=student)
    else:
        flash('You are not logged in', 'danger')
        return redirect(url_for('login_page'))
    

@app.route('/create_course')
def create_course():
    departments = {record.Department_Name for record in DeptSemSection.query.all()}
    return render_template('admin/create_course.html', departments=departments)

@app.route('/submit_course', methods=['POST'])
def submit_course():
    department_name = request.form['department']
    semester_number = request.form['semester']
    course_name = request.form['courseName']
    course_code = request.form['courseCode']
    
    new_course = Course(
        Department_Name=department_name,
        Semester_Number=semester_number,
        Course_Name=course_name,
        Course_Number=course_code,
    )
    
    db.session.add(new_course)
    db.session.commit()
    flash('Course created successfully', 'success')
    return redirect(url_for('create_course'))

    
@app.route('/student_subject')
def student_subject():
    # Your code to handle the 'student_subject' endpoint
    return render_template('student/student_subject.html')

@app.route('/studentTimetable')
def student_timetable():
    # Logic to fetch and display the student's timetable goes here
    return render_template('student/studentTimetable.html')



@app.route('/teacher_subject')
def teacher_subject():
    teacher_id = session.get('teacher_id')  # Assuming you store the teacher's ID in session after login
    if not teacher_id:
        flash('You must be logged in to view this page.', 'warning')
        return redirect(url_for('login'))

    assigned_courses = CourseForTeacher.query.filter_by(Course_Instructor=teacher_id).all()
    return render_template('teacher/teacher_subject.html', assigned_courses=assigned_courses)

@app.route('/teacherTimeTable')
def teacherTimeTable():
    return render_template('teacher/teacherTimeTable.html')

@app.route('/upload_profile_photo', methods=['POST'])
def upload_profile_photo():
    if 'teacher_id' not in session:
        flash('You are not logged in', 'danger')
        return redirect(url_for('login_page'))

    if 'profile_photo' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('teacher_profile'))

    file = request.files['profile_photo']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('teacher_profile'))

    if file:
        teacher = Teacher.query.filter_by(Teacher_id=session['teacher_id']).first()
        teacher.Image = file.read()
        db.session.commit()
        flash('Profile photo uploaded successfully', 'success')
        return redirect(url_for('teacher_profile'))

@app.route('/upload_student_profile_photo', methods=['POST'])
def upload_student_profile_photo():
    if 'student_usn' not in session:
        flash('You are not logged in', 'danger')
        return redirect(url_for('login_page'))

    if 'profile_photo' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('student_profile'))

    file = request.files['profile_photo']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('student_profile'))

    if file:
        student = Student.query.filter_by(USN=session['student_usn']).first()
        student.Image = file.read()
        db.session.commit()
        flash('Profile photo uploaded successfully', 'success')
        return redirect(url_for('student_profile'))

@app.route('/download_student_image/<int:student_id>')
def download_student_image(student_id):
    student = Student.query.get_or_404(student_id)
    if student.Image:
        return send_file(io.BytesIO(student.Image), mimetype='image/jpeg', as_attachment=True, download_name=f'student_{student_id}.jpg')
    else:
        flash('No image found for the student.', 'danger')
        return redirect(url_for('student_profile'))

@app.route('/download_teacher_image/<int:teacher_id>')
def download_teacher_image(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    if teacher.Image:
        return send_file(io.BytesIO(teacher.Image), mimetype='image/jpeg', as_attachment=False)
    else:
        flash('No image found for the teacher.', 'danger')
        return redirect(url_for('teacher_profile'))

@app.route('/create_teacher')
def create_teacher():
    departments = {record.Department_Name for record in DeptSemSection.query.all()}
    return render_template('admin/create_teacher.html', departments=departments)

@app.route('/create_student')
def create_student():
    departments = {record.Department_Name for record in DeptSemSection.query.all()}
    return render_template('admin/create_student.html', departments=departments)

@app.route('/assign_teacher_course', methods=['GET', 'POST'])
def assign_teacher_course():
    if request.method == 'POST':
        department = request.form['department']
        semester = request.form['semester']
        course = request.form['course']
        teacher = request.form['teacher']
        section = request.form['section']

        new_assignment = CourseForTeacher(
            Department_Name=department,
            Course_Name=course,
            Course_Instructor=teacher,
            Semester_Number=semester,
            Section_Name=section
        )
        db.session.add(new_assignment)
        db.session.commit()

        flash('Course assigned to teacher successfully!', 'success')
        return redirect(url_for('assign_teacher_course'))

    departments = Department.query.all()
    return render_template('admin/assign_teacher_course.html', departments=departments)

@app.route('/get_courses/<department_name>/<semester_number>')
def get_courses(department_name, semester_number):
    try:
        app.logger.info(f"Fetching courses for department: {department_name}, semester: {semester_number}")
        
        courses = Course.query.with_entities(Course.Course_Name).filter_by(Department_Name=department_name, Semester_Number=semester_number).all()
        
        course_list = [{'Course_Name': course.Course_Name} for course in courses]
        
        app.logger.info(f"Courses fetched: {course_list}")
        return jsonify({'courses': course_list})
    except Exception as e:
        app.logger.error(f"Error fetching courses: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/get_teachers/<department_name>')
def get_teachers(department_name):
    teachers = Teacher.query.filter_by(Department_Name=department_name).all()
    teacher_data = [{'Teacher_id': teacher.Teacher_id, 'name': f"{teacher.F_Name} {teacher.L_Name}"} for teacher in teachers]
    return jsonify({'teachers': teacher_data})

@app.route('/get_semesters/<department_name>')
def get_semesters(department_name):
    records = DeptSemSection.query.filter_by(Department_Name=department_name).all()
    semester_data = {record.Semester_Number for record in records}
    return jsonify({'semesters': list(semester_data)})

@app.route('/get_sections/<department_name>/<semester_number>')
def get_sections(department_name, semester_number):
    records = DeptSemSection.query.filter_by(Department_Name=department_name, Semester_Number=semester_number).all()
    section_data = {record.Section_Name for record in records}
    return jsonify({'sections': list(section_data)})

@app.route('/submit_student', methods=['POST'])
def submit_student():
    f_name = request.form['first-name']
    m_name = request.form.get('middle-name')
    l_name = request.form['last-name']
    gender = request.form['gender']
    dob = request.form['dob']
    phno = request.form['phone-number']
    email = request.form['email']
    password = request.form['password']
    department_name = request.form['department']
    enrollment_year = request.form['enrollment-year']
    semester_number = request.form['semester']
    section_name = request.form['section']
    
    enrollment_year_date = datetime.strptime(enrollment_year, '%Y-%m-%d').date()
    
    new_student = Student(
        F_Name=f_name,
        M_Name=m_name,
        L_Name=l_name,
        Gender=gender,
        DOB=dob,
        PHNO=phno,
        Email=email,
        Password=password,
        Department_Name=department_name,
        Enrollment_Year=enrollment_year_date,
        Semester_Number=semester_number,
        Section_Name=section_name
    )
    
    db.session.add(new_student)
    db.session.commit()
    flash('Student created successfully', 'success')
    return redirect(url_for('create_student'))

@app.route('/submit_teacher', methods=['POST'])
def submit_teacher():
    f_name = request.form['first-name']
    m_name = request.form.get('middle-name')
    l_name = request.form['last-name']
    gender = request.form['gender']
    dob = request.form['dob']
    phno = request.form['phone-number']
    email = request.form['email']
    password = request.form['password']
    department_name = request.form['department']
    enrollment_year = request.form['enrollment-year']
    
    enrollment_year_date = datetime.strptime(enrollment_year, '%Y-%m-%d').date()
    
    new_teacher = Teacher(
        F_Name=f_name,
        M_Name=m_name,
        L_Name=l_name,
        Gender=gender,
        DOB=dob,
        PHNO=phno,
        Email=email,
        Password=password,
        Department_Name=department_name,
        Enrollment_Year=enrollment_year_date
    )
    
    db.session.add(new_teacher)
    db.session.commit()
    flash('Teacher created successfully', 'success')
    return redirect(url_for('create_teacher'))



@app.route('/manage_students', methods=['GET'])
def manage_students():
    teacher_id = session.get('teacher_id')  # Assuming teacher_id is stored in the session
    if not teacher_id:
        return "Unauthorized", 401

    teacher = Teacher.query.filter_by(Teacher_id=teacher_id).first()
    if not teacher:
        flash('Teacher not found', 'danger')
        return redirect(url_for('login_page'))

    # Fetch courses for the teacher to determine the sections they are assigned to
    assigned_sections = CourseForTeacher.query.filter_by(Course_Instructor=teacher_id).all()

    # Organize students by sections assigned to the teacher
    sections = {}
    for assignment in assigned_sections:
        students = Student.query.filter_by(
            Department_Name=assignment.Department_Name,
            Semester_Number=assignment.Semester_Number,
            Section_Name=assignment.Section_Name
        ).all()
        
        section_key = assignment.Section_Name
        if section_key not in sections:
            sections[section_key] = []
        
        sections[section_key].extend(students)

    return render_template('teacher/manageStudents.html', sections=sections, teacher=teacher)



@app.route('/view_dashboard')
def view_dashboard():
    return render_template('admin/admin_dashboard.html')

@app.route('/create_time_table')
def create_time_table():
    return render_template('admin/create_TimeTable.html')


if __name__ == "__main__":
    app.run(debug=True)
