# Manually written so SQLite and PostgreSQL both ADD COLUMN without remaking tables.

from django.db import migrations, models


def add_twitter_url_column(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    existing = {
        col.name
        for col in schema_editor.connection.introspection.get_table_description(
            cursor, "accounts_userprofile"
        )
    }
    if "twitter_url" not in existing:
        cursor.execute(
            "ALTER TABLE accounts_userprofile"
            " ADD COLUMN twitter_url VARCHAR(200) NOT NULL DEFAULT ''"
        )


def remove_twitter_url_column(apps, schema_editor):
    db = schema_editor.connection.vendor
    if db == "sqlite":
        return
    cursor = schema_editor.connection.cursor()
    cursor.execute(
        "ALTER TABLE accounts_userprofile DROP COLUMN IF EXISTS twitter_url"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_userprofile_preferences"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="userprofile",
                    name="twitter_url",
                    field=models.URLField(blank=True),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    add_twitter_url_column,
                    reverse_code=remove_twitter_url_column,
                ),
            ],
        ),
    ]
