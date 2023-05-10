# <span style="color:#f9b000">Tutorial</span>


## Prerequisites
* [Docker & Docker Compose](https://docs.docker.com/desktop/) (<span style="color:orange">Local Development with Docker</span> only)


***
***

## Repository
Clone or pull from the dev branch before you begin coding.
```
#cloning
git clone git@github.com:Sapphirine/202305-16_DJANGO_CHATGPT_ECOMMERCE.git .

```

***
***



## Environment variable and secrets
1. Create a .env file from .env.template
    ```
    #Unix and MacOS
    cd backend && cp .env.template .env

    #windows
    cd sandbox && copy .env.template .env
    ```

2. Add your ChatGPT api key tha can be found [here](https://platform.openai.com/account/api-keys)

***
***

## Fire up Docker:

>Note: You will need to make sure Docker is running on your machine!

Use the following command to build the docker images:
```
docker-compose  up -d --build
```

Alternatively, If you have [make](https://platform.openai.com/account/api-keys) installed, you can run the following command:
```
make build
```


### Finished
You should now be up and running!

* The web app is running on  http://localhost:8000


For running data scraping
### Install Selenium Webdriver 
The instructions to install Selenium Webdriver can found here https://www.selenium.dev/documentation/webdriver/getting_started/
The version of chrome webdriver and google chrome needs to be the same. 

For set up connection with OpenAI
### OpenAPI key
The OpenAI API key needs to be updated in .env in order to connect with OpenAI


***
***

### References
This project is based on the official ChatGPT quick-start tutorial that can be found [here](https://platform.openai.com/docs/quickstart/build-your-application)

