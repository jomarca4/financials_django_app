# Generated by Django 3.2.23 on 2023-11-26 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financials', '0002_auto_20231126_2049'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='analyst_estimates',
            table='analyst_estimates',
        ),
        migrations.AlterModelTable(
            name='companies',
            table='companies',
        ),
        migrations.AlterModelTable(
            name='financial_ratios',
            table='financial_ratios',
        ),
        migrations.AlterModelTable(
            name='financial_statement_items',
            table='financial_statement_items',
        ),
        migrations.AlterModelTable(
            name='financial_statements',
            table='financial_statements',
        ),
        migrations.AlterModelTable(
            name='market_data',
            table='market_data',
        ),
        migrations.AlterModelTable(
            name='quarters',
            table='quarters',
        ),
    ]
