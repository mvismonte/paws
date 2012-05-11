# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# Main Views
# The views in this app contain the main views of the PAWS application.

from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template

# Home View.
@login_required
def home(request):
  t = get_template('index.html')
  context = { 'page': 'home' }
  html = t.render(RequestContext(request, context))
  return HttpResponse(html)

# Enrichment view.
@login_required
def enrichments(request):
  t = get_template('enrichments.html')
  context = { 'page': 'enrichment' }
  html = t.render(RequestContext(request, context))
  return HttpResponse(html)

# Animal view.
@login_required
def animals(request):
  t = get_template('animals.html')
  context = { 'page': 'animal' }
  html = t.render(RequestContext(request, context))
  return HttpResponse(html)

# Logout View.
def logout(request):
  # Logout of the application and redirect.
  django_logout(request)
  redirect = request.GET.get('next','/auth/login/')
  return HttpResponseRedirect(redirect)

# Template debug View.
# TODO(steven): Remove this view when debugging is finished.
def template_debug(request, templ):
  t = get_template(templ)
  context = { 'page': 'debug' }
  html = t.render(RequestContext(request, context))
  return HttpResponse(html)
