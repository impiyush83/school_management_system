import datetime

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)


def get_subject_id_from_active_exams(active_exams):
    subjects_active_for_exam = []
    for exam in active_exams:
        subjects_active_for_exam.append(exam.subject_id)
    return subjects_active_for_exam


def get_list_of_users_marks(data):
    students = []
    marks = []
    for entry in data:
        if entry.get('student_id'):
            students.append(entry['student_id'])
        elif entry.get('marks'):
            marks.append(entry['marks'])
        else:
            continue
    return students, marks


def encrypt_password(password):
    return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)


def get_current_local_date():
    local_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
    local_date = local_time.strftime('%Y-%m-%d')
    return local_date


def get_current_local_date_in_datetime_format():
    local_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
    local_date = local_time
    return local_date


