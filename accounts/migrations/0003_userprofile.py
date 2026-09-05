# Generated manually to safely restore UserProfile schema and migration state

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_userprofile_table(apps, schema_editor):
    from django.apps import apps as global_apps
    UserProfile = global_apps.get_model('accounts', 'UserProfile')
    table_name = UserProfile._meta.db_table
    if table_name not in schema_editor.connection.introspection.table_names():
        schema_editor.create_model(UserProfile)


def drop_userprofile_table(apps, schema_editor):
    from django.apps import apps as global_apps
    UserProfile = global_apps.get_model('accounts', 'UserProfile')
    table_name = UserProfile._meta.db_table
    if table_name in schema_editor.connection.introspection.table_names():
        schema_editor.delete_model(UserProfile)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0002_oauthaccount'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='UserProfile',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('avatar_url', models.URLField(blank=True, max_length=500, null=True)),
                        ('headline', models.CharField(blank=True, max_length=255)),
                        ('bio', models.TextField(blank=True)),
                        ('phone_number', models.CharField(blank=True, max_length=20)),
                        ('target_role', models.CharField(blank=True, max_length=150)),
                        ('interests', models.JSONField(blank=True, default=list)),
                        ('skills', models.JSONField(blank=True, default=list)),
                        ('is_profile_completed', models.BooleanField(default=False)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
                    ],
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    code=create_userprofile_table,
                    reverse_code=drop_userprofile_table,
                ),
            ],
        ),
    ]
