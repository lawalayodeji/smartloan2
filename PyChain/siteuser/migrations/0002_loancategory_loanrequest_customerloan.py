# Generated by Django 4.2.5 on 2023-09-21 20:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("siteuser", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="loanCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("loan_name", models.CharField(max_length=250)),
                ("creation_date", models.DateField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="loanRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("request_date", models.DateField(auto_now_add=True)),
                (
                    "status_date",
                    models.CharField(
                        blank=True, default=None, max_length=150, null=True
                    ),
                ),
                ("reason", models.TextField()),
                ("status", models.CharField(default="pending", max_length=100)),
                ("amount", models.PositiveIntegerField(default=0)),
                ("year", models.PositiveIntegerField(default=1)),
                (
                    "category",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="siteuser.loancategory",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="loan_customer",
                        to="siteuser.siteuser",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CustomerLoan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_loan", models.PositiveIntegerField(default=0)),
                ("payable_loan", models.PositiveIntegerField(default=0)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="loan_user",
                        to="siteuser.siteuser",
                    ),
                ),
            ],
        ),
    ]
