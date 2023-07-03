from .models import *
from .forms import *
from .filters import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserModel
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, date
from django.http import HttpResponse
from .xhtml2pdf import pisa
from io import BytesIO
import os
from django.conf import settings
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from time import sleep

# Create your views here.


def developer(request):
    context = {}
    return render(request, 'developer.html', context)


def loginPage(request):
    form = UserModel()
    if request.user.is_authenticated:
        return redirect('amanaApp:livraison')
    else:
        if request.method == 'POST':
            u = request.POST.get('username')
            p = request.POST.get('password')
            account = authenticate(request, username=u, password=p)

            if account is not None:                                 # redirect to some page after login
                login(request, account)
                return redirect('amanaApp:livraison')
            elif not u and not p:
                messages.error(request, 'Type your USERNAME and PASSWORD')
            elif not u:
                messages.error(request, 'Missing USERNAME, Try again')
            elif not User.objects.exclude().filter(username=u).exists():
                messages.error(request, 'USERNAME is incorrect, Try again..')
            elif User.objects.exclude().filter(username=u).exists() and not p:
                messages.error(request, 'Missing PASSWORD, Try again')
            elif u and not p:
                messages.error(request, 'PASSWORD is incorrect, Try again..')
            else:
                messages.error(request, 'PASSWORD is incorrect, Try again..')

        return render(request, 'login.html', {'form': form})


def logoutUser(request, **kwargs):
    if request.user.is_authenticated:                     # if the user logged in
        u = request.user
        logout(request)
        messages.info(request, f'See You soon {u}')

        return redirect('amanaApp:login_page')
    else:                                                 # else if anonymous access to logout direction
        messages.error(request, 'Log in First')
        return redirect('amanaApp:login_page')

# load img inside PDF


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-16')),
                            result, link_callback=link_callback)
    if pdf.err:
        return HttpResponse('Error')
    return HttpResponse(result.getvalue(), content_type='application/pdf')


@login_required(login_url='amanaApp:login_page')
def livraison(request):
    global pdf_queryset
    global filtered

    queryset = Livraison.objects.order_by('-cab')
    OwnFilter = LivraisonFilter(request.GET, queryset=queryset)
    queryset = OwnFilter.qs
    filtered = queryset

    # Statistics
    # n*100/total to calcul percentage
    total = queryset.count()
    total_exp = queryset.filter(status=1).count()
    total_delivered = queryset.filter(status=2).count()
    total_paid = queryset.filter(status=3).count()
    total_returned = queryset.filter(status=4).count()
    fees = total*54

    try:
        percentage_exp = f'{round(total_exp * 100 / total,2)} %'
        percentage_delivered = f'{round(total_delivered * 100 / total,2)} %'
        percentage_paid = f'{round(total_paid * 100 / total,2)} %'
        percentage_returned = f'{round(total_returned * 100 / total,2)} %'

    except:
        percentage_exp = '0 %'
        percentage_delivered = '0 %'
        percentage_paid = '0 %'
        percentage_returned = '0 %'
    # calcul MT
    # All
    sum_mt_all = sum([p.price for p in queryset])
    # Expedié
    sum_mt_exp = sum([p.price for p in queryset.filter(status=1)])
    # Livré
    sum_mt_delivered = sum([p.price for p in queryset.filter(status=2)])
    # Payé
    sum_mt_paid = sum([p.price for p in queryset.filter(status=3)])
    # Retour
    sum_mt_returned = sum([p.price for p in queryset.filter(status=4)])

    TotaldeliveredANDpaid = total_delivered + total_paid
    SumdeliveredANDpaid = sum_mt_delivered + sum_mt_paid
    fonds_net = SumdeliveredANDpaid - (TotaldeliveredANDpaid*54)
    # Pagination
    paginator = Paginator(queryset, 100)
    page = request.GET.get('page')
    queryset = paginator.get_page(page)

    context = {
        'livraison': queryset,
        'fees': fees,
        'total': total,
        'total_exp': total_exp,
        'total_delivered': total_delivered,
        'total_paid': total_paid,
        'total_returned': total_returned,
        'percentage_exp': percentage_exp,
        'percentage_delivered': percentage_delivered,
        'percentage_paid': percentage_paid,
        'percentage_returned': percentage_returned,
        'filter': OwnFilter,
        'sum_mt_all': sum_mt_all,
        'sum_mt_exp': sum_mt_exp,
        'sum_mt_delivered': sum_mt_delivered,
        'sum_mt_paid': sum_mt_paid,
        'sum_mt_returned': sum_mt_returned,
        'TotaldeliveredANDpaid': TotaldeliveredANDpaid,
        'SumdeliveredANDpaid': SumdeliveredANDpaid,
        'fonds_net': fonds_net,
        'loss': total_returned * 54,
        'paginator': paginator,
    }

    # get checked objects by AJAX (see base.html)
    selected_ids = request.POST.getlist('pdf_ids[]')
    pdf_queryset = Livraison.objects.filter(
        cab__in=selected_ids, status=1).order_by('cab')

    # Delete objects
    if request.method == 'POST':
        deleted_ids = request.POST.getlist('deleted_ids[]')
        for id in deleted_ids:
            d = Livraison.objects.get(pk=id)
            d.delete()

    # Set Selected To Delivered
    if request.method == 'POST':
        delivered_ids = request.POST.getlist('delivered_ids[]')
        for id in delivered_ids:
            l = Livraison.objects.filter(pk=id)
            l.update(status=2)

    # Set Selected To Paid
    if request.method == 'POST':
        paid_ids = request.POST.getlist('paid_ids[]')
        for id in paid_ids:
            l = Livraison.objects.filter(pk=id)
            l.update(status=3)

    # Set Selected To Returned
    if request.method == 'POST':
        returned_ids = request.POST.getlist('returned_ids[]')
        for id in returned_ids:
            l = Livraison.objects.filter(pk=id)
            l.update(status=4)

    return render(request, 'livraison.html', context)


@staff_member_required(login_url='amanaApp:login_page')
def add_livraison(request):
    if request.method == 'POST':
        form = LivraisonAddForm(request.POST)
        if form.is_valid():
            form.save()
            site = form['site'].value()
            name = form['name'].value()
            city = form['city'].value()
            phone = form['phone'].value()
            mt = form['price'].value()
            messages.info(
                request, f'Livraison : "AIH{form.instance.cab}MA - {site} - {name} {city} {phone} - {mt} DH" a été ajouté')
            return redirect('amanaApp:add_livraison')
        else:
            return HttpResponse('Les données ne sont pas valide veuillez retourner et réessayer')
    else:
        form = LivraisonAddForm()

    context = {
        'form': form,
    }

    return render(request, 'add_livraison.html', context)


@staff_member_required(login_url='amanaApp:login_page')
def update_livraison(request, id):
    queryset = Livraison.objects.filter(status=1)
    try:
        obj = get_object_or_404(queryset, cab=id)
        form = LivraisonForm(request.POST or None, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('amanaApp:livraison')

        context = {"form": form, 'id': id}
        return render(request, "update_livraison.html", context)
    except:
        return HttpResponse('Vous ne pouvez pas modifier que les livraisons Expedié')


@login_required(login_url='amanaApp:login_page')
def search(request):
    query = ''
    if request.GET:
        query = request.GET['q']
        if not query or not query.isspace():
            results = Livraison.objects.filter(Q(cab__icontains=query) | Q(site__icontains=query) | Q(name__icontains=query) | Q(
                phone__icontains=query) | Q(price__icontains=query) | Q(city__icontains=query) | Q(address__icontains=query)).order_by('-cab')
            # Statistics
            # n*100/total to calcul percentage
            total = results.count()
            total_exp = results.filter(status=1).count()
            total_delivered = results.filter(status=2).count()
            total_paid = results.filter(status=3).count()
            total_returned = results.filter(status=4).count()
            try:
                percentage_exp = f'{round(total_exp * 100 / total,2)} %'
                percentage_delivered = f'{round(total_delivered * 100 / total,2)} %'
                percentage_paid = f'{round(total_paid * 100 / total,2)} %'
                percentage_returned = f'{round(total_returned * 100 / total,2)} %'

            except:
                percentage_exp = '0 %'
                percentage_delivered = '0 %'
                percentage_paid = '0 %'
                percentage_returned = '0 %'
            # calcul MT
            # All
            sum_mt_all = sum([p.price for p in results])
            # Expedié
            sum_mt_exp = sum([p.price for p in results.filter(status=1)])
            # Livré
            sum_mt_delivered = sum([p.price for p in results.filter(status=2)])
            # Payé
            sum_mt_paid = sum([p.price for p in results.filter(status=3)])
            # Retour
            sum_mt_returned = sum([p.price for p in results.filter(status=4)])
            context = {
                'result': results,
                'total': total,
                'total_exp': total_exp,
                'total_delivered': total_delivered,
                'total_paid': total_paid,
                'total_returned': total_returned,
                'percentage_exp': percentage_exp,
                'percentage_delivered': percentage_delivered,
                'percentage_paid': percentage_paid,
                'percentage_returned': percentage_returned,
                'sum_mt_all': sum_mt_all,
                'sum_mt_exp': sum_mt_exp,
                'sum_mt_delivered': sum_mt_delivered,
                'sum_mt_paid': sum_mt_paid,
                'sum_mt_returned': sum_mt_returned,
                'query': query,
            }
        else:
            return redirect('amanaApp:livraison')

    else:
        context = {}

    return render(request, 'livraison_search.html', context)


class Etiquette(View):
    @method_decorator(login_required(login_url='amanaApp:login_page'))
    def get(self, request, *args, **kwargs):
        server_url = request.build_absolute_uri('/')

        data = {
            'livraison': pdf_queryset,
            'server_url': server_url,
            'today': date.today().strftime('%d-%m-%Y'),
        }
        pdf = render_to_pdf('etiquette.html', data)

        if pdf_queryset:
            return HttpResponse(pdf, content_type='application/pdf')
        else:
            return HttpResponse('Refresh or Go back and try again..')


class Ramassage(View):
    @method_decorator(login_required(login_url='amanaApp:login_page'))
    def get(self, request, *args, **kwargs):
        server_url = request.build_absolute_uri('/')
        data = {
            'livraison': pdf_queryset,
            'today': date.today().strftime('%d-%m-%Y'),
            'total': len(pdf_queryset),
            'server_url': server_url,
        }
        pdf = render_to_pdf('ramassage.html', data)

        if pdf_queryset:
            return HttpResponse(pdf, content_type='application/pdf')
        else:
            return HttpResponse('Refresh or Go back and try again..')
