#VIKTIGT TILL JOHAN: För att logga in, användarnamn: johan    lösenord: wrang
#Alla användarnamn & lösenord finns i users_db.csv

import csv
import os
import locale
import msvcrt

#Funktion för att formatera valutan till svenskt format
def format_currency(value):
    return locale.currency(value, grouping=True)

#Klass för att hantera användare och autentisering när man loggar in
class UserManager:
    def __init__(self):
        self.users = [] #Lista för att lagra användare
        self.load_users()

    #Funktion som laddar användarna från users_db csv-filen
    def load_users(self):
        if os.path.exists("users_db.csv"): #Kontrollerar att databasen finns, sedan öppnar
            with open("users_db.csv", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader: #Lägger till varje användare i listan
                    self.users.append({
                        "username": row['username'],
                        "password": row['password']
                    })

    #Funktion för att verifiera användarnamn och lösenord
    def authenticate(self, username, password):
        for user in self.users: #Jämför användarnamn och lösenord
            if user['username'] == username and user['password'] == password:
                return True
        return False

#Klass för produktkategorierna
class Category:
    def __init__(self, id, name, desc):
        self.id = id
        self.name = name
        self.desc = desc
        self.products = [] #Lista för produkter i denna kategori

    #Funktion för att lägga till produkt i kategorin
    def add_product(self, product):
        self.products.append(product)

    #Funktion för att ta bort en produkt ur en kategori
    def remove_product(self, product_id):
        #Filterar bort produkten med matchande ID
        self.products = [p for p in self.products if p['id'] != product_id]

#Huvudklass för produkthantering
class ProductManager:
    def __init__(self):
        self.products = [] #Alla produkter
        self.categories = [] #Alla kategorier
        self.load_data()
        self.ensure_reserve_category()

    #Funktion som skapar ett reservkategori om den inte finns 
    def ensure_reserve_category(self):
        #Kontrollerar om reservkategorin redan finns
        reserve_category = self.get_category_by_id(999)
        if not reserve_category: #Skapar ny reservkategori med ID 999 om den inte finns
            reserve_category = Category(999, "Reservkategori", "Produkter utan kategori")
            self.categories.append(reserve_category)
            self.save_categories()

    #Funktion för att ladda produkt- och kategoridata från CSV-filerna
    def load_data(self):
        #Laddar och öppnar kategorierna från CSV-filen (categories_db)
        if os.path.exists("categories_db.csv"):
            with open("categories_db.csv", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader: #Skapar kategoriobjekt för varje rad
                    category = Category(
                        int(row['id']),
                        row['name'],
                        row['desc']
                    )
                    self.categories.append(category)

        #Laddar produktdata från CSV-filen (products_db)
        if os.path.exists("products_db.csv"):
            with open("products_db.csv", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader: #Hanterar både gamla och nya csv-format 
                    if 'category_id' in row:
                        category_id = int(row['category_id'])
                    else:
                        category_id = 999 #default kategori ID till reservat
                    
                    #Skapar och definierar produktobjekt
                    product = {
                        "id": int(row['id']),
                        "name": row['name'],
                        "desc": row['desc'],
                        "price": float(row['price']),
                        "quantity": int(row['quantity']),
                        "category_id": category_id
                    }
                    self.products.append(product)
                    
                    #Lägger till produkten i rätt kategori
                    category = self.get_category_by_id(category_id)
                    if category:
                        category.add_product(product)

    #Funktion som sparar data (förkortar kod)
    def save_data(self):
        self.save_categories()
        self.save_products()

    #Funktion som sparar data för kategorier när dem ändras, tas bort eller läggs till i csv-filen
    def save_categories(self):
        with open("categories_db.csv", mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["id", "name", "desc"])
            writer.writeheader()
            for category in self.categories: #Skriver varje kategori som en rad i csv-filen
                writer.writerow({
                    "id": category.id,
                    "name": category.name,
                    "desc": category.desc
                })

    #Funktion för att spara data till produkter när de ändras, tas bort eller läggs till i csv-filen
    def save_products(self):
        with open("products_db.csv", mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["id", "name", "desc", "price", "quantity", "category_id"])
            writer.writeheader()
            for product in self.products: #Skriver varje produkt som en rad i csv-filen
                writer.writerow({
                    "id": product['id'],
                    "name": product['name'],
                    "desc": product['desc'],
                    "price": product['price'],
                    "quantity": product['quantity'],
                    "category_id": product['category_id']
                })

    #Funktion som hämtar nästa lediga produkt ID efter det nuvarande största
    def get_next_product_id(self):
        if self.products: #Hittar högsta ID och lägger till 1
            return max(p['id'] for p in self.products) + 1
        return 1 #Första ID

    #Funktion som hämtar nästa lediga kategori ID efter det nuvarande största
    def get_next_category_id(self):
        if self.categories: #Hittar högsta ID och lägger till 1, exkluderar samt 999 (reservkategorin)
            max_id = max(c.id for c in self.categories if c.id != 999)
            return max_id + 1
        return 1

    #Funktion för att hämta kategori med ID
    def get_category_by_id(self, category_id):
        for category in self.categories:
            if category.id == category_id:
                return category
        return None #Returnerar inget om kategorins ID inte hittas

    #Funktion för att hämta kategori med namn
    def get_category_by_name(self, category_name):
        for category in self.categories: #Jämför namn
            if category.name.lower() == category_name.lower():
                return category
        return None #Returnerar inget om kategori namnet inte hittas

    #Funktion för att hämta produkt med ID
    def get_product_by_id(self, product_id):
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None #Returnerar inget om produktens ID inte hittas

    #Funktion för att visa alla produkter organiserat efter kategori
    def show_products_by_category(self):
        print("\033[1;34m" + "="*80)
        print(" " * 30 + "PRODUKTER EFTER KATEGORI")
        print("="*80 + "\033[0m")
        
        if not self.categories:
            print("Inga kategorier finns.")
            return

        #Separerar vanliga kategorier från reservkategori, reservatet visas sist alltid
        regular_categories = [c for c in self.categories if c.id != 999]
        reserve_category = self.get_category_by_id(999)
        
        #Visar alla vanliga kategorier
        for category in regular_categories:
            print(f"\n\033[1;33m{category.name.upper()}\033[0m")
            print(f"\033[1;36m{category.desc}\033[0m")
            print("\033[1;33m" + "-"*80 + "\033[0m")
            
            #Visar produkterna och deras information (objekt) efter kategorin
            if category.products:
                for product in category.products:
                    print(f"ID: {product['id']} | {product['name']} - {product['desc']}, "
                          f"{format_currency(product['price'])}, {product['quantity']} st")
            else: #Om kategorin har inga produkter
                print("Inga produkter i denna kategori")
            print()

        #Visar reservkategorin alltid sist (även om den är tom)
        print("\n\033[1;31m" + "="*80)
        print(" " * 25 + "PRODUKTER UTAN KATEGORI")
        print("="*80 + "\033[0m")
        print(f"\n\033[1;33m{reserve_category.name.upper()}\033[0m")
        print(f"\033[1;36m{reserve_category.desc}\033[0m")
        print("\033[1;33m" + "-"*80 + "\033[0m")
        
        #Visar produkterna i reservkategorin eller om den är tom
        if reserve_category.products:
            for product in reserve_category.products:
                print(f"ID: {product['id']} | {product['name']} - {product['desc']}, "
                      f"{format_currency(product['price'])}, {product['quantity']} st")
        else:
            print("Inga produkter i denna kategori")
        print()

    #Funktion för att visa alla produkter i en kompakt lista efter ID nummer (utan efter kategorier)
    def show_all_products_compact(self):
        print("\033[1;34m" + "="*80)
        print(" " * 30 + "ALLA PRODUKTER")
        print("="*80 + "\033[0m")
        
        if not self.products:
            print("Inga produkter finns.")
            return

        #Visar varje produkt med numrering
        for i, product in enumerate(self.products, 1):
            category = self.get_category_by_id(product['category_id'])
            category_name = category.name if category else "Okänd"
            print(f"{i:2d}. ID: {product['id']} | {product['name']} - {format_currency(product['price'])} | {category_name}")

    #Funktion för att visa alla kategorier och deras information
    def show_all_categories(self):
        print("\033[1;34m" + "="*60)
        print(" " * 20 + "ALLA KATEGORIER")
        print("="*60 + "\033[0m")
        
        #Visar vanliga kategorier först och reservkategori sist
        regular_categories = [c for c in self.categories if c.id != 999]
        reserve_category = self.get_category_by_id(999)
        
        #Loop som visar alla vanliga kategorier
        for category in regular_categories:
            print(f"\033[1;36mID: {category.id}\033[0m")
            print(f"\033[1;32mNamn: {category.name}\033[0m")
            print(f"\033[1;35mBeskrivning: {category.desc}\033[0m")
            print(f"\033[1;33mAntal produkter: {len(category.products)}\033[0m")
            print("\033[1;33m" + "-"*60 + "\033[0m")

        #Prints som visar reservkategorin sist (alltid)
        print("\n\033[1;31m" + "="*60)
        print(" " * 20 + "RESERVKATEGORI")
        print("="*60 + "\033[0m")
        print(f"\033[1;36mID: {reserve_category.id}\033[0m")
        print(f"\033[1;32mNamn: {reserve_category.name}\033[0m")
        print(f"\033[1;35mBeskrivning: {reserve_category.desc}\033[0m")
        print(f"\033[1;33mAntal produkter: {len(reserve_category.products)}\033[0m")
        print("\033[1;33m" + "-"*60 + "\033[0m")

    #Funktion för att visa detaljerad information om en produkt
    def show_product_detail(self, product):
        category = self.get_category_by_id(product['category_id'])
        category_name = category.name if category else "Okänd"
        
        print("\033[1;34m" + "="*80)
        print(" " * 30 + "PRODUKTDETAILJER")
        print("="*80 + "\033[0m")
        print(f"\033[1;36mID: {product['id']}\033[0m")
        print(f"\033[1;32mNamn: {product['name']}\033[0m")
        print(f"\033[1;35mBeskrivning: {product['desc']}\033[0m")
        print(f"\033[1;31mPris: {format_currency(product['price'])}\033[0m")
        print(f"\033[1;36mAntal: {product['quantity']} st\033[0m")
        print(f"\033[1;33mKategori: {category_name}\033[0m")
        print("\033[1;34m" + "="*80 + "\033[0m")

    #Funktion för att bläddre genom produkt med piltangenter (Blädringsläge)
    def browse_products(self):
        if not self.products:
            print("Inga produkter finns.")
            return

        current_index = 0 #Den aktuella produktens ID
        
        while True:
            os.system('cls') #Rensar skärmen
            product = self.products[current_index]
            self.show_product_detail(product)
            
            print("\nNavigering: [←] Föregående [→] Nästa [E] Redigera [D] Ta bort [ESC] Avbryt")
            print(f"Produkt {current_index + 1} av {len(self.products)}")
            
            #Läser tangenttryckning
            key = ord(msvcrt.getch())
            if key == 27:  #ESC - avbryt
                break
            elif key == 224:  #Special tangenter (arrows)
                key = ord(msvcrt.getch())
                if key == 75:  #Vänster pil - Föregående produkt
                    current_index = (current_index - 1) % len(self.products)
                elif key == 77:  #Höger pil - Nästa produkt
                    current_index = (current_index + 1) % len(self.products)
            elif key == 101 or key == 69:  #E - redigera produkt
                self.edit_product_direct(product['id'])
            elif key == 100 or key == 68:  #D - Radera produkt
                if self.remove_product_direct(product['id']):
                    #Om produkt tas bort så justeras index om nödvändigt
                    if not self.products:
                        print("Inga produkter kvar.")
                        input("\nTryck enter för att fortsätta...")
                        break
                    current_index = min(current_index, len(self.products) - 1)

    #Funktion för att kunna redigera en produkt direkt från blädringsläget
    def edit_product_direct(self, product_id):
        product = self.get_product_by_id(product_id)
        if not product:
            print("Produkten finns inte.")
            return

        print("Skriv 'x' för att avbryta ändring, lämna tomt för att behålla nuvarande värde:")
        
        #Ber användaren om nya värden för produkten ('x' avbryter)
        new_name = input(f"Nytt namn [{product['name']}]: ")
        if new_name.lower() == 'x':
            print("Ändring avbruten.")
            return
            
        new_desc = input(f"Ny beskrivning [{product['desc']}]: ")
        if new_desc.lower() == 'x':
            print("Ändring avbruten.")
            return
            
        new_price = input(f"Nytt pris [{product['price']}]: ")
        if new_price.lower() == 'x':
            print("Ändring avbruten.")
            return
            
        new_quantity = input(f"Nytt antal [{product['quantity']}]: ")
        if new_quantity.lower() == 'x':
            print("Ändring avbruten.")
            return
        
        print("Tillgängliga kategorier:")
        self.show_all_categories()
        new_category = input(f"Ny kategori ID [{product['category_id']}]: ")
        if new_category.lower() == 'x':
            print("Ändring avbruten.")
            return

        #Samlar uppdateringar i ordboken
        updates = {}
        if new_name: updates['name'] = new_name
        if new_desc: updates['desc'] = new_desc
        if new_price: updates['price'] = float(new_price)
        if new_quantity: updates['quantity'] = int(new_quantity)
        if new_category: updates['category_id'] = int(new_category)

        #Utför uppdateringen
        if self.update_product(product_id, **updates):
            print("Produkten är uppdaterad!")
        else:
            print("Kunde inte uppdatera produkten.")
        input("\nTryck enter för att fortsätta...")

    #Funktion för att direkt kunna ta bort produkten i bläddringsläge
    def remove_product_direct(self, product_id):
        product = self.get_product_by_id(product_id)
        if product: #Bekräftar och utför raderingen
            print(f"Är du säker att du vill ta bort '{product['name']}'? (j/n)")
            confirm = input().lower()
            if confirm == 'j':
                if self.remove_product(product_id):
                    print("Produkten är borttagen.")
                    input("\nTryck enter för att fortsätta...")
                    return True
            else:
                print("Borttagning avbruten.")
                input("\nTryck enter för att fortsätta...")
        return False

    #Funktion för att lägga till ny kategori
    def add_category(self, name, desc):
        new_id = self.get_next_category_id()
        category = Category(new_id, name, desc)
        self.categories.append(category)
        self.save_data() #Sparas till databasen
        return category

    #Funktion för att uppdatera kategorins värde
    def update_category(self, category_id, name=None, desc=None):
        category = self.get_category_by_id(category_id)
        if category:
            #Uppdaterar namn om angiven
            if name is not None:
                category.name = name
            #Uppdaterar beskrivning om angiven
            if desc is not None:
                category.desc = desc
            self.save_data()
            return True
        return False

    #Funktion för att radera kategori och flytta innehållande produkter till reservkategori
    def remove_category(self, category_id):
        if category_id == 999:
            print("Reservkategorin kan inte tas bort.")
            return False
            
        category = self.get_category_by_id(category_id)
        if category:
            #Hämtar reservkategori för att flytta produkter
            reserve_category = self.get_category_by_id(999)
            
            #Flyttar alla produkter till reservkategorin istället för att radera dem
            for product in category.products[:]:
                product['category_id'] = 999
                category.remove_product(product['id'])
                reserve_category.add_product(product)
            
            #Tar bort kategorin från listan
            self.categories = [c for c in self.categories if c.id != category_id]
            self.save_data()
            return True
        return False

    #Funktion för att lägga till ny produkt
    def add_product(self, name, desc, price, quantity, category_id):
        new_id = self.get_next_product_id()
        product = {
            "id": new_id,
            "name": name,
            "desc": desc,
            "price": price,
            "quantity": quantity,
            "category_id": category_id
        }
        self.products.append(product) #Lägger till produkten
        
        #Lägger till produkten i kategorin
        category = self.get_category_by_id(category_id)
        if category:
            category.add_product(product)
        
        self.save_data()
        return product

    #Funktion för att ta bort produkt
    def remove_product(self, product_id):
        product = self.get_product_by_id(product_id)
        if product:
            self.products = [p for p in self.products if p['id'] != product_id] #Tar bort produkt från huvudlistan
            category = self.get_category_by_id(product['category_id']) #Tar bort produkt från kategorin
            if category:
                category.remove_product(product_id)
            
            self.save_data() #Sparar
            return True
        return False

    #Funktion för att uppdaterar en produkts värden
    def update_product(self, product_id, name=None, desc=None, price=None, quantity=None, category_id=None):
        product = self.get_product_by_id(product_id)
        if product:
            old_category_id = product['category_id']
            
            #Uppdaterar värden om de är angivna
            if name is not None:
                product['name'] = name
            if desc is not None:
                product['desc'] = desc
            if price is not None:
                product['price'] = price
            if quantity is not None:
                product['quantity'] = quantity
            if category_id is not None:
                product['category_id'] = category_id

            #Uppdaterar kategoritillhörighet om nödvändigt
            if category_id is not None and category_id != old_category_id:
                #Tar bort produkt från gamla kategorin
                old_category = self.get_category_by_id(old_category_id)
                if old_category:
                    old_category.remove_product(product_id)
                
                #Lägger till produkt i nya kategorin
                new_category = self.get_category_by_id(category_id)
                if new_category:
                    new_category.add_product(product)

            self.save_data()
            return True
        return False

locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8') #Svensk valutaformatering

#Initierar användarhanterare
user_manager = UserManager()

#Skapar användardatabas om den inte finns
if not os.path.exists("users_db.csv"):
    with open("users_db.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["username", "password"])
        writer.writeheader()

#Inloggningsprocess
logged_in = False
attempts = 0

while not logged_in and attempts < 3:
    #Startar inloggningsrutan och rensar skärmen
    os.system('cls') 
    print("--- INLOGGNING ---")
    username = input("Användarnamn: ")
    password = input("Lösenord: ")
    
    #Om du skriver rätt användarnamn och lösenord som finns i databasen så loggas du in
    if user_manager.authenticate(username, password):
        logged_in = True
        print("Inloggning lyckades!")
        input("\nTryck enter för att fortsätta...")
    else: #Om du misslyckas höjs dina försök, max 3
        attempts += 1
        print("Fel användarnamn eller lösenord.")
        if attempts < 3:
            print(f"Du har {3 - attempts} försök kvar.")
            input("\nTryck enter för att försöka igen...")
        else:
            print("För många felaktiga försök. Programmet avslutas.")
            exit()

#Initierar produkthanterare
manager = ProductManager()

#Huvudmeny-loop
while True:
    #Rensar skärmen och visar alternativ
    os.system('cls')
    print("\033[1;34m" + "="*50)
    print(" " * 15 + "PRODUKTHANTERARE")
    print("="*50 + "\033[0m")
    print("1.  Visa alla produkter (efter kategori)")
    print("2.  Visa alla produkter (kompakt lista)") 
    print("3.  Bläddra bland produkter")
    print("4.  Hämta produkt med ID")
    print("5.  Lägg till produkt")
    print("6.  Ta bort produkt")
    print("7.  Ändra produkt")
    print("8.  Visa alla kategorier")
    print("9.  Lägg till kategori")
    print("10. Ändra kategori")
    print("11. Ta bort kategori")
    print("12. Avsluta")
    print("\033[1;34m" + "="*50 + "\033[0m")
    
    choice = input("Välj ett alternativ: ")
    
    #1. Visar alla produkter efter kategori
    if choice == "1":
        manager.show_products_by_category()
        input("\nTryck enter för att fortsätta...")

    #2. Visar alla produkter i en kompakt lista
    elif choice == "2":
        manager.show_all_products_compact()
        input("\nTryck enter för att fortsätta...")

    #3. Bläddringsläge
    elif choice == "3":
        manager.browse_products()

    #4. Visar en viss produkt och dens information efter ID
    elif choice == "4":
        manager.show_products_by_category()
        try:
            pid = int(input("Ange produkt ID: "))
            product = manager.get_product_by_id(pid)
            if product:
                manager.show_product_detail(product)
                print("\nVill du redigera denna produkt? (j/n)")
                if input().lower() == 'j':
                    manager.edit_product_direct(pid)
            else:
                print("Ingen produkt med det ID hittades.")
        except ValueError:
            print("Felaktig inmatning.")
        input("\nTryck enter för att fortsätta...")

    #5. Lägger till produkt
    elif choice == "5":
        name = input("Produktens namn: ")
        desc = input("Beskrivning: ")
        
        try:
            price = float(input("Pris: "))
            quantity = int(input("Antal: "))
        except ValueError:
            print("Felaktig inmatning för pris eller antal.")
            input("\nTryck enter för att fortsätta...")
            continue
        
        #Visar kategorier innan man väljer en
        print("\nTillgängliga kategorier:")
        manager.show_all_categories()
        
        category_choice = input("Ange kategori ID eller namn: ")
        
        #Hittar kategori baserat på namn eller ID
        category = None
        if category_choice.isdigit():
            category = manager.get_category_by_id(int(category_choice))
        else:
            category = manager.get_category_by_name(category_choice)

        #Frågar användaren om de vill skapa en ny kategori och sedan lägger till produkten där
        if not category:
            print("Kategorin finns inte. Vill du skapa en ny kategori? (j/n)")
            if input().lower() == 'j':
                category_name = input("Kategorins namn: ")
                category_desc = input("Kategoribeskrivning: ")
                category = manager.add_category(category_name, category_desc)
                print(f"Ny kategori '{category.name}' skapad!")
            else:
                print("Produkt ej tillagd.")
                continue
        
        manager.add_product(name, desc, price, quantity, category.id)
        print("Produkten är tillagd!")
        input("\nTryck enter för att fortsätta...")

    #6. Ta bort produkt med ID
    elif choice == "6":
        manager.show_products_by_category()
        try:
            pid = int(input("\nAnge produkt ID att ta bort: "))
            product = manager.get_product_by_id(pid)
            if product: #Frågar och utför raderingen
                print(f"Är du säker att du vill ta bort '{product['name']}'? (j/n)")
                confirm = input().lower()
                if confirm == 'j':
                    if manager.remove_product(pid):
                        print("Produkten är borttagen.")
                    else:
                        print("Kunde inte ta bort produkten.")
                else:
                    print("Borttagning avbruten.")
            else:
                print("Ingen produkt med det ID hittades.")
        except ValueError:
            print("Felaktig inmatning.")
        input("\nTryck enter för att fortsätta...")

    #7. Ändra produkt
    elif choice == "7":
        manager.show_products_by_category()
        try:
            pid = int(input("Ange produkt ID att ändra: "))
            product = manager.get_product_by_id(pid)
            if not product:
                print("Produkten finns inte.")
                input("\nTryck enter för att fortsätta...")
                continue
            
            #Bekräftar ändringen
            print(f"Är du säker att du vill ändra på '{product['name']}'? (j/n)")
            confirm = input().lower()
            if confirm != 'j':
                print("Ändring avbruten.")
                input("\nTryck enter för att fortsätta...")
                continue

            print("Skriv 'x' för att avbryta ändring, lämna tomt för att behålla nuvarande värde:")
            new_name = input(f"Nytt namn [{product['name']}]: ")
            if new_name.lower() == 'x':
                print("Ändring avbruten.")
                input("\nTryck enter för att fortsätta...")
                continue
                
            new_desc = input(f"Ny beskrivning [{product['desc']}]: ")
            if new_desc.lower() == 'x':
                print("Ändring avbruten.")
                input("\nTryck enter för att fortsätta...")
                continue
                
            new_price = input(f"Nytt pris [{product['price']}]: ")
            if new_price.lower() == 'x':
                print("Ändring avbruten.")
                input("\nTryck enter för att fortsätta...")
                continue
                
            new_quantity = input(f"Nytt antal [{product['quantity']}]: ")
            if new_quantity.lower() == 'x':
                print("Ändring avbruten.")
                input("\nTryck enter för att fortsätta...")
                continue
            
            print("Tillgängliga kategorier:")
            manager.show_all_categories()
            new_category = input(f"Ny kategori ID [{product['category_id']}]: ")
            if new_category.lower() == 'x':
                print("Ändring avbruten.")
                input("\nTryck enter för att fortsätta...")
                continue
            
            #Samlar uppdateringarna
            updates = {}
            if new_name: updates['name'] = new_name
            if new_desc: updates['desc'] = new_desc
            if new_price: updates['price'] = float(new_price)
            if new_quantity: updates['quantity'] = int(new_quantity)
            if new_category: updates['category_id'] = int(new_category)

            #Utför uppdateringen
            if manager.update_product(pid, **updates):
                print("Produkten är uppdaterad!")
            else:
                print("Kunde inte uppdatera produkten.")

        except ValueError:
            print("Felaktig inmatning.")
        input("\nTryck enter för att fortsätta...")

    #8. Visa alla kategorier och deras information
    elif choice == "8":
        manager.show_all_categories()
        input("\nTryck enter för att fortsätta...")

    #9. Lägg till ny kategori
    elif choice == "9":
        name = input("Kategorins namn: ")
        desc = input("Beskrivning: ")
        manager.add_category(name, desc)
        print("Kategorin är tillagd!")
        input("\nTryck enter för att fortsätta...")

    #10. Ändra kategori med ID eller namn
    elif choice == "10":
        manager.show_all_categories()
        try:
            category_input = input("Ange kategori ID eller namn att ändra: ")
            category = None
            if category_input.isdigit():
                category = manager.get_category_by_id(int(category_input))
            else:
                category = manager.get_category_by_name(category_input)

            if not category:
                print("Kategorin finns inte.")
                input("\nTryck enter för att fortsätta...")
                continue
            
            #Bekräftar ändringen
            print(f"Är du säker att du vill ändra på '{category.name}'? (j/n)")
            confirm = input().lower()
            if confirm != 'j':
                print("Ändring avbruten.")
                input("\nTryck enter för att fortsätta...")
                continue

            print("Skriv 'x' för att avbryta ändring, lämna tomt för att behålla nuvarande värde:")
            new_name = input(f"Nytt namn [{category.name}]: ")
            if new_name.lower() == 'x':
                print("Ändring avbruten.")
                input("\nTryck enter för att fortsätta...")
                continue
                
            new_desc = input(f"Ny beskrivning [{category.desc}]: ")
            if new_desc.lower() == 'x':
                print("Ändring avbruten.")
                input("\nTryck enter för att fortsätta...")
                continue
            
            #Utför uppdateringen
            if new_name:
                category.name = new_name
            if new_desc:
                category.desc = new_desc

            manager.save_data() #Sparar data
            print("Kategorin är uppdaterad!")
        except ValueError:
            print("Felaktig inmatning.")
        input("\nTryck enter för att fortsätta...")

    #11. Ta bort kategori, flytta eventuella innehållande produkter till reservat
    elif choice == "11":
        manager.show_all_categories()
        try:
            category_input = input("Ange kategori ID eller namn att ta bort: ")
            category = None
            
            #Kontrollerar om användaren matar in ett namn eller ID
            if category_input.isdigit():
                category = manager.get_category_by_id(int(category_input))
            else:
                category = manager.get_category_by_name(category_input)

            if category:
                #Förhindrar borttagning av reservkategori
                if category.id == 999:
                    print("Reservkategorin kan inte tas bort.")
                    input("\nTryck enter för att fortsätta...")
                    continue
                
                #Bekräftar borttagning
                print(f"Är du säker att du vill ta bort kategorin '{category.name}'? (j/n)")
                confirm = input().lower()
                if confirm == 'j':
                    if manager.remove_category(category.id):
                        print("Kategorin är borttagen. Alla produkter har flyttats till reservkategorin.")
                    else:
                        print("Kunde inte ta bort kategorin.")
                else:
                    print("Borttagning avbruten.")
            else:
                print("Ingen kategori med det ID/namn hittades.")
        except ValueError:
            print("Felaktig inmatning.")
        input("\nTryck enter för att fortsätta...")

    #12. Avsluta programmet
    elif choice == "12":
        print("Avslutar...")
        break

    else:
        print("Felaktigt val.")
        input("\nTryck enter för att fortsätta...")