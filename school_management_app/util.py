def get_subject_id_from_active_exams(active_exams):
    subjects_active_for_exam = []
    for exam in active_exams:
        subjects_active_for_exam.append(exam.subject_id)
    return subjects_active_for_exam