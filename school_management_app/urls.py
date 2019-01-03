from django.urls import path

from school_management_app import teacher_views
from . import views

urlpatterns = [
    path('', views.index, name='index_page'),
    path('user/signup/', views.add_user, name='insert_new_user'),
    path('user/login/', views.user_login, name='login_user'),
    path('user/home/', views.render_homepage, name='render_homepage'),
    path('user/logout/', views.user_logout, name='user_logout'),
    path('teacher/enroll-student/', views.enroll_student, name='enroll_students_to_course-dashboard'),
    path('teacher/student-engagement/', teacher_views.engage_student, name='engage_students'),
    path('teacher/exams/', teacher_views.create_exams, name='create-exams-dashboard'),
    path('teacher/exam/add/', teacher_views.insert_exam, name='create-exams'),
    path('teacher/active-exams/', teacher_views.close_active_exams_dashboard, name='close-active-exam-dashboard'),
    path('teacher/exam/finish/', teacher_views.close_active_exams, name='close-active-exam'),
    path('teacher/exam/marks/', teacher_views.assign_exam_marks_dashboard, name='assign-marks'),
    path('teacher/exam/assign-marks/', teacher_views.assign_exam_marks, name='assign-exam-marks'),

]
