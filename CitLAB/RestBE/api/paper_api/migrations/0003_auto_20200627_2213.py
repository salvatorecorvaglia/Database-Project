# Generated by Django 3.0.6 on 2020-06-27 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper_api', '0002_auto_20200626_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paper',
            name='created_on',
            field=models.CharField(max_length=200, null=True),
        ),
    ]