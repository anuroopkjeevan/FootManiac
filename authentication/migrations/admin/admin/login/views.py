from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True,max_age=0)
def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method =='POST':
        username=request.POST['username']
        pass1=request.POST['pass1']
        
        user=authenticate(username=username,password=pass1)
        
        if user is not None:
            login(request,user)
            return redirect('home')
        
        else:
            messages.error(request,"Incorrect username or password")
            return redirect('signin')
    return render(request, 'signin.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True,max_age=0)
def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method =='POST':
        username=request.POST['username']
        name=request.POST['name']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        
        
        if User.objects.filter(username=username):
            messages.error(request, "username already exists !,Try another username")
            return redirect("signup")
        if User.objects.filter(email=email):
            messages.error(request,"Email already registered.")
            return redirect('signup')
        if pass1 != pass2:
            messages.error(request ,"Password didnt match")
            return redirect('signup')
        
        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name=name
        
        myuser.save()
        
        messages.success(request,'Your account has been succesfully created')
        return redirect('signin')
    return render(request ,'signup.html')
@cache_control(no_cache=True, must_revalidate=True, no_store=True,max_age=0)
def home(request):
    if request.user.is_authenticated:
        name=request.user.first_name
        return render(request,'home.html',{'name': name})
    else:
        messages.error(request,'Please Login')
        return redirect('signin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True,max_age=0)
def signout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,'Logged Out succesfully')
        # return render(request,'signin.html')
    # else:
        return redirect('signin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True,max_age=0)
def admin_panel(request):
    if request.user.is_superuser:
        
        if request.GET.get('search') is not None:
            search=request.GET.get('search')
            users=User.objects.filter(username__contains=search)
        else:
            users=User.objects.all()
        context={
            'users':users
        }
        return render(request, 'admin_panel.html',context)
    else:
        return redirect('home')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True,max_age=0)
def update_user(request,user_id):
    if request.user.is_superuser:

        user=User.objects.get(id=user_id)
        
        if request.method == 'POST':
            username=request.POST['username']
            email=request.POST['email']
            name=request.POST['name']
            password=request.POST['pass1']
            
            user.username=username
            user.first_name=name
            user.email=email
            user.set_password=password
            
            user.save()
            messages.success(request,'Updated succesfully')
            
            return redirect('admin_panel')
        
        return render(request,'edit.html' , {'user':user})
    else:
        return redirect('home')

@cache_control(no_cache=True, must_revalidate=True, no_store=True,max_age=0)
def delete_user(request,user_id):
    if request.user.is_superuser:
        
        user=User.objects.get(id=user_id)
        
        user.delete()
        
        return redirect('adminpanel')
    else:
        return redirect('home')
     
@cache_control(no_cache=True, must_revalidate=True, no_store=True,max_age=0)
def create_user(request):
    if request.user.is_superuser:

        if request.method =='POST':
            username=request.POST['username']
            name=request.POST['name']
            email=request.POST['email']
            password=request.POST['pass1']
            
            myuser=User.objects.create_user(username,email,password)
            myuser.first_name=name
            
            myuser.save()
            messages.success(request,'Account successfully created')
            return redirect('admin_panel')
            
        return render(request,'create_user.html')
    else:
        return redirect('home')