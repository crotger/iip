# -*- coding: utf-8 -*-

import logging
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from iip_search_app import common, settings_app
from iip_search_app.forms import SearchForm

log = logging.getLogger(__name__)


def hello( request ):
    """ Testing url handoff. """
    log.debug( u'hello() starting' )
    log.info( u'about to return' )
    return HttpResponse( u'HELLO_WORLD!' )


def iip_results( request ):
    """ Handles /search/ GET, POST, and ajax-GET. """
    log.debug( u'in views.iip_results(); starting' )
    log_id = common.get_log_identifier( request.session )
    log.debug( u'in views.iip_results(); log_id, %s' % log_id )
    if not u'authz_info' in request.session:
        request.session[u'authz_info'] = { u'authorized': False }
    if request.method == u'POST':  # form has been submitted by user
        log.debug( u'in views.iip_results(); id, %s; POST' % log_id )
        post_context = _get_POST_context( request )
        return render_to_response( u'iip_search_templates/base_extend.html', post_context )
    elif request.is_ajax():  # user has requested another page, a facet, etc.
        log.debug( u'in views.iip_results(); id, %s; ajax-GET' % log_id )
        return_unistring = _get_ajax_unistring( request )
        return HttpResponse( return_unistring )
    else:  # regular GET
        log.debug( u'in views.iip_results(); id, %s; regular GET' % log_id )
        context = _get_GET_context( request )
        return render( request, u'iip_search_templates/search_form.html', context )

# def iip_results( request ):
#     """ Handles /search/ GET, POST, and ajax-GET. """
#     try:
#         log.debug( u'in views.iip_results(); starting' )
#         log_id = common.get_log_identifier( request.session )
#         log.debug( u'in views.iip_results(); log_id, %s' % log_id )
#         if not u'authz_info' in request.session:
#             request.session[u'authz_info'] = { u'authorized': False }
#         if request.method == u'POST':  # form has been submitted by user
#             log.debug( u'in views.iip_results(); id, %s; POST' % log_id )
#             post_context = _get_POST_context( request )
#             return render_to_response( u'base_extend.html', post_context )
#         elif request.is_ajax():  # user has requested another page, a facet, etc.
#             log.debug( u'in views.iip_results(); id, %s; ajax-GET' % log_id )
#             return_unistring = _get_ajax_unistring( request )
#             return HttpResponse( return_unistring )
#         else:  # regular GET
#             log.debug( u'in views.iip_results(); id, %s; regular GET' % log_id )
#             context = _get_GET_context( request )
#             return render( request, u'iip_search_templates/search_form.html', context )
#     except Exception as e:
#         log.error( u'in views.iip_results(); id, %s; exception, %s' % (common.get_log_identifier(request.session), unicode(repr(e))) )
#         return HttpResponse( 'oops; unhandled error logged' )

def _get_POST_context( request ):
    """ Returns correct context for POST.
        Called by iip_results() """
    request.encoding = u'utf-8'
    form = SearchForm( request.POST ) # form bound to the POST data
    if form.is_valid():
        initial_qstring = form.generateSolrQuery()
        resultsPage = 1
        updated_qstring = common.updateQstring(
            initial_qstring=initial_qstring, session_authz_dict=request.session['authz_info'], log_identifier=common.get_log_identifier(request.session) )['modified_qstring']
        context = common.paginateRequest(
            qstring=updated_qstring, resultsPage=resultsPage, log_identifier=common.get_log_identifier(request.session) )
        context[u'session_authz_info'] = request.session[u'authz_info']
        return context

def _get_ajax_unistring( request ):
    """ Returns unicode string based on ajax update.
        Called by iip_results() """
    log_identifier = request.session[u'log_identifier']
    initial_qstring = request.GET.get( u'qstring', u'*:*' )
    updated_qstring = common.updateQstring( initial_qstring, request.session[u'authz_info'], log_identifier )[u'modified_qstring']
    resultsPage = int( request.GET[u'resultsPage'] )
    context = paginateRequest( updated_qstring, resultsPage, log_identifier )
    return_str = render_block_to_string(u'base_extend.html', u'content', context)
    return unicode( return_str )

def _get_GET_context( request ):
    """ Returns correct context for GET.
        Called by iip_results() """
    if not u'authz_info' in request.session:
        request.session[u'authz_info'] = { u'authorized': False }
    log.debug( u'in views._get_GET_context(); about to instantiate form' )
    form = SearchForm()  # an unbound form
    log.debug( u'in views._get_GET_context(); form instantiated' )
    context = {
        u'form': form,
        u'session_authz_info': request.session[u'authz_info'],
        u'settings_app': settings_app }
    log.debug( u'in views._get_GET_context(); context, %s' % context )
    return context
