# Generated to ensure all certificates models and columns exist in production PostgreSQL and fresh databases

from django.conf import settings
from django.db import migrations


def sync_certificates_schema(apps, schema_editor):
    from django.apps import apps as global_apps
    app_config = global_apps.get_app_config('certificates')
    conn = schema_editor.connection
    existing_tables = set(conn.introspection.table_names())

    for model in app_config.get_models():
        table_name = model._meta.db_table
        if table_name not in existing_tables:
            schema_editor.create_model(model)
            existing_tables.add(table_name)

    for model in app_config.get_models():
        table_name = model._meta.db_table
        with conn.cursor() as cursor:
            existing_columns = {col.name for col in conn.introspection.get_table_description(cursor, table_name)}
        for field in model._meta.local_fields:
            column_name = field.column
            if column_name and column_name not in existing_columns:
                schema_editor.add_field(model, field)
                existing_columns.add(column_name)


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0001_initial'),
        ('courses', '0002_sync_courses_schema'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(
            code=sync_certificates_schema,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
