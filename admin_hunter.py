import requests
import os
from pyfiglet import Figlet
from colorama import init, Fore

# Colorama'yi başlatma
init()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    f = Figlet(font='slant', width=100)
    print(Fore.RED + f.renderText('Admin Hunter'))
    print(Fore.MAGENTA + "                      | - |  By : F3NR1R - Cyber Security | - |         \n" + Fore.RESET)

def validate_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    if not url.endswith("/"):
        url += "/"
    return url

def find_admin_panels(target_url, paths):
    print(Fore.CYAN + "[+] Tarama başlatıldı..." + Fore.RESET)
    for path in paths:
        url = target_url + path
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(Fore.GREEN + f"[+] Admin panel bulundu: {url}" + Fore.RESET)
            else:
                print(Fore.YELLOW + f"[-] Admin panel bulunamadı: {url} (Durum Kodu: {response.status_code})" + Fore.RESET)
        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"[!] İstek gönderilirken hata oluştu: {e}" + Fore.RESET)

def main():
    clear_screen()
    print_banner()

    # Kontrol edilecek admin panel yolları
    admin_paths = [
    "admin",
    "adminpanel",
    "login",
    "wp-admin",
    "administrator",
    "admin/login",
    "admin/login.php",
    "admin/index.php",
    "admin/index.html",
    "admin/",
    "administrator/",
    "moderator/",
    "webadmin/",
    "adminarea/",
    "bb-admin/",
    "adminLogin/",
    "admin_area/",
    "panel-administracion/",
    "instadmin/",
    "memberadmin/",
    "administratorlogin/",
    "adm/",
    "account.asp",
    "admin/account.asp",
    "admin/index.asp",
    "admin/login.asp",
    "admin/admin.asp",
    "admin_area/admin.asp",
    "admin_area/login.asp",
    "admin/account.html",
    "admin/login.html",
    "admin/admin.html",
    "admin_area/index.html",
    "admin_area/index.asp",
    "bb-admin/index.asp",
    "bb-admin/login.asp",
    "bb-admin/admin.asp",
    "bb-admin/index.html",
    "bb-admin/login.html",
    "bb-admin/admin.html",
    "admin/home.html",
    "admin/controlpanel.html",
    "admin.html",
    "admin/cp.html",
    "cp.html",
    "administrator/index.html",
    "administrator/login.html",
    "administrator/account.html",
    "login.html",
    "modelsearch/login.html",
    "moderator.html",
    "moderator/login.html",
    "moderator/admin.html",
    "account.html",
    "controlpanel.html",
    "admincontrol.html",
    "admin_login.html",
    "panel-administracion/login.html",
    "admin/home.asp",
    "admin/controlpanel.asp",
    "admin.asp",
    "pages/admin/admin-login.asp",
    "admin/admin-login.asp",
    "admin-login.asp",
    "admin/cp.asp",
    "administrator/account.asp",
    "administrator.asp",
    "login.asp",
    "modelsearch/login.asp",
    "moderator.asp",
    "moderator/login.asp",
    "administrator/login.asp",
    "moderator/admin.asp",
    "controlpanel.asp",
    "adminpanel.html",
    "webadmin.html",
    "pages/admin/admin-login.html",
    "admin/admin-login.html",
    "webadmin/index.html",
    "webadmin/admin.html",
    "webadmin/login.html",
    "user.asp",
    "user.html",
    "admincp/index.asp",
    "admincp/login.asp",
    "admincp/index.html",
    "admin/adminLogin.html",
    "adminLogin.html",
    "home.html",
    "adminarea/index.html",
    "adminarea/admin.html",
    "adminarea/login.html",
    "panel-administracion/index.html",
    "panel-administracion/admin.html",
    "modelsearch/index.html",
    "modelsearch/admin.html",
    "admincontrol/login.html",
    "adm/index.html",
    "adm.html",
    "admincontrol.asp",
    "adminpanel.asp",
    "webadmin.asp",
    "webadmin/index.asp",
    "webadmin/admin.asp",
    "webadmin/login.asp",
    "admin/admin_login.asp",
    "panel-administracion/login.asp",
    "adminLogin.asp",
    "home.asp",
    "adminarea/index.asp",
    "adminarea/admin.asp",
    "adminarea/login.asp",
    "admin-login.html",
    "panel-administracion/index.asp",
    "panel-administracion/admin.asp",
    "modelsearch/index.asp",
    "modelsearch/admin.asp",
    "administrator/index.asp",
    "admincontrol/login.asp",
    "adm/admloginuser.asp",
    "admloginuser.asp",
    "admin2.asp",
    "admin2/login.asp",
    "admin2/index.asp",
    "adm/index.asp",
    "adm.asp",
    "affiliate.asp",
    "adm_auth.asp",
    "memberadmin.asp",
    "siteadmin/login.asp",
    "siteadmin/index.asp",
    "siteadmin/login.html"
]


    target_url = input(Fore.BLUE + "Hedef URL'yi girin (örneğin, example.com): " + Fore.RESET).strip()
    target_url = validate_url(target_url)

    find_admin_panels(target_url, admin_paths)

if __name__ == "__main__":
    main()
