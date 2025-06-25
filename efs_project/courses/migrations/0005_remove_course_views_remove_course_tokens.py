from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_alter_course_difficulty'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='views',
        ),
        migrations.RemoveField(
            model_name='course',
            name='tokens',
        ),
    ] 