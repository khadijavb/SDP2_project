from django.db import models
from django.utils import timezone

class Users(models.Model):
	name = models.CharField(max_length=200, null=True)
	phone = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200, null=True)
	date_created = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.name


class SavedResult(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    level = models.IntegerField()
    filename = models.CharField(max_length=255)
    score = models.FloatField()
    name = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Level {self.level}: {self.filename} (Score: {self.score})"

