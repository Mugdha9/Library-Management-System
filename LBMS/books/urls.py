from django.urls import path
from . import views


urlpatterns = [
    path('',views.searchBooks,name='searchBooks'),
    path('list',views.listBooks,name='listBooks'),
    path('addBorrowers',views.addBorrowers,name='addBorrowers'),
    path('submit_borrower',views.submitBorrower,name='submitBorrower'),
    path('checkoutBooks',views.checkoutBooks,name='checkoutBooks'),
    path('borrowerLoans',views.borrowerLoans,name='borrowerLoans'),
    path('searchcheckOutBooks',views.searchcheckOutBooks,name='searchcheckOutBooks'),
    path('displayCheckedOutBooks',views.displayCheckedOutBooks,name='displayCheckedOutBooks'),
    path('checkInBooks/<str:value>',views.checkInBooks,name='checkInBooks'),
    path('checkFines',views.checkFines,name='checkFines'),
    path('payFines/<str:value>',views.payFines,name='payFines'),
    path('checkHistory',views.checkHistory,name='checkHistory')
]
