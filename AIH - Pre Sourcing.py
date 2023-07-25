from tkinter import messagebox, ttk
from tkinter import *
from tkcalendar import DateEntry
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml import etree
import re, time, os, requests, sys, json
from datetime import datetime, datetime, timedelta
from dateutil.parser import parse
from threading import Thread
from pathlib import Path
import babel.numbers

if not os.path.isfile("__auth__.py" or "suppliers.json"):
    messagebox.showerror('AIH Sourcing', 'Missing File "__auth__" OR "suppliers.json"')
    sys.exit()
from __auth__ import * 

####################### Invoices Downloader & Products Exporter #######################
fileN = f'{datetime.now().strftime("%Y-%m-%d-%Hh-%Mmin")}.csv'
DEFAULT_SUPPLIER = "CDP"

with open("suppliers.json", "r") as f:
    suppliers_products = json.load(f)
    ALL_PRODUCTS = [product for List in suppliers_products.values() for product in List]


class Sourcing:
    def __init__(self, DictProducts = {DEFAULT_SUPPLIER: {}}, total_cmds = 0, total_products = 0, total_quantities = 0): 
        self.DictProducts = DictProducts
        self.total_cmds = total_cmds
        self.total_products = total_products
        self.total_quantities = total_quantities
   

    def __check_date_validation(self):
        From = re.sub('[^0-9-]' , '', fromDate.get())
        To = re.sub('[^0-9-]' , '', toDate.get())
        date1 = From.split('-')
        date2 = To.split('-')
        try:
            parse(From)
            parse(To)
            if date1 > date2:
                messagebox.showerror('INVALID DATE', 'Date "From" must be before Date "To" - Set a VALID Date \nEx : \n2022-01-01 \n2022-01-02')
                return 0
            else:
                return 1
        except:
            messagebox.showerror('INVALID DATE', 'Invalid Format - Set a VALID Date \nEx : \n2023-01-01 \n2023-01-02')
            return 0




    ########## Invoices downloader ##########
    def Para_CMDs(self):
        if not self.__check_date_validation(): return
        start = time.time()

        cmdBtn.config(state='disabled')

        if selected.get() == 'Parabio':
            apiSite = PARABIO_API_LINK
        else:
            apiSite = STORE_API_LINK
            
        toDate_ = datetime.strptime(toDate.get(),'%Y-%m-%d')+timedelta(1)
        toDate_ = toDate_.strftime('%Y-%m-%d')
        exactTime_ = re.sub('[^0-9]', '', exactTime.get())
        exactTime_ = f'{exactTime_[:2]}:{exactTime_[2:4]}:{exactTime_[4:]}'
        try:
            ordersLink= f'{apiSite}?filter[invoice_date]=[{fromDate.get()} {exactTime_},{toDate_}]&filter[current_state]=[2,3]'
            request = requests.get(ordersLink, auth=(apiKey,''))
            root = etree.fromstring(request.content)
            orders =  root.xpath('//order')
            IDs = [order.attrib['id'] for order in orders]

            if IDs:
                for id in IDs:
                    cmdProgress.pack(pady=5)
                    cmdLabel.pack()
                    cmdLabel.config(text=f'Téléchargement : Commande {IDs.index(id)+1}/{len(IDs)}')
                    top.update_idletasks()
                    cmdProgress['value'] += 100/len(IDs)
                    pdf_link = PDF_LINK_GENERATOR
                    pdf_request = requests.get(pdf_link)
                    if not os.path.isdir("commandes"): os.mkdir("commandes")
                    filename = Path(f'commandes/{id}.pdf')
                    filename.write_bytes(pdf_request.content)


                cmdProgress.stop()
                cmdProgress.pack_forget()
                cmdLabel.pack_forget()
                end = time.time()
                duration = end-start
                messagebox.showinfo('Commandes', f'Terminée en: {round(duration,2)} Secs\n\n{len(IDs)} Commandes Téléchargées')
            else:
                messagebox.showinfo('Commandes' ,'9adia nashfa..')
        
        except Exception as e:
                    messagebox.showerror('Error', f'{e}\nerror line: {sys.exc_info()[-1].tb_lineno}')
                    cmdProgress.stop()
                    cmdLabel.config(text=f'Téléchargement : Erreur')
                    
        cmdBtn.config(state='active')
    

    ########## Products Exporter ##########
    def __getProducts(self, orderLink):
        try:
            r = requests.get(orderLink, auth=(apiKey,''))
            root = etree.fromstring(r.content)
            products =  root.xpath("//product_name")
            prices = root.xpath("//product_price")
            quantities = root.xpath("//product_quantity")

            for product, price,quantity in zip(products,prices,quantities):
                product = product.text.replace("  ", " ")
                item = f"{product} | {price.text[:-4]} DH"
                if product not in ALL_PRODUCTS:
                    self.DictProducts[DEFAULT_SUPPLIER][item] = int(self.DictProducts[DEFAULT_SUPPLIER][item]) + int(quantity.text) if item in self.DictProducts[DEFAULT_SUPPLIER] else int(quantity.text)
                else:
                    for supplier, products in suppliers_products.items():
                        if product in products:
                            if supplier in self.DictProducts:
                                self.DictProducts[supplier][item] = int(self.DictProducts[supplier][item]) + int(quantity.text) if item in self.DictProducts[supplier] else int(quantity.text)
                            else:
                                self.DictProducts[supplier] = {}
                                self.DictProducts[supplier][item] = int(self.DictProducts[supplier][item]) + int(quantity.text) if item in self.DictProducts[supplier] else int(quantity.text)
                            break

        except Exception as e:
            messagebox.showerror('Produits', e)


    def exportToCSV(self):
        for key, value in self.DictProducts.items():
            with open(f"{key}-{fileN}", 'a', encoding='utf-16') as f:
                for key, value in value.items():
                    f.write(f"{key} | Qté : {value}\n")

        messagebox.showinfo('Produits' , f'Total Produits : {self.total_products}\nTotal Quantité : {self.total_quantities}\nExported to CSV')
        self.DictProducts = {DEFAULT_SUPPLIER : {}}
        self.total_cmds = 0
        self.total_products = 0   
        self.total_quantities = 0
        dictInfo.config(bg="lightblue",text=f'Total CMDs : {self.total_cmds}\nTotal Produits : {self.total_products}\nTotal Quantité : {self.total_quantities}')
        exportBtn.config(state='disabled')

    
    def Para_Products(self):
        if not self.__check_date_validation(): return

        start = time.time()

        productsBtn.config(state='disabled')
        exportBtn.config(state='disabled')

        if selected.get() == "Parabio":
            apiSite = PARABIO_API_URL
        else:
            apiSite = STORE_API_URL
        
        toDate_ = datetime.strptime(toDate.get(),'%Y-%m-%d')+timedelta(1)
        toDate_ = toDate_.strftime('%Y-%m-%d')
        exactTime_ = re.sub('[^0-9]', '', exactTime.get())
        exactTime_ = f'{exactTime_[:2]}:{exactTime_[2:4]}:{exactTime_[4:]}'

        try:
            ordersLink= f'{apiSite}?filter[invoice_date]=[{fromDate.get()} {exactTime_},{toDate_}]&filter[current_state]=[2,3]'
            request = requests.get(ordersLink, auth=(apiKey,''))
            root = etree.fromstring(request.content)
            orders =  root.xpath('//order')
            cmd_links = set([order.attrib['{http://www.w3.org/1999/xlink}href'] for order in orders])
        
        
            for link in cmd_links:
                progress.pack(pady=5)
                productsLabel.pack()
                productsLabel.config(text=f'l\'Extraction des Produits : Commande {list(cmd_links).index(link)+1}/{len(cmd_links)}')
                top.update_idletasks()
                progress['value'] += 100/len(cmd_links)
               
                self.__getProducts(link)
            
            self.total_cmds += len(cmd_links)
            progress.stop()
            progress.pack_forget()
            productsLabel.pack_forget()
            end = time.time()
            duration = end-start
            if cmd_links:
                self.total_products = sum(len(v) for v in self.DictProducts.values())
                self.total_quantities = sum([sum(q.values()) for q in (v for v in self.DictProducts.values())])
                dictInfo.config(bg="lightgreen",text=f'Total CMDs : {self.total_cmds}\nTotal Produits : {self.total_products}\nTotal Quantité : {self.total_quantities}')              
                messagebox.showinfo('Produits' ,f'Terminée en : {round(duration,2)} Secs')
            else: messagebox.showinfo('Produits' ,'9adia nashfa..')

            cmd_links.clear() # clear cmd_links to avoid re-exporting old orders
            
            

        except Exception as e:
            messagebox.showerror('Error', f"{e},'\nerror line: ',{sys.exc_info()[-1].tb_lineno}")
            progress.stop()
            progress.pack_forget()
            productsLabel.pack_forget()

        if self.DictProducts != {"CDP": {}}: exportBtn.config(state='active')

        productsBtn.config(state='active')
    

    ########## Suppliers Products Updater ##########
    def updateSuppliersProducts(self):
        global suppliers_products, ALL_PRODUCTS
        try:
            r = requests.get(SUPPLIERS_LINK, auth=(apiKey,''))
            root = etree.fromstring(r.content)
            suppliers =  root.xpath("//supplier")
            EXCLUDED = ["3", "4", "10"]
            IDs = [supplier.attrib['id'] for supplier in suppliers if supplier.attrib['id'] not in EXCLUDED]
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.maximize_window()
            driver.get(PARAPHARMA_BACKOFFICE)
            user = driver.find_element(By.ID, "email")
            user.send_keys(u)
            passwd = driver.find_element(By.ID, "passwd")
            passwd.send_keys(p)
            driver.find_element(By.NAME , "submitLogin").click()
            # Wait until it loads
            WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.XPATH, '//*[@id="tab-AdminDashboard"]/a/span')))
            # Go to Suppliers
            driver.find_element(By.XPATH , '//*[@id="subtab-AdminCatalog"]/a/span').click()
            time.sleep(1.5)
            driver.find_element(By.ID, 'subtab-AdminParentManufacturers').click()
            # Get Token 
            token_value = driver.find_element(By.XPATH, '/html/body').get_attribute('data-token')
            suppliers_data = {}
            for id in IDs:
                driver.get(f"https://parapharma.ma/ADMINISTRATION/index.php/sell/catalog/suppliers/{id}/products?_token={token_value}")
                name = driver.find_element(By.TAG_NAME, "h1").text
                products = driver.find_elements(By.CLASS_NAME, "card-header.clearfix")
                suppliers_data[name] = [product.text for product in products]

            with open("suppliers.json", "w+") as f:
                json.dump(suppliers_data, f)
                suppliers_products = json.load(f)
                ALL_PRODUCTS = [product for List in suppliers_products.values() for product in List]
                driver.quit()
                messagebox.showinfo('Fournisseurs', "La liste des fournisseurs à été mise à jour")
        
        
        except Exception as e:
            messagebox.showerror('Fournisseurs', e)


autoSourcing = Sourcing()

################################ GUI ################################

top = Tk()
if os.path.isfile("para17.ico"): top.iconbitmap('para17.ico')
top.title("AIH Sourcing - v3.0")
top.configure(background='coral')

if os.path.isfile("bg.png"):
    filename = PhotoImage(file = r"bg.png")
    background_label = Label(top, image=filename)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

menu = Menu()
update = Menu(menu,tearoff=False)
menu.add_cascade(label = 'Mise à jour', menu = update)
update.add_command(label = 'Mettre à jour les fournisseurs' , command = autoSourcing.updateSuppliersProducts)
top.config(menu=menu)
top.geometry('500x850+800+100')

stores = ['Parapharma', 'Coinpara', 'Parabio']
selected = StringVar()
selected.set(stores[0])
drop = OptionMenu( top , selected , *stores )
drop.pack(pady=5)
drop["menu"].configure(bg="lightgreen", borderwidth=1, font=("Helvetica", "9", 'bold'))


fromlabel = Label(top, text='From :',bg='lightblue')
fromlabel.pack(pady=15)
fromDate = DateEntry(date_pattern='yyyy-mm-dd')
fromDate.pack()
tolabel = Label(top, text='To : ',bg='lightblue')
tolabel.pack(pady=5)
toDate = DateEntry(date_pattern='yyyy-mm-dd')
toDate.pack(pady=5)
timeLabel = Label(top, text='HHMMSS',bg='orange')
timeLabel.pack()
exactTime = Entry(top, width=6)
exactTime.pack(pady=5)
exactTime.insert(END, '000000')

cmdFrame = LabelFrame(top,bd=5, text='Commandes', font=("Helvetica", "15", 'bold'), bg='lightblue')
cmdFrame.pack(pady=20)
cmdBtn = Button(cmdFrame,text='Télécharger',command=lambda: Thread(target=autoSourcing.Para_CMDs).start(),activebackground='white',activeforeground='black',bg='cyan',bd =5,padx=5,pady=3,width=9,font='mincho 12')
cmdBtn.pack(pady=20)
cmdProgress = ttk.Progressbar(top, orient=HORIZONTAL, length=300, mode='determinate')
cmdLabel = Label(top,bg='lightblue')

# Products Frame
productsFrame = LabelFrame(top,bd=5, text='Produits', font=("Helvetica", "15", 'bold'), bg='#FCD1AC')
productsFrame.pack()
productsBtn = Button(productsFrame,text='Collecter',command=lambda: Thread(target=autoSourcing.Para_Products).start(),activebackground='white',activeforeground='black',bg='LightPink1',bd =5,padx=5,pady=3,width=9,font='mincho 12')
productsBtn.pack(pady=20)


dictInfo = Label(productsFrame, width=20, height=5, bg='lightblue',text=f'Total CMDs : 0\nTotal Produits : 0\nTotal Quantité : 0')
dictInfo.pack(pady=20)
exportBtn = Button(productsFrame, text='Export to CSV',bd =3, command=autoSourcing.exportToCSV, state="disabled")
exportBtn.pack(pady=20)

progress = ttk.Progressbar(top, orient=HORIZONTAL, length=300, mode='determinate')
productsLabel = Label(top,bg='lightblue')

top.mainloop()
