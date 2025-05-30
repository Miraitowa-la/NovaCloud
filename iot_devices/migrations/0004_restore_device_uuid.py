# Generated manually 

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot_devices', '0003_alter_device_device_id_alter_device_device_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='device_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='设备ID'),
        ),
        migrations.AlterField(
            model_name='device',
            name='device_key',
            field=models.CharField(editable=False, max_length=128, verbose_name='设备密钥'),
        ),
    ] 