from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_alter_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentitem',
            name='url',
            field=models.URLField(
                blank=True,
                help_text='Playback URL returned to Android (Cloudflare R2 public URL or sample MP4).',
                max_length=1000,
            ),
        ),
        migrations.AddField(
            model_name='contentitem',
            name='storage_key',
            field=models.CharField(
                blank=True,
                help_text='Cloudflare R2 object key, e.g. videos/python/welcome.mp4',
                max_length=500,
            ),
        ),
    ]
