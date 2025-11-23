from django.contrib import admin

from school.models import Grade, Classe

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["id", "student_fullname", "ball", "date"]
    search_fields = [
        "student__username",
        "student__first_name",
        "student__last_name",
        "ball"
    ]
    ordering = ["-ball"]  # ball bo‘yicha kamayish tartibi
    list_filter = ["date", "ball"]

    def student_fullname(self, obj):
        if obj.student:
            return f"{obj.student.first_name} {obj.student.last_name}"
        return "No student"
    
    student_fullname.short_description = "Student"
admin.site.register(Classe)