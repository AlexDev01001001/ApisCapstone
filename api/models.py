# api/models.py
from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'users'
        managed = False

class CustomUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    # agrega más campos si los necesitas; no es obligatorio para el FK

    class Meta:
        db_table = 'usuarios_customuser'
        managed = False

class Event(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"
    STATUS_DRAFT = "draft"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_DRAFT, "Draft"),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    organizer_id = models.IntegerField()
    venue_id = models.IntegerField()

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)


    organizer_user = models.ForeignKey(
        CustomUser,
        db_column="organizer_user_id",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="organized_events",
        db_constraint=False,
    )

    description = models.TextField(null=True, blank=True)
    image_url = models.CharField(max_length=512, null=True, blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "events"
        managed = False

    def __str__(self):
        return f"[{self.id}] {self.title}"
