from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db import connection
from django.contrib import messages
import datetime
from collections import OrderedDict

#call the main search page
def searchBooks(request):
    return render(request,'searchbooks.html')

#list the books based on the search
def listBooks(request):
    if request.method in ['POST']:
        searchValue = request.POST.get('searchValue', '')
        search = searchValue.split(' ')
        bookList = OrderedDict()

        for x in search:
            x = x.strip()
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT B.isbn FROM books B "
                    "INNER JOIN book_authors BA ON B.isbn = BA.isbn "
                    "INNER JOIN authors A ON A.author_id = BA.author_id "
                    "WHERE B.title LIKE %s OR B.isbn LIKE %s OR A.name LIKE %s ",
                    ['%' + x + '%', '%' + x + '%', '%' + x + '%']
                )
                result = cursor.fetchall()

                isbn = set()

                for row in result:
                    isbn.add(row[0])

                for isbn_val in isbn:
                    cursor.execute(
                        "SELECT name FROM authors INNER JOIN book_authors "
                        "ON authors.author_id = book_authors.author_id "
                        "where book_authors.isbn = %s",
                        [isbn_val]
                    )
                    result1 = cursor.fetchall()

                    cursor.execute("SELECT title FROM books WHERE isbn = %s", [isbn_val])
                    title = cursor.fetchone()[0]

                    cursor.execute("SELECT count(*) FROM book_availability WHERE isbn = %s", [isbn_val])
                    count = cursor.fetchone()[0]
                    status = ''
                    if(count == 0):
                        status = 'Available'
                    elif(count != 0):
                        cursor.execute("SELECT status FROM book_availability WHERE isbn = %s", [isbn_val])
                        val = cursor.fetchone()[0]
                        if(val == 'Checked In'):
                            status = 'Available'
                        else:
                            status = 'Not Available'

                    authors = ", ".join(value[0] for value in result1)
                    book_info = {
                        'isbn': isbn_val,
                        'title': title,
                        'authors': authors,
                        'status': status
                    }
                    entry = (
                        book_info['isbn'],
                        book_info['title'],
                        book_info['authors'],
                        book_info['status']
                    )
                    bookList[entry] = book_info
        checkOutList1 = list(bookList.values())
        checkOutList1 = sorted(checkOutList1, key=lambda x: x['isbn'])
        return render(request, 'bookslist.html', {'bookList': checkOutList1,'size': len(checkOutList1)})
    else:
        return render(request, 'searchbooks.html')
    

def addBorrowers(request):
    return render(request,'addBorrower.html')

def submitBorrower(request):
    if request.method == 'POST':
        borrower_name = request.POST['borrowerName']
        ssn = request.POST['ssn']
        address = request.POST['address']
        phone = request.POST['phone']
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(card_id) FROM borrowers")
        maxId = cursor.fetchone()[0]
        numeric_part = int(maxId[2:])
        numeric_part += 1
        incremented_Id = f'ID{numeric_part:06}'
        print(incremented_Id)
        cursor.execute("SELECT count(*) FROM borrowers where ssn = %s",[ssn])
        countOfSsn = cursor.fetchone()[0]
        if(countOfSsn == 0):
            cursor.execute("INSERT INTO borrowers VALUES (%s,%s,%s,%s,%s)",[incremented_Id,ssn,borrower_name,address,phone])
            messages.success(request,"Borrower added successfully")
            return render(request,'addBorrower.html')
        else:
            messages.warning(request,"Borrower already exists")
            return redirect('/addBorrowers')
    else:
        return render(request,'addBorrower.html')
    
def checkoutBooks(request):
    selected_books = request.GET.getlist('selected')
    request.session['selected_books'] = selected_books
    return render(request,'borrowerInfo.html')
    
def borrowerLoans(request):
    if request.method == 'POST':
        borrowercardid = request.POST['borrowercardid']
        cursor = connection.cursor()
        cursor.execute("SELECT count(*) FROM borrowers where card_id = %s",[borrowercardid])
        borrowerExists = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM book_loans where card_id = %s AND date_in IS NULL",[borrowercardid])
        booksNotReturned = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM book_loans INNER JOIN book_fines ON book_loans.loan_id = book_fines.loan_id where card_id = %s AND (date_in IS NULL OR (date_in >= due_date AND paid != 1))",[borrowercardid])
        lateBooks = cursor.fetchone()[0]

        borrowedCount = booksNotReturned
        selected_books = request.session.get('selected_books', [])
        if(borrowerExists == 0):
            messages.warning(request,"Borrower does not exist")
        elif(lateBooks > 0):
            messages.warning(request,"Borrower has impending fines")
        elif(borrowedCount + len(selected_books) > 3):
            messages.warning(request,"Cannot check out more than three books")
        elif(borrowerExists != 0):
            date_out = datetime.date.today()
            due_date = date_out + datetime.timedelta(days = 14)
            for selected_book in selected_books:
                cursor.execute("SELECT count(*),status FROM book_availability WHERE isbn = %s GROUP BY status",[selected_book])
                result = cursor.fetchall()
                count = 0
                status = ""
                for row in result:
                    count = row[0]
                    status = row[1]
                if(count == 0):
                    cursor.execute("INSERT INTO book_loans(date_out,due_date,card_id,isbn) VALUES (%s,%s,%s,%s)",[date_out,due_date,borrowercardid,selected_book])
                    cursor.execute("INSERT INTO book_availability(status,borrower_card_id,isbn) VALUES (%s,%s,%s)",["Checked Out",borrowercardid,selected_book])
                    messages.success(request,f"Book with ISBN " + str(selected_book) + " checked out successfully")
                elif(count != 0 and status != "Checked Out"):
                    cursor.execute("INSERT INTO book_loans(date_out,due_date,card_id,isbn) VALUES (%s,%s,%s,%s)",[date_out,due_date,borrowercardid,selected_book])
                    cursor.execute("UPDATE book_availability SET status = %s WHERE isbn = %s",['Checked Out',selected_book])
                    messages.success(request,f"Book with ISBN " + str(selected_book) + " checked out successfully")
                else:
                    messages.warning(request,f"Book with ISBN "+  str(selected_book) + " is already checked out")
            
        return render(request,'borrowerInfo.html')
        
    else:
       return render(request,'borrowerInfo.html') 
    
def searchcheckOutBooks(request):
    return render(request,'searchCheckedoutBooks.html')

def displayCheckedOutBooks(request):
    if request.method in ['POST']:
        searchCheckoutVal = request.POST.get('searchCheckoutVal')
        request.session['searchCheckoutVal'] = searchCheckoutVal
        search = searchCheckoutVal.split(' ')
        checkOutDict = OrderedDict()

        for x in search:
            x = x.strip()
            with connection.cursor() as cursor:
                cursor.execute("SELECT BL.isbn,B.title,BL.card_id,BB.borrower_name,BL.date_out,BL.due_date,BL.date_in FROM book_loans BL INNER JOIN borrowers BB ON BL.card_id = BB.card_id INNER JOIN book_availability BA ON BL.isbn = BA.isbn INNER JOIN books B ON B.isbn = BL.isbn WHERE (BL.isbn like %s OR BL.card_id like %s OR BB.borrower_name like %s) AND BA.status = 'Checked Out' AND BL.date_in is NULL",['%' + x + '%', '%' + x + '%', '%' + x + '%']) 
                result = cursor.fetchall()
                for row in result:
                    checkedOutBook_info = {
                        'isbn': row[0],
                        'title': row[1],
                        'card_id': row[2],
                        'borrower_name': row[3],
                        'date_out': row[4],
                        'due_date':row[5],
                        'date_in': row[6]
                    }
                    entry = (
                        checkedOutBook_info['isbn'],
                        checkedOutBook_info['title'],
                        checkedOutBook_info['card_id'],
                        checkedOutBook_info['borrower_name'],
                        checkedOutBook_info['date_out'],
                        checkedOutBook_info['due_date'],
                        checkedOutBook_info['date_in']
                    )
                    checkOutDict[entry] = checkedOutBook_info
        checkOutList = list(checkOutDict.values())
        return render(request,'displayCheckedOutBooks.html',{'result': checkOutList})
    else:
        return render(request,'searchCheckedoutBooks.html')
    
def checkInBooks(request,value):
    with connection.cursor() as cursor:
        searchCheckoutVal = request.session.get('searchCheckoutVal', [])
        cursor.execute("UPDATE book_availability SET status = %s WHERE isbn = %s",['Checked In',value]) 
        cursor.execute("UPDATE book_loans SET date_in = %s WHERE isbn = %s",[datetime.date.today(),value]) 
        search = searchCheckoutVal.split(' ')
        checkOutDict = OrderedDict()

        for x in search:
            x = x.strip()
            with connection.cursor() as cursor:
                cursor.execute("SELECT BL.isbn,B.title,BL.card_id,BB.borrower_name,BL.date_out,BL.due_date,BL.date_in FROM book_loans BL INNER JOIN borrowers BB ON BL.card_id = BB.card_id INNER JOIN book_availability BA ON BL.isbn = BA.isbn INNER JOIN books B ON B.isbn = BL.isbn WHERE (BL.isbn like %s OR BL.card_id like %s OR BB.borrower_name like %s) AND BA.status = 'Checked Out' AND BL.date_in is NULL",['%' + x + '%', '%' + x + '%', '%' + x + '%']) 
                result = cursor.fetchall()
                for row in result:
                    checkedOutBook_info = {
                        'isbn': row[0],
                        'title':row[1],
                        'card_id': row[2],
                        'borrower_name': row[3],
                        'date_out': row[4],
                        'due_date':row[5],
                        'date_in': row[6]
                    }
                    entry = (
                        checkedOutBook_info['isbn'],
                        checkedOutBook_info['title'],
                        checkedOutBook_info['card_id'],
                        checkedOutBook_info['borrower_name'],
                        checkedOutBook_info['date_out'],
                        checkedOutBook_info['due_date'],
                        checkedOutBook_info['date_in']
                    )
                    checkOutDict[entry] = checkedOutBook_info
        checkOutList = list(checkOutDict.values())

    return render(request,'displayCheckedOutBooks.html',{'result': checkOutList})

def checkFines(request):
    with connection.cursor() as cursor:
        todays_date = datetime.date.today()
        cursor.execute("SELECT loan_id,date_in,due_date FROM book_loans WHERE due_date < %s and date_in is null UNION SELECT loan_id,date_in,due_date FROM book_loans WHERE date_in > due_date;",[todays_date]) 
        result = cursor.fetchall()
        for row in result:
            loan_id = row[0]
            date_in = row[1]
            due_date = row[2]
            fine = '0.0'
            if date_in is None:
                #book not returned
                fine = (todays_date-due_date).days * 0.25
            else:
                #book returned
                fine = (date_in-due_date).days * 0.25
            cursor.execute("SELECT count(*) FROM book_fines WHERE loan_id = %s",[loan_id])
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("INSERT INTO book_fines(loan_id,fine_amt) VALUES(%s,%s)",[loan_id,fine])
            else:
                cursor.execute("UPDATE book_fines SET fine_amt = %s WHERE loan_id = %s",[fine,loan_id])
        cursor.execute("SELECT b.card_id,SUM(f.fine_amt) FROM borrowers b INNER JOIN book_loans bl ON b.card_id = bl.card_id INNER JOIN book_fines F ON bl.loan_id = f.loan_id WHERE f.paid = 0 GROUP BY b.card_id")
        resultlist = cursor.fetchall()
        fineDict = OrderedDict()
        fines = []
        for row in resultlist:
            cursor.execute("SELECT b.borrower_name FROM borrowers b WHERE b.card_id = %s",[row[0]])
            fineList = cursor.fetchall()

            for fine in fineList:
                fine_info = {
                    'card_id': row[0],
                    'borrower_name': fine[0],
                    'fine_amt': row[1]
                }
                fineDict[fine_info['card_id']] = fine_info
            fines = list(fineDict.values())    
    return render(request,'fines.html',{'result': fines})

def payFines(request,value):
    with connection.cursor() as cursor:
        todays_date = datetime.date.today()
        cursor.execute("SELECT COUNT(*) FROM book_loans bl INNER JOIN book_fines bf ON bl.loan_id = bf.loan_id WHERE date_in IS NULL AND card_id = %s AND paid = 0",[value])
        isBookCheckedIn = cursor.fetchone()[0]

        #all books are checked in
        if(isBookCheckedIn == 0):
            cursor.execute("UPDATE book_fines SET paid = 1,paid_on = %s WHERE loan_id IN (select loan_id FROM book_loans WHERE card_id = %s)",[todays_date,value]) 
            #cursor.execute("UPDATE book_availability SET status = 'Checked In' WHERE borrower_card_id = %s",[value]) 
        else:
            messages.success(request,f"Kindly ask the borrower to check in all the books before paying fine.")
        
        cursor.execute("SELECT b.card_id,SUM(f.fine_amt) FROM borrowers b INNER JOIN book_loans bl ON b.card_id = bl.card_id INNER JOIN book_fines F ON bl.loan_id = f.loan_id WHERE f.paid = 0 GROUP BY b.card_id")
        resultlist = cursor.fetchall()
        fineDict = OrderedDict()
        fines = []
        for row in resultlist:
            cursor.execute("SELECT b.borrower_name FROM borrowers b WHERE b.card_id = %s",[row[0]])
            fineList = cursor.fetchall()

            for fine in fineList:
                fine_info = {
                    'card_id': row[0],
                    'borrower_name': fine[0],
                    'fine_amt': row[1]
                }
                fineDict[fine_info['card_id']] = fine_info
            fines = list(fineDict.values())    
        return render(request,'fines.html',{'result': fines})
    

def checkHistory(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT b.card_id,SUM(f.fine_amt) FROM borrowers b INNER JOIN book_loans bl ON b.card_id = bl.card_id INNER JOIN book_fines F ON bl.loan_id = f.loan_id WHERE f.paid = 1 GROUP BY b.card_id")
        resultlist = cursor.fetchall()
        fineDict = OrderedDict()
        fines = []
        for row in resultlist:
            cursor.execute("SELECT b.borrower_name,bf.paid_on FROM borrowers b INNER JOIN book_loans bl ON b.card_id = bl.card_id INNER JOIN book_fines bf ON bl.loan_id = bf.loan_id WHERE b.card_id = %s AND paid_on IS NOT NULL",[row[0]])
            fineList = cursor.fetchall()

            for fine in fineList:
                fine_info = {
                    'card_id': row[0],
                    'borrower_name': fine[0],
                    'fine_amt': row[1],
                    'paid_on': fine[1]
                }
                fineDict[fine_info['card_id']] = fine_info
            fines = list(fineDict.values())    
    return render(request,'showFineHistory.html',{'result': fines})

            
   
