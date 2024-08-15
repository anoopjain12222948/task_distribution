from django.db import models
import enum
from datetime import date
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


@enum.unique
class ProjectStatus(str, enum.Enum):
    CREATED = 'CREATED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


@enum.unique
class TaskStatus(str, enum.Enum):
    CREATED = 'CREATED'
    ALLOCATED = 'ALLOCATED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


@enum.unique
class Priority(str, enum.Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class Project(models.Model):
    title = models.CharField(max_length=200, unique=True)
    status = models.CharField(choices=ProjectStatus.choices(), max_length=200, default=ProjectStatus.CREATED)
    description = models.TextField()
    start_date = models.DateField(_('start_date'))
    end_date = models.DateField(_('end_date'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self, *args, **kwargs):
        if self.start_date < date.today():
            raise ValidationError("The date cannot be in the past!")
        if self.start_date > self.end_date:
            raise ValidationError("start_date cannot be greater than end_date!")
        super(Project, self).clean(*args, **kwargs)

    def __str__(self):
        return self.title


class Resource(models.Model):
    name = models.CharField(max_length=200)
    busy_days_count = models.PositiveIntegerField(default=0)
    skills = ArrayField(models.CharField(max_length=200), help_text='Enter skills separated with commas')

    # email_id = models.EmailField(max_length=255,blank=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    # STATUS_CHOICES = [
    #     ('to_do', 'To Do'),
    #     ('in_progress', 'In Progress'),
    #     ('completed', 'Completed'),
    # ]
    #
    # PRIORITY_CHOICES = [
    #     ('low', 'Low'),
    #     ('medium', 'Medium'),
    #     ('high', 'High'),
    # ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    start_date = models.DateField(_('start_date'))
    end_date = models.DateField(_('end_date'))
    skill_required = ArrayField(models.CharField(max_length=200), help_text='Enter skills separated with commas', )
    resource = models.ForeignKey(Resource, on_delete=models.PROTECT, blank=True, null=True)
    status = models.CharField(choices=TaskStatus.choices(), max_length=200, default=TaskStatus.CREATED)
    priority = models.CharField(choices=Priority.choices(), max_length=200, default=Priority.LOW)
    due_date = models.DateField()
    # users = models.ManyToManyField(User, through='TaskAssignment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('title', 'project')

    def clean(self, *args, **kwargs):
        if self.start_date < date.today():
            raise ValidationError("The date cannot be in the past!")
        if self.start_date > self.end_date:
            raise ValidationError("start_date cannot be greater than end_date!")
        super(Task, self).clean(*args, **kwargs)

    def __str__(self):
        return self.project.title + " - " + self.title


class TaskResourceMapping(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.PROTECT, related_name='resource')
    start_date = models.DateField(_('start_date'))
    end_date = models.DateField(_('end_date'))
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'task', 'resource')
