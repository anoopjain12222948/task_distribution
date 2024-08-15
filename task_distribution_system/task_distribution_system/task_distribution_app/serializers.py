from rest_framework import serializers
from .models import Project, Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'start_date', 'end_date', 'skill_required', 'priority', 'due_date']


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)

    class Meta:
        model = Project
        fields = ['title', 'status', 'description', 'start_date', 'end_date', 'tasks']


class ProjectsSerializer(serializers.Serializer):
    projects = ProjectSerializer(many=True)

    # class Meta:
    #     #     model = Project
    #     fields = ['projects']

    # def create(self, validated_data):
    #     tasks_data = validated_data.pop('tasks')
    #     project = Project.objects.create(**validated_data)
    #     for task_data in tasks_data:
    #         Task.objects.create(project=project, **task_data)
    #     return project
