# Manually written so SQLite and PostgreSQL both ADD COLUMN without remaking tables.

from django.db import migrations, models


def add_preference_columns(apps, schema_editor):
    db = schema_editor.connection.vendor
    cursor = schema_editor.connection.cursor()
    existing = {
        col.name
        for col in schema_editor.connection.introspection.get_table_description(
            cursor, "accounts_userprofile"
        )
    }
    notifications_sql = (
        "INTEGER NOT NULL DEFAULT 1"
        if db == "sqlite"
        else "BOOLEAN NOT NULL DEFAULT TRUE"
    )
    columns = (
        ("language", "VARCHAR(10) NOT NULL DEFAULT 'en'"),
        ("notifications_enabled", notifications_sql),
        ("timezone", "VARCHAR(64) NOT NULL DEFAULT 'Asia/Kolkata'"),
    )
    for column_name, column_sql in columns:
        if column_name not in existing:
            cursor.execute(
                f"ALTER TABLE accounts_userprofile ADD COLUMN {column_name} {column_sql}"
            )


def remove_preference_columns(apps, schema_editor):
    db = schema_editor.connection.vendor
    if db == "sqlite":
        return
    cursor = schema_editor.connection.cursor()
    for column_name in ("timezone", "notifications_enabled", "language"):
        cursor.execute(
            f"ALTER TABLE accounts_userprofile DROP COLUMN IF EXISTS {column_name}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_userprofile_education_and_contact"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="userprofile",
                    name="language",
                    field=models.CharField(
                        default="en",
                        help_text='BCP 47 language code, e.g. "en" or "hi".',
                        max_length=10,
                    ),
                ),
                migrations.AddField(
                    model_name="userprofile",
                    name="notifications_enabled",
                    field=models.BooleanField(default=True),
                ),
                migrations.AddField(
                    model_name="userprofile",
                    name="timezone",
                    field=models.CharField(
                        default="Asia/Kolkata",
                        help_text='IANA timezone identifier, e.g. "Asia/Kolkata".',
                        max_length=64,
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    add_preference_columns,
                    reverse_code=remove_preference_columns,
                ),
            ],
        ),
    ]
