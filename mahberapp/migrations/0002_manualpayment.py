from django.db import migrations, models
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('mahberapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('reason', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('ethiopian_month', models.IntegerField(
                    blank=True, null=True,
                    choices=[
                        (1, 'Meskerem'), (2, 'Tikimit'), (3, 'Hidar'), (4, 'Tahsas'),
                        (5, 'Tir'), (6, 'Yekatit'), (7, 'Megabit'), (8, 'Miazia'),
                        (9, 'Ginbot'), (10, 'Sene'), (11, 'Hamle'), (12, 'Nehase'), (13, 'Pagume'),
                    ]
                )),
                ('ethiopian_year', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
