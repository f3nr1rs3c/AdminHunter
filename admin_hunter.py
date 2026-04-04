#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Admin Hunter - Professional Admin Panel Finder for Penetration Testers
Author: Sirius (Updated via Antigravity)

Bu tool, hedeflenen web sitelerinde yetkisiz erişim noktalarını (admin panelleri,
giriş sayfaları vs.) tespit etmek amacıyla sızma testlerinde (penetration testing)
kullanılmak üzere tasarlanmıştır.

Özellikleri ve Pentest Notları:
- **Asenkron Yapı (asyncio & aiohttp):** Saniyede yüzlerce istek göndererek tarama
  süresini minimuma indirir. Aktif bilgi toplama aşamasında büyük zaman kazandırır.
- **WAF ve 404 Catch-All Tespiti:** Sunucu olmayan her isteğe "200 OK" dönüyor olabilir (Custom 404).
  Script, önce sahte rastgele bir dizine istek atar; eğer 200 dönerse hedefte "Catch-All" yapısı var demektir.
  Bu durumda, bulunan sayfaların içerik boyutu (content-length) sahte sayfanın boyutu ile karşılaştırılır,
  böylece false-positive (yanlış pozitif) sonuçlar büyük ölçüde filtrelenir.
- **Gizlilik (User-Agent):** IPS/IDS veya log analiz sistemlerini yanıltmak ve basit engel
  mekanizmalarını atlatmak için popüler tarayıcılara ait User-Agent başlıkları rastgele kullanılır.
- **Durum Kodu Analizi (401/403):** Sadece 200 dönenleri değil, aynı zamanda 403 (Forbidden) veya 
  401 (Unauthorized) dönen hassas dizinleri de loglar. Kilitli paneller değerli hedeflerdir.
- **Proxy ve Steath Desteği:** '--proxy' argümanı ile tarama trafiğinizi Burp Suite, ZAP veya Tor 
  üzerinden geçirebilirsiniz. Ayrıca '--threads' argümanı ile eşzamanlı istek (concurrency) sayısı azaltılarak WAF atlatması denenebilir.
"""

import argparse
import asyncio
import os
import random
import string
import sys
import time
from urllib.parse import urlparse, urljoin

try:
    import aiohttp
    from colorama import init, Fore, Style
    from pyfiglet import Figlet
except ImportError as e:
    print(f"[-] Gerekli kütüphaneler eksik. Lütfen yükleyin: pip install aiohttp colorama pyfiglet")
    sys.exit(1)

# Colorama Başlatma (Terminal renklerini aktifleştirir)
init(autoreset=True)

# Penetration testing sırasında sık karşılaşılan standart panelleri,
# yapılandırma hatalarını ve gelişmiş CMS giriş yollarını içeren hedef listesi.
DEFAULT_PATHS = [
    "admin", "adminpanel", "login", "wp-admin", "administrator",
    "admin/login", "admin/login.php", "admin/index.php", "admin/index.html",
    "admin/", "administrator/", "moderator/", "webadmin/", "adminarea/",
    "bb-admin/", "adminLogin/", "admin_area/", "panel-administracion/",
    "instadmin/", "memberadmin/", "administratorlogin/", "adm/",
    "account.asp", "admin/account.asp", "admin/index.asp", "admin/login.asp",
    "admin/admin.asp", "admin_area/admin.asp", "admin_area/login.asp",
    "admin/account.html", "admin/login.html", "admin/admin.html",
    "admin_area/index.html", "admin_area/index.asp", "bb-admin/index.asp",
    "bb-admin/login.asp", "bb-admin/admin.asp", "bb-admin/index.html",
    "bb-admin/login.html", "bb-admin/admin.html", "admin/home.html",
    "admin/controlpanel.html", "admin.html", "admin/cp.html", "cp.html",
    "administrator/index.html", "administrator/login.html",
    "administrator/account.html", "login.html", "modelsearch/login.html",
    "moderator.html", "moderator/login.html", "moderator/admin.html",
    "account.html", "controlpanel.html", "admincontrol.html",
    "admin_login.html", "panel-administracion/login.html", "admin/home.asp",
    "admin/controlpanel.asp", "admin.asp", "pages/admin/admin-login.asp",
    "admin/admin-login.asp", "admin-login.asp", "admin/cp.asp",
    "administrator/account.asp", "administrator.asp", "login.asp",
    "modelsearch/login.asp", "moderator.asp", "moderator/login.asp",
    "administrator/login.asp", "moderator/admin.asp", "controlpanel.asp",
    "adminpanel.html", "webadmin.html", "pages/admin/admin-login.html",
    "admin/admin-login.html", "webadmin/index.html", "webadmin/admin.html",
    "webadmin/login.html", "user.asp", "user.html", "admincp/index.asp",
    "admincp/login.asp", "admincp/index.html", "admin/adminLogin.html",
    "adminLogin.html", "home.html", "adminarea/index.html",
    "adminarea/admin.html", "adminarea/login.html",
    "panel-administracion/index.html", "panel-administracion/admin.html",
    "modelsearch/index.html", "modelsearch/admin.html",
    "admincontrol/login.html", "adm/index.html", "adm.html",
    "admincontrol.asp", "adminpanel.asp", "webadmin.asp",
    "webadmin/index.asp", "webadmin/admin.asp", "webadmin/login.asp",
    "admin/admin_login.asp", "panel-administracion/login.asp",
    "adminLogin.asp", "home.asp", "adminarea/index.asp",
    "adminarea/admin.asp", "adminarea/login.asp", "admin-login.html",
    "panel-administracion/index.asp", "panel-administracion/admin.asp",
    "modelsearch/index.asp", "modelsearch/admin.asp",
    "administrator/index.asp", "admincontrol/login.asp",
    "adm/admloginuser.asp", "admloginuser.asp", "admin2.asp",
    "admin2/login.asp", "admin2/index.asp", "adm/index.asp", "adm.asp",
    "affiliate.asp", "adm_auth.asp", "memberadmin.asp", "siteadmin/login.asp",
    "siteadmin/index.asp", "siteadmin/login.html",
    # Modern Framework / Sık Unutulan / Hassas Yollar
    "cpanel", "manager", "console", "dashboard", "kibana", "phpmyadmin",
    "pma", "dbadmin", "myadmin", "mysql", "sql", "sqlite", "auth",
    "secure", "system", "vnc", "terminal", "ssh", "root", "super",
    "grafana", "zabbix", "nagios", "jenkins", "gitlab", "jira", "confluence",
    "bitbucket", "swagger-ui.html", "api/docs", "api/swagger.json"
]

# Çeşitli User-Agent'lar, WAF (Web Application Firewall) tarafında varsayılan 
# aiohttp bot başlıklarının engellenmesini (block) önler.
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    f = Figlet(font='slant', width=100)
    print(Fore.RED + Style.BRIGHT + f.renderText('Admin Hunter'))
    str_info = "                      | - |  By : Sirius - Penetration Tester | - |         "
    print(Fore.MAGENTA + Style.BRIGHT + str_info + "\n" + Fore.RESET)

def format_url(url):
    """
    Kullanıcının girdiği URL'yi formatlar.
    Pentest aşamasında http/https HTTP servisi standartlarına dökülür.
    """
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    if not url.endswith("/"):
        url += "/"
    return url

async def check_catch_all(session, target_url):
    """
    Hedef sunucunun olmayan sayfalara 404 (Not Found) yerine 200 OK 
    (Catch-All / Custom 404) dönüp dönmediğini kontrol eder.
    Ayrıca dönen sahte sayfanın içeriğinin uzunluğunu ölçerek eşik değer sağlar.
    """
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
    test_url = urljoin(target_url, random_str)
    try:
        async with session.get(test_url) as response:
            content = await response.read()
            content_length = len(content)
            if response.status == 200:
                print(Fore.YELLOW + f"[!] Uyarı: Sunucuda Custom 404 (Catch-all) davranışı tespit edildi!")
                print(Fore.YELLOW + f"[!] Sahte sonuçları engellemek için baz alınacak veri boyutu: {content_length} bytes.\n")
                return True, content_length
            else:
                return False, -1
    except Exception as e:
        print(Fore.RED + f"[-] Hedefle bağlantı kurulamadı: {e}")
        return None, None

async def fetch(session, target_url, path, semaphore, catch_all_length, found_urls, results_file):
    """
    Semafor eşliğinde asenkron HTTP isteğini gerçekleştirir. 
    Concurrency limiti, semaphore ile sınırlandırılmıştır.
    """
    url = urljoin(target_url, path)
    
    # Her istekte dinamik bir User-Agent alınır.
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    async with semaphore:
        try:
            # allow_redirects=True (Pentestte 301/302 ile asıl panele yönlenmeleri takip etmek için)
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                content = await response.read()
                
                # Başarılı sayfa tespiti: 
                # 1. 200 dönmesi,
                # 2. Eğer catch-all varsa sayfa büyüklüğünün ondan kayda değer şekilde farklı olması (tolerans +- 100 byte verilir).
                if response.status == 200:
                    if catch_all_length > 0 and abs(len(content) - catch_all_length) < 100:
                        # Sayfa uzunluğu, custom 404 sayfasıyla hemen hemen aynıysa bu sahte pozitiftir (False-Positive).
                        pass
                    else:
                        msg = f"[+] Bulundu [200 OK]: {url} (Boyut: {len(content)} byte)"
                        print(Fore.GREEN + Style.BRIGHT + msg)
                        found_urls.append(url)
                        if results_file:
                            with open(results_file, 'a', encoding='utf-8') as f:
                                f.write(url + "\n")
                                
                elif response.status in [401, 403]:
                    # 403 Forbidden veya 401 Unauthorized dönen yerler çoğunlukla aradığımız kilitli yönetim dizinleridir.
                    msg = f"[*] Yetki Reddedildi / Hassas Dizin [{response.status}]: {url}"
                    print(Fore.CYAN + msg)
                    found_urls.append(url)
                    if results_file:
                        with open(results_file, 'a', encoding='utf-8') as f:
                            f.write(msg + "\n")
                            
        except asyncio.TimeoutError:
            pass # Zaman aşımı, konsolu kirletmemesi açısından atlanıyor
        except Exception:
            pass # WAF RST bağlantı kopmaları veya geçersiz yanıt vb.

async def main_async(target_url, wordlist, concurrency, timeout, proxy, results_file):
    target_url = format_url(target_url)
    print(Fore.BLUE + f"[*] Hedef URL: {target_url}")
    
    paths = DEFAULT_PATHS
    if wordlist:
        try:
            with open(wordlist, 'r', encoding='utf-8') as f:
                paths = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(Fore.BLUE + f"[*] Özel Wordlist yüklendi ({len(paths)} yol).")
        except FileNotFoundError:
            print(Fore.RED + "[-] Belirtilen wordlist dosyası bulunamadı. Varsayılan liste kullanılacak.")
            print(Fore.BLUE + f"[*] Varsayılan Wordlist ({len(paths)} yol).")
    else:
        print(Fore.BLUE + f"[*] Varsayılan Wordlist yükleniyor ({len(paths)} yol).")
        
    print(Fore.BLUE + f"[*] Concurrency (Eşzamanlı İstek): {concurrency}")
    if proxy:
        print(Fore.BLUE + f"[*] Proxy Kullanılıyor: {proxy}")
        
    print(Fore.MAGENTA + "\n[=========== TARAMA BAŞLIYOR ===========]\n")
    start_time = time.time()
    
    # SSL Sertifika hatalarını yok say
    timeout_obj = aiohttp.ClientTimeout(total=timeout)
    connector = aiohttp.TCPConnector(ssl=False)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout_obj) as session:
        # Önce WAF / Catch-All analizi (False Positive Engelleme)
        has_catch_all, catch_all_length = await check_catch_all(session, target_url)
        if has_catch_all is None:
            return

        semaphore = asyncio.Semaphore(concurrency)
        tasks = []
        found_urls = []
        
        # Sonuç dosyasını başlat
        if results_file:
            with open(results_file, 'w', encoding='utf-8') as f:
                f.write(f"Admin Hunter Scan Results - {target_url}\n")
                f.write("=" * 50 + "\n")

        # İş parçacıklarını planlama
        for path in paths:
            task = asyncio.create_task(
                fetch(session, target_url, path, semaphore, catch_all_length if has_catch_all else -1, found_urls, results_file)
            )
            tasks.append(task)
            
        await asyncio.gather(*tasks)
        
    end_time = time.time()
    print(Fore.MAGENTA + "\n[=========== TARAMA TAMAMLANDI ===========]")
    print(Fore.BLUE + f"[*] Toplam Süre: {end_time - start_time:.2f} saniye")
    print(Fore.BLUE + f"[*] Bulunan Giriş/Dizin Sayısı: {len(found_urls)}")
    
    if results_file and len(found_urls) > 0:
        print(Fore.GREEN + f"[+] Sonuçlar başarıyla kaydedildi: {results_file}")

def print_help_and_exit(parser):
    """Parametresiz çalıştırılmada interaktif kullanım alternatifi"""
    parser.print_help(sys.stderr)
    print("\n" + Fore.YELLOW + "[!] Argüman kullanılmadı, İnteraktif Moda geçiliyor..." + Fore.RESET)
    try:
        target = input(Fore.BLUE + "Hedef URL'yi girin (örneğin, example.com): " + Fore.RESET).strip()
        if not target:
            sys.exit(0)
        asyncio.run(main_async(target, None, 30, 10, None, None))
    except KeyboardInterrupt:
        pass
    sys.exit(0)


def format_args_proxy(proxy_arg):
    if proxy_arg:
        # aiohttp genelde os.environ proxy değişkenlerini alıp işleyebilir 
        os.environ['HTTP_PROXY'] = proxy_arg
        os.environ['HTTPS_PROXY'] = proxy_arg

def main():
    clear_screen()
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="Gelişmiş Asenkron Admin Panel Tespit Aracı - Pentester Sürümü",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Pentest Önerileri:
-------------------
• Hedefte WAF / Rate-Limit engeli varsa: -t (threads) değerini 5-10 seviyesine düşürün.
• Yerel ağ taramalarında veya BurpSuite proxyi üzerinden geçmek için: --proxy http://127.0.0.1:8080 kullanın.
• Kendi özel dictionary/wordlist'iniz varsa -w ile araca dahil edin.
        
Örnek Kullanım:
  python admin_hunter.py -u http://example.com
  python admin_hunter.py -u http://example.com -w my_wordlist.txt -t 50
  python admin_hunter.py -u http://example.com --proxy http://127.0.0.1:8080 -o sonuc.txt
"""
    )
    
    # Parametreleri tanımla
    parser.add_argument("-u", "--url", help="Hedef URL (örn: http://example.com)")
    parser.add_argument("-w", "--wordlist", help="Özel bir path listesi / wordlist dosyası yolu")
    parser.add_argument("-t", "--threads", type=int, default=30, help="Eşzamanlı maksimum bağlantı sayısı (Varsayılan: 30)")
    parser.add_argument("-o", "--output", help="Bulunan hedeflerin kaydedileceği dosya yolu")
    parser.add_argument("-p", "--proxy", help="İstekleri proxy üzerinden geçir (örn: http://127.0.0.1:8080)")
    parser.add_argument("--timeout", type=int, default=10, help="Zaman aşımı (saniye) (Varsayılan: 10)")

    if len(sys.argv) == 1:
        print_help_and_exit(parser)

    args = parser.parse_args()
    
    if not args.url:
        print(Fore.RED + "[-] Lütfen bir hedef URL belirtin (-u veya --url)")
        sys.exit(1)

    format_args_proxy(args.proxy)

    try:
        # Windows ortamlarında asyncio için event loop ayarı
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
        asyncio.run(main_async(args.url, args.wordlist, args.threads, args.timeout, args.proxy, args.output))
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Tarama kullanıcı tarafından iptal edildi.")
        sys.exit(0)

if __name__ == "__main__":
    main()
