from tkinter import messagebox, ttk
from tkinter import *
from tkcalendar import DateEntry
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml import etree
import re
import time
import os
import requests
import sys
from datetime import datetime, date, datetime, timedelta
from threading import Thread
import babel.numbers


################################ AUTH ################################
apiKey = 'API_KEY'
u = 'Email'
p = 'Password'
################################ Func ################################


def login(driver, paraLink):
    driver.get(paraLink)
    user = driver.find_element(By.ID, "email")
    user.send_keys(u)
    passwd = driver.find_element(By.ID, "passwd")
    passwd.send_keys(p)
    driver.find_element(By.NAME, "submitLogin").click()
    # Wait until it loads
    WebDriverWait(driver, 1000).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="tab-AdminDashboard"]/a/span')))
    # Go to CMDs
    driver.find_element(
        By.XPATH, '//*[@id="subtab-AdminParentOrders"]/a').click()
    time.sleep(1.5)
    driver.find_element(By.ID, 'subtab-AdminOrders').click()
    WebDriverWait(driver, 1000).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="page-header-desc-configuration-add"]')))


def Para_CMDs():
    start = time.time()
    if selected.get() == 'Parapharma':
        site = "BACKOFFICE_LINK"
        apiSite = "API_LINK"
    elif selected.get() == 'Coinpara':
        site = "BACKOFFICE_LINK"
        apiSite = "API_LINK"
    elif selected.get() == 'Parabio':
        site = "BACKOFFICE_LINK"
        apiSite = "API_LINK"

    # add 1 day to "Date_To"
    toDate_ = datetime.strptime(toDate.get(), '%Y-%m-%d')+timedelta(1)
    toDate_ = toDate_.strftime('%Y-%m-%d')
    # add ":" between Hour and Minute and Second
    exactTime_ = f'{exactTime.get()[:2]}:{exactTime.get()[2:4]}:{exactTime.get()[4:]}'
    exactTime_ = re.sub('[^0-9:]', '', exactTime_)
    # create api filter link including Datetime & states
    ordersLink = f'{apiSite}?filter[invoice_date]=[{fromDate.get()} {exactTime_},{toDate_}]&filter[current_state]=[2,3]'
    # get orders' IDs
    request = requests.get(ordersLink, auth=(apiKey, ''))
    root = etree.fromstring(request.content)
    orders = root.xpath('//order')
    IDs = [order.attrib['id'] for order in orders]
    # open webdriver & login
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    login(driver, site)
    # Get Token
    token_path = driver.find_element(By.XPATH, '/html/body')
    token_value = token_path.get_attribute('data-token')

    for id in IDs:
        cmdProgress.pack(pady=5)
        cmdLabel.pack()
        cmdLabel.config(
            text=f'Téléchargement : Commande {IDs.index(id)+1}/{len(IDs)}')
        top.update_idletasks()
        cmdProgress['value'] += 100/len(IDs)
        # Download Invoices
        driver.get(
            f'{site}/index.php/sell/orders/{str(id)}/generate-invoice-pdf?_token={token_value}')

    cmdProgress.stop()
    cmdProgress.pack_forget()
    cmdLabel.pack_forget()
    end = time.time()
    duration = end-start
    messagebox.showinfo(
        'Commandes', f'Terminée en: {round(duration,2)} Secs\n\n{len(IDs)} Commandes Téléchargées\n\nNOTE : Tsnaw tay telechargea kolchi 3ad sedo navigateur')

# my own algo to check date validation (not good enough)


def check_cmd():
    cmdBtn.config(state='disabled')
    From = fromDate.get()
    From = re.sub('[^0-9-]', '', From)
    To = toDate.get()
    To = re.sub('[^0-9-]', '', To)
    date1 = From.split('-')
    date2 = To.split('-')
    if not From or not To:
        messagebox.showwarning(
            'BLANK DATE', 'One or both of date fields are Blank \nSet a valid date\nEx : \n2022-01-01 \n2022-01-02')
    elif len(From) != 10 or len(To) != 10:
        messagebox.showerror(
            'INVALID DATE', '10 characters REQUIRED ! Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
    elif not From.startswith('20') or not To.startswith('20') or From.endswith('-') or To.endswith('-'):
        messagebox.showerror(
            'INVALID DATE', 'Invalid Format - Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
    elif From[4] != '-' or To[4] != '-' or From[7] != '-' or To[7] != '-':
        messagebox.showerror(
            'INVALID DATE', 'Invalid Format - Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
    elif From[8:10] > '31' or To[8:10] > '31' or From[8:10] == '00' or To[8:10] == '00':
        messagebox.showerror(
            'INVALID DATE', 'Invalid Day- Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
    elif From[5:7] > '12' or To[5:7] > '12' or From[5:7] == '00' or To[5:7] == '00':
        messagebox.showerror(
            'INVALID DATE', 'Invalid Month - Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
    elif date1 > date2:
        messagebox.showerror(
            'INVALID DATE', 'Date From must be before Date To - Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
    else:
        try:
            Para_CMDs()
        except Exception as e:
            messagebox.showerror(
                'Error', f'{e}\nerror line: {sys.exc_info()[-1].tb_lineno}')
            cmdProgress.stop()
            cmdLabel.config(text=f'Téléchargement : Erreur')

    cmdBtn.config(state='active')


####################### Products Exporter #######################
fileN = f'Produits-{date.today()}--{datetime.now().strftime("%Hh-%Mmin")}.csv'
DictProducts = {}


class Scraper:
    def __init__(self, total_cmds=0):
        self.total_cmds = total_cmds

    # Function to get Products Names from CSV Files
    def getProductsFromFiles(self, File):
        with open(File, 'r', encoding='utf-16') as f:
            return [product.replace('\n', '') for product in f]

    # Function to write orders' products in CSV files
    def getProducts(self, Dict):
        for key in Dict.keys():
            if key.startswith('Distrimar'):
                with open(f'Distrimar-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('BDM'):
                with open(f'BDM-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Pharmadouce'):
                with open(f'Pharmadouce-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Tradiphar'):
                with open(f'Tradiphar-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('BioLife'):
                with open(f'BioLife-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Jerraflore'):
                with open(f'Jerraflore-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Formule Nature'):
                with open(f'Formule Nature-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('La Para'):
                with open(f'La Para-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Nuby'):
                with open(f'Nuby-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Distribio'):
                with open(f'Distribio-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Locamed'):
                with open(f'Locamed-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Lisqa'):
                with open(f'Lisqa-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Pharcomedic'):
                with open(f'Pharcomedic-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Maison du Bebe'):
                with open(f'Maison du Bebe-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Medixana'):
                with open(f'Medixana-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('BioShop'):
                with open(f'BioShop-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Jouvence'):
                with open(f'Jouvence-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Arnaud'):
                with open(f'Arnaud-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Casa Attitude'):
                with open(f'Casa Attitude-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Four Seasons'):
                with open(f'Four Seasons-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Pharmessence'):
                with open(f'Pharmessence-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Casa Brand'):
                with open(f'Casa Brand-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('SportOne'):
                with open(f'SportOne-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Sienbiose'):
                with open(f'Sienbiose-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Medipaco'):
                with open(f'Medipaco-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Africa IH'):
                with open(f'Africa IH-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('Promolead'):
                with open(f'Promolead-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            elif key.startswith('PharmNature'):
                with open(f'PharmNature-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')
            else:
                with open(f'Autres-{fileN}', 'a', encoding='utf-16') as f:
                    f.write(f'{key} | Qté: {Dict[key]}\n')

    # Export products names from CSV files to Dicts
    def suppliers(self):
        start = time.time()
        # Suppliers Dict :
        if os.path.isdir('Suppliers_Products'):
            try:
                # BDM
                self.bdmlist = self.getProductsFromFiles(
                    'Suppliers_Products/bdmlist.csv')
                # Distrimar
                self.distrimarlist = self.getProductsFromFiles(
                    'Suppliers_Products/distrimarlist.csv')
                # Pharmadouce & Gilbert
                self.doucelist = self.getProductsFromFiles(
                    'Suppliers_Products/doucelist.csv')
                # Tradiphar
                self.tradilist = self.getProductsFromFiles(
                    'Suppliers_Products/tradilist.csv')
                # Biolife
                self.biolifelist = self.getProductsFromFiles(
                    'Suppliers_Products/biolifelist.csv')
                # Jerraflore
                self.jerraflorelist = self.getProductsFromFiles(
                    'Suppliers_Products/jerraflorelist.csv')
                # Formule Nature
                self.formulelist = self.getProductsFromFiles(
                    'Suppliers_Products/formulelist.csv')
                # La Para
                self.laparalist = self.getProductsFromFiles(
                    'Suppliers_Products/laparalist.csv')
                # Nuby
                self.nubylist = self.getProductsFromFiles(
                    'Suppliers_Products/nubylist.csv')
                # Distribio
                self.distribiolist = self.getProductsFromFiles(
                    'Suppliers_Products/distribiolist.csv')
                # Locamed
                self.locamedlist = self.getProductsFromFiles(
                    'Suppliers_Products/locamedlist.csv')
                # Lisqa
                self.lisqalist = self.getProductsFromFiles(
                    'Suppliers_Products/lisqalist.csv')
                # Pharcomedic
                self.pharcomediclist = self.getProductsFromFiles(
                    'Suppliers_Products/pharcomediclist.csv')
                # La maison du bebe
                self.maisonbblist = self.getProductsFromFiles(
                    'Suppliers_Products/maisonbblist.csv')
                # Medixana
                self.medixanalist = self.getProductsFromFiles(
                    'Suppliers_Products/medixanalist.csv')
                # bioshop
                self.bioshoplist = self.getProductsFromFiles(
                    'Suppliers_Products/bioshoplist.csv')
                # Jouvence
                self.jouvencelist = self.getProductsFromFiles(
                    'Suppliers_Products/jouvencelist.csv')
                # Arnaud
                self.arnaudlist = self.getProductsFromFiles(
                    'Suppliers_Products/arnaudlist.csv')
                # Casa attitude
                self.casaattitudelist = self.getProductsFromFiles(
                    'Suppliers_Products/casaattitudelist.csv')
                # 4 seasons
                self.fourseasonslist = self.getProductsFromFiles(
                    'Suppliers_Products/fourseasonslist.csv')
                # Pharmessence
                self.pharmessencelist = self.getProductsFromFiles(
                    'Suppliers_Products/pharmessencelist.csv')
                # Promolead
                self.promoleadlist = self.getProductsFromFiles(
                    'Suppliers_Products/promoleadlist.csv')
                # Pharmnature
                self.pharmnaturelist = self.getProductsFromFiles(
                    'Suppliers_Products/pharmnaturelist.csv')
                # Casa brand
                self.casabrandlist = self.getProductsFromFiles(
                    'Suppliers_Products/casabrandlist.csv')
                # Sportone
                self.sportonelist = self.getProductsFromFiles(
                    'Suppliers_Products/sportonelist.csv')
                # Sienbiose
                self.sienbioselist = self.getProductsFromFiles(
                    'Suppliers_Products/sienbioselist.csv')
                # Medipaco
                self.medipacolist = self.getProductsFromFiles(
                    'Suppliers_Products/medipacolist.csv')
                # AIH
                self.aihlist = self.getProductsFromFiles(
                    'Suppliers_Products/aihlist.csv')
                productsBtn.pack(pady=20)
                suppliersBtn.destroy()
                dictInfo.pack(pady=5)
                exportBtn.pack(pady=5)

            except Exception as e:
                print(e)
                messagebox.showerror(
                    'Produits', f'"{str(e)[57:]}" had fichier tmse7 mn dossier "Suppliers_Products"')
        else:
            messagebox.showerror(
                'Produits', 'dossier "Suppliers_Products" makinch')

    def Para_Products(self):
        start = time.time()
        exportBtn.config(state='disabled')

        if selected.get() == 'Parapharma':
            apiSite = 'https://parapharma.ma/api/orders'
        elif selected.get() == 'Coinpara':
            apiSite = 'https://coinpara.ma/api/orders'
        elif selected.get() == 'Parabio':
            apiSite = 'https://www.parabio.ma/api/orders'

        exactTime_ = f'{exactTime.get()[:2]}:{exactTime.get()[2:4]}:{exactTime.get()[4:]}'
        exactTime_ = re.sub('[^0-9:]', '', exactTime_)
        toDate_ = datetime.strptime(toDate.get(), '%Y-%m-%d')+timedelta(1)
        toDate_ = toDate_.strftime('%Y-%m-%d')
        ordersLink = f'{apiSite}?filter[invoice_date]=[{fromDate.get()} {exactTime_},{toDate_}]&filter[current_state]=[2,3]'
        request = requests.get(ordersLink, auth=(apiKey, ''))
        root = etree.fromstring(request.content)
        orders = root.xpath('//order')
        cmd_links = set(
            [order.attrib['{http://www.w3.org/1999/xlink}href'] for order in orders])

        try:
            for link in cmd_links:
                progress.pack(pady=5)
                productsLabel.pack()
                productsLabel.config(
                    text=f'l\'Extraction des Produits : Commande {list(cmd_links).index(link)+1}/{len(cmd_links)}')
                top.update_idletasks()
                progress['value'] += 100/len(cmd_links)
                r = requests.get(link, auth=(apiKey, ''))
                root = etree.fromstring(r.content)
                products = root.xpath("//product_name")
                prices = root.xpath("//product_price")
                quantities = root.xpath("//product_quantity")

                for product, price, quantity in zip(products, prices, quantities):
                    # print(product.text, price.text, quantity.text)
                    item = 'Nom : ' + product.text
                    if item in self.distrimarlist:
                        item = 'Distrimar  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.bdmlist:
                        item = 'BDM  | ' + item + ' | ' + \
                            f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.doucelist:
                        item = 'Pharmadouce  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.tradilist:
                        item = 'Tradiphar  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.biolifelist:
                        item = 'BioLife  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.jerraflorelist:
                        item = 'Jerraflore  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.formulelist:
                        item = 'Formule Nature  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.laparalist:
                        item = 'La Para  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.nubylist:
                        item = 'Nuby  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.distribiolist:
                        item = 'Distribio  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.locamedlist:
                        item = 'Locamed  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.lisqalist:
                        item = 'Lisqa  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.pharcomediclist:
                        item = 'Pharcomedic  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.maisonbblist:
                        item = 'Maison du Bebe  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.medixanalist:
                        item = 'Medixana  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.bioshoplist:
                        item = 'BioShop  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.jouvencelist:
                        item = 'Jouvence  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.arnaudlist:
                        item = 'Arnaud  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.casaattitudelist:
                        item = 'Casa Attitude  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.fourseasonslist:
                        item = 'Four Seasons  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.pharmessencelist:
                        item = 'Pharmessence  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.promoleadlist:
                        item = 'Promolead  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.pharmnaturelist:
                        item = 'PharmNature  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.casabrandlist:
                        item = 'Casa Brand  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.sportonelist:
                        item = 'SportOne  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.sienbioselist:
                        item = 'Sienbiose  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.medipacolist:
                        item = 'Medipaco  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    elif item in self.aihlist:
                        item = 'Africa IH  | ' + item + \
                            ' | ' + f'{price.text[:-4]} DH'
                        DictProducts[item] = int(
                            DictProducts[item]) + int(quantity.text) if item in DictProducts else int(quantity.text)
                    else:
                        DictProducts[f'{product.text} | {price.text[:-4]} DH'] = int(DictProducts[f'{product.text} | {price.text[:-4]} DH']) + int(
                            quantity.text) if f'{product.text} | {price.text[:-4]} DH' in DictProducts else int(quantity.text)

            self.total_cmds += len(cmd_links)
            progress.stop()
            progress.pack_forget()
            productsLabel.pack_forget()
            end = time.time()
            duration = end-start

            if cmd_links:
                dictInfo.config(
                    bg="lightgreen", text=f'Total CMDs : {self.total_cmds}\nTotal Produits : {len(DictProducts)}\nTotal Quantité : {sum(DictProducts.values())}')
                messagebox.showinfo(
                    'Produits', f'Terminée en : {round(duration,2)} Secs')
            else:
                messagebox.showinfo('Produits', '9adia nashfa..')
            cmd_links.clear()  # clear cmd_links to avoid re-exporting old orders

        except Exception as e:
            print(e, '\nerror line: ', sys.exc_info()[-1].tb_lineno)
            messagebox.showerror(
                'Produits', 'Zguel chi produit wla chi cmd 3awdo 7awlo')
        exportBtn.config(state='active')

    def exportToCSV(self):
        if DictProducts:
            self.getProducts(DictProducts)
            print('Products exported to CSV files')
            messagebox.showinfo(
                'Produits', f'Total Produits : {len(DictProducts)}\nTotal Quantité : {sum(DictProducts.values())}\nExported to CSV')
            DictProducts.clear()
            self.total_cmds = 0
            dictInfo.config(
                bg="lightblue", text=f'Total CMDs : {self.total_cmds}\nTotal Produits : {len(DictProducts)}\nTotal Quantité : {sum(DictProducts.values())}')
        else:
            print('Products Dict is Empty')
            messagebox.showinfo(
                'Produits', 'diro l etape "Collecter"\nila dertoha 9bel rah 9adiya nashfa ')

    def check_products(self):
        productsBtn.config(state='disabled')
        From = fromDate.get()
        From = re.sub('[^0-9-]', '', From)
        To = toDate.get()
        To = re.sub('[^0-9-]', '', To)
        date1 = From.split('-')
        date2 = To.split('-')
        if not From or not To:
            messagebox.showwarning(
                'BLANK DATE', 'One or both of date fields are Blank \nSet a valid date\nEx : \n2022-01-01 \n2022-01-02')
        elif len(From) != 10 or len(To) != 10:
            messagebox.showerror(
                'INVALID DATE', '10 characters REQUIRED ! Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
        elif not From.startswith('20') or not To.startswith('20') or From.endswith('-') or To.endswith('-'):
            messagebox.showerror(
                'INVALID DATE', 'Invalid Format - Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
        elif From[4] != '-' or To[4] != '-' or From[7] != '-' or To[7] != '-':
            messagebox.showerror(
                'INVALID DATE', 'Invalid Format - Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
        elif From[8:10] > '31' or To[8:10] > '31' or From[8:10] == '00' or To[8:10] == '00':
            messagebox.showerror(
                'INVALID DATE', 'Invalid Day- Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
        elif From[5:7] > '12' or To[5:7] > '12' or From[5:7] == '00' or To[5:7] == '00':
            messagebox.showerror(
                'INVALID DATE', 'Invalid Month - Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
        elif date1 > date2:
            messagebox.showerror(
                'INVALID DATE', 'Date From must be before Date To - Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
        else:
            self.Para_Products()
        productsBtn.config(state='active')


scraper = Scraper()


################################ GUI ################################

top = Tk()
if os.path.isfile("para17.ico"):
    top.iconbitmap('para17.ico')
top.title("Para - Commandes | Produits - v2.0")
top.geometry('500x850+800+100')
top.configure(background='coral')
if os.path.isfile("bg.png"):
    filename = PhotoImage(file=r"bg.png")
    background_label = Label(top, image=filename)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)


options = ['Parapharma', 'Coinpara', 'Parabio']
selected = StringVar()
selected.set("Parapharma")
drop = OptionMenu(top, selected, *options)
drop.pack(pady=5)
drop["menu"].configure(bg="lightgreen", borderwidth=1,
                       font=("Helvetica", "9", 'bold'))


fromlabel = Label(top, text='From :', bg='lightblue')
fromlabel.pack(pady=15)
fromDate = DateEntry(date_pattern='yyyy-mm-dd')
fromDate.pack()
tolabel = Label(top, text='To : ', bg='lightblue')
tolabel.pack(pady=5)
toDate = DateEntry(date_pattern='yyyy-mm-dd')
toDate.pack(pady=5)
timeLabel = Label(top, text='HHMMSS', bg='orange')
timeLabel.pack()
exactTime = Entry(top, width=6)
exactTime.pack(pady=5)
exactTime.insert(END, '000000')

cmdFrame = LabelFrame(top, bd=5, text='Commandes', font=(
    "Helvetica", "15", 'bold'), bg='lightblue')
cmdFrame.pack(pady=20)
cmdBtn = Button(cmdFrame, text='Télécharger', command=lambda: Thread(target=check_cmd).start(
), activebackground='white', activeforeground='black', bg='cyan', bd=5, padx=5, pady=3, width=9, font='mincho 12')
cmdBtn.pack(pady=20)
cmdProgress = ttk.Progressbar(
    top, orient=HORIZONTAL, length=300, mode='determinate')
cmdLabel = Label(top, bg='lightblue')

# Products Frame
productsFrame = LabelFrame(top, bd=5, text='Produits', font=(
    "Helvetica", "15", 'bold'), bg='#FCD1AC')
productsFrame.pack()
productsBtn = Button(productsFrame, text='Collecter', command=lambda: Thread(target=scraper.check_products).start(
), activebackground='white', activeforeground='black', bg='LightPink1', bd=5, padx=5, pady=3, width=9, font='mincho 12')
suppliersBtn = Button(productsFrame, text='Fournisseurs', command=scraper.suppliers, activebackground='white',
                      activeforeground='black', bg='Lightgreen', bd=5, padx=5, pady=3, width=15, font='mincho 12')
suppliersBtn.pack(pady=20)

dictInfo = Label(productsFrame, width=20, height=5, bg='lightblue',
                 text=f'Total CMDs : 0\nTotal Produits : 0\nTotal Quantité : 0')
exportBtn = Button(productsFrame, text='Export to CSV',
                   bd=3, command=scraper.exportToCSV)

progress = ttk.Progressbar(top, orient=HORIZONTAL,
                           length=300, mode='determinate')
productsLabel = Label(top, bg='lightblue')


top.resizable(False, False)
top.mainloop()
