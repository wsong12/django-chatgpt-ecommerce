# --------------------------------------------------------------
# Django imports
# --------------------------------------------------------------
from django.views import generic
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
# --------------------------------------------------------------
# App imports
# --------------------------------------------------------------
from core.forms import InputForm

# --------------------------------------------------------------
# Project imports
# --------------------------------------------------------------
from utils.decorators import ajax_required
from utils.mixins import FormErrors

# --------------------------------------------------------------
# 3rd Party imports
# --------------------------------------------------------------
import openai
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import wget
from lxml import html
from selenium.webdriver.common.by import By
import re
from django.contrib.staticfiles.storage import staticfiles_storage
openai.api_key = settings.OPENAI_API_KEY
import os
from django.conf import settings
from webdriver_manager.chrome import ChromeDriverManager

class HomeView(generic.FormView):
    """
    FormView used for our home page.

    **Template:**

    :template:`index.html`
    """
    template_name = "generate_analysis.html"
    form_class = InputForm
    success_url = "/"
    def scraping_data(self,search):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        #chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        #chrome_driver_binary = "/usr/local/bin/chromedriver"
        #chrome_driver_binary = "/desktop/chromedriver"
        #driver = webdriver.Chrome(executable_path=r'/Desktop/chromedriver',options=chrome_options)

        driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
        # scrape data using webdriver
        page = 1
        all_items = []
        # The number of pages 
        page_num=5
        while page<page_num:
            print("getting page", page)
            #save each product info into a list
            results = self.get_items(driver,search, page)
            all_items += results

            if len(results) == 0:
                break

            page += 1
            driver.close()
            driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

        print("scraped",len(all_items))
        return all_items
    
    def get_items(self,driver,search, page):
        search = search.replace(" ", "_")
        url = "https://www.aliexpress.com/af/{}.html?SearchText=dress&catId=0&g=y&initiative_id=SB_20230412113716&spm=a2g0o.productlist.1000002.0&sortType=total_tranpro_desc&page={}".format(
            search, page
        )
        driver.get(url)
        time.sleep(1)
        
        # sleep for a second then scroll to the bottom of the page

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
      
        items = driver.find_elements(By.CSS_SELECTOR, ".manhattan--container--1lP57Ag")
        output = []
        urls=[i.get_attribute('href') for i in items]
        #print("links",links)
        for url in urls:
            driver.get(url)
            try:
                price = driver.find_element(By.CLASS_NAME,"product-price-value").text
            except:
                price = None

            try:
                name = driver.find_element(By.CLASS_NAME,"product-title-text").text
            except:
                name = None

            try:
                rating=driver.find_element(By.CLASS_NAME,"overview-rating-average").text
            except:
                rating = None

            try:
                qty_sold=driver.find_element(By.CLASS_NAME,"product-reviewer-sold").text

            except:
                qty_sold=None

            try:
                num_reviews=driver.find_element(By.CLASS_NAME,"product-reviewer-reviews").text
            except:
                num_reviews=None

            output_item = {"name": name, "price": price,"rating":rating,"qty_sold":qty_sold, "num_reviews":num_reviews}
            if all(output_item.values()):
                output.append(output_item)

        return output

    def generate_prompt(self, scraped_data,context,question,input):

        if question=="order":

            return f'Can you analyze the keywords or patterns in the name for the top sales product data for '+input+' below? \
            Such as what types of products are in trend now?'+str(context)

        elif question=="order_pre":
            return f'Please return the top 10 keywords that appeared in the name and\
             their aggregated counts for the second item below and add the numbers up to the first one. \
             The first item is:'+context+'The second item is:'+str(scraped_data)
        elif question=="price_pre":
                    return f'Please return the price range into 5 ranges and\
                     its correspoding aggregated qty_sold based on the two items below \
                     The first item is:'+context+'The second item is:'+str(scraped_data)
        else:
            return f'Can you analyze the patterns between the price and qty_sold for' +input+' for the top sales products'+str(context)\
            +' and what advice will you give the business owner when they set the prices'



    def send_request_openai(self, scraped_data,question,input):
        #make it small batches
        max_elements=15
        num_of_batches=int(len(scraped_data)/max_elements)
        context=''
        if question=='order':
            scraped_data=[{i['name'],i['qty_sold']} for i in scraped_data]      

        for i in range(num_of_batches):
            small_batch=scraped_data[max_elements*i:max_elements*i+max_elements]
         
            response = openai.Completion.create(
                engine='text-davinci-003',
                prompt=self.generate_prompt(small_batch,context, question+"_pre",input),
                max_tokens=2048,
                temperature=0.4,
            )
            context=response.choices[0].text
            print("context is", context)
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=self.generate_prompt("",context,question,input),
            max_tokens=2048,
            temperature=0.4,
        )
        print("response is", response.choices[0].text)
        return response.choices[0].text
    def generate_word_count(self, scraped_data,keyword):

        word_count={}
        word_order={}
        for i in scraped_data:

            words= i['name'].split()

            for word in words:
                if word.lower()!=keyword.lower() and word.lower()!=keyword.lower()+'s' and word.lower()!=keyword.lower()+'es':
                    if word in word_count:
                        word_count[word] += 1
                        word_order[word]+= int(re.sub('\D', '', i['qty_sold']))
                    else:
                        word_count[word] = 1
                        word_order[word]= int(re.sub('\D', '', i['qty_sold']))
        sorted_dict=dict(sorted(word_count.items(), key=lambda x: x[1], reverse=True))
        top_10= dict(list(sorted_dict.items())[0: 10])
        result=[]
        avg_count=sum(top_10.values())/len(top_10)
        for key, value in top_10.items():
            result.append({"word":key,"count":value,"normalized_count":(value/avg_count)*5,"order_count":word_order[key]})
        return result

    def generate_price_range_sales(self, scraped_data):
        #divide the scraped data into several price ranges and their corresponding order counts
  
        result={}
        prices=[]
        for i in scraped_data:
            p=float(i['price'].split("$",1)[1])
            prices.append(p)

        first_price=min(prices)+(max(prices)-min(prices))/5

        second_price=min(prices)+(max(prices)-min(prices))*2/5
        third_price=min(prices)+(max(prices)-min(prices))*3/5
        fourth_price=min(prices)+(max(prices)-min(prices))*4/5
        fifth_price=min(prices)+(max(prices)-min(prices))*5/5
        result[first_price]=0
        result[second_price]=0
        result[third_price]=0
        result[fourth_price]=0
        result[fifth_price]=0
        for i in scraped_data:
            p=float(i['price'].split("$",1)[1])
            qty=int(re.sub('\D', '', i['qty_sold']))
            if p <first_price:
                result[first_price]+=qty
            elif p <second_price:
                result[second_price]+=qty
            elif p <third_price:
                result[third_price]+=qty
            elif p <fourth_price:
                result[fourth_price]+=qty
            else:
                result[fifth_price]+=qty
        f=[]
        for key, value in result.items():
            f.append({"x":key,"y":value})        
        return f



    @method_decorator(ajax_required)
    def post(self, request,*args, **kwargs):
        data = {'result': 'Error', 'message': "Something went wrong, please try again", "redirect": False, "data":None,"word_count":None}
        #word_count={'result': 'Error', 'message': "Something went wrong, please try again", "redirect": False, "data":None}
        form = InputForm(request.POST)
        if form.is_valid():

            input = form.cleaned_data.get("input")
            #scrape data from aliexpress
            scraped_data=self.scraping_data(input)
           
            #scraped_data=open(os.path.join(settings.BASE_DIR, 'static', "product.json")).read()
            #scraped_data = json.loads(scraped_data)
            

            # Send request to chatgpt and get response
            chatgpt_response_1=self.send_request_openai(scraped_data,"order", input)
            chatgpt_response_2=self.send_request_openai(scraped_data,"price", input)
            word_count=self.generate_word_count(scraped_data,input)
            price_range_sales=self.generate_price_range_sales(scraped_data)


            response = openai.Completion.create(
                engine='text-davinci-003',
                prompt=self.generate_prompt("",price_range_sales,"price",input),
                max_tokens=2048,
                temperature=0.4,
            )

            # Update data 
            data.update({
                'result': "Success",
                'message': "ChatGPT has suggested some names",
                #'data': list(filter(None,response.choices[0].text.splitlines( )))
                'word_count': str(word_count),
                'price_range_sales':str(self.generate_price_range_sales(scraped_data)),
                'word_order_count':str([{'label':i['word'], 'y':i['order_count']} for i in word_count]),
                'chatgpt_response_1':chatgpt_response_1,
                'chatgpt_response_2':response.choices[0].text
               
            })


            #send the data back to js
            return JsonResponse(data)


        else:
            data["message"] = FormErrors(form)
            return JsonResponse(data, status=400)
