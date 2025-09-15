# Generated manually

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('campanhas', '0004_copy_mestre_to_organizador'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='campanha',
            name='organizador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campanhas_organizadas', to=settings.AUTH_USER_MODEL, verbose_name='Organizador'),
        ),
        migrations.RemoveField(
            model_name='campanha',
            name='mestre',
        ),
    ]