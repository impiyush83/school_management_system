from enum import Enum


class UserType(Enum):
    PARENT = "PARENT"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class AttendanceStatus(Enum):
    PRESENT = "P"
    ABSENT = "A"


class ExamStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
