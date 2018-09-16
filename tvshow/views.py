from django.shortcuts import render,get_object_or_404,redirect
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import show,movie
import string
import time,re,json,requests
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.chrome.options import Options
except:
    pass

def clean(findx):
    print("cleaning input")
    findx= re.sub(r's\d','',findx)
    findx= re.sub(r's \d','',findx)
    findx= re.sub(r'season\d','',findx)
    findx= re.sub(r'season \d','',findx)
    if findx[-1] == " ":
        findx= findx[:-1]
    return findx


def getrating(findx):
    print("getting rating")
    a=[]
    try:
        findx=clean(findx)

        chromedriver= CHROMEDRIVER_PATH //'D:\\webdrivers\\chromedriver'
        options = Options()
        options.binary_location = GOOGLE_CHROME_BIN
        options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
        prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 4096}
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(chromedriver,chrome_options=options)

        browser.get('https://www.imdb.com/')
        search=browser.find_element_by_name("q")
        search.clear()
        search.send_keys(findx)
        search.submit()
        time.sleep(2)
        showtype=browser.find_element_by_xpath("""//*[@id="quicksearch"]/option[2]""").click()
        time.sleep(2)
        cur=browser.find_element_by_xpath("""//*[@id="main"]/div/div[2]/table/tbody/tr[1]/td[2]/a""").click()
        ratingline=browser.find_element_by_xpath("""//*[@id="title-overview-widget"]/div[2]/div[2]/div/div[1]/div[1]/div[1]/strong""")
        ratingVal=browser.find_element_by_xpath("""//*[@id="title-overview-widget"]/div[2]/div[2]/div/div[1]/div[1]/div[1]/strong/span""")
        a.append(ratingline.get_attribute('title'))
        a.append(ratingVal.text)
        browser.quit()
        return a
    except:
        a.append("No data available")
        a.append("0")
        return a

# Create your views here.


def index(request):
    print("tv index called")
    return render(request,'index.html')

def movie_index(request):
    print("movie index called")
    return render(request,'movie_index.html')


def checknpass(request):
    print("check and pass")
    if (request.method == 'POST'):
        val= request.POST['val']
        val=clean(val)
        print("checkpass first cleaning"+val)
        try:
            x= show.objects.filter(name=val).first()
            content= {
                'links' : x.links.split(','),
                'val'   : string.capwords(val),
                'rating' : x.ratingdetails.split('#')
            }
            return render(request,'details.html',content)
        except:
            return(tv(request))   
    else:
        return render(request,'index.html')

def movie_checknpass(request):
    print("movie check and pass")
    if (request.method == 'POST'):
        val= request.POST['val']
        val=clean(val)
        print("checkpass first cleaning"+val)
        try:
            x= movie.objects.filter(name=val).first()
            content= {
                'links' : x.links.split(','),
                'val'   : string.capwords(val),
                'rating' : x.ratingdetails.split('#')
            }
            return render(request,'details.html',content)
        except:
            return(mo(request))   
    else:
        return render(request,'movie_index.html')



def tv(request):
    print("in tv")
    if(request.method == 'POST'):
        try:
            findx=request.POST['val']
            findx= clean(findx)
            find='index of series ' + findx
            cleanfindx= findx.replace(' ','').replace('.','') # search with no spaces and dots
            result=set()
            try:
                chromedriver= CHROMEDRIVER_PATH //'D:\\webdrivers\\chromedriver'
                options = Options()
                options.binary_location = GOOGLE_CHROME_BIN
                options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
                prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 4096}
                options.add_experimental_option("prefs", prefs)
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                browser = webdriver.Chrome(chromedriver,chrome_options=options)
                print("browser in tv open")
            except:
                print("browser error")
            browser.get('https://www.google.com')
            search=browser.find_element_by_name("q")
            search.clear()
            search.send_keys(find)
            search.submit()
            time.sleep(1)
            l=browser.find_elements_by_xpath("""//*[@id="rso"]/div/div/div/div/div/h3/a""")
            for item in l:
                link=item.get_attribute('href')
                link=link.replace('%20',' ')
                orglink=link
                #print("original link =" +link)
                cleanlink=link.replace(' ','').replace('.','') #link with no spaces and dots
                if link[-1] !="/":
                    #link=link[:-1]
                    link=link+"/"
                text=item.get_attribute('text')
                ntext= '_' + text
                if re.search(r'Index of',ntext,re.M|re.I):
                    if re.search(cleanfindx,cleanlink,re.M|re.I):
                        try:
                            index= re.search( findx, link, re.M|re.I).start()
                            link=link[: index+link[index:].find('/')]
                            #print("link value now"+link+"\n")
                        except:
                            link=link[:link.rfind('/')]
                            link=link[:link.rfind('/')]
                            #print("link value now= "+link+"\n")
                        if link.endswith(('series','series/','Series','Series/','Serial','Serial/')):
                            link=orglink
                        result.add(link)
            #print('\n'.join(set(result)))
            browser.quit()
            #content={}
            print("till here")
            try:
                ratingval=getrating(findx)   #getting array
            except:
                print("error getting rating")
            if result:
                try:
                    cddc=','.join(map(str, result)) 
                    dcdcd= '#'.join(map(str, ratingval)) 
                    x=show(name=findx,links=cddc,ratingdetails=dcdcd)
                    x.save()
                except:
                    pass
            else:
                result.add("No links available Try later")
            content= {
                'links': result,
                'val' : string.capwords(findx),
                'rating' : ratingval
            }
            return render(request,'details.html',content)
        except:
            return render(request,'index.html')
    else:
        return render(request,'index.html')



def mo(request):
    print("in mo")
    if(request.method == 'POST'):
        try:
            findx=request.POST['val']
            findx= clean(findx)
            find='index of movies ' + findx
            cleanfindx= findx.replace(' ','').replace('.','') # search with no spaces and dots
            result=set()
            try:
                chromedriver= CHROMEDRIVER_PATH //'D:\\webdrivers\\chromedriver'
                options = Options()
                options.binary_location = GOOGLE_CHROME_BIN
                options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
                prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 4096}
                options.add_experimental_option("prefs", prefs)
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                browser = webdriver.Chrome(chromedriver,chrome_options=options)
                print("browser in tv open")
            except:
                print("browser error")
            browser.get('https://www.google.com')
            search=browser.find_element_by_name("q")
            search.clear()
            search.send_keys(find)
            search.submit()
            time.sleep(1)
            l=browser.find_elements_by_xpath("""//*[@id="rso"]/div/div/div/div/div/h3/a""")
            for item in l:
                link=item.get_attribute('href')
                link=link.replace('%20',' ')
                orglink=link
                #print("original link =" +link)
                cleanlink=link.replace(' ','').replace('.','') #link with no spaces and dots
                if link[-1] !="/":
                    #link=link[:-1]
                    link=link+"/"
                text=item.get_attribute('text')
                ntext= '_' + text
                if re.search(r'Index of',ntext,re.M|re.I):
                    if re.search(cleanfindx,cleanlink,re.M|re.I):
                        try:
                            index= re.search( findx, link, re.M|re.I).start()
                            link=link[: index+link[index:].find('/')]
                            #print("link value now"+link+"\n")
                        except:
                            link=link[:link.rfind('/')]
                            link=link[:link.rfind('/')]
                            #print("link value now= "+link+"\n")
                        if link.endswith(('series','series/','Series','Series/','Serial','Serial/')):
                            link=orglink
                        result.add(link)
            #print('\n'.join(set(result)))
            browser.quit()
            #content={}
            print("till here")
            try:
                ratingval=getrating(findx)   #getting array
            except:
                print("error getting rating")
            if result:
                try:
                    cddc=','.join(map(str, result)) 
                    dcdcd= '#'.join(map(str, ratingval)) 
                    x=movie(name=findx,links=cddc,ratingdetails=dcdcd)
                    x.save()
                except:
                    pass
            else:
                result.add("No links available Try later")
            content= {
                'links': result,
                'val' : string.capwords(findx),
                'rating' : ratingval
            }
            return render(request,'details.html',content)
        except:
            return render(request,'movie_index.html')
    else:
        return render(request,'movie_index.html')
