from django.shortcuts import render
from django.http import HttpResponse


def map(request):

    # TODO display map to user

    return render(request, 'routing/map.html')


def route(request, id):

    # TODO display created route to user

    context_dict = {"id":id}

    return render(request, 'routing/route.html', context=context_dict)