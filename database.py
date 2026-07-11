import json
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_file = "database_state.json"
        self.webapp_products_file = "products.json"
        self.load_data()

    def load_data(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.users = data.get("users", {})
                    self.products = data.get("products", [])
                    self.orders = data.get("orders", [])
                    self.carts = data.get("carts", {})
                    self.admins = data.get("admins", [])
                    self.couriers = data.get("couriers", [])
                    self.admin_contact = data.get("admin_contact", {"name": "Fast Food Admin", "phone": "+998 90 123 45 67", "username": "@admin"})
                    self.categories = data.get("categories", [])
                    self.admin_accounts = data.get("admin_accounts", [{"login": "opetito321", "password": "opetittox555", "name": "Asosiy Admin", "is_superadmin": True}])
                    self.admin_sessions = data.get("admin_sessions", {})
                    self.companies = data.get("companies", [])
                except Exception:
                    self._init_default()
        else:
            self._init_default()

        # Eski admin_accounts ga is_superadmin field qo'shish (migratsiya)
        for acc in self.admin_accounts:
            if 'is_superadmin' not in acc:
                if acc.get('login') == 'opetito321':
                    acc['is_superadmin'] = True
                else:
                    acc['is_superadmin'] = False

        self.save_data()
        self.export_webapp_products()

    def _init_default(self):
        self.users = {}
        self.products = []
        self.orders = []
        self.carts = {}
        self.admins = []
        self.couriers = []
        self.admin_contact = {"name": "Fast Food Admin", "phone": "+998 90 123 45 67", "username": "@admin"}
        self.categories = []
        self.admin_accounts = [{"login": "opetito321", "password": "opetittox555", "name": "Asosiy Admin", "is_superadmin": True}]
        self.admin_sessions = {}
        self.companies = []
        self.save_data()

    def save_data(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump({
                "users": getattr(self, 'users', {}),
                "products": getattr(self, 'products', []),
                "orders": getattr(self, 'orders', []),
                "carts": getattr(self, 'carts', {}),
                "admins": getattr(self, 'admins', []),
                "couriers": getattr(self, 'couriers', []),
                "admin_contact": getattr(self, 'admin_contact', {"name": "Fast Food Admin", "phone": "+998 90 123 45 67", "username": "@admin"}),
                "categories": getattr(self, 'categories', []),
                "admin_accounts": getattr(self, 'admin_accounts', []),
                "admin_sessions": getattr(self, 'admin_sessions', {}),
                "companies": getattr(self, 'companies', [])
            }, f, ensure_ascii=False, indent=4)

    def export_webapp_products(self):
        """Export all companies' products for WebApp"""
        # Global fallback (barcha kompaniyalar produktlari)
        all_products = [p for p in self.products if p.get('is_active', 1)]
        cats = getattr(self, 'categories', [])

        # Kompaniyalar ro'yxatini ham export qilamiz
        companies_export = []
        for c in self.companies:
            if c.get('is_frozen'): continue
            company_products = [p for p in c.get('products', []) if p.get('is_active', 1)]
            company_cats = c.get('categories', [])
            companies_export.append({
                "id": c['id'],
                "name": c['name'],
                "categories": company_cats,
                "products": company_products
            })

        data_obj = {
            "categories": cats,
            "products": all_products,
            "companies": companies_export
        }

        dir_name = os.path.dirname(self.webapp_products_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(self.webapp_products_file, 'w', encoding='utf-8') as f:
            json.dump(data_obj, f, ensure_ascii=False, indent=4)

    async def connect(self):
        print("JSON bazasi ishga tushdi")

    async def close(self):
        self.save_data()

    # ========================
    # COMPANY METHODS
    # ========================
    async def get_companies(self):
        return getattr(self, 'companies', [])

    async def get_company(self, company_id):
        for c in self.companies:
            if c['id'] == company_id:
                return c
        return None

    async def get_company_by_login(self, login):
        """Admin login bo'yicha kompaniyani topish"""
        for acc in self.admin_accounts:
            if acc.get('login') == login:
                company_id = acc.get('company_id')
                if company_id:
                    return await self.get_company(company_id)
        return None

    async def add_company(self, name, login, password):
        """Yangi kompaniya va uning admin akkauntini qo'shish"""
        c_id = 1
        if self.companies:
            c_id = max(c['id'] for c in self.companies) + 1

        new_company = {
            "id": c_id,
            "name": name,
            "products": [],
            "categories": [],
            "couriers": [],
            "orders": [],
            "admin_contact": {"name": name, "phone": "", "username": ""},
            "is_frozen": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.companies.append(new_company)

        # Kompaniya uchun admin akkaunt yaratamiz
        self.admin_accounts.append({
            "login": login,
            "password": password,
            "name": name + " Admin",
            "is_superadmin": False,
            "company_id": c_id
        })

        self.save_data()
        self.export_webapp_products()
        return new_company

    async def delete_company(self, company_id):
        """Kompaniyani va uning admin akkauntini o'chirish"""
        # Kompaniyaning admin akkauntlarini o'chirish
        self.admin_accounts = [
            a for a in self.admin_accounts
            if a.get('company_id') != company_id
        ]
        # Kompaniyani o'chirish
        self.companies = [c for c in self.companies if c['id'] != company_id]
        self.save_data()
        self.export_webapp_products()

    async def toggle_company_freeze(self, company_id):
        """Kompaniyani muzlatish yoki faollashtirish"""
        for c in self.companies:
            if c['id'] == company_id:
                c['is_frozen'] = not c.get('is_frozen', False)
                break
        self.save_data()
        self.export_webapp_products()

    async def get_company_id_for_admin(self, user_id):
        """Admin user_id bo'yicha uning kompaniyasini topish"""
        login = self.admin_sessions.get(str(user_id))
        if not login:
            return None
        for acc in self.admin_accounts:
            if acc.get('login') == login:
                return acc.get('company_id')  # None = superadmin
        return None

    async def is_superadmin_session(self, user_id):
        """Foydalanuvchi superadmin sifatida kirganmi?"""
        login = self.admin_sessions.get(str(user_id))
        if not login:
            return False
        for acc in self.admin_accounts:
            if acc.get('login') == login:
                return acc.get('is_superadmin', False)
        # Agar login topilmasa — eski superadmin
        return True

    # ========================
    # USER METHODS
    # ========================
    async def add_user(self, telegram_id, fullname, phone=None, lang="uz", username=None):
        telegram_id_str = str(telegram_id)
        if telegram_id_str not in self.users:
            self.users[telegram_id_str] = {
                "id": len(self.users) + 1,
                "telegram_id": telegram_id,
                "fullname": fullname,
                "username": username,
                "phone": phone,
                "lang": lang,
                "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            self.save_data()
        elif username and self.users[telegram_id_str].get("username") != username:
            self.users[telegram_id_str]["username"] = username
            self.save_data()

    async def set_user_lang(self, telegram_id, lang):
        telegram_id_str = str(telegram_id)
        if telegram_id_str in self.users:
            self.users[telegram_id_str]['lang'] = lang
            self.save_data()

    async def get_user(self, telegram_id):
        return self.users.get(str(telegram_id))

    async def get_all_users(self):
        return list(self.users.values())

    async def add_admin(self, admin_id):
        if admin_id not in self.admins:
            self.admins.append(admin_id)
            self.save_data()

    async def get_admins(self):
        return self.admins

    async def get_admin_contact(self, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                return company.get('admin_contact', {"name": "Admin", "phone": "", "username": ""})
        return getattr(self, 'admin_contact', {"name": "Fast Food Admin", "phone": "+998 90 123 45 67", "username": "@admin"})

    async def update_admin_contact(self, name, phone, username, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                company['admin_contact'] = {"name": name, "phone": phone, "username": username}
        else:
            self.admin_contact = {"name": name, "phone": phone, "username": username}
        self.save_data()

    async def get_categories(self, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                return company.get('categories', [])
            return []
        return getattr(self, 'categories', [])

    async def add_category(self, cat, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                if cat not in company.get('categories', []):
                    if 'categories' not in company:
                        company['categories'] = []
                    company['categories'].append(cat)
                    self.save_data()
                    self.export_webapp_products()
        else:
            if cat not in self.categories:
                self.categories.append(cat)
                self.save_data()

    async def remove_category(self, cat, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company and cat in company.get('categories', []):
                company['categories'].remove(cat)
                self.save_data()
                self.export_webapp_products()
        else:
            if cat in self.categories:
                self.categories.remove(cat)
                self.save_data()
                self.export_webapp_products()

    async def get_admin_accounts(self):
        return getattr(self, 'admin_accounts', [])

    async def add_admin_account(self, login, password, name, company_id=None, is_superadmin=False):
        self.admin_accounts.append({
            "login": login,
            "password": password,
            "name": name,
            "is_superadmin": is_superadmin,
            "company_id": company_id
        })
        self.save_data()

    async def remove_admin_account(self, login):
        self.admin_accounts = [a for a in self.admin_accounts if a['login'] != login]
        self.save_data()

    async def set_admin_session(self, user_id, login):
        if not hasattr(self, 'admin_sessions'):
            self.admin_sessions = {}
        self.admin_sessions[str(user_id)] = login
        if user_id not in self.admins:
            self.admins.append(user_id)
        self.save_data()

    async def get_admin_session(self, user_id):
        if not hasattr(self, 'admin_sessions'):
            return "Noma'lum Admin"
        return self.admin_sessions.get(str(user_id), "Asosiy Admin")

    # ========================
    # PRODUCT METHODS (company-aware)
    # ========================
    async def get_products(self, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                return [p for p in company.get('products', []) if p.get('is_active', 1)]
            return []
        return [p for p in self.products if p.get('is_active', 1)]

    async def add_product(self, name, description, price, category="Boshqa", image="", company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if not company:
                return
            products_list = company.setdefault('products', [])
            product_id = 1
            if products_list:
                product_id = max(p['id'] for p in products_list) + 1

            products_list.append({
                "id": product_id,
                "name": name,
                "category": category,
                "description": description,
                "price": price,
                "is_active": 1,
                "emoji": "🍽",
                "image": image if image else "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=500&q=80",
                "company_id": company_id
            })
        else:
            product_id = 1
            if self.products:
                product_id = max(p['id'] for p in self.products) + 1
            self.products.append({
                "id": product_id,
                "name": name,
                "category": category,
                "description": description,
                "price": price,
                "is_active": 1,
                "emoji": "🍽",
                "image": image if image else "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=500&q=80"
            })

        self.save_data()
        self.export_webapp_products()

    async def toggle_product(self, product_id, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                for p in company.get('products', []):
                    if p['id'] == product_id:
                        p['is_active'] = 0 if p.get('is_active', 1) == 1 else 1
                        break
        else:
            for p in self.products:
                if p['id'] == product_id:
                    p['is_active'] = 0 if p.get('is_active', 1) == 1 else 1
                    break
        self.save_data()
        self.export_webapp_products()

    async def edit_product(self, product_id, new_price, new_image, new_desc=None, company_id=None):
        product_list = self.products
        if company_id:
            company = await self.get_company(company_id)
            if company:
                product_list = company.get('products', [])

        for p in product_list:
            if p['id'] == product_id:
                if new_price is not None:
                    p['price'] = new_price
                if new_image:
                    p['image'] = new_image
                if new_desc:
                    p['description'] = new_desc
                break

        self.save_data()
        self.export_webapp_products()

    async def delete_product(self, product_id, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                company['products'] = [p for p in company.get('products', []) if p['id'] != product_id]
        else:
            self.products = [p for p in self.products if p['id'] != product_id]
        self.save_data()
        self.export_webapp_products()

    def get_all_products_for_company(self, company_id):
        """DB sync uchun (non-async)"""
        for c in self.companies:
            if c['id'] == company_id:
                return c.get('products', [])
        return []

    # ========================
    # COURIER METHODS (company-aware)
    # ========================
    async def get_couriers(self, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                return company.get('couriers', [])
            return []
        return getattr(self, 'couriers', [])

    async def add_courier(self, telegram_id, fullname, phone, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if not company:
                return None
            couriers_list = company.setdefault('couriers', [])
            c_id = 1 if not couriers_list else max(c['id'] for c in couriers_list) + 1
            new_courier = {
                "id": c_id,
                "telegram_id": telegram_id,
                "fullname": fullname,
                "phone": phone,
                "company_id": company_id,
                "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            couriers_list.append(new_courier)
        else:
            if not hasattr(self, 'couriers'):
                self.couriers = []
            c_id = 1 if not self.couriers else max(c['id'] for c in self.couriers) + 1
            new_courier = {
                "id": c_id,
                "telegram_id": telegram_id,
                "fullname": fullname,
                "phone": phone,
                "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            self.couriers.append(new_courier)

        self.save_data()
        return new_courier

    async def delete_courier(self, courier_id, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                company['couriers'] = [c for c in company.get('couriers', []) if c['id'] != courier_id]
        else:
            if hasattr(self, 'couriers'):
                self.couriers = [c for c in self.couriers if c['id'] != courier_id]
        self.save_data()

    async def get_courier_company(self, telegram_id):
        """Kuryer qaysi kompaniyaga tegishli ekanini topish"""
        for c in self.companies:
            for courier in c.get('couriers', []):
                if courier['telegram_id'] == telegram_id:
                    return c['id']
        return None

    # ========================
    # ORDER METHODS (company-aware)
    # ========================
    async def create_order(self, user_id, total_price, location, phone, items, order_type="Oddiy", room_table=None, comment="", company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if not company:
                return None
            orders_list = company.setdefault('orders', [])
            order_id = 1
            if orders_list:
                order_id = max(o['id'] for o in orders_list) + 1

            orders_list.append({
                "id": order_id,
                "user_id": user_id,
                "total_price": total_price,
                "location": location,
                "phone": phone,
                "status": "Yangi",
                "items": items,
                "order_type": order_type,
                "room_table": room_table,
                "comment": comment,
                "courier_id": None,
                "company_id": company_id,
                "created_at": datetime.now().strftime('%d.%m.%Y %H:%M')
            })
        else:
            order_id = 1
            if self.orders:
                order_id = max(o['id'] for o in self.orders) + 1

            self.orders.append({
                "id": order_id,
                "user_id": user_id,
                "total_price": total_price,
                "location": location,
                "phone": phone,
                "status": "Yangi",
                "items": items,
                "order_type": order_type,
                "room_table": room_table,
                "comment": comment,
                "courier_id": None,
                "created_at": datetime.now().strftime('%d.%m.%Y %H:%M')
            })

        self.save_data()
        return order_id

    async def get_user_orders(self, user_id, limit=10):
        all_orders = list(self.orders)
        # Kompaniyalardan ham zakazlarni qo'shamiz
        for c in self.companies:
            all_orders.extend(c.get('orders', []))
        user_orders = [o for o in all_orders if o['user_id'] == user_id]
        return list(reversed(user_orders))[:limit]

    async def get_user_stats(self, user_id):
        all_orders = list(self.orders)
        for c in self.companies:
            all_orders.extend(c.get('orders', []))
        user_orders = [o for o in all_orders if o['user_id'] == user_id and o['status'] != "Bekor qilingan"]
        total_spent = sum(o['total_price'] for o in user_orders)
        return {
            "order_count": len(user_orders),
            "total_spent": total_spent
        }

    async def get_dashboard_stats(self, company_id=None):
        today_str = datetime.now().strftime('%d.%m.%Y')
        if company_id:
            company = await self.get_company(company_id)
            orders = company.get('orders', []) if company else []
        else:
            orders = self.orders

        today_orders = [o for o in orders if o.get('created_at', '').startswith(today_str)]
        total_revenue = sum(o.get('total_price', 0) for o in orders if o.get('status') not in ["Bekor qilingan", "Archivlangan"])
        today_revenue = sum(o.get('total_price', 0) for o in today_orders if o.get('status') not in ["Bekor qilingan", "Archivlangan"])

        if company_id:
            company = await self.get_company(company_id)
            products_count = len([p for p in company.get('products', []) if p.get('is_active', 1)]) if company else 0
        else:
            products_count = len([p for p in self.products if p.get('is_active', 1)])

        return {
            "products": products_count,
            "orders": len(orders),
            "users": len(self.users),
            "today_orders": len(today_orders),
            "total_revenue": total_revenue,
            "today_revenue": today_revenue
        }

    async def update_order_status(self, order_id, status, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                for o in company.get('orders', []):
                    if o['id'] == order_id:
                        o['status'] = status
                        break
        else:
            for o in self.orders:
                if o['id'] == order_id:
                    o['status'] = status
                    break
        self.save_data()

    def find_order(self, order_id, company_id=None):
        """Zakazni topish (sync)"""
        if company_id:
            for c in self.companies:
                if c['id'] == company_id:
                    for o in c.get('orders', []):
                        if o['id'] == order_id:
                            return o
            return None
        return next((o for o in self.orders if o['id'] == order_id), None)

    async def reset_revenue(self, company_id=None):
        if company_id:
            company = await self.get_company(company_id)
            if company:
                for o in company.get('orders', []):
                    if o['status'] not in ["Bekor qilingan"]:
                        o['status'] = "Archivlangan"
        else:
            for o in self.orders:
                if o['status'] not in ["Bekor qilingan"]:
                    o['status'] = "Archivlangan"
        self.save_data()
