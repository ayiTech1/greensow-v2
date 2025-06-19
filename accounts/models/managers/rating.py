from django.db import models

class RatingManager(models.Manager):
    def rate_employee(self, rater, employee, score, comment=""):
        return self.create(rater=rater, employee=employee, score=score, comment=comment)

    def rate_employer(self, rater, employer, score, comment=""):
        return self.create(rater=rater, employer=employer, score=score, comment=comment)
