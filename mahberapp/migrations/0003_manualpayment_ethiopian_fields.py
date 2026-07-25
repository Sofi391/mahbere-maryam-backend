from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mahberapp', '0002_manualpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='manualpayment',
            name='ethiopian_month',
            field=models.IntegerField(
                blank=True, null=True,
                choices=[
                    (1, 'Meskerem'), (2, 'Tikimit'), (3, 'Hidar'), (4, 'Tahsas'),
                    (5, 'Tir'), (6, 'Yekatit'), (7, 'Megabit'), (8, 'Miazia'),
                    (9, 'Ginbot'), (10, 'Sene'), (11, 'Hamle'), (12, 'Nehase'), (13, 'Pagume'),
                ]
            ),
        ),
        migrations.AddField(
            model_name='manualpayment',
            name='ethiopian_year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
