# Generated by Django 4.1.4 on 2023-01-31 02:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bacterial_genome_annotation', '0007_remove_comment_isanswer_remove_comment_question_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
