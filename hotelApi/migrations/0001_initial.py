# Generated by Django 2.0.5 on 2019-04-01 22:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HotelModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hotelName', models.CharField(max_length=100)),
                ('hotelId', models.CharField(max_length=100)),
                ('modelId', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('domain', models.CharField(max_length=100)),
                ('bed', models.CharField(max_length=100)),
                ('breakfast', models.CharField(max_length=150)),
                ('totalPrice', models.FloatField()),
                ('amount', models.FloatField()),
                ('commission', models.FloatField()),
                ('price', models.FloatField()),
                ('roomLeft', models.IntegerField()),
                ('crawler', models.SmallIntegerField(default=0)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='预定时间')),
                ('update', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新时间')),
                ('insertDate', models.DateTimeField(default=django.utils.timezone.now, verbose_name='插入时间')),
                ('platform', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': '酒店',
                'db_table': 'hotel',
            },
        ),
    ]
