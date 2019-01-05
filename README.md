# School Management System 

1. **LOCAL INSTALLATIONS** 

    * pip install -r requirements.txt
    * python manage.py migrate
    * python manage.py runserver

2. **SYSTEM FLOW**

    * Types of Users:
    
       * Student
       * Teache / Admin  
       * Parent - Requires 123456 as signup key 
       
    * Functionalities :
    
        * Student : 
            1. Can view his attendance
            2. Can view his exam marks
            3. Can view ongoing exams 
     
        * Parent : 
            
            1. Requires student's username and password to view student's attendance.
            2.  Requires student's username and password to view student's marks obtained in exam.
            
        * Teacher 
        
            1. Can enroll a student in a particular course.
                * Currently 8 subjects of 4 courses of 2 departments to select. 
                * Addition of new courses ( WIP ) 
            2. Can create on-spot exams, subject-wise.
                * Constraints : 
                    1. Only one exam per subject at one time.
            3. Can finish ongoing exam. 
            4. Can enter students marks. 
            5. Can enter students attendance. 
 