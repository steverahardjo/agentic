from django.db import models

# Model 
class User(models.Model):
    userID = models.AutoField(primary_key=True)
    userName = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    signinDate = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    catID=models.CharField(max_length=3)
    catDesc= models.CharField(max_length= 30)

class Expense (models.Model): 
    expID= models.AutoField(primary_key= True)
    userID= models.ForeignKey(Category, on_delete=models.CASCADE)
    inputDate= models.DateTimeField(auto_now_add=True)
    catID = models.ForeignKey(Category, on_delete=models.CASCADE)
    catID= models.CharField(max_length=3)