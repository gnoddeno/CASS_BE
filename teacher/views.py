from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from accounts.models import Teacher, Student
from .models import Problem, Matching
from django.shortcuts import get_object_or_404


class TeacherInfo(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *arg, **kwargs):
        teacher = get_object_or_404(Teacher, user=request.user)

        pending = Matching.objects.filter(teacher=teacher, status="pending")
        pending_students = [matching.student for matching in pending]
        pending_students_data = [
            {"username": student.user.username, "name": student.user.name}
            for student in pending_students
        ]

        matched = Matching.objects.filter(teacher=teacher, status="matching")
        matched_students = [matching.student for matching in matched]
        matched_students_data = [
            {"username": student.user.username, "name": student.user.name}
            for student in matched_students
        ]

        problems = Problem.objects.filter(teacher=teacher)
        problem_urls = [
            {
                "id": problem.id,
                "url": problem.url,
            }
            for problem in problems
        ]

        return Response(
            {
                "pending_students": pending_students_data,
                "matching_students": matched_students_data,
                "problems": problem_urls,
            }
        )


class MatchingAccept(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id, *args, **kwargs):
        teacher = get_object_or_404(Teacher, user=request.user)
        student = get_object_or_404(Student, user__username=student_id)

        matching = Matching.objects.get(
            teacher=teacher, student=student, status="pending"
        )

        if matching.status != "pending":
            return Response(
                {
                    "success": 0,
                    "msg": "요청실패 - 완료된 요청",
                },
                status=400,
            )
        else:
            student.matched = True
            matching.status = "matching"
            matching.save()
            return Response(
                {
                    "status": 1,
                    "msg": "요청성공",
                },
                status=200,
            )


class MatchingReject(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, student_id, *args, **kwargs):
        teacher = get_object_or_404(Teacher, user=request.user)
        student = get_object_or_404(Student, user__username=student_id)

        matching = Matching.objects.filter(teacher=teacher, student=student)
        if not matching.exists():
            return Response(
                {
                    "success": 0,
                    "msg": "삭제실패 - 매칭 정보가 없습니다.",
                },
                status=404,
            )

        matching.delete()
        return Response(
            {
                "status": 1,
                "msg": "삭제성공",
            },
            status=200,
        )


class DeleteStudent(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, student_id, *args, **kwargs):
        teacher = get_object_or_404(Teacher, user=request.user)
        student = get_object_or_404(Student, user__username=student_id)

        matching = Matching.objects.filter(
            teacher=teacher, student=student, status="matching"
        )
        if not matching.exists():
            return Response(
                {
                    "success": 0,
                    "msg": "삭제실패 - 매칭 정보가 없습니다.",
                },
                status=404,
            )

        matching.delete()
        return Response(
            {
                "status": 1,
                "msg": "삭제성공",
            },
            status=200,
        )


class AddProblem(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        teacher = get_object_or_404(Teacher, user=request.user)
        url = request.data.get("url")

        Problem.objects.create(teacher=teacher, url=url)

        problems = Problem.objects.filter(teacher=teacher)
        problem_urls = [
            {
                "id": problem.id,
                "url": problem.url,
            }
            for problem in problems
        ]

        return Response(
            {
                "success": 1,
                "msg": "문제 추가 성공",
            },
            status=200,
        )


class DeleteProblem(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        problem_id = request.data.get("id")

        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response(
                {
                    "success": 0,
                    "msg": "삭제실패 - 존재하지 않는 문제",
                },
                status=404,
            )

        problem.delete()
        return Response(
            {
                "success": 1,
                "msg": "삭제성공",
            },
            status=200,
        )


class SubmitCheck(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, problem_id, *args, **kwargs):
        teacher = get_object_or_404(Teacher, user=request.user)
        problem = get_object_or_404(Problem, id=problem_id, teacher=teacher)

        return Response(
            {
                "teacher": teacher.user.name,
                "problem": problem.id,
            }
        )
