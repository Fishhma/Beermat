from django.contrib.auth import get_user_model
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class NewsItem(models.Model):
    title = models.CharField(max_length=150)
    body = models.TextField(max_length=150, blank=True)
    published = models.BooleanField(default=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        from django.utils import timezone

# костыль для галочки. 
        if self.published is None:
            self.published = False
        
        if self.published and not self.published_at:
            self.published_at = timezone.now()
        elif not self.published:
            self.published_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Beermat(models.Model):
    name = models.CharField(max_length=120, help_text="Coaster name")
    beer_name = models.CharField(max_length=120, blank=True, help_text="Beer name / brand")
    brewery = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=80, blank=True, help_text='Country of origin')
    style = models.CharField(max_length=120, blank=True)

    photo_front = models.ImageField(upload_to='beermats/originals/', blank=True, null=True)
    photo_back = models.ImageField(upload_to='beermats/originals/', blank=True, null=True)

    photo_front_thumb = models.ImageField(upload_to='beermats/thumbs/', blank=True, null=True)
    photo_back_thumb = models.ImageField(upload_to='beermats/thumbs/', blank=True, null=True)

    diameter_mm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    weight_g = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    thickness_mm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    description = models.TextField(blank=True)
    approved = models.BooleanField(default=False, help_text="Approve to show in public catalog")
    approved_at = models.DateTimeField(blank=True, null=True, help_text="When the beermat was approved")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Ensure approved_at is set when approving, cleared when unapproving.
        if self.approved and not self.approved_at:
            from django.utils import timezone
            self.approved_at = timezone.now()
        if not self.approved:
            self.approved_at = None

        # Generate thumbnail versions (200x200) without modifying original image
        super().save(*args, **kwargs)
        self._create_thumbnails()

    def _create_thumbnails(self):
        """Create thumbnail images for front/back if originals exist."""
        from io import BytesIO
        from PIL import Image
        from django.core.files.base import ContentFile

        def make_thumb(source_field, thumb_field):
            source = getattr(self, source_field)
            if not source:
                return

            # Skip regeneration if thumbnail already exists and source hasn't changed
            thumb = getattr(self, thumb_field)
            if thumb and thumb.name and source.name in thumb.name:
                return

            try:
                img = Image.open(source)
            except Exception:
                return

            # Preserve original format where possible (JPEG/PNG)
            original_format = (img.format or '').upper()
            if original_format not in ('JPEG', 'PNG'):
                original_format = 'JPEG'

            if original_format == 'PNG':
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')

            img.thumbnail((200, 200), Image.Resampling.LANCZOS)

            buffer = BytesIO()
            img.save(buffer, format=original_format, quality=85)
            buffer.seek(0)

            ext = 'png' if original_format == 'PNG' else 'jpg'
            thumb_name = f"{source.name.rsplit('.', 1)[0]}_thumb.{ext}"
            getattr(self, thumb_field).save(thumb_name, ContentFile(buffer.read()), save=False)

        make_thumb('photo_front', 'photo_front_thumb')
        make_thumb('photo_back', 'photo_back_thumb')
        super().save(update_fields=['photo_front_thumb', 'photo_back_thumb'])

    def __str__(self):
        display = self.name
        if self.beer_name:
            display = f"{self.name} ({self.beer_name})"
        return display


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class CollectionItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collection_items')
    beermat = models.ForeignKey(Beermat, on_delete=models.CASCADE, related_name='collected_by')
    note = models.CharField(max_length=255, blank=True)
    acquired_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'beermat')
        ordering = ['-acquired_at']

    def __str__(self):
        return f"{self.user.username} -> {self.beermat.name}"
