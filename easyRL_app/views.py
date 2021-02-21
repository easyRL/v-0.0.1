from django.conf import settings
from django.core.cache import caches
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import redirect, render
from django.shortcuts import render, redirect
from pymemcache.client import base
from . import forms

import boto3
import os
from easyRL_app.utilities import get_aws_s3, get_aws_lambda,\
    invoke_aws_lambda_func, is_valid_aws_credential, generate_jobID
from easyRL_app import apps

DEBUG_JOB_ID = generate_jobID()

session = boto3.session.Session()

# Create your views here.

def index(request):
    # send the user back to the login form if the user did not sign in or session expired
    debug_sessions(request)
    if 'aws_succeed' not in request.session or not request.session['aws_succeed']:
        return HttpResponseRedirect("/easyRL_app/login/")

    my_dict = {}
    my_dict["list"]=[1,2,3]
    files = os.listdir(os.path.join(settings.BASE_DIR, "static/easyRL_app/images"))
    my_dict['files'] = files
    form = forms.HyperParameterForm()
    if request.method == "GET":
        my_dict['form'] = form
        return render(request, "easyRL_app/index.html", context=my_dict)
    
    elif request.method == "POST":
        form = forms.HyperParameterForm(request.POST)
        if form.is_valid():
            my_dict['form'] = form
        return render(request, "easyRL_app/index.html", context=my_dict)

def login(request):
    form = forms.AwsCredentialForm()
    if request.method == "GET":
        return render(request, "easyRL_app/login.html", context={'form': form})
    elif request.method == "POST":
        form = forms.AwsCredentialForm(request.POST)
        if form.is_valid() and is_valid_aws_credential(
            form.cleaned_data["aws_access_key"], 
            form.cleaned_data["aws_secret_key"], 
            form.cleaned_data["aws_security_token"]):
            request.session['aws_access_key'] = form.cleaned_data["aws_access_key"]
            request.session['aws_secret_key'] = form.cleaned_data["aws_secret_key"]
            request.session['aws_security_token'] = form.cleaned_data["aws_security_token"]
            request.session['job_id'] = generate_jobID()
            # create ec2 instance
            debug_sessions(request)
            lambda_create_instance(
                request.session['aws_access_key'],
                request.session['aws_secret_key'],
                request.session['aws_security_token'],
                request.session['job_id']
            )
            request.session['aws_succeed'] = True
            return HttpResponseRedirect("/easyRL_app/")
        else:
            request.session['aws_succeed'] = False
            return HttpResponseRedirect("/easyRL_app/login/")

def logout(request):
    # store the keys (to avoid deep copy)
    keys = [key for key in request.session.keys()]
    # terminate the instance for the user
    lambda_terminate_instance(
        request.session['aws_access_key'],
        request.session['aws_secret_key'],
        request.session['aws_security_token'],
        request.session['job_id']
    )
    # clear up all sessions
    for key in keys:
        del request.session[key]
    return HttpResponseRedirect("/easyRL_app/login/")

def train(request):
    debug_sessions(request)
    if 'aws_succeed' not in request.session or not request.session['aws_succeed']:
        return HttpResponse(apps.ERROR_UNAUTHENTICATED)
    
    lambda_run_job(
        request.session['aws_access_key'],
        request.session['aws_secret_key'],
        request.session['aws_security_token'],
        request.session['job_id'],
        {
            "environment": int(request.GET['environment']),
            "agent": int(request.GET['agent']),
            "episodes": int(request.GET['episodes']),
            "steps": int(request.GET['steps']),
            "gamma": float(request.GET['gamma']),
            "minEpsilon": float(request.GET['minEpsilon']),
            "maxEpsilon": float(request.GET['maxEpsilon']),
            "decayRate": float(request.GET['decayRate']),
            "batchSize": int(request.GET['batchSize']),
            "memorySize": int(request.GET['memorySize']),
            "targetInterval": int(request.GET['targetInterval']),
        }
    )
    return HttpResponse(apps.ERROR_NONE)
    

def lambda_create_instance(aws_access_key, aws_secret_key, aws_security_token, job_id):
    lambdas = get_aws_lambda(os.getenv("AWS_ACCESS_KEY_ID"), os.getenv("AWS_SECRET_ACCESS_KEY"))
    data = {
        "accessKey": aws_access_key,
        "secretKey": aws_secret_key,
        "sessionToken": aws_security_token,
        "jobID": job_id,
        "task": apps.TASK_CREATE_INSTANCE,
        "arguments": {"instanceType": "c4.xlarge"},
    }
    response = invoke_aws_lambda_func(lambdas, str(data).replace('\'','"'))
    print("{}lambda_create_instance{}={}".format(apps.FORMAT_RED, apps.FORMAT_RESET, response['Payload'].read()))
    if response['StatusCode'] == 200:
        return True
    return False

def lambda_terminate_instance(aws_access_key, aws_secret_key, aws_security_token, job_id):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html
    lambdas = get_aws_lambda(os.getenv("AWS_ACCESS_KEY_ID"), os.getenv("AWS_SECRET_ACCESS_KEY"))
    data = {
        "accessKey": aws_access_key,
        "secretKey": aws_secret_key,
        "sessionToken": aws_security_token,
        "jobID": job_id,
        "task": apps.TASK_TERMINAL_INSTANCE,
        "arguments": "",
    }
    response = invoke_aws_lambda_func(lambdas, str(data).replace('\'','"'))
    print("{}lambda_terminate_instance{}={}".format(apps.FORMAT_RED, apps.FORMAT_RESET, response['Payload'].read()))
    if response['StatusCode'] == 200:
        return True
    return False

def lambda_run_job(aws_access_key, aws_secret_key, aws_security_token, job_id, arguments):
    lambdas = get_aws_lambda(os.getenv("AWS_ACCESS_KEY_ID"), os.getenv("AWS_SECRET_ACCESS_KEY"))
    data = {
        "accessKey": aws_access_key,
        "secretKey": aws_secret_key,
        "sessionToken": aws_security_token,
        "jobID": job_id,
        "task": apps.TASK_RUN_JOB,
        "arguments": arguments,
    }
    response = invoke_aws_lambda_func(lambdas, str(data).replace('\'','"'))
    print("{}lambda_run_job{}={}".format(apps.FORMAT_RED, apps.FORMAT_RESET, response['Payload'].read()))
    if response['StatusCode'] == 200:
        return True
    return False

def test_data(request):
    if request.method == 'GET' and 'name' in request.GET:
        return HttpResponse("Hello {}".format(request.GET['name']))
    return HttpResponse("Hello World")

def debug_sessions(request):
    for key in request.session.keys():
        print("{}{}{}={}".format(apps.FORMAT_CYAN, key, apps.FORMAT_RESET, request.session[key]))

