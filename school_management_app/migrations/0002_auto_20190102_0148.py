# Generated by Django 2.0 on 2019-01-02 01:48

from django.db import migrations

from school_management_app.models import Subjects


def add_subjects(apps, schema_editor):
    subjects = [['ML', 'CS', 'Engineering'], ['NLP', 'CS', 'Engineering'], ['Web Development', 'IT', 'Engineering'],
                ['Software Engineering', 'IT', 'Engineering'], ['MedSub1', 'Medicine', 'Pharma'],
                ['MedSub2', 'Medicine', 'Pharma'], [
                    'DentalSub1', 'Dental', 'Pharma'], ['DentalSub2', 'Dental', 'Pharma']]
    for subject in subjects:
        subject = Subjects(
            name=subject[0],
            course=subject[1],
            department=subject[2]
        )
        subject.save(force_insert=True)


# backward function
def remove_subjects(apps, schema_editor):
    subjects = Subjects.objects.all()
    for subject in subjects:
        subject.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('school_management_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_subjects,
            remove_subjects
        )
    ]