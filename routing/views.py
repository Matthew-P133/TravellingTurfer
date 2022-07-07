from django.shortcuts import render
from django.http import HttpResponse


def map(request):

    # TODO display map to user

    return HttpResponse("MAP")


def route(request, id):

    # TODO display created route to user

    return HttpResponse(f"Route {id}")