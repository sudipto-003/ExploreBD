# Generated by Django 2.2.2 on 2019-11-17 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exploreuser', '0004_auto_20190929_0851'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='follow',
            field=models.ManyToManyField(related_name='follows', to='exploreuser.Profile'),
        ),
    ]
