from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import User,Personal_Detail,Work_Detail,Contact_Detail,Experience_Detail,Bank_Detail,Paper_Publication,Patent,PHD_Awarded,Awards,Books,Books_Conference,CSV_Download,Head
from datetime import date
from django.contrib import messages

import datetime
from .decorators import login_or_head_required,admin_or_head_required,admin_required
import re

from django.contrib.auth import update_session_auth_hash





import os
import pandas as pd
import csv
# Create your views here.


def date_suffix(myDate):
    date_suffix = ["th", "st", "nd", "rd"]

    if myDate % 10 in [1, 2, 3] and myDate not in [11, 12, 13]:
        return date_suffix[myDate % 10]
    else:
        return date_suffix[0]
    
def current_date():
    today = date.today()
    current_day = today.day
    suffix = date_suffix(current_day)
    current = today.strftime('%A , %B %d')
    updated = str(current + suffix)
    return updated

def get_time_of_day():
    time = datetime.datetime.now().hour
    if time < 12:
        return "Morning"
    elif time < 16:
        return "Afternoon"
    elif time < 21:
        return "Evening"
    else:
        return "Night"

def profile(logged_user):
    score = 0
    empty_fields = []
    #check profile complete or not
    try:
        personal = Personal_Detail.objects.filter(user=logged_user).get()
        score += 20
    except:
        empty_fields.append('personal')
    try:
        work = Work_Detail.objects.filter(user=logged_user).get()
        score += 20
    except:
        empty_fields.append('work')
    try:
        contact = Contact_Detail.objects.filter(user=logged_user).get()
        score += 20
    except:
        empty_fields.append('contact')
    try:
        bank = Bank_Detail.objects.filter(user=logged_user).get()
        score += 20
    except:
        empty_fields.append('bank')
    try:
        experience = Experience_Detail.objects.filter(user=logged_user).get()
        score += 20
    except:
        empty_fields.append('experience')

    return score,empty_fields


def login_view(request):
    if request.method == "POST":
        user_type = request.POST.get("user_type")

       

        if user_type == "teacher":
            employee_code = request.POST.get("employee_code")
            password = request.POST.get("password")
            user = authenticate(request, username=employee_code, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Teacher logged in successfully.')
                return redirect("index")
            else:
                
                return render(request, "website/login.html", {
                    "message_teacher": "Invalid employee code or password."
                })

        elif user_type == "head":
            department = request.POST.get("dept", "").strip()

            password = request.POST.get("password")


            try:
                head = Head.objects.filter(department__iexact=department).first()

                if head is None:
                    
                    return render(request, "website/login.html", {
                        "message_head": "Department not found."
                    })
                
                elif check_password(password, head.password):
                        request.session["is_head"] = True
                        request.session["head_department"] = head.department

                        messages.success(request, "Head logged in successfully.")
                    
                        return redirect("index")
                        

        
               
                else:
                    return render(request, "website/login.html", {
                        "message_head": "Incorrect password for Head."
                    })
            except Head.DoesNotExist:
                return render(request, "website/login.html", {
                    "message_head": "Department not found."
                })


        elif user_type == "admin":
            username=request.POST.get("username")

            password = request.POST.get("password")
            email=request.POST.get("email")
            aadhar=request.POST.get("aadhar")
            


           
            
            user = authenticate(request, username=username, password=password)
            
           

            if user is not None:
                if user.email==email and user.aadhar_number==aadhar:
                   
                
                     
                    request.session["is_admin"] = True
                    user.save()
                    messages.success(request, 'Admin logged in successfully.')
                
                    return redirect("index")

                else:
                     return render(request, "website/login.html", {
                    "message_admin": "Invalid  aadharno/email"
                })
                
               
                
            else:
                return render(request, "website/login.html", {
                    "message_admin": "Invalid  password"
                })
            
            

            
            

    return render(request, "website/login.html")




@admin_required
def add_head(request):
    if request.method=='POST':
        department=request.POST.get('department')
        password=request.POST.get('password')


        if Head.objects.filter(department=department).exists():
            
            messages.error(request,'Head already exists')
            return render(request,'website/add_head.html')


        else:
            head=Head()
        head.department=department
        head.password=password
        head.save()
        messages.success(request,'Head Added Successfully')
        return redirect('index')

    else:
        return render(request,'website/add_head.html')

@admin_required   
def delete_head(request):
    if request.method == 'POST':
        department = request.POST.get('department')
        try:
            head = Head.objects.get(department=department)
            head.delete()
            messages.success(request, 'Head Deleted successfully')
            return render(request, 'website/delete_head.html')

        except Head.DoesNotExist:
            messages.error(request,'Head Doesnt Exist')
            return render(request, 'website/delete_head.html')
    else:
         return render(request, 'website/delete_head.html')

@admin_required
def update_head(request):
    if request.method=='POST':
        dept = request.POST.get('department')

        password=request.POST.get('password')

        try:
          user=Head.objects.get(department=dept)
          user.password=password
          user.save()
          messages.success(request, 'Head Updated successfully')
          return render(request, 'website/update.html')

        except Head.DoesNotExist: 
        
           messages.error(request,'Head Doesnt Exist')
           return render(request, 'website/update.html')

      


    else:

        return render(request,'website/update.html')
@admin_required   
def update_email_admin(request):
    if request.method=='POST':
        email=request.POST["email"]

        pattern2=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

        if not re.match(pattern2,email):
            messages.error(request,'Invalid email format')
            return render(request,'website/update_email_admin.html')

        try:
           user_id=User.objects.get(username='admin')
           user_id.email=email
           user_id.save()
           messages.success(request, "Email updated successfully.")
           return render(request,'website/update_email_admin.html')

        except User.DoesNotExist:
            messages.error(request,'Admin Doesnt Exist')
            return render(request,'website/update_email_admin.html')


    
    else:
        return render(request,'website/update_email_admin.html')
    
@admin_required
def update_aadhar_admin(request):
    if request.method=='POST':
        aadhar=request.POST.get("aadhar")

        pattern4=r'^\d{12}$'

        if not re.match(pattern4,aadhar):
            messages.error(request,'Invalid Aadhar number format,it should only have 12 digit numbers')
            return render(request,'website/update_aadhar_admin.html')
        try:

            if User.objects.filter(aadhar_number=aadhar):
                messages.error(request,'Aadhar no. already exists')
                return render(request,'website/update_aadhar_admin.html')
            
            user_id=User.objects.get(username='admin')
            user_id.aadhar_number=aadhar
            user_id.save()
            messages.success(request,"Aadhar no updated successfully")
            return render(request,'website/update_aadhar_admin.html')

        except User.DoesNotExist:
           messages.error(request,'Admin Doesnt Exist')
           return render(request,'website/update_aadhar_admin.html')


    
    else:
        return render(request,'website/update_aadhar_admin.html')


    
def register_user(request):
    if request.method == "POST":

        #register details
        mail_id = request.POST["mail_id"]
        employer_id = request.POST["employer_id"]
        employer_name = request.POST["employer_name"]
        password = request.POST["password"]
        confirmation = request.POST["confirm_password"]
        aadhar = request.POST['aadhar']
        dept=request.POST['dept']


        pattern1=r'^[A-Za-z.\s]+$'
        pattern2=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        pattern3=r'^[A-Za-z0-9_\/\-]+$'
        pattern4=r'^\d{12}$'
        error_ans=False


        

        if not re.match(pattern1,employer_name):
            messages.error(request,'Employee name can only contain letters and spaces and dot')
            error_ans=True
            error_ans=True


        if not re.match(pattern2,mail_id):
            messages.error(request,'Invalid email format')
            error_ans=True

        if not re.match(pattern3,employer_id):
            messages.error(request,'Invalid employer ID format')
            error_ans=True

        if not re.match(pattern4,aadhar):
            messages.error(request,'Invalid Aadhar number format,it should only have 12 digit numbers')
            error_ans=True


        if error_ans:
            return render(request, 'website/register.html')


        

        
        
        if password != confirmation:
            return render(request,'website/register.html',{
                'message':'Passwords Must Match'
            })
        
        try:
            user = User.objects.create_user(username=employer_id, email=mail_id, password=password)
            user.aadhar_number = aadhar
            user.employee_name = employer_name
            user.dept=dept
            
            user.save()

            messages.success(request, 'New User Registered Successfully')

            login(request, user)

            return HttpResponseRedirect(reverse("index"))

        except IntegrityError:
            return render(request, "website/register.html", {
                "message": "Existing User/Employee-id."
            })

    else:
        return render(request, "website/register.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse(login_view))

def index(request):
    if request.user.is_authenticated:
        # Teacher logged in
        current_user = request.user
        score, empty_list = profile(current_user)

       
        
            # Regular teacher
        patents = len(Patent.objects.filter(user=current_user))
        phds = len(PHD_Awarded.objects.filter(user=current_user))
        papers = len(Paper_Publication.objects.filter(user=current_user))
        awards = len(Awards.objects.filter(user=current_user))
        books = len(Books.objects.filter(user=current_user))
        books_conference = len(Books_Conference.objects.filter(user=current_user))

    elif request.session.get("is_head"):
        # Head is logged in — use department info from session
        department = request.session.get("head_department")

        # Filter by department (not user)
        patents = len(Patent.objects.filter(user__dept=department))
        phds = len(PHD_Awarded.objects.filter(user__dept=department))
        papers = len(Paper_Publication.objects.filter(user__dept=department))
        awards = len(Awards.objects.filter(user__dept=department))
        books = len(Books.objects.filter(user__dept=department))
        books_conference = len(Books_Conference.objects.filter(user__dept=department))

        current_user = None  # No actual user object
        score = None
        empty_list = []


    elif request.session.get("is_admin"):
        
        # Admin is logged in — use department info from session
       
        department = request.session.get("admin_department")
        # Filter by department (not user)
        patents = len(Patent.objects.all())
        phds = len(PHD_Awarded.objects.all())
        papers = len(Paper_Publication.objects.all())
        awards = len(Awards.objects.all())
        books = len(Books.objects.all())
        books_conference = len(Books_Conference.objects.all())

    

        current_user = None  # No actual user object
        score = None
        empty_list = []

    else:
        # Not logged in
        return redirect("login_view")

    return render(request, 'website/index.html', {
        'current_user': current_user,
        'date': current_date(),
        'mor_eve': get_time_of_day(),
        'empty_list': empty_list,
        'patents': patents,
        'phds': phds,
        'papers': papers,
        'awards': awards,
        'books': books,
        'conference': books_conference,
        'score': score,
    })


@login_required(login_url=login_view)
def personal_details(request):
    if request.method == "POST":
        father_name = request.POST["father_name"]
        mother_name = request.POST["mother_name"]
        dateofbirth = request.POST["dateofbirth"]
        bloodgrp = request.POST["blood_group"]
        gender = request.POST["gender"]
        maritial_status = request.POST["maritial_status"]
        gpf_nps=request.POST['gpf_ornps']
        if maritial_status == 'Married':
            spouse_name = request.POST["spouse_name"]

        current_user = request.user


        pattern1=r'^[A-Za-z.\s]+$'
        pattern2=r'^[A-Za-z0-9\/\-]+$'
        ans_error = False

        if not re.match(pattern1,father_name):
            messages.error(request,'Father name can only contain letters and spaces and dot')
            ans_error = True


        if not re.match(pattern1,mother_name):
            messages.error(request,'Mother name can only contain letters and spaces and dot')
            ans_error = True


        if not re.match(pattern2,gpf_nps):
            messages.error(request,'GPF/NPS can only contain letters, numbers, slashes(/) and dashes(-)')
            ans_error = True

        if maritial_status == 'Married':
             if not re.match(pattern1,spouse_name):
                messages.error(request,'Spouse name can only contain letters and spaces and dot')
                ans_error = True



        if ans_error:
              return redirect(personal_details)


        try:
            details = Personal_Detail.objects.filter(user=current_user).first()
            details.father_name = father_name
            details.mother_name = mother_name
            details.maritial_status = maritial_status
            if maritial_status == 'Married':
                details.spouse_name = spouse_name
            details.date_of_birth = dateofbirth
            details.gender = gender
            details.blood_group = bloodgrp
            details.gpf_ornps=gpf_nps
            details.save()

            messages.success(request, 'Personal Details Updated.')
        except:
            personal = Personal_Detail()
            personal.user = current_user
            personal.father_name = father_name
            personal.mother_name = mother_name
            personal.maritial_status = maritial_status
            if maritial_status == 'Married':
                personal.spouse_name = spouse_name
            personal.date_of_birth = dateofbirth
            personal.gender = gender
            personal.blood_group = bloodgrp
            personal.gpf_ornps=gpf_nps

            personal.save()

            messages.success(request, 'Personal Details Saved. ')
        
        #return kya karana yaha par
        return redirect("personal_details")
        
    else:
        current_user = request.user
        score,empty_list = profile(current_user)
        try:
            details = Personal_Detail.objects.filter(user=current_user).get()
            return render(request,'website/personal.html',{
                          
                'current_user' :current_user,
                'date': current_date(),
                'score':score,
                'empty_list':empty_list,
                'mor_eve' : get_time_of_day(),
                'father_name':details.father_name,
                'mother_name':details.mother_name,
                'maritial_status':details.maritial_status,
                'spouse_name':details.spouse_name,
                'date_of_birth':details.date_of_birth,
                'gender':details.gender,
                'blood_group':details.blood_group,
                'gpf_ornps':details.gpf_ornps,
            })
        except:
            return render(request,'website/personal.html',{
                'current_user' :current_user,
                'date': current_date(),
                'mor_eve' : get_time_of_day(),
                'message': 'Enter data',
                'score':score,
                'empty_list':empty_list,
            })
        
@login_required(login_url=login_view)
def work_details(request):
    if request.method == "POST":
        designation = request.POST["designation"]
        mode_of_recruitment = request.POST["mode_of_recruitment"]
        dob_joining = request.POST["dob_joining"]
        dob_retirement = request.POST["dob_retirement"]

        current_user = request.user

        try:
            details = Work_Detail.objects.filter(user=current_user).get()
            details.designation = designation
            details.mode_of_recruitment = mode_of_recruitment
            details.dob_joining = dob_joining
            details.dob_retirement = dob_retirement
            
            details.save()

            messages.success(request, 'Work Details Updated. ')
        except:
            work = Work_Detail()
            current_user = request.user
            work.user = current_user
            work.designation = designation
            work.mode_of_recruitment = mode_of_recruitment
            work.dob_joining = dob_joining
            work.dob_retirement = dob_retirement

            work.save()
            messages.success(request, 'Work Details Saved. ')
        
        return redirect(work_details)
    else:
        current_user = request.user
        score,empty_list = profile(current_user)
        try:
            details = Work_Detail.objects.filter(user=current_user).get()
            return render(request,'website/work.html',{
                'current_user' :current_user,
                'date': current_date(),
                'score':score,
                'empty_list':empty_list,
                'mor_eve' : get_time_of_day(),
                'designation':details.designation,
                'mode_of_recruitment':details.mode_of_recruitment,
                'dob_joining':details.dob_joining,
                'dob_retirement':details.dob_retirement,
            })
        except:
            return render(request,'website/work.html',{
                'current_user' :current_user,
                'date': current_date(),
                'score':score,
                'empty_list':empty_list,
                'mor_eve' : get_time_of_day(),
                'message':'Enter data'
            })
        
@login_required(login_url=login_view)


def contact_details(request):
    if request.method == "POST":
        aadhar = request.POST.get("aadhar")
        pan_number = request.POST.get("pan_number")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")
        district = request.POST.get("district")
        mobile = request.POST.get("mobile")
        mobile_alt = request.POST.get("mobile_alternate")
        corresponding_address = request.POST.get("corresponding_address")
        permanent_address = request.POST.get("permanent_address")
        personal_email=request.POST.get("personal_email")
        official_email=request.POST.get("official_email")



        pattern1=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        pattern2=r'^[A-Za-z\s]+$'
        pattern3=r'^[0-9]{10}$'
        pattern4=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        pattern5=r'^[A-Za-z0-9 :.,\/\-\s]+$'
        pattern6=r'^\d{6}$'
        ans_error = False



        if not re.match(pattern1,pan_number):
            messages.error(request,'Invalid PAN Number,it must be in sequence of ABCDE1234F')
            ans_error = True

        
        if not re.match(pattern2,state):
            messages.error(request,'State should only include proper name cant use abbreviations ')
            ans_error = True

        if not re.match(pattern2,district):
            messages.error(request,'District should only include proper name like cant use abbreviations ')
            ans_error = True


        if not re.match(pattern3,mobile):
            messages.error(request,'Mobile number must be 10 digits.')

            ans_error = True
        
        if not re.match(pattern3,mobile_alt):
            messages.error(request,'Mobile number must be 10 digits.')
            ans_error = True

        if not re.match(pattern4,personal_email):
            messages.error(request,'Invalid email format.')
            ans_error = True

        if not re.match(pattern4,official_email):
            messages.error(request,'Invalid email format.')
            ans_error = True

        if not re.match(pattern5, permanent_address):
            messages.error(request,'Invalid permanent address format.,it should be House no:12 ,Street no:1 colony:xyz')
            ans_error = True

        if not re.match(pattern5, corresponding_address):
            messages.error(request,'Invalid corresponding address format.,it should be House no:12 ,Street no:1 colony:xyz')
            ans_error = True

        if not re.match(pattern6, pincode):
            messages.error(request,'Invalid pincode format, it should be a 6-digit number.')
            ans_error = True




        if ans_error:
            return render(request,'website/contact.html')

        try:
            details = Contact_Detail.objects.get_or_create(user=request.user)

            # Assign values
            details.aadhar = aadhar
            details.pan_number = pan_number
            details.state = state
            details.district = district
            details.pin = pincode
            details.mobile = mobile
            details.mobile_alt = mobile_alt
            
            details.corresponding_address = corresponding_address
            details.personal_email=personal_email
            details.official_email=official_email
            details.permanent_address = permanent_address

            
            
            details.save()

            
            messages.success(request, "Contact Details Updated.")
            
               
        except:

            details=Contact_Detail()
            details.user=request.user
            details.aadhar = aadhar
            details.pan_number = pan_number
            details.state = state
            details.district = district
            details.pin = pincode
            details.mobile = mobile
            details.mobile_alt = mobile_alt
            
            details.corresponding_address = corresponding_address
            details.personal_email=personal_email
            details.official_email=official_email
            details.permanent_address = permanent_address

            details.save()

            messages.success(request, "Contact Details Saved.")
            




            

        return redirect("contact_details")  # Redirect to avoid form resubmission

    else:
        current_user = request.user
        score, empty_list = profile(current_user)
        try:
            details = Contact_Detail.objects.get(user=current_user)
            return render(request,'website/contact.html', {
                "current_user": current_user,
                "date": current_date(),
                "mor_eve": get_time_of_day(),
                "score": score,
                "empty_list": empty_list,
                "aadhar": details.aadhar,
                "pan_number": details.pan_number,
                "state": details.state,
                "district": details.district,
                "pincode": details.pin,
                "mobile": details.mobile,
                "mobile_alt": details.mobile_alt,
                "personal_email":details.personal_email,
                "official_email":details.official_email,

                "corresponding_address":details.corresponding_address,
                "permanent_address": details.permanent_address,
            })
        except Contact_Detail.DoesNotExist:
            return render(request, "website/contact.html", {
                "current_user": current_user,
                "date": current_date(),
                "mor_eve": get_time_of_day(),
                "score": score,
                "empty_list": empty_list,
                "message": "Enter data", 
            })

        

        
@login_required(login_url="login_view")
def bank_details(request):
    current_user = request.user

    if request.method == "POST":
        bank_name = request.POST.get("bank_name")
        bank_account = request.POST.get("bank_account")
        bank_ifsc = request.POST.get("ifsc_code")
        bank_branch = request.POST.get("bank_branch")


        pattern1=r'^[A-Za-z.\s\-]+$'
        pattern2=r'^[0-9]{9,18}$'
        pattern3=r'^[A-Z]{4}0[A-Z0-9]{6}$'
        pattern4=r'^[A-Za-z0-9.,\s\-]+$'
        ans_error = False

      

        if not re.match(pattern1,bank_name):
            messages.error(request,'Bank name can only contain letters, spaces and dots.')
            ans_error = True

        if not re.match(pattern2,bank_account):
            messages.error(request,'Bank account number must be between 9 to 18 digits')
            ans_error = True


        if not re.match(pattern3,bank_ifsc):
            messages.error(request, 'Invalid IFSC code format.')
            ans_error = True

        if not re.match(pattern4,bank_branch):
            messages.error(request, 'Bank branch can only contain letters, numbers, spaces, and dots.')
            ans_error = True
            
        if ans_error:
            return redirect(bank_details)


        try:
           
            details = Bank_Detail.objects.filter(user=current_user).get()

            details.bank_name = bank_name
            details.bank_account = bank_account
            details.bank_ifsc = bank_ifsc
            details.bank_branch = bank_branch

            
           
            details.save()

            messages.success(request, "Bank Details Updated.")

        except:

            details=Bank_Detail()
            
            details = Bank_Detail()
            details.user = current_user
            details.bank_name = bank_name
            details.bank_account = bank_account
            details.bank_ifsc = bank_ifsc
            details.bank_branch = bank_branch

            details.save()

            messages.success(request, "Bank Details Saved.")

            

        return redirect(bank_details)

    else:
        # GET request: Load existing details or show 'Enter data' message
        score, empty_list = profile(current_user)

        try:
            details = Bank_Detail.objects.filter(user=current_user).get()
            return render(request, "website/bank.html", {
                "current_user": current_user,
                "date": current_date(),
                "mor_eve": get_time_of_day(),
                "score": score,
                "empty_list": empty_list,
                "bank_name": details.bank_name,
                "bank_ifsc": details.bank_ifsc,
                "bank_account": details.bank_account,
                "bank_branch": details.bank_branch,
            })
        except Bank_Detail.DoesNotExist:
            return render(request, "website/bank.html", {
                "current_user": current_user,
                "date": current_date(),
                "mor_eve": get_time_of_day(),
                "score": score,
                "empty_list": empty_list,
                "message": "Enter data"
            })


        
@login_required(login_url=login_view)



@login_required(login_url="login_view")
def experience_details(request):
    current_user = request.user

    if request.method == "POST":
        
            teaching_exp = request.POST.get("teaching_experience")
            industry_exp = request.POST.get("industry_experience")
            research_exp = request.POST.get("research_experience")
            teaching_exp_pup = request.POST.get("teaching_experience_pup")
            specialization = request.POST.get("specialization")
            postgraduate = request.POST.get("postgraduate")
            undergraduate = request.POST.get("undergraduate")

            pattern=r'^\d+(\.\d{1,2})?$'
            pattern1=r'^[A-Za-z\s]+(\s*,\s*[A-Za-z\s]+)*\s*$'
            ans_error = False
       


            if not re.match(pattern,teaching_exp):
                messages.error(request,'Invalid teaching experience! Please enter a positive number with up to 2 decimal places.')
                ans_error = True

            if not re.match(pattern,industry_exp):
                messages.error(request,'Invalid industry experience! Please enter a positive number with up to 2 decimal places.')
                ans_error = True

            if not re.match(pattern,research_exp):
                messages.error(request,'Invalid research experience! Please enter a positive number with up to 2 decimal places.')
                ans_error = True

            if not re.match(pattern,teaching_exp_pup):
                messages.error(request,'Invalid teaching experience at pup  Please enter a positive number with up to 2 decimal places.')
                ans_error = True

            if not re.match(pattern,postgraduate):
                messages.error(request,'Invalid postgraduate experience! Please enter a positive number with up to 2 decimal places.')
                ans_error = True

            if not re.match(pattern,undergraduate):
                messages.error(request,'Invalid undergraduate experience! Please enter a positive number with up to 2 decimal places.')
                ans_error = True

            if not re.match(pattern1,specialization):
                messages.error(request,'Invalid specialization format. It should only contain letters and commas.')
                ans_error = True          
                
            if ans_error:
                return redirect(experience_details)

            


            try:
                # Try to fetch existing details
                experience = Experience_Detail.objects.filter(user=current_user).get()

                experience.teaching_experience = teaching_exp
                experience.research_experience = research_exp
                experience.industry_experience = industry_exp
                experience.pup_teaching_experience = teaching_exp_pup
                experience.specialization = specialization
                experience.postgraduate = postgraduate
                experience.undergraduate = undergraduate

               
                experience.save()

                messages.success(request, "Experience Details Updated.")

            except Experience_Detail.DoesNotExist:
                # Create new details if none exist
                experience = Experience_Detail(
                    user=current_user,
                    teaching_experience=teaching_exp,
                    research_experience=research_exp,
                    industry_experience=industry_exp,
                    pup_teaching_experience=teaching_exp_pup,
                    specialization=specialization,
                    postgraduate=postgraduate,
                    undergraduate=undergraduate
                )
               
                experience.save()

                messages.success(request, "Experience Details Saved.")

   

            return redirect(experience_details)

    else:
        score, empty_list = profile(current_user)

        try:
             details = Experience_Detail.objects.filter(user=current_user).get()
             return render(request, 'website/experience.html', {
                 'current_user': current_user,
                 'date': current_date(),
                 'mor_eve': get_time_of_day(),
                 'score': score,
                'empty_list': empty_list,
                'teaching_experience': details.teaching_experience,
                'research_experience': details.research_experience,
                'industry_experience': details.industry_experience,
                'pup_teaching_experience': details.pup_teaching_experience,
                'specialization': details.specialization,
                'undergraduate': details.undergraduate,
                'postgraduate': details.postgraduate
            })
        except Experience_Detail.DoesNotExist:
            return render(request, 'website/experience.html', {
                'current_user': current_user,
                'date': current_date(),
                'mor_eve': get_time_of_day(),
                'score': score,
                'empty_list': empty_list,
                'message': 'Enter data'
            })

        
@login_required(login_url=login_view)
def patent_register(request):
    if request.method == "POST":
        patent_number = request.POST["patent_number"]
        patent_title = request.POST["patent_title"]
        year_awarded = request.POST["year_awarded"]
        author_name = request.POST['author_name']
        category = request.POST['category']
        level = request.POST['level']
        patent_type=request.POST['patent_type']

        if(category=='Published'):
           date_published=request.POST['date_published']
        

        if(category=='Awarded/Granted'):
           date_award=request.POST['date_award']


        pattern1=r'^[A-Za-z0-9]+$'

        pattern2= r'^[A-Za-z0-9.,:;!?()&\'\"\- ]+$'
        pattern3=r'^[A-Za-z\s]+(\s*,\s*[A-Za-z\s]+)*\s*$'
        ans_error = False
        

      
        if not re.match(pattern2, patent_title):
            messages.error(request, 'Title can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True
            


        if not re.match(pattern1, patent_number):
            messages.error(request, 'Patent number can only contain letters and numbers.')
            ans_error = True

        if not re.match(pattern3,author_name):
            messages.error(request,'invalid author names,it should be in format author1 ,author2 ')
            ans_error = True
            
        

        if ans_error:
            return redirect(reverse("patent_register"))

        

        


        
        
        


        patent = Patent()
        patent.user = request.user
        patent.author_name = author_name
        patent.patent_number = patent_number
        patent.patent_title = patent_title
        patent.patent_year = year_awarded
        patent.category = category
        patent.level=level
        patent.patent_type=patent_type
        
        

        if(category=='Published'):
             patent.date_published=date_published

        if(category=='Awarded/Granted'):
              patent.date_award=date_award

        patent.save()

        messages.success(request, 'Patent Registered Successfully')

        return HttpResponseRedirect(reverse(patent_display))
    else:
        current_user=request.user
        score,empty_list = profile(current_user)
        return render(request,'website/patent.html',{
            'current_user': current_user,
            'mor_eve' : get_time_of_day(),
            'date': current_date(),
            'score':score,
            'empty_list':empty_list,
            
        })
    
@login_required(login_url=login_view)
def phd_awarded(request):
    if request.method == "POST":
        department = request.POST["dept"]
        # guide_names = request.POST["guide_names"]
        thesis_title = request.POST["thesis_title"]
        registration_date = request.POST["registration_date"]
        # award_date = request.POST["award_date"]
        scholor_name = request.POST['scholor_name']
        enrollment_date=request.POST['enrollment_date']
        thesis_submission_date=request.POST['thesis_submit_date']
        thesis_awarded_date=request.POST['award_date']
        supervisor=request.POST['supervisor_name']
        co_supervisor=request.POST['co_supervisor_name']
        faculty_title=request.POST['faculty_title']


         # Regex validation
        pattern1= r'^[A-Za-z.\s]+$'
        pattern2= r"^[A-Za-z0-9.,:;!?()&'\"\- ]+$"
        ans_error = False
        

        if not re.match(pattern1, scholor_name):
            
            messages.error(request, 'Invalid Scholar Name! Use only letters, spaces, and dots.')
            ans_error = True
            
        
        if not re.match(pattern1, supervisor):
            
            messages.error(request, 'Invalid Supervisor Name! Use only letters, spaces, and dots.')
            ans_error = True

        if not re.match(pattern2, thesis_title):
            messages.error(request,'Title can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True
           
            


        if not re.match(pattern1, co_supervisor):
           
            messages.error(request, 'Invalid Co-Supervisor Name! Use only letters, spaces, and dots.')
            ans_error = True
            

        
        if ans_error:
            return redirect(phd_awarded)




        phd = PHD_Awarded()
        phd.user = request.user
        phd.scholor_name = scholor_name
        phd.department = department
        # phd.guide_names = guide_names
        phd.thesis_title = thesis_title
        phd.thesis_awarded_date = thesis_awarded_date
        phd.registration_date = registration_date
        phd.enrollment_date=enrollment_date
        phd.thesis_submission_date=thesis_submission_date
        phd.supervisor=supervisor
        phd.co_supervisor=co_supervisor
        phd.faculty_title=faculty_title

        phd.save()

        messages.success(request, 'Ph.D Registered Successfully')

        return HttpResponseRedirect(reverse(phd_display))

    else:
        current_user=request.user
        score,empty_list = profile(current_user)
        return render(request,'website/phd.html',{
            'current_user': current_user,
            'mor_eve' : get_time_of_day(),
            'date': current_date(),
            'score':score,
            'empty_list':empty_list,
        })
    
@login_required(login_url=login_view)
def research_publication(request):
    if request.method == "POST":
        title = request.POST["title"]
        author_names = request.POST["author_names"]
        journal_name = request.POST["journal_name"]
        journal_url = request.POST["journal_url"]
        issn = request.POST["issn"]
        publisher = request.POST["publisher"]
        month_published = request.POST["month_published"]
        year_published = request.POST["year_published"]
        volume_number = request.POST["volume_number"]
        issue_number = request.POST["issue_number"]
        pp = request.POST["pp"]
        doi = request.POST["doi"]
        ugc_core = request.POST["ugc_core"]
        scopus = request.POST["scopus"]
        
        sci_scie_esci = request.POST.get('sci_scie_esci')

        if sci_scie_esci != 'None':
             impact_factor = request.POST.get('impact_factor')

        
        pattern1 = r'^[A-Za-z0-9\s,.:&()\'-]+$'
        pattern2=r'^[0-9A-Za-z\-()]+$'
        pattern3=r'^\d+\s*-\s*\d+$'
        pattern4=r'^[A-Za-z0-9\-\/]+$'
        pattern5=r'^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$'
        pattern6=r'^\d+(\.\d{1,2})?$'
        pattern7=r'^[A-Za-z0-9&.,: \-]+$'
        pattern8= r'^[A-Za-z0-9.,:;!?()&\'\"\- ]+$'
        pattern9=r'^[A-Za-z\s]+(\s*,\s*[A-Za-z\s]+)*\s*$'
        pattern10=r'^\d{4}[-\s]?\d{4}$'
        pattern11 = r'^(https?://)?([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?$'
        ans_error = False




        

        if not re.match(pattern1,journal_name):
            
            messages.error(request, 'It can include letters (A-Z, a-z), numbers (0-9), spaces, and these special characters , . : & ( ) - ')
            ans_error = True
        if not re.match(pattern2,volume_number):
            
            messages.error(request,'it can include letters ,numbers,and special characters - () ')
            ans_error = True


        if not re.match(pattern3,pp):
            messages.error(request,'pp should be in the format of 12-34')
            ans_error = True

        if not re.match(pattern4,issue_number):
            messages.error(request,'Issue number can have numbers,letters,special characters  - /')
            ans_error = True

        if not re.match(pattern5,doi):
            messages.error(request,'A DOI must start with 10. followed by a numeric code, a /, and a unique suffix.Example: 10.1016/j.jss.2018.04.027')
            ans_error = True

        
        if sci_scie_esci!='None':
            if not re.match(pattern6, impact_factor):
                   messages.error(request, 'Impact factor must be a number and can have up to two decimal places.')
                   ans_error = True
               

        if not re.match(pattern7, publisher):
            
            messages.error(request, 'Publisher name can only contain letters, numbers, spaces, and & . , : - characters.')
            ans_error = True
        
        


        
        if not re.match(pattern8,title):
            messages.error(request,'Title can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True

        if not re.match(pattern9,author_names):
            messages.error(request,'invalid author names,it should be in format author1 ,author2 ')
            ans_error = True

        if not re.match(pattern10,issn):
            messages.error(request,'ISSN should be in the format of 1234-5678 or 12345678.')
            ans_error = True

        if not re.match(pattern11,journal_url):
            messages.error(request,'Invalid journal URL format.')
            ans_error = True

        if ans_error:
            return redirect(research_publication)


        

        paper = Paper_Publication()
        paper.user = request.user
        paper.title = title
        paper.author_names = author_names
        paper.journal_name = journal_name
        paper.journal_website = journal_url
        paper.issn = issn
        paper.publisher = publisher
        paper.month_published = month_published
        paper.year_published = year_published
        paper.volume_number = volume_number
        paper.issue_number = issue_number
        paper.pp = pp
        paper.doi = doi
        paper.ugc_core = ugc_core
        paper.scopus = scopus
        paper.sci_scie_esci = sci_scie_esci
        if sci_scie_esci != 'None':
            paper.impact_factor = impact_factor
        paper.save()

        return HttpResponseRedirect(reverse(research_display))
    else:
        current_user=request.user
        score,empty_list = profile(current_user)
        return render(request,'website/research.html',{
            'current_user': current_user,
            'mor_eve' : get_time_of_day(),
            'date': current_date(),
            'score':score,
            'empty_list':empty_list,
        })

@login_required(login_url=login_view)
def awards(request):
    if request.method == "POST":
        activity = request.POST["activity"]
        award_name = request.POST["award_name"]
        authority_name = request.POST["authority_name"]
        date_award=request.POST["date_award"]
        
        level = request.POST['level']
        awardee=request.POST['awardee_name']


        pattern1 = r'^[A-Za-z0-9 .,\':&()\-:;!?\"\[\]]+$'
        pattern2 = r'^[A-Za-z.\s]+$'
        pattern3=r'^[A-Za-z0-9.,\'’\-()&\s]+$'

        ans_error = False
       


        if not re.match(pattern1, activity):
            
            messages.error(request, 'Name of the activity can only contain letters, numbers, spaces, and common symbols: . , \' : & ( ) - ; ! ? " [ ]')
            ans_error=True
            
        
        if not re.match(pattern3, award_name):  
            messages.error(request,'Award name can only contain letters,numbers,spaces and these symbols . , \' ’ \-( ) &')
            ans_error=True



         
        if not re.match(pattern3, authority_name):  
            messages.error(request,'Authority name can only contain letters,numbers,spaces and these symbols . , \' ’ \-( ) &')
            ans_error=True
       
        
        

        if not re.match(pattern2, awardee):
            
            messages.error(request, 'Awardee Name! Use only letters, spaces, and dots.')
            ans_error=True

        if ans_error:
            return redirect('awards')
    
        


        award = Awards()
        award.user = request.user
       
        award.activity = activity
        award.award_name = award_name
        award.authority_name = authority_name
        award.date_award=date_award
        award.level = level
        award.awardee=awardee
        award.save()
        
        messages.success(request, 'Award Registered Successfully')

        return HttpResponseRedirect(reverse(award_display))
    else:
        current_user=request.user
        score,empty_list = profile(current_user)
        return render(request,'website/award.html',{
            'current_user': current_user,
            'mor_eve' : get_time_of_day(),
            'date': current_date(),
            'score':score,
            'empty_list':empty_list,
        })
    
@login_required(login_url=login_view)
def books(request):
    if request.method == "POST":
        author_name = request.POST["author_name"]
        book_title = request.POST["book_title"]
        publisher = request.POST["publisher"]
        isbn = request.POST["isbn"]
        year_published = request.POST["year_published"]
        affiliate_uni = request.POST['affiliate_uni']
        level=request.POST['level']


        pattern1=r'^[A-Za-z0-9&.,: \-]+$'
        pattern2= r'^[A-Za-z0-9.,:;!?()&\'\"\- ]+$'

        pattern3=r'^[A-Za-z0-9 .,\'&() \-]+$'
        pattern4=r'^[A-Za-z\s]+(\s*,\s*[A-Za-z\s]+)*\s*$'
        pattern5=r'^(?:\d{3}[- ]?)?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,7}[- ]?\d{1,7}$'


        ans_error = False



      

        if not re.match(pattern1, publisher):
            
            messages.error(request, 'Publisher name can only contain letters, numbers, spaces, and & . , : - characters.')
            ans_error = True
        
        


        
        if not re.match(pattern2, book_title):
            messages.error(request,'Title can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True



        if not re.match(pattern3, affiliate_uni):
            messages.error(request, 'Affiliate University can only contain letters, numbers, spaces and symbols . , \' & () -')
            ans_error = True

        if not re.match(pattern4,author_name):
            messages.error(request,'invalid author names,it should be in format author1 ,author2 ')
            ans_error = True

        if not re.match(pattern5,isbn):
            messages.error(request,'invalid isbn number')
            ans_error = True
        
        
        if ans_error:
            return redirect('books')


    
        
        books = Books()
        books.user = request.user
        books.authors = author_name
        books.title = book_title
        books.publisher = publisher
        books.isbn = isbn
        books.year_published = year_published
        books.affiliating_institute = affiliate_uni
        books.level = level
        books.save()

        messages.success(request, 'Book Registered Successfully')

        return HttpResponseRedirect(reverse(books_display))
    else:
        current_user=request.user
        score,empty_list = profile(current_user)
        return render(request,'website/books.html',{
            'current_user': current_user,
            'date': current_date(),
            'mor_eve' : get_time_of_day(),
            'score':score,
            'empty_list':empty_list,
        })
    
@login_required(login_url=login_view)
def conference(request):
    if request.method == "POST":
        author_name = request.POST["author_name"]
        category = request.POST["category"]
        type = request.POST["type"]
        publisher = request.POST["publisher"]
        date = request.POST["date"]
        title_ch_paper = request.POST['title_ch_paper']
        title_book_conf = request.POST['title_book_conf']
        isbn = request.POST['isbn']
        pp = request.POST['pp']



        pattern1=r'^[A-Za-z0-9&.,: \-]+$'
        pattern2= r"^[A-Za-z0-9.,:;!?()&'\"\- ]+$"

        pattern3 = r'^[A-Za-z\s]+(?:,\s?[A-Za-z\s]+)?$'

        pattern4=r'^[A-Za-z\s]+(\s*,\s*[A-Za-z\s]+)*\s*$'
        pattern5=r'^(?:\d{3}[- ]?)?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,7}[- ]?\d{1,7}$'
        ans_error = False


        if not re.match(pattern1, publisher):
            
            messages.error(request, 'Publisher name can only contain letters, numbers, spaces, and & . , : - characters.')
            ans_error = True
        
        


        
        if not re.match(pattern2, title_ch_paper):
            messages.error(request,'Title can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True
        
        if not re.match(pattern2, title_book_conf):
            messages.error(request,'Title  can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True

        if not re.match(pattern3,pp):
            messages.error(request,'Place of Publication (PP) can only have data in this format, for example: New York, USA')
            ans_error = True

        if not re.match(pattern4,author_name):
            messages.error(request,'invalid author names,it should be in format author1 ,author2 ')
            ans_error = True

        if not re.match(pattern5,isbn):
            messages.error(request,'invalid isbn number')
            ans_error = True

        if ans_error:
            return redirect(conference)

        

        books_conf = Books_Conference()
        books_conf.user = request.user
        books_conf.authors = author_name
        books_conf.category = category
        books_conf.publisher = publisher
        books_conf.isbn = isbn
        books_conf.title_book_conf = title_book_conf
        books_conf.title_chap_paper = title_ch_paper
        books_conf.type_conf = type
        books_conf.date = date
        books_conf.pp = pp
        books_conf.save()

        messages.success(request, 'Proceeding Registered Successfully')

        return HttpResponseRedirect(reverse(conference_display))
    else:
        current_user=request.user
        score,empty_list = profile(current_user)
        return render(request,'website/conference.html',{
            'current_user': current_user,
            'date': current_date(),
            'mor_eve' : get_time_of_day(),
            'score':score,
            'empty_list':empty_list,
        })


@login_or_head_required
def personal_display(request):
    current_user = request.user
   
    is_admin=request.session.get("is_admin",False)
    is_head=request.session.get("is_head",False)
    head_dept=request.session.get("head_department",None)
    
    if request.method == 'POST':

        field = request.POST['field']

        data = request.POST['q']

        
       
        if is_admin:

          
            filter_personal = Personal_Detail.objects.filter(**{f"{field}__iexact":data})
        elif is_head and head_dept:
         
            
            filter_personal = Personal_Detail.objects.filter(**{f"{field}__iexact":data}, user__dept=head_dept)
        
       
        filter_personal_len = len(filter_personal)

        filter_personal_list = []
        f_count = 1
        for personal in filter_personal:
            filter_personal_list.append((f_count,personal))
            f_count+=1


        if is_admin or is_head:
            df = pd.DataFrame(list(filter_personal.values()))
            
            filename = 'Filter_personal_download.xlsx'
            path = '.\website\csv_files'
            df.to_excel(os.path.join(path,filename))


           
        if filter_personal_len == 0:
            return render(request,'website/personal_display.html',{
            'filter_field':field,
            'filter_data':data,
            'message':'No Data Available',
            'current_user': current_user,
            'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
           
            })
        return render(request,'website/personal_display.html',{
            'filter_field':field,
            'filter_data':data,
            'filter_personal':filter_personal,
            
            'filter_personal_list':filter_personal_list,
            'current_user': current_user,
            'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
    })
    else:
        current_user = request.user

        if is_admin:
            personal = Personal_Detail.objects.all()



        elif is_head and head_dept:
             personal= Personal_Detail.objects.filter(user__dept=head_dept) 

        if is_admin or is_head:
             df = pd.DataFrame(list(personal.values()))
             filename = 'Personal_details_download.xlsx'
             path = '.\website\csv_files'
             df.to_excel(os.path.join(path,filename))
     
    personal_list = []
    count = 1
    for personal in personal:
            personal_list.append((count,personal))
            count+=1

    return render(request,'website/personal_display.html',{
                'personal':personal,
               
                'personal_list':personal_list,
                'current_user': current_user,
                'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept, 
            })

@login_or_head_required
def work_display(request):

    current_user = request.user


    is_admin=request.session.get("is_admin",False)
    is_head=request.session.get("is_head",False)
    head_dept=request.session.get("head_department",None)

    if request.method == 'POST':
        
        field = request.POST['field']

        data = request.POST['q']
       
        

        if is_admin:

          filter_work = Work_Detail.objects.filter(**{f"{field}__iexact":data})


        elif is_head and head_dept:

         filter_work = Work_Detail.objects.filter(**{f"{field}__iexact":data},user__dept=head_dept)

        if is_admin or is_head:
            df = pd.DataFrame(list(filter_work.values()))
            filename = 'Filter_work_details_download.xlsx'
            path = '.\website\csv_files'
            df.to_excel(os.path.join(path,filename))
        
        
       
        filter_work_len=len(filter_work)

        filter_work_list = []
        f_count = 1
        for work in filter_work:
            filter_work_list.append((f_count,work))
            f_count+=1


        

           
        if filter_work_len == 0:
            return render(request,'website/work_display.html',{
            'filter_field':field,
            'filter_data':data,
            'message':'No Data Available',
            'current_user': current_user,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept, 
           
            })
        return render(request,'website/work_display.html',{
            'filter_field':field,
            'filter_data':data,
            'filter_work':filter_work,
          
            'filter_work_list':filter_work_list,
            'current_user': current_user,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept, 
            
    })
    else:
        current_user = request.user
        
        if is_admin:
            works = Work_Detail.objects.all()



        elif is_head and head_dept:
             works= Work_Detail.objects.filter(user__dept=head_dept) 



        if is_admin or is_head:
            df = pd.DataFrame(list(works.values()))
            filename = 'work_download.xlsx'
            path = '.\website\csv_files'
            df.to_excel(os.path.join(path,filename))
       
        work_list = []
        count = 1
        for work in works:
                work_list.append((count,work))
                count+=1

        return render(request,'website/work_display.html',{
                'work':works,
               
                'work_list':work_list,
                'current_user': current_user,
                 'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,  
            })
    


@login_or_head_required
def contact_display(request):
    current_user = request.user

    
    is_admin=request.session.get("is_admin",False)
    is_head=request.session.get("is_head",False)
    head_dept=request.session.get("head_department",None)

    if request.method == 'POST':
       
        field = request.POST['field']

        data = request.POST['q']
       
        
       
        if is_admin:

          filter_contact = Contact_Detail.objects.filter(**{f"{field}__iexact":data})
        
        elif is_head and head_dept:

           filter_contact = Contact_Detail.objects.filter(**{f"{field}__iexact":data},user__dept=head_dept)
        
        filter_contact_len=len(filter_contact)

        filter_contact_list = []
        f_count = 1
        for contact in filter_contact:
            filter_contact_list.append((f_count,contact))
            f_count+=1



        
        if is_admin or is_head:
            df = pd.DataFrame(list(filter_contact.values()))
           
            filename = 'Filter_contact_download.xlsx'
            path = '.\website\csv_files'
            df.to_excel(os.path.join(path,filename))

           
        if filter_contact_len == 0:
            return render(request,'website/contact_display.html',{
            'filter_field':field,
            'filter_data':data,
            'message':'No Data Available',
            'current_user': current_user,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept, 
           
            })
        return render(request,'website/contact_display.html',{
            'filter_field':field,
            'filter_data':data,
            'filter_contact':filter_contact,
            
            'filter_contact_list':filter_contact_list,
            'current_user': current_user,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept, 
            
    })
    else:
        current_user = request.user


        if is_admin:
            contacts= Contact_Detail.objects.all()
       

        elif is_head and head_dept:
            contacts= Contact_Detail.objects.filter(user__dept=head_dept) 



        if is_admin or is_head:
            df = pd.DataFrame(list(contacts.values()))
            df['employee_name']=request.user.employee_name
            filename = 'contact_download.xlsx'
            path = '.\website\csv_files'
            df.to_excel(os.path.join(path,filename))




      
        contact_list = []
        count = 1
        for contact in contacts:
                contact_list.append((count,contact))
                count+=1

        return render(request,'website/contact_display.html',{
                'contact':contacts,
               
                'contact_list':contact_list,
                'current_user': current_user,
                 'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,  
            })
        


@login_or_head_required
def bank_display(request):
    current_user = request.user


    is_admin=request.session.get("is_admin",False)
    is_head=request.session.get("is_head",False)
    head_dept=request.session.get("head_department",None)
    if request.method == 'POST':
        
        field = request.POST.get('field')

        data = request.POST.get('q')
       
        # filter_bank = Bank_Detail.objects.none()


        if is_admin:

          filter_bank = Bank_Detail.objects.filter(**{f"{field}__iexact":data})
        
        elif is_head and head_dept:


            filter_bank = Bank_Detail.objects.filter(**{f"{field}__iexact":data}, user__dept=head_dept)


        if is_admin or is_head:
            df = pd.DataFrame(list(filter_bank.values()))
            filename = 'Filter_bank_download.xlsx'
            path = '.\website\csv_files'
            df.to_excel(os.path.join(path,filename))
        
       
      
        filter_bank_len=len(filter_bank)
        filter_bank_list = []
        f_count = 1
        for bank in filter_bank:
            filter_bank_list.append((f_count,bank))
            f_count+=1

            df = pd.DataFrame(list(filter_bank.values()))
            filename = 'Filter_bank_details.download.xlsx'
            path = '.\website\csv_files'
            df.to_excel(os.path.join(path,filename))

           
        if filter_bank_len == 0:
            return render(request,'website/bank_display.html',{
            'filter_field':field,
            'filter_data':data,
            'message':'No Data Available',
            'current_user': current_user,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,  
           
            })
        return render(request,'website/bank_display.html',{
            'filter_field':field,
            'filter_data':data,
            'filter_bank':filter_bank,
            
            'filter_bank_list':filter_bank_list,
            'current_user': current_user,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,  
            
    })
    else:
        current_user = request.user

        if is_admin:
            banks= Bank_Detail.objects.all()

        elif is_head and head_dept:
       
            banks= Bank_Detail.objects.filter(user__dept=head_dept)



        if is_admin or is_head:
            df = pd.DataFrame(list(banks.values()))
            filename = 'Bank_download.xlsx'
            path = '.\website\csv_files'
            df.to_excel(os.path.join(path,filename))
         

       
        bank_list = []
        count = 1
        for bank in banks:
                bank_list.append((count,bank))
                count+=1

                df = pd.DataFrame(list(banks.values()))
                filename = 'Filter_bank_details.download.xlsx'
                path = '.\website\csv_files'
                df.to_excel(os.path.join(path,filename))

        return render(request,'website/bank_display.html',{
                'bank':banks,
                
                'bank_list':bank_list,
                'current_user': current_user, 
                 'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,  
            })
    


@login_or_head_required
def experience_display(request):
    current_user = request.user

    is_admin=request.session.get("is_admin",False)
    is_head=request.session.get("is_head",False)
    head_dept=request.session.get("head_department",None)
    if request.method == 'POST':
       
        field = request.POST['field']

        data = request.POST['q']
       


        if is_admin:
          
          if field=='specialization':
                filter_experience= Experience_Detail.objects.filter(specialization__icontains=data)
        
          else:
                filter_experience = Experience_Detail.objects.filter(**{f"{field}__iexact":data})

        elif is_head and head_dept:

            if field=='specialization':
                filter_experience= Experience_Detail.objects.filter(specialization__icontains=data)
        
            else:
                filter_experience = Experience_Detail.objects.filter(**{f"{field}__iexact":data},user__dept=head_dept)
        
       
        filter_experience_len=len(filter_experience_len)
        filter_experience_list = []
        f_count = 1
        for experience in filter_experience:
            filter_experience_list.append((f_count,experience))
            f_count+=1

     
             
        if is_admin or is_head:
            df = pd.DataFrame(list(filter_experience.values()))
            filename = 'Filter_experience_download.xlsx'
            path = '.\website\csv_files'
            df.to_excel(os.path.join(path,filename))

           
        if filter_experience_len == 0:
            return render(request,'website/experience_display.html',{
            'filter_field':field,
            'filter_data':data,
            'message':'No Data Available',
            'current_user': current_user,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,  
           
            })
        return render(request,'website/experience_display.html',{
            'filter_field':field,
            'filter_data':data,
            'filter_experience':filter_experience,
           
            'filter_experience_list':filter_experience_list,
            'current_user': current_user,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,  
            
    })
    else:
        current_user = request.user

        if is_admin:
            experiences= Experience_Detail.objects.all()
       
        elif is_head and head_dept:
           experiences= Experience_Detail.objects.filter(user__dept=head_dept).all()

       
        experience_list = []
        count = 1
        for experience in experiences:
                experience_list.append((count,experience))
                count+=1

        if is_admin or is_head:
            df = pd.DataFrame(list(experiences.values()))
            filename = 'Experience_download.xlsx'
            path = '.\website\csv_files'
            df.to_excel(os.path.join(path,filename))

        return render(request,'website/experience_display.html',{
                'experience':experiences,
                
                'experience_list':experience_list,
                'current_user': current_user,
                 'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,   
            })
        

@login_or_head_required
def research_display(request):
    current_user = request.user
    score, empty_list = profile(current_user)

    is_admin=request.session.get("is_admin",False)
    is_head = request.session.get("is_head", False)
    head_dept = request.session.get("head_department", None)

    if request.method == "POST":
        field = request.POST['field']
        data = request.POST['q']

    
        if is_admin:
            filter_papers = Paper_Publication.objects.filter(**{f"{field}__iexact":data})
        elif is_head and head_dept:
            filter_papers = Paper_Publication.objects.filter(**{f"{field}__iexact":data}, user__dept=head_dept)
        else:
            filter_papers = Paper_Publication.objects.filter(user=current_user, **{f"{field}__iexact":data})

        filter_papers_list = [(i+1, paper) for i, paper in enumerate(filter_papers)]

        
        df = pd.DataFrame(list(filter_papers.values()))
        path = './website/csv_files'
        df.to_excel(os.path.join(path, 'Filter_Paper_Download.xlsx'))

        if not filter_papers:
            return render(request, 'website/research_display.html', {
                'filter_field': field,
                'filter_data': data,
                'message': 'No Data Available',
                'current_user': current_user,
                'score': score,
                'empty_list': empty_list,
                'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
            })
        return render(request,'website/research_display.html',{
            'filter_field':field,
            'filter_data':data,
            'filter_papers':filter_papers,
            
            'filter_papers_len':range(1,len(filter_papers)+1),
            'filter_papers_list':filter_papers_list,
            'current_user': current_user,
            'score':score,
            'empty_list':empty_list,
        })
    else:
        # GET request: Show all records
        if is_admin:
            papers = Paper_Publication.objects.all()
            
        elif is_head and head_dept:
            papers = Paper_Publication.objects.filter(user__dept=head_dept)
        else:
            papers = Paper_Publication.objects.filter(user=current_user)

        papers_list = [(i+1, paper) for i, paper in enumerate(papers)]

        df = pd.DataFrame(list(papers.values()))
        path = './website/csv_files'
        df.to_excel(os.path.join(path, 'PhD_Download.xlsx'))

        return render(request, 'website/research_display.html', {
          'papers_list': papers_list,
            'current_user': current_user,
            'score': score,
            'empty_list': empty_list,
            'is_admin': is_admin,
            'is_head': is_head,
            'head_department': head_dept,
        })



@login_or_head_required
def phd_display(request):
    current_user = request.user
    score, empty_list = profile(current_user)

    is_admin=request.session.get("is_admin",False)
    is_head = request.session.get("is_head", False)
    head_dept = request.session.get("head_department", None)

    if request.method == "POST":
        field = request.POST['field']
        data = request.POST['q']

        # Filtering based on roles
        if is_admin:
            filter_phds = PHD_Awarded.objects.filter(**{f"{field}__iexact": data}).order_by('-registration_date')
        elif is_head and head_dept:
            filter_phds = PHD_Awarded.objects.filter(**{f"{field}__iexact": data}, user__dept=head_dept).order_by('-registration_date')
        else:
            filter_phds = PHD_Awarded.objects.filter(user=current_user, **{f"{field}__iexact": data}).order_by('-registration_date')

        filter_phds_list = [(i+1, phd) for i, phd in enumerate(filter_phds)]

        
        df = pd.DataFrame(list(filter_phds.values()))
        path = './website/csv_files'
        df.to_excel(os.path.join(path, 'Filter_PhD_Download.xlsx'))

        if not filter_phds:
            return render(request, 'website/phd_display.html', {
                'filter_field': field,
                
                'filter_data': data,
                'message': 'No Data Available',
                'current_user': current_user,
                'score': score,
                'empty_list': empty_list,
                'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
            })

        return render(request, 'website/phd_display.html', {
            'filter_field': field,
            'filter_data': data,
            'filter_phds_list': filter_phds_list,
            'current_user': current_user,
            'score': score,
            'empty_list': empty_list,
            'is_admin': is_admin,
            'is_head': is_head,
            'head_department': head_dept,
        })

    else:
        # GET request: Show all records
        if is_admin:
            phds = PHD_Awarded.objects.all().order_by('-registration_date')

           
        elif is_head and head_dept:
            phds = PHD_Awarded.objects.filter(user__dept=head_dept).order_by('-registration_date')
        else:
            phds = PHD_Awarded.objects.filter(user=current_user).order_by('-registration_date')


        
        df = pd.DataFrame(list(phds.values()))
        path = './website/csv_files'
        df.to_excel(os.path.join(path, 'PhD_Download.xlsx'))

        phds_list = [(i+1, phd) for i, phd in enumerate(phds)]

        return render(request, 'website/phd_display.html', {
            'phds_list': phds_list,
            'current_user': current_user,
            'score': score,
            'empty_list': empty_list,
            'is_admin': is_admin,
            'is_head': is_head,
            'head_department': head_dept,
        })



@login_or_head_required
def award_display(request):

    current_user = request.user
    score,empty_list = profile(current_user)

    is_admin=request.session.get("is_admin",False)
    is_head = request.session.get("is_head", False)
    head_dept=request.session.get("head_department",False)


    if request.method == "POST":
        

        field = request.POST['field']
        data = request.POST['q']
       
       
        if is_admin:
            
            filter_awards = Awards.objects.filter(**{f"{field}__iexact": data}).order_by('-date_award')




        elif is_head and head_dept:
             filter_awards = Awards.objects.filter(**{f"{field}__iexact": data},user__dept=head_dept).order_by('-date_award')
        else:
            filter_awards = Awards.objects.filter(**{f"{field}__iexact": data}).order_by('-date_award')
        filter_awards_len = len(filter_awards)

        filter_awards_list = []
        f_count = 1
        for award in filter_awards:
            filter_awards_list.append((f_count,award))
            f_count+=1

      
        df = pd.DataFrame(list(filter_awards.values()))
        filename = 'Filter_Awards_Download.xlsx'
        path = '.\website\csv_files'
        df.to_excel(os.path.join(path,filename))

       
        if filter_awards_len == 0:
            return render(request,'website/award_display.html',{
            'filter_field':field,
            'filter_data':data,
            'message':'No Data Available',
            'current_user': current_user,
            'score':score,
            'empty_list':empty_list,
              'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
            })
        return render(request,'website/award_display.html',{
            'filter_field':field,
            'filter_data':data,
            'filter_awards_list':filter_awards_list,
            'current_user': current_user,
            'score':score,
            'empty_list':empty_list,
            'is_admin': is_admin,
            'is_head': is_head,
            'head_department': head_dept,
        })

    else:
       
        if is_admin:
            awards = Awards.objects.all().order_by('-date_award') 
            
           

        elif is_head  and head_dept:
            awards= Awards.objects.filter(user__dept=head_dept).all().order_by('-date_award')


           
        else:
            awards = Awards.objects.filter(user = current_user).all().order_by('-date_award')

        awards_list=[]
        count = 1
        for award in awards:
            awards_list.append((count,award))
            count+=1

       
        df = pd.DataFrame(list(awards.values()))
        filename = 'Awards_Download.xlsx'
        path = '.\website\csv_files'
        df.to_excel(os.path.join(path,filename))

    
    return render(request,'website/award_display.html',{
                'awards_list':awards_list,
                'current_user': current_user,
                'score':score,
            'empty_list':empty_list,
              'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
            })
    

@login_or_head_required
def books_display(request):

    current_user = request.user

    is_admin=request.session.get("is_admin",False)
    is_head=request.session.get("is_head",False)
    head_dept=request.session.get("head_department",False)

    if request.method == 'POST':
       
        field = request.POST['field']
        data = request.POST['q']
      
       
        if is_admin:
            if field == 'authors':
                filter_books = Books.objects.filter(authors__icontains=data).order_by('-year_published')
            elif field == 'title':
                filter_books = Books.objects.filter(title__icontains=data).order_by('-year_published')
            else:
                filter_books = Books.objects.filter(**{f"{field}__iexact": data}).order_by('-year_published')



        elif is_head and head_dept:
            if field == 'authors':
                filter_books = Books.objects.filter(authors__icontains=data,user__dept=head_dept).all().order_by('-year_published')
            elif field == 'title':
                filter_books = Books.objects.filter(title__icontains=data,user__dept=head_dept).all().order_by('-year_published')
            else:
                filter_books = Books.objects.filter(**{f"{field}__iexact":data},user__dept=head_dept).all().order_by('-year_published')


        else:
            if field == 'authors':
                filter_books = Books.objects.filter(authors__icontains=data,authors__contains=data).order_by('-year_published')
            elif field == 'title':
                filter_books = Books.objects.filter(user=current_user,title__icontains=data).order_by('-year_published')
            else:
                filter_books = Books.objects.filter(**{f"{field}__iexact":data},user=current_user).order_by('-year_published')
        filter_books_len = len(filter_books)
        filter_books_list = []
        f_count = 1
        for book in filter_books:
            filter_books_list.append((f_count,book))
            f_count+=1

      
        df = pd.DataFrame(list(filter_books.values()))
        filename = 'Filter_Books_Download.xlsx'
        path = '.\website\csv_files'
        df.to_excel(os.path.join(path,filename))

        score,empty_list = profile(current_user)
        if filter_books_len == 0:
            return render(request,'website/books_display.html',{
            'filter_field':field,
            'filter_data':data,
            'message':'No Data Available',
            'current_user': current_user,
            'score':score,
            'empty_list':empty_list,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
            })
        return render(request,'website/books_display.html',{
            'filter_field':field,
            'filter_data':data,
            'filter_books_list':filter_books_list,
            'current_user': current_user,
            'score':score,
            'empty_list':empty_list,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
        })
    else:
        current_user = request.user
        score,empty_list = profile(current_user)
        if is_admin:
            books = Books.objects.all().order_by('-year_published') 
            

           
                

        elif is_head and head_dept:
            books = Books.objects.filter(user__dept=head_dept).order_by('-year_published')

            
        else:
            books = Books.objects.filter(user = current_user).order_by('-year_published') 

        df = pd.DataFrame(list(books.values()))
        filename = 'Books_Download.xlsx'
        path = '.\website\csv_files'
        df.to_excel(os.path.join(path,filename))
            

    books_list=[]
    count = 1
    for book in books:
        books_list.append((count,book))
        count+=1

    return render(request,'website/books_display.html',{
                'books_list':books_list,
                'current_user': current_user,
                'score':score,
            'empty_list':empty_list,
             'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
            })
        
@login_or_head_required
def conference_display(request):

    current_user = request.user

    is_admin=request.session.get("is_admin",False)
    is_head=request.session.get("is_head",False)
    head_dept=request.session.get("head_department",False)
    
    if request.method == "POST":
        current_user = request.user
        field = request.POST['field']
        data = request.POST['q']
        
        if is_admin:
            if field == 'authors':
                filter_conferences = Books_Conference.objects.filter(authors__icontains=data).order_by('-date')
            elif field == 'title_chap_paper':
                filter_conferences = Books_Conference.objects.filter(title_chap_paper__icontains=data).order_by('-date')
            elif field == 'title_book_conf':
                filter_conferences = Books_Conference.objects.filter(title_book_conf__icontains=data).order_by('-date')
            else:
                filter_conferences = Books_Conference.objects.filter(**{f"{field}__iexact":data}).order_by('-date')


        elif is_head and head_dept:

            if field == 'authors':
                filter_conferences = Books_Conference.objects.filter(authors__icontains=data,user__dept=head_dept).order_by('-date')
            elif field == 'title_chap_paper':
                filter_conferences = Books_Conference.objects.filter(title_chap_paper__icontains=data,user__dept=head_dept).order_by('-date')
            elif field == 'title_book_conf':
                filter_conferences = Books_Conference.objects.filter(title_book_conf__icontains=data,user__dept=head_dept).order_by('-date')
            else:
                filter_conferences = Books_Conference.objects.filter(**{f"{field}__iexact":data},user__dept=head_dept).order_by('-date')



        else:
            
            if field == 'authors':
                filter_conferences = Books_Conference.objects.filter(authors__icontains=data).order_by('-date')
            elif field == 'title_chap_paper':
                filter_conferences = Books_Conference.objects.filter(user=current_user,title_chap_paper__icontains=data).order_by('-date')
            elif field == 'title_book_conf':
                filter_conferences = Books_Conference.objects.filter(user=current_user,title_book_conf__icontains=data).order_by('-date')
            else:
                filter_conferences = Books_Conference.objects.filter(**{f"{field}__iexact":data},user=current_user).order_by('-date')
        filter_conferences_len = len(filter_conferences)
        filter_conferences_list = []
        f_count = 1
        for conference in filter_conferences:
            filter_conferences_list.append((f_count,conference))
            f_count+=1

      
        df = pd.DataFrame(list(filter_conferences.values()))
        filename = 'Filter_Conference_Download.xlsx'
        path = '.\website\csv_files'
        df.to_excel(os.path.join(path,filename))

        score,empty_list = profile(current_user)
        if filter_conferences_len == 0:
            return render(request,'website/conference_display.html',{
            'filter_field':field,
            'filter_data':data,
            'message':'No Data Available',
            'current_user': current_user,
            'score':score,
            'empty_list':empty_list,
            'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
            })
        return render(request,'website/conference_display.html',{
            'filter_field':field,
            'filter_data':data,
            'filter_conferences_list':filter_conferences_list,
            'current_user': current_user,
            'score':score,
            'empty_list':empty_list,
            'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
        })
    else:
        current_user = request.user
        score,empty_list = profile(current_user)
        if is_admin:
            conferences = Books_Conference.objects.all().order_by('-date') 
            conferences_list=[]
            count = 1
            for conference in conferences:
                conferences_list.append((count,conference))
                count+=1

            if is_admin:
                df = pd.DataFrame(list(conferences.values()))
                filename = 'Conference_Download.xlsx'
                path = '.\website\csv_files'
                df.to_excel(os.path.join(path,filename))

        

        elif is_head and head_dept:

            conferences= Books_Conference.objects.filter(user__dept=head_dept).all().order_by('-date')

            conferences_list=[]
            count = 1
            for conference in conferences:
                conferences_list.append((count,conference))
                count+=1

         
       
           


        else:
            conferences = Books_Conference.objects.filter(user = current_user).order_by('-date') 
            conferences_list=[]
            count = 1
            for conference in conferences:
                conferences_list.append((count,conference))
                count+=1

        df = pd.DataFrame(list(conferences.values()))
        filename = 'Conference_Download.xlsx'
        path = '.\website\csv_files'
        df.to_excel(os.path.join(path,filename))


    
    return render(request,'website/conference_display.html',{
            'conferences_list':conferences_list,
            'current_user': current_user,
            'score':score,
            'empty_list':empty_list,
            'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
            })       
        


        
@login_or_head_required
def patent_display(request):


    current_user = request.user

    is_admin=request.session.get("is_admin",False)
    is_head=request.session.get("is_head",False)
    head_dept=request.session.get("head_department",False)
    if request.method == "POST":
        
        field = request.POST['field']
        data = request.POST['q']
        
        if is_admin:
            if field == 'author_name':
                filter_patents = Patent.objects.filter(author_name__icontains=data).order_by('-patent_year')
            elif field == 'patent_title':
                filter_patents = Patent.objects.filter(patent_title__icontains=data).order_by('-patent_year')
            elif field == 'category':
                filter_patents = Patent.objects.filter(category__icontains=data).order_by('-patent_year')
            else:
                filter_patents = Patent.objects.filter(**{f"{field}__iexact":data}).order_by('-patent_year')



        elif is_head and head_dept:
            if field == 'author_name':
                filter_patents = Patent.objects.filter(author_name__icontains=data,user__dept=head_dept).order_by('-patent_year')
            elif field == 'patent_title':
                filter_patents = Patent.objects.filter(patent_title__icontains=data,user__dept=head_dept).order_by('-patent_year')
            elif field == 'category':
                filter_patents = Patent.objects.filter(category__icontains=data,user__dept=head_dept).order_by('-patent_year')
            else:
                filter_patents = Patent.objects.filter(**{f"{field}__iexact":data},user__dept=head_dept).order_by('-patent_year')
        else:
            if field == 'author_name':
                filter_patents = Patent.objects.filter(user=current_user,author_name__icontains=data).order_by('-patent_year')
            elif field == 'patent_title':
                filter_patents = Patent.objects.filter(user=current_user,patent_title__icontains=data).order_by('-patent_year')
            elif field == 'category':
                filter_patents = Patent.objects.filter(user=current_user,category__icontains=data).order_by('-patent_year')
            else:
                filter_patents = Patent.objects.filter(**{f"{field}__iexact":data}).order_by('-patent_year')
        filter_patents_len = len(filter_patents)
        filter_patents_list = []
        f_count = 1
        for patent in filter_patents:
            filter_patents_list.append((f_count,patent))
            f_count+=1

       
        df = pd.DataFrame(list(filter_patents.values()))
        filename = 'Filter_Patent_Download.xlsx'
        path = '.\website\csv_files'
        df.to_excel(os.path.join(path,filename))

        score,empty_list = profile(current_user)
        if filter_patents_len == 0:
            return render(request,'website/patent_display.html',{
            'filter_field':field,
            'filter_data':data,
            'message':'No Data Available',
            'current_user': current_user,
            'score':score,
            'empty_list':empty_list,
            'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
            })
        return render(request,'website/patent_display.html',{
            'filter_field':field,
            'filter_data':data,
            'filter_patents_list':filter_patents_list,
            'current_user': current_user,
            'score':score,
            'empty_list':empty_list,
            'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
        })
    else:
        
        score,empty_list = profile(current_user)
        if is_admin:
            patents = Patent.objects.all().order_by('-patent_year') 
            patents_list=[]
            count = 1
            for patent in patents:
                patents_list.append((count,patent))
                count+=1

         
        
        


        elif is_head and head_dept:

             patents= Patent.objects.filter(user__dept=head_dept).order_by('-patent_year')


        else:
            patents = Patent.objects.filter(user = current_user).all().order_by('-patent_year') 

        df = pd.DataFrame(list(patents.values()))
        filename = 'Patent_Download.xlsx'
        path = '.\website\csv_files'
        df.to_excel(os.path.join(path,filename))

        patents_list=[]
        count = 1
        for patent in patents:
            patents_list.append((count,patent))
            count+=1
    
    return render(request,'website/patent_display.html',{
            'patents_list':patents_list,
                'current_user': current_user,
                'score':score,
            'empty_list':empty_list,
            'is_admin': is_admin,
                'is_head': is_head,
                'head_department': head_dept,
            })

    
    
# edit info
@login_required(login_url=login_view)
def edit_patent(request,id):
    if request.method == 'POST':
        patent_number = request.POST["patent_number"]
        patent_title = request.POST["patent_title"]
        year_awarded = request.POST["year_awarded"]
        author_name = request.POST['author_name']
        category = request.POST['category']
        level = request.POST['level']
        patent_type=request.POST['patent_type']

        if(category=='Published'):
           date_published=request.POST['date_published']
        

        if(category=='Awarded/Granted'):
           date_award=request.POST['date_award']


        pattern1=r'^[A-Za-z0-9]+$'

        pattern2= r'^[A-Za-z0-9.,:;!?()&\'\"\- ]+$'
        pattern3=r'^[A-Za-z\s]+(\s*,\s*[A-Za-z\s]+)*\s*$'
        ans_error = False
        

      
        if not re.match(pattern2, patent_title):
            messages.error(request, 'Title can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True
            


        if not re.match(pattern1, patent_number):
            messages.error(request, 'Patent number can only contain letters and numbers.')
            ans_error = True

        if not re.match(pattern3,author_name):
            messages.error(request,'invalid author names,it should be in format author1 ,author2 ')
            ans_error = True
            
        

        if ans_error:
            return redirect(edit_patent,id=id)

        patent = Patent.objects.filter(user=request.user).get(id=id)
        patent.author_name = author_name
        patent.patent_number = patent_number
        patent.patent_title = patent_title
        patent.patent_year = year_awarded
        patent.category = category
        patent.level=level
        patent.patent_type=patent_type

        if(category=='Published'):
            patent.date_published=date_published

        if(category=='Awarded/Granted'):
            patent.date_award=date_award
        
        patent.save()

        messages.success(request, 'Patent Edited Successfully')

        return HttpResponseRedirect(reverse(patent_display))
    else:
        patent = Patent.objects.filter(user=request.user).get(id=id)
        score,empty_list = profile(request.user)
        return render(request,'website/patent.html',{
            'edit_patent':patent,
            'current_user': request.user,
            'mor_eve' : get_time_of_day(),
            'date': current_date(),
            'score':score,
            'empty_list':empty_list,
        })
    
@login_required(login_url=login_view)
def edit_phd(request,id):
    if request.method == 'POST':
        department = request.POST["department"]
        guide_names = request.POST["guide_names"]
        thesis_title = request.POST["thesis_title"]
        registration_date = request.POST["registration_date"]
        award_date = request.POST["award_date"]
        scholor_name = request.POST['scholor_name']
        enrollment_date=request.POST['enrollment_date']
        thesis_submission_date=request.POST['thesis_submit_date']
        thesis_awarded_date=request.POST['award_date']
        supervisor=request.POST['supervisor_name']
        co_supervisor=request.POST['co_supervisor_name']
        faculty_title=request.POST['faculty_title']


        pattern1= r'^[A-Za-z.\s]+$'
        pattern2= r"^[A-Za-z0-9.,:;!?()&'\"\- ]+$"
        ans_error = False
        

        if not re.match(pattern1, scholor_name):
            
            messages.error(request, 'Invalid Scholar Name! Use only letters, spaces, and dots.')
            ans_error = True
            
        
        if not re.match(pattern1, supervisor):
            
            messages.error(request, 'Invalid Supervisor Name! Use only letters, spaces, and dots.')
            ans_error = True

        if not re.match(pattern2, thesis_title):
            messages.error(request,'Title can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True
           
            


        if not re.match(pattern1, co_supervisor):
           
            messages.error(request, 'Invalid Co-Supervisor Name! Use only letters, spaces, and dots.')
            ans_error = True
            

        
        if ans_error:
            return redirect(edit_phd,id=id)



        phd = PHD_Awarded.objects.filter(user=request.user).get(id=id)
        phd.user = request.user
        phd.scholor_name = scholor_name
        phd.department = department
        phd.guide_names = guide_names
        phd.thesis_title = thesis_title
        phd.award_date = award_date
        phd.registration_date = registration_date
        phd.enrollment_date=enrollment_date
        phd.thesis_submission_date=thesis_submission_date
        phd.thesis_awarded_date=thesis_awarded_date
        phd.supervisor=supervisor
        phd.co_supervisor=co_supervisor
        phd.faculty_title=faculty_title
        phd.save()

        messages.success(request, 'Ph.D Edited Successfully')

        return HttpResponseRedirect(reverse(phd_display))
    else:
        phd = PHD_Awarded.objects.filter(user=request.user).get(id=id)
        score,empty_list = profile(request.user)
        return render(request,'website/phd.html',{
            'edit_phd':phd,
            'current_user': request.user,
            'mor_eve' : get_time_of_day(),
            'date': current_date(),
            'score':score,
            'empty_list':empty_list,
        })

@login_required(login_url=login_view) 
def edit_research(request,id):
    if request.method == "POST":
        title = request.POST["title"]
        author_names = request.POST["author_names"]
        journal_name = request.POST["journal_name"]
        journal_url = request.POST["journal_url"]
        issn = request.POST["issn"]
        publisher = request.POST["publisher"]
        month_published = request.POST["month_published"]
        year_published = request.POST["year_published"]
        volume_number = request.POST["volume_number"]
        issue_number = request.POST["issue_number"]
        pp = request.POST["pp"]
        doi = request.POST["doi"]
        ugc_core = request.POST["ugc_core"]
        scopus = request.POST["scopus"]
        sci_scie_esci = request.POST["sci_scie_esci"]
        if sci_scie_esci != 'None':
            impact_factor = request.POST["impact_factor"]

        pattern1 = r'^[A-Za-z0-9\s,.:&()\'-]+$'
        pattern2=r'^[0-9A-Za-z\-()]+$'
        pattern3=r'^\d+\s*-\s*\d+$'
        pattern4=r'^[A-Za-z0-9\-\/]+$'
        pattern5=r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
        pattern6=r'^\d+(\.\d{1,2})?$'
        pattern7=r'^[A-Za-z0-9&.,: \-]+$'
        pattern8= r'^[A-Za-z0-9.,:;!?()&\'\"\- ]+$'
        pattern9=r'^[A-Za-z\s]+(\s*,\s*[A-Za-z\s]+)*\s*$'
        pattern10=r'^\d{4}[-\s]?\d{4}$'
        pattern11 = r'^(https?://)?([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?$'
        ans_error = False




        

        if not re.match(pattern1,journal_name):
            
            messages.error(request, 'It can include letters (A-Z, a-z), numbers (0-9), spaces, and these special characters , . : & ( ) - ')
            ans_error = True
        if not re.match(pattern2,volume_number):
            
            messages.error(request,'it can include letters ,numbers,and special characters - () ')
            ans_error = True


        if not re.match(pattern3,pp):
            messages.error(request,'pp should be in the format of 12-34')
            ans_error = True

        if not re.match(pattern4,issue_number):
            messages.error(request,'Issue number can have numbers,letters,special characters  - /')
            ans_error = True

        if not re.match(pattern5,doi):
            messages.error(request,'A DOI must start with 10. followed by a numeric code, a /, and a unique suffix.Example: 10.1016/j.jss.2018.04.027')
            ans_error = True

        if not re.match(pattern6,impact_factor):
            messages.error(request,'Impact factor must be a number and can have up to two decimal places.')
            ans_error = True

        if not re.match(pattern7, publisher):
            
            messages.error(request, 'Publisher name can only contain letters, numbers, spaces, and & . , : - characters.')
            ans_error = True
        
        


        
        if not re.match(pattern8,title):
            messages.error(request,'Title can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True

        if not re.match(pattern9,author_names):
            messages.error(request,'invalid author names,it should be in format author1 ,author2 ')
            ans_error = True

        if not re.match(pattern10,issn):
            messages.error(request,'ISSN should be in the format of 1234-5678 or 12345678.')
            ans_error = True

        if not re.match(pattern11,journal_url):
            messages.error(request,'Invalid journal URL format.')
            ans_error = True

        if ans_error:
            return redirect(edit_research,id=id)

        paper = Paper_Publication.objects.filter(user=request.user).get(id=id)
        paper.user = request.user
        paper.title = title
        paper.author_names = author_names
        paper.journal_name = journal_name
        paper.journal_website = journal_url
        paper.issn = issn
        paper.publisher = publisher
        paper.month_published = month_published
        paper.year_published = year_published
        paper.volume_number = volume_number
        paper.issue_number = issue_number
        paper.pp = pp
        paper.doi = doi
        paper.ugc_core = ugc_core
        paper.scopus = scopus
        paper.sci_scie_esci = sci_scie_esci
        if sci_scie_esci != 'None':
            paper.impact_factor = impact_factor
        paper.save()

        messages.success(request, 'Research Paper Edited Successfully')

        return HttpResponseRedirect(reverse(research_display))
    else:
        research = Paper_Publication.objects.filter(user=request.user).get(id=id)
        score,empty_list = profile(request.user)
        return render(request,'website/research.html',{
            'edit_research':research,
            'current_user': request.user,
            'mor_eve' : get_time_of_day(),
            'date': current_date(),
            'score':score,
            'empty_list':empty_list,
        })
    
@login_required(login_url=login_view)
def edit_award(request,id):
    if request.method == "POST":
        activity = request.POST["activity"]
        award_name = request.POST["award_name"]
        authority_name = request.POST["authority_name"]
        date_award=request.POST['date_award']
        level = request.POST['level']
        awardee=request.POST['awardee_name']

        award = Awards.objects.filter(user=request.user).get(id=id)
        award.user = request.user


        pattern1 = r'^[A-Za-z0-9 .,\':&()\-:;!?\"\[\]]+$'
        pattern2 = r'^[A-Za-z.\s]+$'
        pattern3=r'^[A-Za-z0-9.,\'’\-()&\s]+$'

        ans_error = False
       


        if not re.match(pattern1, activity):
            
            messages.error(request, 'Name of the activity can only contain letters, numbers, spaces, and common symbols: . , \' : & ( ) - ; ! ? " [ ]')
            ans_error=True
            
        
        if not re.match(pattern3, award_name):  
            messages.error(request,'Award name can only contain letters,numbers,spaces and these symbols . , \' ’ \-( ) &')
            ans_error=True



         
        if not re.match(pattern3, authority_name):  
            messages.error(request,'Authority name can only contain letters,numbers,spaces and these symbols . , \' ’ \-( ) &')
            ans_error=True
       
        
        

        if not re.match(pattern2, awardee):
            
            messages.error(request, 'Awardee Name! Use only letters, spaces, and dots.')
            ans_error=True

        if ans_error:
            return redirect('edit_award',id=id)
        
       

        
        award.activity = activity
        award.award_name = award_name
        award.authority_name = authority_name
        
        award.level = level
        award.date_award=date_award
        award.awardee=awardee
        award.save()

        messages.success(request, 'Award Edited Successfully')

        return HttpResponseRedirect(reverse(award_display))
    else:
        award = Awards.objects.filter(user=request.user).get(id=id)
        score,empty_list = profile(request.user)
        return render(request,'website/award.html',{
            'edit_award':award,
            'current_user': request.user,
            'mor_eve' : get_time_of_day(),
            'date': current_date(),
            'score':score,
            'empty_list':empty_list,
        })

@login_required(login_url=login_view)
def edit_book(request,id):
    if request.method == "POST":
        author_name = request.POST["author_name"]
        book_title = request.POST["book_title"]
        publisher = request.POST["publisher"]
        isbn = request.POST["isbn"]
        year_published = request.POST["year_published"]
        affiliate_uni = request.POST['affiliate_uni']
        level=request.POST['level']

        

        pattern1=r'^[A-Za-z0-9&.,: \-]+$'
        pattern2= r'^[A-Za-z0-9.,:;!?()&\'\"\- ]+$'

        pattern3=r'^[A-Za-z0-9 .,\'&() \-]+$'
        pattern4=r'^[A-Za-z\s]+(\s*,\s*[A-Za-z\s]+)*\s*$'
        pattern5=r'^(?:\d{3}[- ]?)?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,7}[- ]?\d{1,7}$'


        ans_error = False



      

        if not re.match(pattern1, publisher):
            
            messages.error(request, 'Publisher name can only contain letters, numbers, spaces, and & . , : - characters.')
            ans_error = True
        
        


        
        if not re.match(pattern2, book_title):
            messages.error(request,'Title can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True



        if not re.match(pattern3, affiliate_uni):
            messages.error(request, 'Affiliate University can only contain letters, numbers, spaces and symbols . , \' & () -')
            ans_error = True

        if not re.match(pattern4,author_name):
            messages.error(request,'invalid author names,it should be in format author1 ,author2 ')
            ans_error = True

        if not re.match(pattern5,isbn):
            messages.error(request,'invalid isbn number')
            ans_error = True
        
        
        if ans_error:
            return redirect(edit_book,id=id)
        
        books = Books.objects.filter(user=request.user).get(id=id)
        books.user = request.user
        books.authors = author_name
        books.title = book_title
        books.publisher = publisher
        books.isbn = isbn
        books.year_published = year_published
        books.affiliating_institute = affiliate_uni
        books.level=level
        books.save()

        messages.success(request, 'Book Edited Successfully')

        return HttpResponseRedirect(reverse(books_display))
    else:
        book = Books.objects.filter(user=request.user).get(id=id)
        score,empty_list = profile(request.user)
        return render(request,'website/books.html',{
            'edit_book':book,
            'current_user': request.user,
            'mor_eve' : get_time_of_day(),
            'date': current_date(),
            'score':score,
            'empty_list':empty_list,
        })
    
@login_required(login_url=login_view)
def edit_conference(request,id):
    if request.method == "POST":
        author_name = request.POST["author_name"]
        category = request.POST["category"]
        type = request.POST["type"]
        publisher = request.POST["publisher"]
        date = request.POST["date"]
        title_ch_paper = request.POST['title_ch_paper']
        title_book_conf = request.POST['title_book_conf']
        isbn = request.POST['isbn']
        pp = request.POST['pp']

        pattern1=r'^[A-Za-z0-9&.,: \-]+$'
        pattern2= r"^[A-Za-z0-9.,:;!?()&'\"\- ]+$"

        pattern3 = r'^[A-Za-z\s]+(?:,\s?[A-Za-z\s]+)?$'

        pattern4=r'^[A-Za-z\s]+(\s*,\s*[A-Za-z\s]+)*\s*$'
        pattern5=r'^(?:\d{3}[- ]?)?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,7}[- ]?\d{1,7}$'
        ans_error = False


        if not re.match(pattern1, publisher):
            
            messages.error(request, 'Publisher name can only contain letters, numbers, spaces, and & . , : - characters.')
            ans_error = True
        
        


        
        if not re.match(pattern2, title_ch_paper):
            messages.error(request,'Title can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True
        
        if not re.match(pattern2, title_book_conf):
            messages.error(request,'Title  can only contain letters, numbers, spaces, and these symbols: . , : ; ! ? ( ) & \' " -')
            ans_error = True

        if not re.match(pattern3,pp):
            messages.error(request,'Place of Publication (PP) can only have data in this format, for example: New York, USA')
            ans_error = True

        if not re.match(pattern4,author_name):
            messages.error(request,'invalid author names,it should be in format author1 ,author2 ')
            ans_error = True

        if not re.match(pattern5,isbn):
            messages.error(request,'invalid isbn number')
            ans_error = True

        

        if ans_error:
            return redirect(edit_conference,id=id)
        
        books_conf = Books_Conference.objects.filter(user=request.user).get(id=id)
        books_conf.user = request.user
        books_conf.authors = author_name
        books_conf.category = category
        books_conf.publisher = publisher
        books_conf.isbn = isbn
        books_conf.title_book_conf = title_book_conf
        books_conf.title_chap_paper = title_ch_paper
        books_conf.type_conf = type
        books_conf.date = date
        books_conf.pp = pp
        books_conf.save()

        messages.success(request, 'Conference Edited Successfully')

        return HttpResponseRedirect(reverse(conference_display))
    else:
        conference = Books_Conference.objects.filter(user=request.user).get(id=id)
        score,empty_list = profile(request.user)
        return render(request,'website/conference.html',{
            'edit_conference':conference,
            'current_user': request.user,
            'mor_eve' : get_time_of_day(),
            'date': current_date(),
            'score':score,
            'empty_list':empty_list,
        })
    
   
'''
    Delete the Info
'''
@login_required(login_url=login_view)
def delete_patent(request,id):
    patent = Patent.objects.filter(user=request.user).get(id=id)
    patent.delete()
    messages.error(request, f'{patent.patent_title} Removed')
    return HttpResponseRedirect(reverse(patent_display))

@login_required(login_url=login_view)
def delete_phd(request,id):
    phd = PHD_Awarded.objects.filter(user=request.user).get(id=id)
    phd.delete()
    messages.error(request, f'{phd.scholor_name} Removed')
    return HttpResponseRedirect(reverse(phd_display))

@login_required(login_url=login_view)
def delete_research(request,id):
    research = Paper_Publication.objects.filter(user=request.user).get(id=id)
    research.delete()
    messages.error(request, f'{research.title} Removed')
    return HttpResponseRedirect(reverse(research_display))

@login_required(login_url=login_view)
def delete_award(request,id):
    award = Awards.objects.filter(user=request.user).get(id=id)
    award.delete()
    messages.error(request, f'{award.award_name} Removed')
    return HttpResponseRedirect(reverse(award_display))

@login_required(login_url=login_view)
def delete_book(request,id):
    book = Books.objects.filter(user=request.user).get(id=id)
    book.delete()
    messages.error(request, f'{book.title} Removed')
    return HttpResponseRedirect(reverse(books_display))

@login_required(login_url=login_view)
def delete_conference(request,id):
    conference = Books_Conference.objects.filter(user=request.user).get(id=id)
    conference.delete()
    messages.error(request, f'{conference.title_book_conf} Removed')
    return HttpResponseRedirect(reverse(conference_display))


'''
    CSV Download FILES
'''

@login_or_head_required
def patent_download(request):
    if request.method=="GET" and 'patent' in request.GET:
        filename = 'Patent_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))

        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Patents_CSV_Downloads.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index','Author Name', 'Patent Number', 'Patent Title', 'Category','Patent Year', 'Level', 'Patent Type', 'Date Published', 'Date Awarded'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['author_name'], row['patent_number'], row['patent_title'], row['category'],str(row['patent_year']).replace(' 00:00:00',''),row['level'],row['patent_type'],row['date_published'],row['date_award']])    
        return response
    elif request.method == "GET" and 'filter_patent' in request.GET:
        filename = 'Filter_Patent_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Filter_Patents_CSV_Download.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index','Author Name', 'Patent Number', 'Patent Title', 'Category','Patent Year', 'Level', 'Patent Type', 'Date Published', 'Date Awarded'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['author_name'], row['patent_number'], row['patent_title'], row['category'],str(row['patent_year']).replace(' 00:00:00',''),row['level'],row['patent_type'],row['date_published'],row['date_award']])    

        return response
    
@login_or_head_required
def research_download(request):
    if request.method =="GET" and 'research' in request.GET:
        filename = 'Research_Paper_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Research_Paper_CSV_Download.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index', 'Title', 'Author Name(s)', 'Journal Name', 'Journal Website', 'ISSN','Publisher', 'Month Published', 'Year Published', 'Volume Number', 'Issue Number', 'PP', 'D.O.I', 'UGC Core', 'Scopus', 'SCI/SCIE/ESCI', 'Impact Factor'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['title'], row['author_names'], row['journal_name'], row['journal_website'], row['issn'], row['publisher'], row['month_published'], row['year_published'], row['volume_number'], row['issue_number'], row['pp'], row['doi'], row['ugc_core'], row['scopus'], row['sci_scie_esci'], row['impact_factor']])
        return response
    elif request.method == "GET" and 'filter_research' in request.GET:
        filename = 'Filter_Research_Paper_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Filter_Research_Paper_CSV_Download.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index', 'Title', 'Author Name(s)', 'Journal Name', 'Journal Website', 'ISSN','Publisher', 'Month Published', 'Year Published', 'Volume Number', 'Issue Number', 'PP', 'D.O.I', 'UGC Core', 'Scopus', 'SCI/SCIE/ESCI', 'Impact Factor'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['title'], row['author_names'], row['journal_name'], row['journal_website'], row['issn'], row['publisher'], row['month_published'], row['year_published'], row['volume_number'], row['issue_number'], row['pp'], row['doi'], row['ugc_core'], row['scopus'], row['sci_scie_esci'], row['impact_factor']])    

        return response

@login_or_head_required
def phd_download(request):
    if request.method =="GET" and 'phd' in request.GET:
        filename = 'PhD_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Phd_CSV_Download.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index', 'Scholor Name', 'Department',  'Thesis Title', 'Thesis submission date','Thesis awarded date','Supervisor Name','Co-Supervisor Name','Faculty Title','Registration Date',])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['scholor_name'], row['department'], row['thesis_title'], row['thesis_submission_date'],row['thesis_awarded_date'],row['supervisor_name'],row['co_supervisor_name'],row['faculty_title'],str(row['registration_date']).replace(' 00:00:00','')])    

        return response
    elif request.method == "GET" and 'filter_phd' in request.GET:
        filename = 'Filter_PhD_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Filter_PhD_CSV_Download.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index', 'Scholor Name', 'Department',  'Thesis Title', 'Thesis submission date','Thesis awarded date','Supervisor Name','Co-Supervisor Name','Faculty Title','Registration Date',])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['scholor_name'], row['department'], row['thesis_title'], row['thesis_submission_date'],row['thesis_awarded_date'],row['supervisor_name'],row['co_supervisor_name'],row['faculty_title'],str(row['registration_date']).replace(' 00:00:00','')])    
        return response
    
@login_or_head_required
def award_download(request):
    if request.method =="GET" and 'award' in request.GET:
        filename = 'Awards_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Awards_CSV_Download.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index','Activity', 'Award Name', 'Authority Name', 'Year Awarded','Level','Awardee'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['activity'], row['award_name'], row['authority_name'], row['date_award'], row['level'],row['awardee']])    

        return response
    elif request.method == "GET" and 'filter_award' in request.GET:
        filename = 'Filter_Awards_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Filter_Awards_CSV_Download.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index','Activity', 'Award Name', 'Authority Name', 'Year Awarded','Level','Awardee'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['activity'], row['award_name'], row['authority_name'], row['date_award'], row['level'],row['awardee']])    

        return response

@login_or_head_required   
def books_download(request):
    if request.method =="GET" and 'books' in request.GET:
        filename = 'Books_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Books_CSV_Download.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index', 'Author Name(s)', 'Title', 'Publisher', 'ISBN', 'Year Published', 'Affiliating Institute','Level'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['authors'], row['title'], row['publisher'], row['isbn'], row['year_published'], row['affiliating_institute'],row['level']])    

        return response
    elif request.method == "GET" and 'filter_books' in request.GET:
        filename = 'Filter_Books_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Filter_Books_CSV_Download.csv"'},
        )
        
        writer = csv.writer(response)
        writer.writerow(['Index', 'Author Name(s)', 'Title', 'Publisher', 'ISBN', 'Year Published', 'Affiliating Institute','Level'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['authors'], row['title'], row['publisher'], row['isbn'], row['year_published'], row['affiliating_institute'],row['level']])    

        return response

@login_or_head_required   
def conference_download(request):
    if request.method =="GET" and 'conference' in request.GET:
        filename = 'Conference_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Conference_Proceedings_CSV_Download.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index', 'Author Name(s)', 'Category', 'Title of Chapter/Paper', 'Title of Book/Conference', 'Type of Conference', 'Date', 'ISBN', 'Publisher', 'PP'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['authors'], row['category'], row['title_chap_paper'], row['title_book_conf'], row['type_conf'], str(row['date']).replace(' 00:00:00',''), row['isbn'], row['publisher'], row['pp']])    

        return response
    
    elif request.method == "GET" and 'filter_conference' in request.GET:
        filename = 'Filter_Conference_Download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Filter_Conference_Proceedings_CSV_Download.csv"'},
        )
        
        writer = csv.writer(response)
        writer.writerow(['Index', 'Author Name(s)', 'Category', 'Title of Chapter/Paper', 'Title of Book/Conference', 'Type of Conference', 'Date', 'ISBN', 'Publisher', 'PP'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['authors'], row['category'], row['title_chap_paper'], row['title_book_conf'], row['type_conf'], row['date'], row['isbn'], row['publisher'], row['pp']])    
        return response



from .helpers import forget_password_mail,forget_password_mail_admin
import uuid
def forget_password(request):
    if request.method == 'POST':
        aadhar_number = request.POST['aadhar']

        try:
            user_obj = User.objects.exclude(username='admin').get(aadhar_number=aadhar_number)
        except User.DoesNotExist:
            messages.warning(request, 'No user found')
            return render(request, 'website/forget_password.html')
        
        token = str(uuid.uuid4())
        user_obj.password_reset_token = token
        user_obj.save()
        ans=forget_password_mail(user_obj.email,token,user_obj.employee_name)

        if ans==True:
             return render(request,'website/success.html',{
            'heading' : 'Mail Sent Successfully',
            'message' : 'A password reset mail has been sent to the email id linked to your account. Remember this mail can be used only once.',
        })

        else:
             messages.error(request, 'We could not send a password reset email at this moment. Please try again later.')
             return render(request, 'website/forget_password.html')

       

    else:
        return render(request,'website/forget_password.html')


def change_password(request,token):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        aadhar = request.POST['aadhar']

        user_id = User.objects.filter(password_reset_token = token).first()

        if user_id is None:
            messages.warning(request,'No user id given')
            return render(request, 'website/password_change.html',{'token': token})
        
        
        if new_password != confirm_password:
            messages.warning(request, "Passwords don't match")  

            return render(request, 'website/password_change.html',{'token': token})
        
        
        try:
            user_obj = User.objects.get(aadhar_number=aadhar)
        except User.DoesNotExist:
           messages.warning(request, "Invalid Aadhar number")
           return render(request, 'website/password_change.html', {'token': token})


        user_obj.set_password(new_password)
        user_obj.save()

        return render(request,'website/success.html',{
            'heading':'Password Changed Successfully',
            'message':f'Hi {user_obj.employee_name},\n Aadhar Number {user_obj.aadhar_number},\n Your Password has been reset successfully.',
            'user' : user_obj,
            'msg':'useriam',
        })
    else:
        user_id = User.objects.filter(password_reset_token = token).first()
        if not user_id:
            
            return redirect('login')
        return render(request,'website/password_change.html',
            {
                'token':token,
                'user_obj':user_id
            })
    



def forget_password_admin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        aadhar_number = request.POST['aadhar']


        try:
            user_obj = User.objects.get(aadhar_number=aadhar_number,username='admin')
        except User.DoesNotExist:
            messages.warning(request, 'No user found')
            return render(request, 'website/forget_password_admin.html')
        
        token = str(uuid.uuid4())
        user_obj.password_reset_token = token
        user_obj.save()
        ans=forget_password_mail_admin(user_obj.email,token)


        if ans==True:
             return render(request,'website/success.html',{
            'heading' : 'Mail Sent Successfully',
            'message' : 'A password reset mail has been sent to the email id linked to your account. Remember this mail can be used only once.',
        })

        else:
             messages.error(request, 'We could not send a password reset email at this moment. Please try again later.')
             return render(request, 'website/forget_password_admin.html')

    else:
        return render(request,'website/forget_password_admin.html')
    


def change_password_admin(request,token):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        email = request.POST.get('email')
        aadhar=request.POST.get('aadhar')

        user_id = User.objects.filter(password_reset_token = token).first()

        if user_id is None:
            messages.warning(request, 'No user id given')
            return render(request, 'website/password_change_admin.html', {'token': token})
        
        if new_password != confirm_password:
            messages.warning(request, "Passwords don't match")
            return render(request, 'website/password_change_admin.html', {'token': token})
        
        try:
            user_obj = User.objects.get(aadhar_number=aadhar)
        except User.DoesNotExist:
           messages.warning(request, "Invalid Aadhar number")
           return render(request, 'website/password_change_admin.html', {'token': token})
        user_obj.set_password(new_password)
        user_obj.save()

        return render(request,'website/success.html',{
            'heading':'Password Changed Successfully',
            'message':'Your Password has been reset successfully.',
            'user' : user_obj
            
         
        })
    else:
        user_id = User.objects.filter(password_reset_token = token).first()
        if not user_id:
            
            return render('login')
        
        return render(request,'website/password_change_admin.html',
            {
                'token':token,
                'user_obj':user_id
            })
    




@admin_or_head_required
def personal_data_download(request):
    if request.method=="GET" and 'filter_personal' in request.GET:
        filename = 'Filter_personal_download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))

        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="PersonalData_CSV_Downloads.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Index','Employee name','Father Name', 'Mother Name', 'Date Of Birth', 'Blood Group','Gender','Maritial Status','Spouse Name','GPF/NPS no.'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['employee_name'],row['father_name'], row['mother_name'], row['date_of_birth'], row['blood_group'], row['gender'], row['maritial_status'], row['spouse_name'], row['gpf_ornps']])    

        return response
    elif request.method == "GET" and 'personal' in request.GET:
        filename = 'Personal_details_download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="PersonalData_CSV_Downloads.csv"'},
        )

        writer = csv.writer(response)
       
        writer.writerow(['Index','Father Name', 'Mother Name', 'Date Of Birth', 'Blood Group','Gender','Maritial Status','Spouse Name','GPF/NPS no.'])
       
        for index, row in df.iterrows():
            writer.writerow([index+1,row['father_name'], row['mother_name'], row['date_of_birth'], row['blood_group'], row['gender'], row['maritial_status'], row['spouse_name'], row['gpf_ornps']])    
        return response
    

@admin_or_head_required
def work_data_download(request):
    if request.method=="GET" and 'filter_work' in request.GET:
        filename = 'Filter_work_details_download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))

        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="WorkData_CSV_Downloads.csv"'},
        )

        writer.writerow(['Index','Designation', 'mode_of_Recruitment', 'Dob_joining', 'Dob_Retirement',])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['designation'], row['mode_of_recruitment'], row['dob_joining'], row['dob_retirement']])    
        return response
    
    elif request.method == "GET" and 'work' in request.GET:
        filename = 'work_download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="WorkData_CSV_Downloads.csv"'},
        )

        writer = csv.writer(response)
       
        writer.writerow(['Index','Designation', 'mode_of_Recruitment', 'Dob_joining', 'Dob_Retirement',])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['designation'], row['mode_of_recruitment'], row['dob_joining'], row['dob_retirement']])    
        return response
    


@admin_or_head_required
def contact_data_download(request):
    if request.method=="GET" and 'filter_contact' in request.GET:
        filename = 'Filter_contact_download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))

        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="ContactData_CSV_Downloads.csv"'},
        )

        writer = csv.writer(response)
       
        writer.writerow(['Aadhar','Pan_number',  'State ', 'District','Pin','Mobile','Mobile_alt','Personal_email','Official_email','Corresponding_address','Permanent_address'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['aadhar'], row['pan_number'], row['state '], row['district'], row['pin'], row['mobile'], row['mobile_alt'], row['personal_email'],row['official_email'],row['corresponding_address'],row['permanent_address']])    
        return response
    
    elif request.method == "GET" and 'contact' in request.GET:
        filename = 'contact_download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="ContactData_CSV_Downloads.csv"'},
        )

        writer = csv.writer(response)
       
        writer.writerow(['Aadhar','Pan_number', 'Mother Name', 'State ', 'District','Pin','Mobile','Mobile_alt','Personal_email','Official_email','Corresponding_address','Permanent_address','Employee Name'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['aadhar'], row['pan_number'], row['state'], row['district'], row['pin'], row['mobile'], row['mobile_alt'], row['personal_email'],row['official_email'],row['corresponding_address'],row['permanent_address'],row['employee_name']])    
        return response
    
@admin_or_head_required
def bank_data_download(request):
    if request.method=="GET" and 'filter_bank' in request.GET:
        filename = 'Filter_bank_download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))

        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="BankData_CSV_Downloads.csv"'},
        )

        writer = csv.writer(response)
       
        writer.writerow(['Bank_Name','Bank_ifsc', 'bank_account', 'bank_branch '])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['bank_nam'], row['bank_ifsc'], row['bank_account'], row['bank_branch']])    
        return response
    
    elif request.method == "GET" and 'bank' in request.GET:
        filename = 'Bank_download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="BanklData_CSV_Downloads.csv"'},
        )

        writer = csv.writer(response)
       
        writer.writerow(['Bank_Name','Bank_ifsc', 'bank_account', 'bank_branch '])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['bank_name'], row['bank_ifsc'], row['bank_account'], row['bank_branch']])    
        return response
    

@admin_or_head_required
def experience_data_download(request):
    if request.method=="GET" and 'filter_experience' in request.GET:
        filename = 'Filter_experience_download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))

        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="ExperienceData_CSV_Downloads.csv"'},
        )

        writer = csv.writer(response)
       
        writer = csv.writer(response)
       
        writer.writerow(['Teaching_experience','Research_experience', 'Industry_experience', 'Pup_Teaching_experience','Specialization','Undergraduate','Postgraduate'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['teaching_experience'], row['research_experience'], row['industry_experience'], row['pup_teaching_experience'],row['specialization'],row['undergraduate'],row['postgraduate']])    
        return response
    
    elif request.method == "GET" and 'experience' in request.GET:
        filename = 'Experience_download.xlsx'
        path = '.\website\csv_files'
        df = pd.read_excel(os.path.join(path,filename))
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="ExperienceData_CSV_Downloads.csv"'},
        )

        writer = csv.writer(response)
       
        writer.writerow(['Teaching_experience','Research_experience', 'Industry_experience', 'Pup_Teaching_experience','Specialization','Undergraduate','Postgraduate'])
        for index, row in df.iterrows():
            writer.writerow([index+1,row['teaching_experience'], row['research_experience'], row['industry_experience'], row['pup_teaching_experience'],row['specialization'],row['undergraduate'],row['postgraduate']])    
        return response