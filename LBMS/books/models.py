from django.db import models

# Create your models here.
'''class Books(models.Model):
    isbn = models.CharField(primary_key='True',max_length=15)
    title = models.CharField(max_length=200)

class Authors(models.Model):
    author_id = models.CharField(primary_key='True',max_length=100)
    name = models.CharField(max_length=200)

class BookAuthors(models.Model):
    class Meta:
        unique_together = (('author_id','isbn'))
    author_id = models.ForeignKey(Authors,on_delete=models.CASCADE)
    isbn = models.ForeignKey(Books,on_delete=models.CASCADE)

class Borrowers(models.Model):
    card_id = models.CharField(primary_key=True,max_length=20)
    ssn = models.CharField(max_length=11,unique=True)
    borrower_name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=15)

class BookLoans(models.Model):
    loan_id = models.AutoField(primary_key=True)
    isbn = models.ForeignKey(Books,on_delete=models.CASCADE)
    card_id = models.ForeignKey(Borrowers,on_delete=models.CASCADE)
    date_out = models.DateField()
    due_date = models.DateField()
    date_in = models.DateField(null=True)

class BookAvailability(models.Model):
    id = models.AutoField(primary_key=True)
    isbn = models.ForeignKey(Books,on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    borrowed_by = models.ForeignKey(Borrowers,on_delete=models.CASCADE)

class Fines(models.Model):
    loan_id = models.ForeignKey(BookLoans,on_delete=models.CASCADE)
    fine_amt = models.FloatField(max_length=2)
    paid = models.IntegerField(default=0)'''




