from django.db import migrations

def create_missing_profiles(apps, schema_editor):
    User = apps.get_model("auth", "User")  # or your custom user app if any
    Profile = apps.get_model("profiles", "Profile")
    missing = User.objects.filter(profile__isnull=True).only("id")
    Profile.objects.bulk_create([Profile(user=u) for u in missing])

class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0001_initial"),  # adjust to your initial migration name
    ]

    operations = [
        migrations.RunPython(create_missing_profiles, migrations.RunPython.noop),
    ]