from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
# from django.contrib.auth.views import *
from django.contrib.auth.forms import UserModel
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages  
from django.contrib.auth.models import User
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.views import View
from django.template.loader import get_template
from io import BytesIO
from datetime import date, timedelta
import pandas as pd
from django.utils.decorators import method_decorator
from .filters import *
from django.core.paginator import Paginator 
from django.db.models import Q
import subprocess, requests
from lxml import etree
import ezgmail
####################### render livraison to PDF file ############################
import os,re
from django.conf import settings
from django.contrib.staticfiles import finders  

authKey = 'apiKey'

def sendEmails(website, cmd):
    WEBSITES = ["parapharma", "coinpara", "parabio"]
    if cmd and website in WEBSITES: 
        try: 
            if website == 'parabio': website = 'www.parabio'
            ezgmail.init(tokenFile=f'sendEmails/{website}.ma_token.json', credentialsFile=f'sendEmails/{website}.ma_credentials.json')

            cmd_link = f'https://{website}.ma/api/orders/{cmd}'
            r = requests.get(cmd_link, auth=(authKey,''))
            root = etree.fromstring(r.content)
            reference = root.xpath('//reference')[0].text
            id_customer =  root.xpath("//id_customer")[0].text
            customerLink = f'https://{website}.ma/api/customers/{id_customer}'
            r2 = requests.get(customerLink, auth=(authKey,''))
            root2 = etree.fromstring(r2.content)
            email =  root2.xpath("//email")[0].text
            fullName = f'{root2.xpath("//firstname")[0].text} {root2.xpath("//lastname")[0].text}'
            cmd_info = f'Commande N° {reference} au Nom de: {fullName}'

            msg = f'''Bonjour Cher Client,<br><br>
                    Merci d'avoir passé votre commande chez {website}, 
                    <br><br>

                    Le livreur a tenté de vous appeler mais votre numéro de téléphone est injoignable ou incorrect,
                    veuillez nous envoyer un numero de téléphone joignable SVP,

                    <br><br>
                    Cordialement
                    <br><br><br>
                    L'équipe du service client {website.title()}.ma

                    '''
        
            ezgmail.send(email, cmd_info, msg, mimeSubtype='html')
            return "|Email envoyé"
        
        except Exception as e:
            print(e)
            return "|Echec"
        
    return ""


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
                path=result[0]
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
    pdf = pisa.pisaDocument(BytesIO(html.encode('ISO-8859-1')), result, link_callback=link_callback)
    if pdf.err:
        return HttpResponse('Error')
    return HttpResponse(result.getvalue(), content_type='application/pdf')


def index(request):
    context = {}
    return render(request, 'index.html', context)


def developer(request):
    context = {}
    return render(request, 'developer.html', context)


@login_required(login_url='livraison:login_page')
def livraison(request):
    global filtered
    global selected_ones
    user = request.user
    queryset = Livraison.objects.order_by('-created', '-id')
    # Filter
    OwnFilter = LivraisonFilter(request.GET, queryset=queryset)
    queryset = OwnFilter.qs
    # calcul MT 
    # All
    sum_mt_all = sum([mt.montant_DH for mt in queryset])
    # Livré 
    sum_mt_delivered = sum([mt.montant_DH for mt in queryset.filter(status=2)])
    # Retour
    sum_mt_returned = sum([mt.montant_DH for mt in queryset.filter(status=3)])
    # Encours
    sum_mt_encours = sum([mt.montant_DH for mt in queryset.filter(status=1)])
    # Reporter
    sum_mt_reporter = sum([mt.montant_DH for mt in queryset.filter(status=4)])
    # Filtered Objects to use them in other func
    # livraison.filtered = OwnFilter.qs
    filtered = OwnFilter.qs
    # Statistics
    # n*100/total to calcul percentage
    total           = queryset.count()
    total_delivered = queryset.filter(status=2).count()
    total_returned  = queryset.filter(status=3).count() 
    total_encours   = queryset.filter(status=1).count()
    total_reporter   = queryset.filter(status=4).count()
    try:
        percentage_delivered = f'{round(total_delivered * 100 / total,2)} %'
        percentage_returned = f'{round(total_returned * 100 / total,2)} %'
        percentage_encours = f'{round(total_encours * 100 / total,2)} %'
        percentage_reporter = f'{round(total_reporter * 100 / total,2)} %'
    except:
        percentage_delivered = '0 %'
        percentage_returned = '0 %'
        percentage_encours = '0 %'
        percentage_reporter = '0 %'
    
    # Pagination
    paginator = Paginator(queryset, 200)
    page = request.GET.get('page')
    queryset = paginator.get_page(page) 

    # Livreur
    livreurs = set([l.zone.livreur for l in queryset])  
    livreur_count = len(livreurs)
    livreur = 'All'
    if livreur_count == 1:
        livreur = list(livreurs)[0] 
        
        
    context = {
    'livraison': queryset,
    'total': total,
    'total_delivered':total_delivered,
    'total_returned':total_returned, 
    'total_encours': total_encours,
    'total_reporter':total_reporter,
    'percentage_delivered': percentage_delivered,
    'percentage_returned': percentage_returned,
    'percentage_encours': percentage_encours,
    'percentage_reporter':percentage_reporter,
    'filter': OwnFilter,
    'sum_mt_all': sum_mt_all,
    'sum_mt_delivered' : sum_mt_delivered,
    'sum_mt_returned' : sum_mt_returned,
    'sum_mt_encours': sum_mt_encours,
    'sum_mt_reporter':sum_mt_reporter,
    'paginator': paginator,
    'livreur': livreur,
    'user':user,
    'today': date.today().strftime('%Y-%m-%d'),
    'server_url': request.build_absolute_uri('/'),
    }
    # get checked objects by AJAX (see base.html)
    selected_ones = request.GET.getlist('id[]')     
    # Delete multiple obj by selecting method
    if request.method == 'POST':
        deleted_ids = request.POST.getlist('id[]')
        for id in deleted_ids:
            dl = Livraison.objects.get(pk=id)
            dl.delete()

    # Set Selected To Delivered 
    if request.method == 'POST':
        delivered_ids = request.POST.getlist('ids[]')  
        for id in delivered_ids:
            l = Livraison.objects.filter(pk=id)
            l.update(status=2)
    
    # Set Selected To Returned
    if request.method == 'POST':
        returned_ids = request.POST.getlist('ids_r[]')  
        for id in returned_ids:
            rl = Livraison.objects.filter(pk=id)
            rl.update(status=3,commentaire='Annulée')
                
    if request.method == 'POST':
        pr_ids = request.POST.getlist('ids_pr[]')  
        for id in pr_ids:
            pr = Livraison.objects.filter(pk=id)

            emailing = sendEmails(pr[0].site.lower(), pr[0].n_commande)    
            pr.update(status=3,commentaire=f'PR/Inj/Inc{emailing}')

    if request.method == 'POST':
        double_ids = request.POST.getlist('ids_double[]')  
        for id in double_ids:
            double = Livraison.objects.filter(pk=id)
            double.update(status=3,commentaire='CMD Double')

    # Reporter
    if request.method == 'POST':
        today_ids = request.POST.getlist('today_ids[]')  
        newDate = request.POST.get('newDate', '') 
        for id in today_ids:
            obj_clone = Livraison.objects.get(pk=id)
            obj_clone.pk, obj_clone.created = None, newDate
            obj_clone.save()
            obj_date = Livraison.objects.filter(pk=id)  
            obj_date.update(status=4, commentaire=f"Reportée le {newDate}")
            

    return render(request, 'livraison.html', context)

@login_required(login_url='livraison:login_page')
def search(request):
    query = ''  
    if request.GET:
        query = request.GET['q']
        if query != '' and query != ' ':
            results = Livraison.objects.filter(Q(zone__nom__icontains=query) | Q(phone__icontains=query) | Q(montant_DH__icontains=query) | Q(commentaire__icontains=query) | Q(n_commande__icontains=query)).order_by('-id', '-created')
            # calcul MT 
            # All
            sum_mt_all = sum([mt.montant_DH for mt in results])
            # Livré 
            sum_mt_delivered = sum([mt.montant_DH for mt in results.filter(status=2)])
            # Retour
            sum_mt_returned = sum([mt.montant_DH for mt in results.filter(status=3)])
            # Encours
            sum_mt_encours = sum([mt.montant_DH for mt in results.filter(status=1)])
            # Reporter
            sum_mt_reporter = sum([mt.montant_DH for mt in results.filter(status=4)])
            # Statistics
            total = results.count()
            total_delivered = results.filter(status=2).count()
            total_returned = results.filter(status=3).count() 
            total_encours = results.filter(status=1).count()
            total_reporter = results.filter(status=4).count()
            context = {
                'result': results,
                'total': total,
                'total_delivered':total_delivered,
                'total_returned':total_returned, 
                'total_encours':total_encours,
                'total_reporter':total_reporter,
                'sum_mt_all': sum_mt_all,
                'sum_mt_delivered' : sum_mt_delivered,
                'sum_mt_returned' : sum_mt_returned,
                'sum_mt_encours': sum_mt_encours,
                'sum_mt_reporter':sum_mt_reporter,
                'query': query,
            }
        else:
            return redirect('livraison:livraison')

    else:
        context = {}
     
    return render(request, 'livraison_search.html', context)

  

# Filtered 2 PDF
class ViewPDF2(View):
    @method_decorator(login_required(login_url='livraison:login_page')) 
    def get(self, request, *args, **kwargs):
        queryset = filtered.filter(status=1).order_by('zone__nom', 'commentaire')
        sum_mt_total = sum([mt.montant_DH for mt in queryset])
        livreurs = set([l.zone.livreur for l in queryset])  
        livreur_count = len(livreurs)
        livreur = ''
        if livreur_count == 1:
            livreur = list(livreurs)[0]
        data = { 
            'livraisons' : queryset,  
            'now' : f'Livraisons-{date.today()}',
            'total' : queryset.count(),
            'sum' : sum_mt_total,
            'livreur' : livreur,
            'livreur_count' : livreur_count,
        }
        pdf = render_to_pdf('pdf_template2.html', data) 
        
        return HttpResponse(pdf, content_type='application/pdf')  


@staff_member_required(login_url='livraison:login_page') 
def add_livraison(request):
    if request.method == 'POST':
        form = LivraisonAddForm(request.POST)
        if form.is_valid():  
            form.save()
            tele = form['phone'].value()
            mt = form['montant_DH'].value()
            messages.success(request, f'Livraison : "{form.instance.site} - {form.instance.n_commande} - {form.instance.zone.nom} - {tele} - [{mt} Dh] {form.instance.commentaire}" a été ajouté')     
            return redirect('livraison:add_livraison')
        else:
            messages.error(request,"Chof telephone aykon na9es")
    else: 
        form = LivraisonAddForm()

    context = {
        'form': form,
    }

    return render(request, 'add_livraison.html', context)  


@staff_member_required(login_url='livraison:login_page')
def update_livraison(request, id):
    queryset = Livraison.objects.filter(status=1)
    try:
        obj = get_object_or_404(queryset, id=id)
        if request.user.is_superuser:
                form = LivraisonForm(request.POST or None, instance=obj)
        else:
                form = LivraisonEditForm(request.POST or None, instance=obj) 
        if form.is_valid(): 
            form.save() 
            return redirect('livraison:livraison')
    
        context ={"form" : form, 'id':id} 
        return render(request, "update_livraison.html", context)
    except:
        return redirect('livraison:livraison')



@user_passes_test(lambda u: u.is_superuser)
def delete(request, id):
    queryset = Livraison.objects.filter(status=1)
    try:
        obj = get_object_or_404(queryset, id=id)
        if request.method == 'POST':
            obj.delete()
            return redirect('livraison:livraison')

        return render(request, 'delete_livraison.html', {'object': obj}) 
    except:
        return redirect('livraison:livraison')


   
@login_required(login_url='livraison:login_page') 
def zones(request):
    queryset = Zone.objects.all().order_by('livreur')
    total = queryset.count()
    context = {'zones': queryset, 'total': total}

    return render(request, 'zones.html', context)

@staff_member_required(login_url='livraison:zones')   
def add_zone(request):  
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('livraison:zones')
    else: 
        form = ZoneForm()
        context = {
            'form' : form
        }
        return render(request, 'add_zone.html', context)


@staff_member_required(login_url='livraison:zones')  
def update_zone(request, id): 
    
    obj = get_object_or_404(Zone, id = id) 
    form = ZoneForm(request.POST or None, instance = obj) 

    if form.is_valid(): 
        form.save() 
        return redirect('livraison:zones') 

    context ={"form" : form} 
    return render(request, "update_zone.html", context) 


def loginPage(request):
    form = UserModel()
    if request.user.is_authenticated:                   
        return redirect('livraison:livraison')
    else:
        if request.method == 'POST':
            u = request.POST.get('username')
            p = request.POST.get('password')
            account = authenticate(request, username=u, password=p)
            
            if account is not None:                                 # redirect to some page after login
                login(request, account)
                return redirect('livraison:livraison')
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
            
        return render(request, 'registration/login.html', {'form': form})
    

def logoutUser(request,**kwargs):
    if request.user.is_authenticated:                     # if the user logged in 
        u = request.user 
        logout(request)
        messages.info(request,f'See You soon {u}')
        
        return redirect('livraison:login_page')  
    else:                                                 # else if anonymous access to logout direction
        messages.error(request,'Log in First')
        return redirect('livraison:login_page')   
          
   



    


##################### Charts #####################
@user_passes_test(lambda u: u.is_superuser)
def chartsView(request):
    queryset = Livraison.objects.order_by('created')
    # Filter
    OwnFilter = LivraisonFilter(request.GET, queryset=queryset)
    queryset = OwnFilter.qs
  

    try:
        start = queryset[0].created
        end = queryset[len(queryset)-1].created 

        date_list = [dt.strftime("%Y%m%d") for dt in pd.date_range(start, end)]   
        total_cmds = [queryset.filter(created=f'{day[:4]}-{day[4:6]}-{day[6:]}').count() for day in date_list]
        total_mt = [sum([mt.montant_DH for mt in queryset.filter(created=f'{day[:4]}-{day[4:6]}-{day[6:]}')]) for day in date_list ]
    except:
        date_list, total_cmds, total_mt = '', '', ''

    
    
   
    context = {
        "qs" : queryset,
        'filter': OwnFilter,
        'date_list': date_list,
        'total_cmds': total_cmds,
        'sum_total_cmds': sum([cmd for cmd in total_cmds]),
        'total_mt': total_mt,
        'sum_total_mt': sum([cmd for cmd in total_mt]),
    }


    return render(request, 'chart.html', context)



@user_passes_test(lambda u: u.is_superuser)
def monthlyChartsView(request):
    query = ''  
    months, monthly_total, monthly_mt, sum_monthly_mt,sum_monthly_orders,monthly_total_retour,monthly_mt_retour,sum_monthly_orders_retour,sum_monthly_mt_retour,zones  = '', '' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ,
    queryset = Livraison.objects.filter(status=2)
    queryset_retour = Livraison.objects.filter(status=3)
    
    
    
      
    if request.GET:
        query = request.GET['q']
        if query:
            YEAR = int(query)
            
            try:
                months = [f'{YEAR}-01',f'{YEAR}-02',f'{YEAR}-03',f'{YEAR}-04',f'{YEAR}-05',f'{YEAR}-06',f'{YEAR}-07',f'{YEAR}-08',f'{YEAR}-09',f'{YEAR}-10',f'{YEAR}-11',f'{YEAR}-12',]
                monthly_total= [queryset.filter(created__icontains=month).count() for month in months]
                monthly_mt = [sum([mt.montant_DH for mt in queryset.filter(created__icontains=month)]) for month in months]
                sum_monthly_orders = sum(monthly_total)
                sum_monthly_mt = sum(monthly_mt)
                # retour 
                monthly_total_retour = [queryset_retour.filter(created__icontains=month).count() for month in months]
                monthly_mt_retour = [sum([mt.montant_DH for mt in queryset_retour.filter(created__icontains=month)]) for month in months]
                sum_monthly_orders_retour = sum(monthly_total_retour)
                sum_monthly_mt_retour = sum(monthly_mt_retour) 
                

            except:
                pass



    context = {
        'query': query,
        "qs" : queryset,
        'monthly_total': monthly_total,
        'monthly_mt': monthly_mt,
        'sum_monthly_orders':sum_monthly_orders,
        'sum_monthly_mt': sum_monthly_mt,
        'monthly_total_retour': monthly_total_retour,
        'monthly_mt_retour': monthly_mt_retour,
        'sum_monthly_orders_retour': sum_monthly_orders_retour,
        'sum_monthly_mt_retour': sum_monthly_mt_retour,
 

    }

    return render(request, 'monthlyChart.html', context)




@user_passes_test(lambda u: u.is_superuser)
def zonesChart(request):
    filter = LivraisonFilter(request.GET, queryset=Livraison.objects.all())
    queryset = filter.qs
    livraison_zones = [livraison.zone.nom for livraison in queryset if livraison.zone] 
    counting_zones = {zone:livraison_zones.count(zone) for zone in livraison_zones}
    counting_zones = dict(sorted(counting_zones.items(), key=lambda x:x[1], reverse=True))
    


    context = {
        'queryset': queryset,
        'filter': filter,
        'counting_zones' : counting_zones,

    }

    return render(request, 'zonesChart.html', context)


@user_passes_test(lambda u: u.is_superuser)
def changeCMDState(request):
    queryset = Livraison.objects.filter(status=1)

    livraisons = {livraison.n_commande:livraison.site.lower() for livraison in queryset if livraison.n_commande}
    succesful = 0
    failed = 0
    failed_livraisons = []

    for cmd_id,website in livraisons.items():
        website = re.sub('[^a-z]' , '', website)
        if website == 'parabio': website = 'www.parabio'
        try:
            proc = subprocess.Popen(f"php changeStatus/updateCmdState.php {website} {cmd_id}", shell=True, stdout=subprocess.PIPE)
            script_response = proc.stdout.read()
            if 'Encours' not in script_response.decode("utf-8"):
                failed += 1
                # failed_livraisons.append(f'{website}-{cmd_id}')
                print(f'FAILED --- {website} - {cmd_id}')
            else:
                succesful += 1    
        except Exception as e:
            print(e)
            continue





    context = {
        'succesful': succesful,
        'failed' : failed,
        'failed_livraisons': failed_livraisons,

    }
    
    
    return render(request, 'changestatus.html', context)

	



  
@login_required(login_url='livraison:login_page')   
def livraisonChecker(request):
    queryset = Livraison.objects.filter(status=1)
    livraisons = {livraison.n_commande:livraison.site.lower() for livraison in queryset if livraison.n_commande}
    NOT_CMI = []
    NOT_SAME_PRICE = []
    NOT_CMD_ID = [livraison for livraison in queryset if not livraison.n_commande]
    REFUND = []

    # CMI & MT Checker
    for cmd_id,website in livraisons.items():
        website = re.sub('[^a-z]' , '', website)
        if website == 'parabio': website = 'www.parabio'
        try:
            link = f'https://{website}.ma/api/orders/{cmd_id}'
            r = requests.get(link, auth=(authKey, ''))
            root = etree.fromstring(r.content)
            orderMt = root.xpath('//total_paid')[0].text[:-7]
            payment = root.xpath('//payment')[0].text
            for obj in queryset.filter(n_commande=cmd_id):
                if obj.montant_DH <= 0 and payment != 'cmi':
                    NOT_CMI.append([website,cmd_id,obj.phone,obj.montant_DH,orderMt,obj.zone.nom,obj.zone.livreur,obj.created])
                elif obj.montant_DH < 0 and payment == 'cmi':
                    REFUND.append([website,cmd_id,obj.phone,obj.montant_DH,orderMt,obj.zone.nom,obj.zone.livreur,obj.created])
                elif payment == 'Paiement comptant à la livraison (Cash on delivery)' and int(obj.montant_DH) != int(orderMt):
                    NOT_SAME_PRICE.append([website,cmd_id,obj.phone,obj.montant_DH,orderMt,obj.zone.nom,obj.zone.livreur,obj.created])

        except Exception as e:
            print(e)
            continue
    
    context = {
        'NOT_CMI': NOT_CMI,
        'NOT_SAME_PRICE': NOT_SAME_PRICE,
        'NOT_CMD_ID': NOT_CMD_ID,
        'REFUND': REFUND,
    }

    return render(request, 'livraisonchecker.html', context)




