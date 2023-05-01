from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import CreateUserForm
import os
import zipfile
import shutil
import tempfile
import docx2txt
import spacy
import re
import docx
from .forms import UploadFileForm
from . import resume_processor
from datetime import datetime
from collections import defaultdict

@login_required(login_url='login')
def help_page(request):
    return render(request, 'accounts/help.html')

@login_required(login_url='login')
def contact_page(request):
    return render(request, 'accounts/contact.html')

@login_required(login_url='login')
def search(request):
    query = request.GET.get('query')
    if query.lower() == 'help':
        return redirect('help')
    elif query.lower() == 'contact' or query.lower() == 'contacts':
        return redirect('contact')
    else:
        return redirect('zero_result')

@login_required(login_url='login')
def zero_result(request):
    return render(request, 'accounts/zero_results.html')

@login_required(login_url='login')
def clear_history(request):
    user_instance, _ = Users.objects.get_or_create(email=request.user.email)
    SavedResult.objects.filter(user=user_instance).delete()
    messages.success(request, 'History cleared successfully.')
    return redirect('view_saved_results')

@login_required(login_url='login')
def save_results(request):
    top_resumes = request.session.get('top_resumes', {})

    print(f"Top resumes: {top_resumes}")  

    user_instance, _ = Users.objects.get_or_create(email=request.user.email)

    for level, resumes in enumerate(top_resumes):
        for resume in resumes:
            result = SavedResult(
                user=user_instance,
                level=level + 1,
                filename=resume['filename'],
                score=resume['score'],
                name=resume['name'],
                phone_number=resume['phone_number'],
                email=resume['email'],
                date_created=timezone.now()  
            )
            result.save()
            print(f"Saved result: {result}")  

    messages.success(request, 'Results saved successfully.')
    return redirect('home')


@login_required(login_url='login')
def view_saved_results(request):
    user_instance, _ = Users.objects.get_or_create(email=request.user.email)
    saved_results = SavedResult.objects.filter(user=user_instance).order_by('date_created', '-level', '-score')

    submissions = defaultdict(list)
    for result in saved_results:
        date_time = result.date_created.strftime('%Y-%m-%d %H:%M:%S')
        submissions[date_time].append(result)

    submissions = dict(submissions)

    context = {'submissions': submissions}
    return render(request, 'accounts/saved_results.html', context)


def remove_random_string(filename):
    return re.sub(r'_\w+(\.docx)$', r'.docx', filename)


@login_required(login_url='login')
def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print("Form is valid:", form.is_valid())
        if form.is_valid():
            files = request.FILES.getlist('file_field')
            file_paths = []
            fs = FileSystemStorage()
            for file in files:
                if os.path.splitext(file.name)[1].lower() == '.docx':
                    filename = fs.save(file.name, file)
                    file_path = fs.path(filename)
                    file_paths.append(file_path)
                else:
                    messages.error(request, f"Invalid file format: {file.name}. Please upload only .docx files.")

            if not file_paths: 
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            requirements = form.cleaned_data['requirements']
            top_resumes = resume_processor.process_resumes(file_paths, requirements)
            print("Top Resumes:", top_resumes)
            request.session['top_resumes'] = top_resumes
            return result(request)  
    else:
        form = UploadFileForm()
    return render(request, 'accounts/hone.html', {'form': form})




@login_required(login_url='login')
def result(request):
    print("Result view called")  
    top_resumes = request.session.get('top_resumes', {})

    for level in top_resumes:
        for resume in level:
            resume['filename'] = remove_random_string(resume['filename'])

    print(top_resumes)
    return render(request, 'accounts/result.html', {'top_resumes': top_resumes})


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                return redirect('login')
        context = {'form': form}
        return render(request, 'accounts/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR Password is incorrect')

        context = {}
        return render(request, 'accounts/login.html', context)

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    context = {}
    return render(request, 'accounts/home.html', context)

@login_required(login_url='login')
def azPage(request):
    return render(request, 'accounts/AZ.html')

@login_required(login_url='login')
def rusPage(request):
    return render(request, 'accounts/RUS.html')

@login_required(login_url='login')
def engPage(request):
    return render(request, 'accounts/ENG.html')


