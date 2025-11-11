from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0005_alter_producto_categoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(upload_to='productos/', null=True, blank=True),
        ),
    ]
