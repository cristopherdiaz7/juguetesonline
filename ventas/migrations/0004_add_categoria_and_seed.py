from django.db import migrations, models


def create_sample_products(apps, schema_editor):
    Producto = apps.get_model('ventas', 'Producto')
    Usuario = apps.get_model('ventas', 'Usuario')
    # pick an existing usuario to be the seller, or create a fallback
    seller = Usuario.objects.first()
    if not seller:
        seller = Usuario.objects.create(nombre='store', correo='store@local.invalid', contraseña='', direccion='', tipo='vendedor')

    categories = ['figuras', 'peluches', 'posters', 'retro', 'vehiculos']
    created = []
    for cat in categories:
        for i in range(10):
            name = f'{cat.capitalize()} Item {i+1}'
            # avoid duplicates
            if Producto.objects.filter(nombre=name, categoria=cat).exists():
                continue
            p = Producto.objects.create(
                nombre=name,
                precio=1000 + i * 50,
                usuario=seller,
                descripcion=f'Producto de prueba en la categoría {cat}.',
                stock=10,
                categoria=cat,
            )
            created.append(p.id)


def delete_sample_products(apps, schema_editor):
    Producto = apps.get_model('ventas', 'Producto')
    categories = ['figuras', 'peluches', 'posters', 'retro', 'vehiculos']
    for cat in categories:
        for i in range(10):
            name = f'{cat.capitalize()} Item {i+1}'
            Producto.objects.filter(nombre=name, categoria=cat).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0003_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='categoria',
            field=models.CharField(choices=[('figuras', 'Figuras'), ('peluches', 'Peluches'), ('posters', 'Posters'), ('retro', 'Retro'), ('vehiculos', 'Vehículos')], default='figuras', max_length=20),
            preserve_default=False,
        ),
        migrations.RunPython(create_sample_products, reverse_code=delete_sample_products),
    ]
