# Generated by Django 3.1.5 on 2021-06-04 18:01

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Livreur',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('phone', models.CharField(blank=True, max_length=10, validators=[django.core.validators.RegexValidator('^0\\d*$', 'Invalid Phone Format, Use : 0#########'), django.core.validators.MinLengthValidator(10, 'Phone Should be 10 numbers')])),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=1000)),
                ('livreur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='casa.livreur')),
            ],
        ),
        migrations.CreateModel(
            name='Livraison',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site', models.CharField(default='Parapharma', max_length=100)),
                ('phone', models.CharField(max_length=20, validators=[django.core.validators.MinLengthValidator(10, 'Phone Should be minimum numbers')])),
                ('montant_DH', models.IntegerField()),
                ('commentaire', models.CharField(blank=True, max_length=1000)),
                ('created', models.CharField(blank=True, default=datetime.date(2021, 6, 4), max_length=100, null=True)),
                ('status', models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='casa.status')),
                ('zone', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='casa.zone')),
            ],
        ),
    ]