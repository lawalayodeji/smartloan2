# Generated by Django 4.2.5 on 2023-09-21 22:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("siteuser", "0002_loancategory_loanrequest_customerloan"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customerloan",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="loan_user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="loanrequest",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="loan_customer",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]