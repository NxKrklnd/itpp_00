from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.validators import RegexValidator

class TrainerRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
        )]
    )
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

    class Meta:
        verbose_name = 'Trainer Registration'
        verbose_name_plural = 'Trainer Registrations'

class CourseInfo(models.Model):
    CATEGORY_CHOICES = [
        ('programming', 'Programming'),
        ('design', 'Design'),
        ('business', 'Business'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]

    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    course_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.course_name

    class Meta:
        verbose_name = 'Course Information'
        verbose_name_plural = 'Course Information'
        ordering = ['-created_at']

class CourseDetails(models.Model):
    course = models.OneToOneField(CourseInfo, on_delete=models.CASCADE, related_name='details')
    description = models.TextField(help_text='Detailed description of the course')
    course_image = models.ImageField(
        upload_to='course_images/',
        help_text='Upload a course cover image'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.course_name} - Details"

    class Meta:
        verbose_name = 'Course Detail'
        verbose_name_plural = 'Course Details'

@receiver(pre_save, sender=CourseInfo)
def course_slug_generation(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.course_name)
        # Handle duplicate slugs
        original_slug = instance.slug
        counter = 1
        while CourseInfo.objects.filter(slug=instance.slug).exists():
            instance.slug = f"{original_slug}-{counter}"
            counter += 1
