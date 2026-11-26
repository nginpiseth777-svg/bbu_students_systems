from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations=[
        migrations.AddField(
            model_name='course',
            name='campus',
            field=models.CharField(
                choices=[('PHNOM_PENH', 'ភ្នំពេញ'), ('SIEM_REAP', 'សៀមរាប')],
                default='PHNOM_PENH',
                max_length=20,
            ),
        ),
    ]
