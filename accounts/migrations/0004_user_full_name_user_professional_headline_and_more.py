# Manually written to avoid SQLite table-remake clash caused by 0003_userprofile.
# Using raw SQL ALTER TABLE + CREATE UNIQUE INDEX so SQLite does not try to
# remake accounts_user (which would conflict with the through-tables already
# created by 0003's RunPython step).

from django.db import migrations, models


def add_columns(apps, schema_editor):
    db = schema_editor.connection.vendor
    cursor = schema_editor.connection.cursor()
    existing = {
        col.name
        for col in schema_editor.connection.introspection.get_table_description(
            cursor, "accounts_user"
        )
    }
    if "full_name" not in existing:
        cursor.execute("ALTER TABLE accounts_user ADD COLUMN full_name VARCHAR(255) NOT NULL DEFAULT ''")
    if "professional_headline" not in existing:
        cursor.execute("ALTER TABLE accounts_user ADD COLUMN professional_headline VARCHAR(255) NOT NULL DEFAULT ''")
    if "username" not in existing:
        cursor.execute("ALTER TABLE accounts_user ADD COLUMN username VARCHAR(150) NULL DEFAULT NULL")
        # Unique index as a separate step (works on SQLite & PostgreSQL)
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS accounts_user_username_uniq "
            "ON accounts_user (username) "
            "WHERE username IS NOT NULL"
        )


def remove_columns(apps, schema_editor):
    # SQLite does not support DROP COLUMN before 3.35 / Django 4.0+; on
    # PostgreSQL we drop normally. For the test runner (SQLite) this is a no-op
    # because the test DB is ephemeral anyway.
    db = schema_editor.connection.vendor
    if db != "sqlite":
        cursor = schema_editor.connection.cursor()
        cursor.execute("DROP INDEX IF EXISTS accounts_user_username_uniq")
        for col in ("username", "professional_headline", "full_name"):
            cursor.execute(f"ALTER TABLE accounts_user DROP COLUMN IF EXISTS {col}")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_userprofile"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="user",
                    name="full_name",
                    field=models.CharField(blank=True, max_length=255),
                ),
                migrations.AddField(
                    model_name="user",
                    name="professional_headline",
                    field=models.CharField(
                        blank=True,
                        help_text="Short professional headline, e.g. 'Senior Android Engineer'.",
                        max_length=255,
                    ),
                ),
                migrations.AddField(
                    model_name="user",
                    name="username",
                    field=models.CharField(
                        blank=True,
                        help_text="Unique public username.",
                        max_length=150,
                        null=True,
                        unique=True,
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(add_columns, reverse_code=remove_columns),
            ],
        ),
    ]
