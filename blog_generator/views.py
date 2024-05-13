from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from pytube import YouTube
from django.conf import settings
import os
import assemblyai as aai
import openai 
from .models import BlogPost
# Create your views here.

@login_required
def home(request):
    return render(request,'index.html')

def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file,new_file)
    return new_file

def get_transcript(link):
    audio_file = download_audio(link)
    aai.settings.api_key = "3bcdcbd58da244a0a357a5ad0e8f3688"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript.text

def generate_blog_from_transcription(transcript):
    openai.api_key = "sk-proj-SRCC281LdYtEsb15lchbT3BlbkFJopA3YJgajdWL1EV44vUl"
    prompt = f'Based on the following transcript from a Youtube video, write a comprehensive blog article, write it based on the transcript,but do not make it look like a youtube video, make it look like a proper blog article:\n\n{transcript}'
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=10
    )
    generated_content = response.choices[0].text.strip()
    return generated_content

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            # return JsonResponse({'content':yt_link})
        except(KeyError,json.JSONDecodeError):
            return JsonResponse({'error':'Invalid data sent'},status=400)
        
        # get youtube title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcript(yt_link)
        if not transcription:
            return JsonResponse({'error':'Failed to get transcript'},status=500)
        

        # use OpenAI to generate blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error':'Failed to generate blog'},statue=500)
        
         # save blog article to database
        new_blog_article = BlogPost.objects.create(
            user = request.user,
            title = title,
            link = yt_link,
            content = blog_content
        )
        new_blog_article.save()
        return JsonResponse({'content':blog_content})

       
        
    


        # return blog article as response


    else:
        return JsonResponse({'error':'Invalid request method'},status=405)


def blog_list(request):
    articles = BlogPost.objects.filter(user = request.user)

    return render(request,'all_blogs.html',{'articles':articles})

def blog_details(request,pk):
    data = BlogPost.objects.get(id=pk)
    if request.user == data.user:
        return render(request,'blog_details.html',{'data':data})
    else:
        return redirect('home')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']

        if password == cpassword:
            try:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()
                login(request,user)
                return redirect('home')
            except:
                error_message = 'Error creating account'
                return render(request,'signup.html',{'error_message':error_message})

        else:
            error_message = 'Password do not match..'
            return render(request,'signup.html',{'error_message':error_message})

    return render(request,'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            error_message = 'Invalid username or password'
            return render(request,'login.html',{'error_message':error_message})

    return render(request,'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')