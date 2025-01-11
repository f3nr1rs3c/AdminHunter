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
        "admin/index.html"
    ]

    target_url = input(Fore.BLUE + "Hedef URL'yi girin (örneğin, example.com): " + Fore.RESET).strip()
    target_url = validate_url(target_url)

    find_admin_panels(target_url, admin_paths)

if __name__ == "__main__":
    main()
