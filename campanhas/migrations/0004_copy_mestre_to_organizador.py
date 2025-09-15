# Generated manually

from django.db import migrations

def copy_mestre_to_organizador(apps, schema_editor):
    Campanha = apps.get_model('campanhas', 'Campanha')
    for campanha in Campanha.objects.all():
        campanha.organizador = campanha.mestre
        campanha.save()

def reverse_copy(apps, schema_editor):
    Campanha = apps.get_model('campanhas', 'Campanha')
    for campanha in Campanha.objects.all():
        campanha.mestre = campanha.organizador
        campanha.save()

class Migration(migrations.Migration):

    dependencies = [
        ('campanhas', '0003_add_organizador_field'),
    ]

    operations = [
        migrations.RunPython(copy_mestre_to_organizador, reverse_copy),
    ]