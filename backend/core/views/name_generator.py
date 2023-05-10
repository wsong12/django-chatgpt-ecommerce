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
from core.forms import InputFormName

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


class NameGenerator(generic.FormView):
    """
    FormView used for our home page.

    **Template:**

    :template:`index.html`
    """
    template_name = "generate_name.html"
    form_class = InputFormName
    success_url = "name_generator/"
    def scraping_data(self,search):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        #chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        #chrome_driver_binary = "/usr/local/bin/chromedriver"
        #driver = webdriver.Chrome(chrome_driver_binary, options=chrome_options)
        driver = webdriver.Chrome(options=chrome_options)

        page = 1
        all_items = []

        while page<2:
            print("getting page", page)
            results = self.get_items(driver,search, page)
            all_items += results

            if len(results) == 0:
                break

            page += 1
            driver.close()
            driver = webdriver.Chrome(options=chrome_options)
        return all_items
    
    def get_items(self,driver,search, page):
        search = search.replace(" ", "_")
        url = "https://www.aliexpress.com/af/{}.html?SearchText=dress&catId=0&g=y&initiative_id=SB_20230412113716&spm=a2g0o.productlist.1000002.0&sortType=total_tranpro_desc&page={}".format(
            search, page
        )
        #print("url",url)
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
                name = driver.find_element(By.CLASS_NAME,"product-title-text").text
            except:
                name = None


            output_item = {"name": name}
            if all(output_item.values()):
                output.append(output_item)

        return output

    def generate_prompt(self, scraped_data,input):
        return f'Return a list of the product names for the below description'+input+' below? \
        Please make it the similar format as the below product names'+str(scraped_data)

     


    @method_decorator(ajax_required)
    def post(self, request,*args, **kwargs):
        data = {'result': 'Error', 'message': "Something went wrong, please try again", "redirect": False, "data":None,"word_count":None}
        #word_count={'result': 'Error', 'message': "Something went wrong, please try again", "redirect": False, "data":None}
        form = InputFormName(request.POST)
        if form.is_valid():

            input = form.cleaned_data.get("input")
            #Scrape data from aliexpress
            scraped_data=self.scraping_data(input)

            #scraped_data=open(os.path.join(settings.BASE_DIR, 'static', "product.json")).read()
            #scraped_data = json.loads(scraped_data)
            
            scraped_data=[i["name"] for i in scraped_data][0:10]

         

            # Send request to openai
            response = openai.Completion.create(
                engine='text-davinci-003',
                prompt=self.generate_prompt(scraped_data,input),
                max_tokens=2048,
                temperature=0.4,
            )
            response_text=response.choices[0].text
            data.update({
                'result': "Success",
                'message': "ChatGPT has suggested some names",
                'data':response.choices[0].text
            })


            return JsonResponse(data)
    

        else:
            data["message"] = FormErrors(form)
            return JsonResponse(data, status=400)
