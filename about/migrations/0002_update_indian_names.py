from django.db import migrations


def update_to_indian_names(apps, schema_editor):
    SuccessStory = apps.get_model('about', 'SuccessStory')
    TeamMember = apps.get_model('about', 'TeamMember')

    # Update Success Stories to Indian names
    SuccessStory.objects.filter(name="Peter Jones").update(name="Aarav Sharma")
    SuccessStory.objects.filter(name="Mia Morris").update(name="Priya Patel")

    # Update Team Members to Indian names
    TeamMember.objects.filter(name="James Perkins").update(name="Vikram Sharma")
    TeamMember.objects.filter(name="Emma Wilson").update(name="Dr. Neha Verma")


def rollback_indian_names(apps, schema_editor):
    SuccessStory = apps.get_model('about', 'SuccessStory')
    TeamMember = apps.get_model('about', 'TeamMember')

    SuccessStory.objects.filter(name="Aarav Sharma").update(name="Peter Jones")
    SuccessStory.objects.filter(name="Priya Patel").update(name="Mia Morris")

    TeamMember.objects.filter(name="Vikram Sharma").update(name="James Perkins")
    TeamMember.objects.filter(name="Dr. Neha Verma").update(name="Emma Wilson")


class Migration(migrations.Migration):

    dependencies = [
        ('about', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_to_indian_names, rollback_indian_names),
    ]
