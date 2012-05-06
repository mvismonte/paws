# Copyright 2012 PAWS. All rights reserved.
# Date: 4/30/2012
# TODO(): Fill in description

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template

@login_required
def home(request):
  t = get_template('index.html')
  context = { 'page': 'home' }
  html = t.render(RequestContext(request, context))
  return HttpResponse(html)

def template_debug(request, templ):
  t = get_template(templ)
  context = { 'page': 'debug' }
  html = t.render(RequestContext(request, context))
  return HttpResponse(html)
