# Generated by Django 4.1.7 on 2023-04-28 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_savedresult_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savedresult',
            name='phone_number',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
