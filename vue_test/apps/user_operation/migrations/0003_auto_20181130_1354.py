# Generated by Django 2.1 on 2018-11-30 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_operation', '0002_auto_20181122_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userleavingmessage',
            name='file',
            field=models.FileField(blank=True, help_text='上传的文件', null=True, upload_to='message/images/', verbose_name='上传的文件'),
        ),
    ]