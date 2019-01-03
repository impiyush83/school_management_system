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
