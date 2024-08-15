from django.db import IntegrityError
from .serializers import ProjectsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import namedtuple
from .models import Task, Resource, TaskResourceMapping, Project
import json
from django.db import transaction
from task_distribution_system.services.logging_services import logging_services
import traceback


# log_data = {
#     "entity": "classname",
#     "entity_id": "classname",
#     "method": "classname+methodname",
#     "errors": str("traceback.format_exc()")
# }
# logging_services.log(log_type='error', data=log_data)


class AssignTaskAPI(APIView):

    def get_all_skill_matching_resources(self, task):
        return Resource.objects.filter(skills__contains=task.skill_required).order_by('busy_days_count')

    def update_task_and_mapping(self, task, resource):
        TaskResourceMapping.objects.create(
            task=task, project=task.project, resource=resource,
            start_date=task.start_date, end_date=task.end_date
        )
        task.resource = resource
        task.status = 'ALLOCATED'
        task.save()
        resource.busy_days_count += (task.end_date - task.start_date).days + 1
        resource.save()

    def get_matching_resource(self, task, resources):
        for resource in resources:
            overlapping_tasks = resource.resource.filter(
                start_date__lt=task.end_date, end_date__gt=task.start_date
            )
            if not overlapping_tasks.exists():
                self.update_task_and_mapping(task, resource)
                return resource
        return None

    def assign_tasks_to_resources(self, project):
        tasks = Task.objects.filter(project=project, status='CREATED').order_by('-priority')

        for task in tasks:
            resources = self.get_all_skill_matching_resources(task)
            if resources.exists():
                matching_resource = self.get_matching_resource(task, resources)
                if not matching_resource:
                    return f"All resources with skills {task.skill_required} are busy.", False
            else:
                return f"No resource exists with skills {task.skill_required}", False
        return "All tasks have been successfully assigned.", True

    def put(self, request):
        try:
            payload = request.data
            project_title = payload.get("project")
            if not project_title:
                log_data = {
                    "entity": "AssignTaskAPI",
                    "entity_id": None,
                    "method": "AssignTaskAPI.put",
                    "errors": "Project title is missing in the request payload."
                }
                logging_services.log(log_type='error', data=log_data)
                raise ValueError("Project title is missing in the request payload.")

            project = Project.objects.filter(title=project_title).first()
            if not project:
                log_data = {
                    "entity": "AssignTaskAPI",
                    "entity_id": None,
                    "method": "AssignTaskAPI.put",
                    "errors": f"Project with title {project_title} does not exist."
                }
                logging_services.log(log_type='error', data=log_data)
                raise ValueError(f"Project with title {project_title} does not exist.")

            status = "FAIL"
            status_code = 400
            details = ""

            with transaction.atomic():
                details, success = self.assign_tasks_to_resources(project)
                if success:
                    status = "OK"
                    status_code = 200

            resp_payload = {"status": status, "details": details}
            return Response(resp_payload, status=status_code)

        except ValueError as ve:
            log_data = {
                "entity": "AssignTaskAPI",
                "entity_id": None,
                "method": "AssignTaskAPI.put",
                "errors": str(traceback.format_exc())
            }
            logging_services.log(log_type='error', data=log_data)
            return Response({"message": str(ve), "success": False}, status=400)
        except Exception as e:
            log_data = {
                "entity": "AssignTaskAPI",
                "entity_id": None,
                "method": "AssignTaskAPI.put",
                "errors": str(traceback.format_exc())
            }
            logging_services.log(log_type='error', data=log_data)
            return Response({"message": "Internal server error", "success": False}, status=500)


class CreateProjectTaskAPI(APIView):

    def post(self, request, *args, **kwargs):
        try:
            payload = request.data
            serializer = ProjectsSerializer(data=payload)
            if serializer.is_valid():
                project_data = payload.get('projects', [])

                if not project_data:
                    log_data = {
                        "entity": "CreateProjectTaskAPI",
                        "entity_id": None,
                        "method": "CreateProjectTaskAPI.post",
                        "errors": "No project data provided."
                    }
                    logging_services.log(log_type='error', data=log_data)
                    return Response({"error": "No project data provided."}, status=400)

                with transaction.atomic():
                    created_projects = []
                    created_tasks = []

                    all_projects = Project.objects.all()
                    all_tasks = Task.objects.all()
                    for project in project_data:
                        title = project.get('title')
                        start_date = project.get('start_date')
                        end_date = project.get('end_date')
                        description = project.get('description')
                        tasks = project.get('tasks', [])

                        if all_projects.filter(title=title).exists():
                            log_data = {
                                "entity": "CreateProjectTaskAPI",
                                "entity_id": None,
                                "method": "CreateProjectTaskAPI.post",
                                "errors": f"Project '{title}' already exists."
                            }
                            logging_services.log(log_type='error', data=log_data)
                            raise IntegrityError(f"Project '{title}' already exists.")

                        new_project = Project(title=title, start_date=start_date, end_date=end_date,
                                              description=description)
                        created_projects.append(new_project)

                        for task in tasks:
                            task_title = task.get('title')
                            task_description = task.get('description')
                            task_start_date = task.get('start_date')
                            task_end_date = task.get('end_date')
                            skill_required = task.get('skill_required', [])
                            priority = task.get('priority')
                            status = task.get('status')
                            due_date = task.get('due_date')

                            if all_tasks.filter(title=task_title, project__title=title).exists():
                                log_data = {
                                    "entity": "CreateProjectTaskAPI",
                                    "entity_id": None,
                                    "method": "CreateProjectTaskAPI.post",
                                    "errors": f"Task '{task_title}' already exists in project '{title}'."
                                }
                                logging_services.log(log_type='error', data=log_data)
                                raise IntegrityError(f"Task '{task_title}' already exists in project '{title}'.")

                            new_task = Task(
                                title=task_title, description=task_description,
                                start_date=task_start_date, end_date=task_end_date,
                                skill_required=skill_required, project=new_project,
                                priority=priority, status=status, due_date=due_date
                            )
                            created_tasks.append(new_task)

                    Project.objects.bulk_create(created_projects)
                    Task.objects.bulk_create(created_tasks)

                return Response({"message": "Projects and tasks created successfully."}, status=201)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            log_data = {
                "entity": "CreateProjectTaskAPI",
                "entity_id": None,
                "method": "CreateProjectTaskAPI.post",
                "errors": str(traceback.format_exc())
            }
            logging_services.log(log_type='error', data=log_data)
            return Response({"message": str(e), "success": False}, status=400)

        except Exception as e:
            log_data = {
                "entity": "CreateProjectTaskAPI",
                "entity_id": None,
                "method": "CreateProjectTaskAPI.post",
                "errors": str(traceback.format_exc())
            }
            logging_services.log(log_type='error', data=log_data)
            return Response({"message": "Internal server error", "success": False}, status=500)


class GetTasks(APIView):

    def calculate_project_completion(self, project, all_tasks):
        priority_weights = {
            'HIGH': 5,
            'MEDIUM': 4,
            'LOW': 3
        }

        completed_tasks = all_tasks.filter(project=project, status='COMPLETED')
        total_completed_weight = sum(
            priority_weights[task.priority] for task in completed_tasks
        )

        total_possible_weight = sum(
            priority_weights[task.priority] for task in Task.objects.filter(project=project)
        )

        if total_possible_weight > 0:
            completion_percentage = (total_completed_weight / total_possible_weight) * 100
        else:
            completion_percentage = 0

        return round(completion_percentage, 2)

    def get(self, request):
        try:
            all_projects = Project.objects.all()
            project_completion_data = []
            all_tasks = Task.objects.all()
            for project in all_projects:
                completion_percentage = self.calculate_project_completion(project, all_tasks)
                project_completion_data.append({
                    'project_title': project.title,
                    'completion_percentage': completion_percentage
                })

            all_tasks = list(
                Task.objects.values('title', 'project__title', 'status', 'skill_required', 'start_date', 'end_date',
                                    'priority'))

            resp_payload = {
                'status': 'OK',
                'project_completion': project_completion_data,
                'all_tasks': all_tasks
            }
            return Response(resp_payload, status=200)

        except Exception as e:
            # traceback.print_exc()
            log_data = {
                "entity": "GetTasks",
                "entity_id": None,
                "method": "GetTasks.get",
                "errors": str(traceback.format_exc())
            }
            logging_services.log(log_type='error', data=log_data)
            return Response({"message": "Internal server error", "success": False}, status=500)


class UpdateTaskStatusAPI(APIView):
    def validate_status_transition(self, current_status, new_status):
        status_order = {
            'CREATED': 0,
            'ALLOCATED': 1,
            'IN_PROGRESS': 2,
            'COMPLETED': 3
        }

        return status_order[current_status] < status_order[new_status]

    def put(self, request, *args, **kwargs):
        try:
            payload = request.data
            status = "FAIL"
            status_code = 400
            details = ""

            tasks_to_update = payload.get("tasks", [])

            if not tasks_to_update:
                log_data = {
                    "entity": "UpdateTaskStatusAPI",
                    "entity_id": None,
                    "method": "UpdateTaskStatusAPI.put",
                    "errors": "No tasks provided in the payload."
                }
                logging_services.log(log_type='error', data=log_data)
                details = "No tasks provided in the payload."
                resp_payload = {"status": status, "details": details}
                return Response(resp_payload, status=status_code)

            updated_tasks = []
            invalid_tasks = []
            non_existent_tasks = []
            all_tasks = Task.objects.all()

            for task_data in tasks_to_update:
                project_title = task_data.get("project")
                task_title = task_data.get("task")
                new_status = task_data.get("status")

                if not project_title or not task_title or not new_status:
                    invalid_tasks.append({"project": project_title, "task": task_title})
                    continue

                task = all_tasks.filter(project__title=project_title, title=task_title).first()

                if not task:
                    non_existent_tasks.append({"project": project_title, "task": task_title})
                    continue

                if self.validate_status_transition(task.status, new_status):
                    task.status = new_status
                    task.save()
                    updated_tasks.append({"project": project_title, "task": task_title, "new_status": new_status})
                else:
                    invalid_tasks.append({"project": project_title, "task": task_title})

            if updated_tasks:
                status = "OK"
                status_code = 200
                details = "Successfully updated tasks: {}".format(updated_tasks)

            if invalid_tasks:
                details += " Invalid status transitions for tasks: {}".format(invalid_tasks)

            if non_existent_tasks:
                details += " Tasks that do not exist: {}".format(non_existent_tasks)

            resp_payload = {"status": status, "details": details}
            return Response(resp_payload, status=status_code)

        except Exception as e:
            log_data = {
                "entity": "UpdateTaskStatusAPI",
                "entity_id": None,
                "method": "UpdateTaskStatusAPI.put",
                "errors": str(traceback.format_exc())
            }
            logging_services.log(log_type='error', data=log_data)
            return Response({"message": "Internal server error", "success": False}, status=500)
