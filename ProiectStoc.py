from datetime import datetime
import pygal
import smtplib
import re
import pymysql


class Stoc:
    """Tine stocul unui depozit"""

    def __init__(self, prod, categ, um='Buc', pret=5, sold=0, limita_stoc = 0):
        self.prod = prod			# parametri cu valori default ii lasam la sfarsitul listei
        self.categ = categ  		# fiecare instanta va fi creata obligatoriu cu primii trei param.
        self.sold = sold			# al patrulea e optional, soldul va fi zero
        self.um = um
        self.pret = pret            #R.8.parametru pret - default 5, cu acesta se face media pentru pretul de iesire
        self.i = {}					# fiecare instanta va avea trei dictionare intrari, iesiri, data
        self.i_p = {}					#R.8. dictionar pret intrare
        self.e = {}					# pentru mentinerea corelatiilor cheia operatiunii va fi unica
        self.e_p = {}					#R.8 dictionar pret iesire
        self.d = {}
        self.limita_stoc = limita_stoc

    def intr(self, cant, data=str(datetime.now().strftime('%Y%m%d')), pret=4):
        self.data = data
        self.cant = cant
        self.sold += cant          # recalculam soldul dupa fiecare tranzactie
        if self.d.keys():               # dictionarul data are toate cheile (fiecare tranzactie are data)
            cheie = max(self.d.keys()) + 1
        else:
            cheie = 1
        self.i[cheie] = cant       # introducem valorile in dictionarele de intrari si data
        self.i_p[cheie] = pret       # introducem valorile in dictionarele de intrari, data si pret intrare
        self.d[cheie] = self.data

    def iesi(self, cant, data=str(datetime.now().strftime('%Y%m%d'))):
        #   datetime.strftime(datetime.now(), '%Y%m%d') in Python 3.5
        self.data = data
        self.cant = cant
        self.sold -= self.cant
        if self.sold<self.limita_stoc:      #2. Trimite automat un email cand stocul este mai mic decat limita minima
            print("Sold mai mic decat limita minima")
            self.trimite_email("Sold mai mic decat limita minima")
            
        if self.d.keys():
            cheie = max(self.d.keys()) + 1
        else:
            cheie = 1
        self.e[cheie] = self.cant       # similar, introducem datele in dictionarele iesiri si data
        self.d[cheie] = self.data
        pret_nou = (int(self.i_p[cheie-1])+int(self.pret))/2
        self.pret = pret_nou
        self.e_p[cheie] = pret_nou       # similar, introducem datele in dictionarele iesiri si data

    def fisa(self):     #3. Fisa trimisa pe mail
        s=""
        s+=str('Fisa produsului - ' + self.prod + ': ' + self.um +'\n')
        s+=str(45 * '-' +'\n')
        s+=str(' Nrc '+ '\t Data '+ '\t Intrari '+ ' Iesiri ' + ' Pret ' +'\n')
        s+=str(45 * '-' +'\n')
        for v in self.d.keys():
            if v in self.i.keys():
                s+=str(str(v).rjust(5)+'\t'+self.d[v]+str(self.i[v]).rjust(6)+str(0).rjust(6) + str(self.i_p[v]).rjust(6) +'\n')
            else:
                s+=str(str(v).rjust(5)+'\t'+self.d[v]+str(0).rjust(6)+str(self.e[v]).rjust(6) + str(self.e_p[v]).rjust(6) +'\n')
        s+=str(45 * '-' +'\n')
        s+=str('Stoc actual:  ' + str(self.sold).rjust(10) +'\n')
        s+=str(45 * '-' + '\n')
        s+=str('Pret actual:  ' + str(self.pret).rjust(24) +'\n')
        s+=str(45 * '-' + '\n')
        return s

    def fisap(self):

        print('Fisa produsului ' + self.prod + ': ' + self.um)
        print(40 * '-')
        print(' Nrc ', '  Data ', ' Intrari ', ' Iesiri ', ' Pret ')
        print(40 * '-')
        for v in self.d.keys():
            if v in self.i.keys():
                print(str(v).rjust(5), self.d[v]+str(self.i[v]).rjust(6), str(0).rjust(6), str(self.i_p[v]).rjust(6))
            else:
                print(str(v).rjust(5), self.d[v], str(0).rjust(6), str(self.e[v]).rjust(6), str(self.e_p[v]).rjust(6))
        print(40 * '-')
        print('Stoc actual:      ' + str(self.sold).rjust(10))
        print(40 * '-' + '\n')
        print('Pret actual:  ' + str(self.pret).rjust(24) +'\n')
        print(40 * '-' + '\n')
        
        #R.9. Mi multe metode noi, diferite de cele facute la clasa
        
    def bar_chart(self):        #R.1. Proiectie grafica a intrarilor si iesirilor cu -pygal-
        lista_intrari = []
        for intrare in self.i:
            lista_intrari.append(self.i[intrare])
            
        lista_iesiri = []
        for iesire in self.e:
            lista_iesiri.append(self.e[iesire])

        idx=0
        lista_date = []
        for data in self.d:
            if(idx%2==0):
                lista_date.append(datetime.strptime(self.d[data],'%Y%m%d').strftime('%d %b %Y'))
            idx=idx+1

        bar_chart = pygal.Bar()
        bar_chart.title = 'Chart Intrari-iesiri'
        bar_chart.x_labels = lista_date
        bar_chart.add('Stoc_intrari', lista_intrari)
        bar_chart.add('Stoc_iesiri', lista_iesiri)
        bar_chart.render_to_file('chart.svg')

    def trimite_email(self, mesaj):     #R.2-3. Metoda trimite un email
        
        self.mesaj = mesaj
        
        to = '***'  #Adresa destinatar
        gmail_user = '***' #Adresa utilizator
        gmail_pwd = '***' #Parola mail
        smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(gmail_user, gmail_pwd)
        header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject: Atentionare stoc \n'
        print(header)
        msg = header + f'\n {mesaj} \n\n'
        smtpserver.sendmail(gmail_user, to, msg)
        print('done!')
        smtpserver.close()
        
    def mail_fisap(self):   #R.3. Trimite pe mail fisa produsului
        mail = self.fisa()
        return self.trimite_email(mail)
    
    def cauta(self, inp):       #R.4.Cauta un produs intordus de utilizator
        if re.findall(inp+'$', self.prod) or re.findall('^'+inp, self.prod): #Pentru produsele deja stocate in clasa
            return True
        return False
    
    def cauta_tranzactie(self, inp, tip_input):     #R.4.Cauta tranzactie
        s=''
        if(re.findall('\D+', inp)):
            return False
        
        cheie=1
        while cheie<=max(self.e.keys()):

            if tip_input==1:
                if(cheie in self.i.keys() and int(self.i[cheie])==int(inp)):
                    print(str(cheie).rjust(5), str(self.d[cheie]), str(self.i[cheie]).rjust(6), str(0).rjust(6))
            else:
                if(cheie in self.e.keys() and int(self.e[cheie])==int(inp)):
                    print(str(cheie).rjust(5), str(self.d[cheie]), str(0).rjust(6), str(self.e[cheie]).rjust(6))
            cheie+=1

    def create_db(self):        #R.5.Creeaza baza de date

        con = pymysql.connect("localhost","root","")
        con1 = pymysql.connect("localhost","root","")

        c = con.cursor()
        curs = con1.cursor()
        c.execute('DROP DATABASE IF EXISTS db_py')
        curs.execute('CREATE DATABASE IF NOT EXISTS db_py')
        c.execute('use db_py')
        
        c.execute("""CREATE TABLE Categoria (
                    idc INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    denc VARCHAR(255)
                    )""")
        c.execute("""CREATE TABLE Produs (
                    idp INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    idc INT NOT NULL,
                    denp VARCHAR(255),
                    pret DECIMAL(8,2) DEFAULT 0
                    )""")
        c.execute("""CREATE TABLE Operatiuni (
                    ido INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    idp INT NOT NULL,
                    cant DECIMAL(10,3) DEFAULT 0,
                    data DATE
                    )""")

    def clear_db(self):     #Curata baza de date inainte de fiecare rulare
        db = pymysql.connect("localhost","root","","db_py" )
        cursor = db.cursor()
        
        sql = """TRUNCATE TABLE categoria"""

        cursor.execute(sql)
        db.commit()
        
        sql = """TRUNCATE TABLE produs"""

        cursor.execute(sql)
        db.commit()

        sql = """TRUNCATE TABLE operatiuni"""

        cursor.execute(sql)
        db.commit()

        db.close()

    def populeaza_db(self):     #R.6.Populare baza de date
        db = pymysql.connect("localhost","root","","db_py" ) 
        cursor = db.cursor()
        
        sql = """INSERT INTO categoria(denc)
        VALUES ('"""+str(self.categ)+"""')"""
        
        cursor.execute(sql)
        db.commit()

        categ_id = cursor.lastrowid
        
        sql = """INSERT INTO produs(idc, denp, pret)
        VALUES ('"""+str(categ_id)+"""', '"""+str(self.prod)+"""', '"""+str(self.pret)+"""')"""
        
        cursor.execute(sql)
        db.commit()
        
        prod_id = cursor.lastrowid
        for cheie in self.i:
            sql = """INSERT INTO operatiuni(idp, cant, data)
            VALUES ('"""+str(prod_id)+"""', '"""+str(self.i[cheie])+"""', CAST('"""+str(self.d[cheie])+"""' as date))"""
            
            cursor.execute(sql)
            db.commit()
        
        for cheie in self.e:
            sql = """INSERT INTO operatiuni(idp, cant, data)
            VALUES ('"""+str(prod_id)+"""', '"""+str(-self.e[cheie])+"""', CAST('"""+str(self.d[cheie])+"""' as date))"""
            
            cursor.execute(sql)
            db.commit()
        
        db.close()
        
# Sunt create instantele clasei
fragute = Stoc('fragute', 'fructe', 'kg', limita_stoc = 30)       
lapte = Stoc('lapte', 'lactate', 'litru', limita_stoc = 24, pret=2)
ceasuri = Stoc('ceasuri', 'ceasuri', limita_stoc = 10)

fragute.sold                    # ATRIBUTE
fragute.prod
fragute.intr(100, '20201012')
fragute.iesi(73, '20201012')
fragute.intr(100, '20201013')
fragute.iesi(85, '20201013')
fragute.intr(100, '20201014')
fragute.iesi(101, '20201014')

fragute.bar_chart()
fragute.mail_fisap()

fragute.d                       # dictionarele produsului cu informatii specializate
fragute.i
fragute.e


fragute.sold
fragute.categ
fragute.prod
fragute.um


fragute.fisap()

lapte.intr(1500)
lapte.iesi(975)
lapte.intr(1200)
lapte.iesi(1490)
lapte.intr(1000)
lapte.iesi(1200)

lapte.fisap()

l = [fragute, lapte, ceasuri]

for i in l:
    i.fisap()


nume_produse_input = input('Ce produs cauti? ').lower()      #R.4.Cauta produs - produsul cautat trebuie sa inceapa sau sa se termine cu literele produselor stocate
gasit = 0
gasit_tranzactie = 0
for produs in l:
    if produs.cauta(nume_produse_input):
        gasit=1
        print('Produsul gasit este:')
        print(produs.fisa())
        tip_input = 0
        while(tip_input<1 or tip_input>2):
            try: 
                tip_input = int(input('Introdu tipul tranzactiei (1=intrari, 2=iesiri): '))
            except ValueError:
                continue
            
        input_corect = False
        while True:
            try:
                tranzactie_input = input('Introdu valoarea tranzactiei: ')
                input_corect = produs.cauta_tranzactie(tranzactie_input, tip_input)
                if input_corect == False:  
                    print('Valoarea nu a fost gasita!')
                else:
                    break
            except ValueError:
                print("Nu exista intrari sau iesiri pentru produsul selectat!")
                break
   
if gasit==0:
    print('Nu am gasit produsul')

fragute.create_db()

for i in l:
    i.clear_db()
    
for i in l:
    i.populeaza_db()
