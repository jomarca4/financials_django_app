# Generated by Django 3.2.23 on 2023-11-27 21:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financials', '0005_financialstatementlabel_mapped_label'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='financial_ratios',
            unique_together={('quarter', 'ratio_name')},
        ),
    ]
