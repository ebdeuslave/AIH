import requests
import subprocess
import re
import sys
from lxml import etree
import json
from tkinter import *
from tkinter import messagebox as msg
from tkinter import ttk
from threading import Thread
import winsound as ws


authKey = 'API_KEY'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
}

auth = {'username': 'username',
        'password': 'password'
        }


def scrapeData(cmd_id):
    global orderDate, orderMt, site, payment, mt, fullName, address, phone, phone_mobile, City, cityName, run, cities
    cities = json.load(open('cities.json', 'r'))
    run = True
    if var.get() == 1:
        site = 'parapharma'
    elif var.get() == 2:
        site = 'coinpara'
    elif var.get() == 3:
        site = 'www.parabio'
    try:
        link = f'https://{site}.ma/api/orders/{cmd_id}'
        r = requests.get(link, auth=(authKey, ''))
        root = etree.fromstring(r.content)
        orderDate = root.xpath('//invoice_date')[0].text[:10]
        orderMt = root.xpath('//total_paid')[0].text[:-7]
        payment = root.xpath('//payment')[0].text
        if price.get():
            mt = price.get()
        elif payment == 'cmi':
            mt = '0'
        else:
            mt = root.xpath('//total_paid')[0].text[:-7]

        # Address & Name
        addressID = root.xpath("//id_address_delivery")[0].text
        addressLink = f'https://{site}.ma/api/addresses/{addressID}'
        r2 = requests.get(addressLink, auth=(authKey, ''))
        root2 = etree.fromstring(r2.content)
        fullName = f'{root2.xpath("//firstname")[0].text} {root2.xpath("//lastname")[0].text}'
        try:
            address1 = root2.xpath("//address1")[0].text
            address2 = root2.xpath("//address2")[0].text
            if address2 != None:
                address = f'{address1} {address2}'
            else:
                address = address1
        except:
            address = root2.xpath("//address1")[0].text

        # Phone
        try:
            phone_mobile = re.sub(
                '[^0-9]', '', root2.xpath("//phone_mobile")[0].text)
        except:
            phone_mobile = ''
        try:
            phone = re.sub('[^0-9]', '', root2.xpath("//phone")[0].text)
        except:
            phone = ''

        if phone_mobile.startswith('2120'):
            phone_mobile = phone_mobile[3:]
        elif phone_mobile.startswith('212'):
            phone_mobile = '0' + phone_mobile[3:]
        elif phone_mobile.startswith('002120'):
            phone_mobile = phone_mobile[5:]
        elif phone_mobile.startswith('00212'):
            phone_mobile = '0' + phone_mobile[5:]
        elif phone_mobile.startswith('0212'):
            phone_mobile = '0' + phone_mobile[4:]
        elif phone_mobile and not phone_mobile.startswith('0'):
            phone_mobile = '0' + phone_mobile

        if phone.startswith('2120'):
            phone = phone[3:]
        elif phone.startswith('212'):
            phone = '0' + phone[3:]
        elif phone.startswith('002120'):
            phone = phone[5:]
        elif phone.startswith('00212'):
            phone = '0' + phone[5:]
        elif phone.startswith('0212'):
            phone = '0' + phone[4:]
        elif phone and not phone.startswith('0'):
            phone = '0' + phone

        if (phone and phone_mobile) and (phone != phone_mobile):
            if phone_mobile.startswith('05'):
                phone_mobile, phone = phone, phone_mobile
            address = f'{address} - {phone}'

        # City
        try:
            City = root2.xpath("//city")[0].text.lower()
        except:
            City = ''

        countryLink = f'https://{site}.ma/api/countries/{root2.xpath("//id_country")[0].text}'
        r3 = requests.get(countryLink, auth=(authKey, ''))
        root3 = etree.fromstring(r3.content)
        cityName = root3.xpath('//name/language')[0].text.lower()
        if City and City[-1] == ' ':
            City = City[:-1]
        if cityName and cityName[-1] == ' ':
            cityName = cityName[:-1]

        if City:
            City = City.replace('é', 'e').replace('è', 'e').replace(
                'ê', 'e').replace('ë', 'e').replace('à', 'a').replace('á', 'a').replace('ä', 'a')
        if cityName:
            cityName = cityName.replace('é', 'e').replace('è', 'e').replace(
                'ê', 'e').replace('ë', 'e').replace('à', 'a').replace('á', 'a').replace('ä', 'a')

        if 'autre' in cityName or cityName == 'casablanca' or cityName == 'r.s.t':
            cityName = ''
        if 'autre' in City or City == 'casablanca' or City == 'r.s.t':
            City = ''
        if city.get():
            cityName = city.get().lower()

    except Exception as e:
        run = False
        msg.showerror('Delivery Creation Bot',
                      f'had commande makinach wla chi error f site wla conx\n\nError :\n{e}')
        cmdID.focus()


ORDERS_IDS = {}


def postToCathedis(event=None):
    CMD_ID = re.sub('[^0-9]', '', cmdID.get())
    if CMD_ID.isnumeric():
        scrapeData(CMD_ID)
        if run:
            if cityName not in cities and City not in cities:
                msg.showerror(
                    'Delivery Creation Bot', 'Had lmdina makinach f cathedis, chof site yla zadoha')
                return
            if (phone_mobile and not phone and len(phone_mobile) < 10) or (phone and not phone_mobile and len(phone) < 10):
                if msg.askyesno('Delivery Creation Bot', 'ATTENTION !! telephone na9es, clique sur oui wdkhel l platform cathedis w modifih\n yla cliquiti 3la Non maradich t ajouta livraison'):
                    pass
                else:
                    return

            try:
                data_to_post = {
                    "data": {
                        "allowOpening": False,
                        "deliveryStatus.type": "PENDING",
                        "multiplePackages": False,
                        "deactivateValidation": True,
                        "caution": "0",
                        "declaredValue": "0",
                        "amount": mt,
                        "rangeWeight": "ONE_FIVE",
                        "customer.acceptMultiDeliveries": False,
                        "typeDelivery": "NORMAL",
                        "fragile": False,
                        "packageCount": 1,
                        "deliveryStatus.styleClass": "info",
                        "status": "UNPAID",
                        "acceptMultiPackages": True,
                        "deliveryType": {
                            "code": "Livraison CRBT",
                            "name": "Livraison CRBT",
                            "id": 1
                        },
                        "recipient": {
                            "delivery": None,
                            "importOrigin": None,
                            "address": address,
                            "updatedBy": None,
                            "isLandLine": False,
                            "city": {
                                "id": cities[cityName] if cityName else cities[City],
                            },
                            "store": {
                                "code": "Parapharmacie AIH",
                                "name": "Parapharmacie AIH",
                                "id": 323
                            },
                            "updatedOn": None,
                            "createdOn": None,
                            "attrs": None,
                            "importId": None,
                            "createdBy": None,
                            "phone": phone_mobile if phone_mobile else phone,
                            "name": fullName,
                            "id": None,
                            "sector": {
                                "id": 158,
                            },
                            "email": None,
                            "selected": False
                        },
                        "deliveryStatus": {
                            "styleClass": "btn btn-white",
                            "type": "PENDING",
                            "name": "En Attente Ramassage",
                            "id": 1
                        },
                        "paymentType": {
                            "code": "ESPECES",
                            "name": "ESPECES",
                            "id": 1
                        },
                        "customer": {
                            "code": "Parapharmacie AIH",
                            "name": "Parapharmacie AIH",
                            "id": 323
                        },
                        "status$value": "unpaid",
                        "subject": site[4:].title() if site == 'www.parabio' else site.title(),
                        "nomOrder": CMD_ID,
                    }
                }

                with requests.Session() as session:
                    login_request = session.post(
                        'https://cathedis.delivery/login.jsp', data=auth, headers=headers)

                    post_request = session.post(
                        'https://cathedis.delivery/ws/rest/com.tracker.delivery.db.Delivery/', json=data_to_post)

                    if post_request.json()['status'] == 0:
                        stateLabel.config(
                            text=f'Order Added\n################\n{site.title()}: N°{CMD_ID}\n{fullName}\n{phone_mobile} - {phone}\n{post_request.json()["data"][0]["city"]["name"]}\n{mt} DHs')
                        ORDERS_IDS[CMD_ID] = site
                        totalIDs.config(text=len(ORDERS_IDS))
                        ws.Beep(500, 500)
                        price.delete(0, 'end')
                        city.delete(0, 'end')
                        cmdID.delete(0, 'end')
                        cmdID.focus()
                    else:
                        msg.showerror(
                            'Failed !', f'Order N° {CMD_ID} Failed to add\n {post_request.json()}')
                        cmdID.focus()

            except Exception as e:
                print(f'{e}\nerror line: {sys.exc_info()[-1].tb_lineno}')
                msg.showerror('Error', f'Error :\n {e}')
                cmdID.focus()

    else:
        msg.showerror('Delivery Creation Bot', 'Give me a numeric ID')
        cmdID.focus()


def changeCMDState(website, cmd_id):
    global proc, script_response
    proc = subprocess.Popen(
        f"php updateCmdState.php {website} {cmd_id}", shell=True, stdout=subprocess.PIPE)
    script_response = proc.stdout.read()
    stateLabel.config(text=script_response)


def mass_changeState():
    if ORDERS_IDS:
        progress.pack()
        success, failed = 0, 0
        total = 1
        for key in ORDERS_IDS:
            app.update_idletasks()
            changeCMDState(ORDERS_IDS[key], key)
            progress['value'] += 100/len(ORDERS_IDS)

            if 'ERROR' in script_response.decode("utf-8"):
                stateLabel.config(
                    text=f'{total}/{len(ORDERS_IDS)} - {ORDERS_IDS[key].title()} - {key} : Erreur')
                failed += 1
                total += 1
            else:
                stateLabel.config(
                    text=f'{total}/{len(ORDERS_IDS)} - {ORDERS_IDS[key].title()} - {key} : Encours de livraison')
                success += 1
                total += 1
        progress.stop()
        progress.pack_forget()
        msg.showinfo(
            'Change Status', f'{success} CMDs : Encours de livraison\n{failed} CMDs : Erreur')

        ORDERS_IDS.clear()
        totalIDs.config(text=len(ORDERS_IDS))
        cmdID.focus()
    else:
        msg.showerror('Change Status', 'No ID found')
        cmdID.focus()


app = Tk()
app.title('Delivery Creation Bot - By Ebdeu')
app.geometry('370x800+1000+30')
app.configure(background='deep sky blue')
var = IntVar()
parapharma = Radiobutton(app, text='Parapharma',
                         variable=var, value=1, bg='deep sky blue')
parapharma.pack(pady=1)
parapharma.select()
coinpara = Radiobutton(app, text='Coinpara', variable=var,
                       value=2, bg='deep sky blue')
coinpara.pack(pady=1)
parabio = Radiobutton(app, text='Parabio', variable=var,
                      value=3, bg='deep sky blue')
parabio.pack(pady=1)

Label(text='ID:', bg='deep sky blue').pack()
cmdID = Entry(app, width=10)
cmdID.pack()
cmdID.focus()

Label(text='Price: (if changed)', bg='deep sky blue').pack()
price = Entry(app, width=5)
price.pack()

Label(text='City (if not written correctly)', bg='deep sky blue').pack()
city = Entry(app, width=15)
city.pack()


stateLabel = Label(width=50, bd=2,)
stateLabel.pack(pady=10)

Label(text='Total Orders:', bg='deep sky blue').pack()
totalIDs = Label(text=len(ORDERS_IDS), width=10, bd=2)
totalIDs.pack(pady=10)

progress = ttk.Progressbar(app, orient=HORIZONTAL,
                           length=300, mode='determinate')


changeStateBtn = Button(app, text="Encours de livraison",
                        command=lambda: Thread(target=mass_changeState).start())
changeStateBtn.pack(pady=20)


Button(app, text="Cathedis API", command=postToCathedis, activebackground='white',
       activeforeground='white', bg='#DE6672', bd=8, padx=5, pady=3, width=17, font='mincho 12').pack(pady=20)
app.bind('<Return>', postToCathedis)

############### RUN APP ###############
app.mainloop()
