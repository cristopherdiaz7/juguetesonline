from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0002_pedidoitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('tipo', models.CharField(choices=[('info', 'Info'), ('success', 'Success'), ('warning', 'Warning'), ('danger', 'Danger')], default='info', max_length=20)),
                ('read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='notifications', to='ventas.usuario')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
