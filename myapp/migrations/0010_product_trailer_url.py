from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='trailer_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]

