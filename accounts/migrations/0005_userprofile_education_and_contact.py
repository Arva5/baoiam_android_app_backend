# Manually written so SQLite and PostgreSQL both ADD COLUMN without remaking tables.

from django.db import migrations, models


NEW_COLUMNS = (
    ("highest_qualification", "VARCHAR(150) NOT NULL DEFAULT ''"),
    ("institution", "VARCHAR(255) NOT NULL DEFAULT ''"),
    ("field_of_study", "VARCHAR(255) NOT NULL DEFAULT ''"),
    ("linkedin_url", "VARCHAR(200) NOT NULL DEFAULT ''"),
    ("github_url", "VARCHAR(200) NOT NULL DEFAULT ''"),
    ("website_url", "VARCHAR(200) NOT NULL DEFAULT ''"),
)


def add_profile_columns(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    existing = {
        col.name
        for col in schema_editor.connection.introspection.get_table_description(
            cursor, "accounts_userprofile"
        )
    }
    for column_name, column_sql in NEW_COLUMNS:
        if column_name not in existing:
            cursor.execute(
                f"ALTER TABLE accounts_userprofile ADD COLUMN {column_name} {column_sql}"
            )


def remove_profile_columns(apps, schema_editor):
    db = schema_editor.connection.vendor
    if db == "sqlite":
        return
    cursor = schema_editor.connection.cursor()
    for column_name, _ in reversed(NEW_COLUMNS):
        cursor.execute(
            f"ALTER TABLE accounts_userprofile DROP COLUMN IF EXISTS {column_name}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_user_full_name_user_professional_headline_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="userprofile",
                    name="highest_qualification",
                    field=models.CharField(blank=True, max_length=150),
                ),
                migrations.AddField(
                    model_name="userprofile",
                    name="institution",
                    field=models.CharField(blank=True, max_length=255),
                ),
                migrations.AddField(
                    model_name="userprofile",
                    name="field_of_study",
                    field=models.CharField(blank=True, max_length=255),
                ),
                migrations.AddField(
                    model_name="userprofile",
                    name="linkedin_url",
                    field=models.URLField(blank=True),
                ),
                migrations.AddField(
                    model_name="userprofile",
                    name="github_url",
                    field=models.URLField(blank=True),
                ),
                migrations.AddField(
                    model_name="userprofile",
                    name="website_url",
                    field=models.URLField(blank=True),
                ),
            ],
            database_operations=[
                migrations.RunPython(add_profile_columns, reverse_code=remove_profile_columns),
            ],
        ),
    ]
