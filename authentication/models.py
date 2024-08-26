from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.

class Skill(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class SkillUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'skill')
    def __str__(self):
        return f"{self.user.username} has skill for {self.skill.name}"

class Internship(models.Model):
    name = models.CharField(max_length=100)
    date_start = models.DateField()
    date_end_selection = models.DateField()
    description = models.TextField()
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(blank=True, null=True, default=now)

    def __str__(self):
        return self.name + " от компании: " + self.company.username 

class SkillInternship(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('internship', 'skill')
    def __str__(self):
        return f"{self.internship.name} has skill for {self.skill.name}"
    
class Test(models.Model):
    title = models.CharField(max_length=255)
    internship = models.OneToOneField('Internship', on_delete=models.CASCADE, blank=True, null=True) 

    def __str__(self):
        return self.title

class Question(models.Model):
    MULTIPLE_CHOICE = 'multiple-choice'
    FILE_UPLOAD = 'file-upload'
    QUESTION_TYPE_CHOICES = [
        (MULTIPLE_CHOICE, 'Тест c выбором ответа'),
        (FILE_UPLOAD, 'Задание c отправкой файла'),
    ]

    test = models.ForeignKey('Test', related_name='questions', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default=MULTIPLE_CHOICE)
    text = models.TextField()
    options = models.JSONField(blank=True, null=True) # Используем JSONField для массива опций
    correct_answer = models.PositiveIntegerField(blank=True, null=True) 
    file_type = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_file = models.FileField(upload_to='uploads/questions/', blank=True, null=True)

    def __str__(self):
        return self.text + " с типом " + self.type


class UserTestResult(models.Model):
    status = models.TextField(default='В обработке')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + str(self.test)

class UserTestQuestionResult(models.Model):
    user_test_result = models.ForeignKey(UserTestResult, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer_file = models.FileField(upload_to='uploads/results/', blank=True, null=True)
    user_answer_choice = models.TextField(max_length=255, default='', blank=True, null=False)

    def __str__(self):
        return str(self.user_test_result.user.id) + str(self.question.id) # type: ignore