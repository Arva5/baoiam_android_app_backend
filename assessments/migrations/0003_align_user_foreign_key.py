from django.conf import settings
from django.db import migrations


def align_user_foreign_key(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != 'postgresql':
        return

    table_name = 'assessments_userassessmentattempt'
    user_table = 'accounts_user'
    constraints = connection.introspection.get_constraints(
        connection.cursor(),
        table_name,
    )

    for constraint_name, constraint in constraints.items():
        foreign_key = constraint.get('foreign_key')
        if (
            constraint.get('columns') == ['user_id']
            and foreign_key
            and foreign_key[0] == 'users_user'
        ):
            quoted_table = schema_editor.quote_name(table_name)
            quoted_constraint = schema_editor.quote_name(constraint_name)
            quoted_user_table = schema_editor.quote_name(user_table)
            schema_editor.execute(
                f'ALTER TABLE {quoted_table} DROP CONSTRAINT {quoted_constraint}'
            )
            schema_editor.execute(
                f'ALTER TABLE {quoted_table} '
                f'ADD CONSTRAINT {quoted_constraint} '
                f'FOREIGN KEY (user_id) REFERENCES {quoted_user_table} (id) '
                'ON DELETE CASCADE'
            )


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0002_sync_assessments_schema'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(align_user_foreign_key, migrations.RunPython.noop),
    ]