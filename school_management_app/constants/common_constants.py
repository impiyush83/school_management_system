MASTER_KEY = "123456"
COOKIE_NAME = 'cookie'


class AttendanceCustomObject(object):

    def __init__(self, subject_id, attendance):
        self.subject_id = subject_id
        self.attendance = attendance
