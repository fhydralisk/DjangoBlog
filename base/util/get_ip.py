"""

"""


def get_client_ip(request):
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        regip = real_ip.split(",")[0]
    except:
        try:
            regip = request.META['REMOTE_ADDR']
        except:
            regip = ""
    return regip


def get_server_ip():
    from django.core.cache import caches
    cached = caches['sessions'].get('server_local_ip')
    if cached:
        return cached
    else:
        import urllib2
        import re

        url = urllib2.urlopen("http://txt.go.sohu.com/ip/soip")
        text = url.read()
        ip = re.findall(r'\d+.\d+.\d+.\d+', text)

        ip = ip[0]
        caches['sessions'].set('server_local_ip', ip, 7200)
        return ip
