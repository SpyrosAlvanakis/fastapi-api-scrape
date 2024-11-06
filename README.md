# rada_tritis_tualetas
This repository contains code which:
1) Creates a database in postgresql
2) Uses 2 api calls methods to collect data and stores them automaticly in the database (1 api for the stock values of Nvidia, apple and amd/ 1 api for random news sites relative with nvidia news from finnhub). The data are collected for a given date range
3) Uses 2 scrape methods to collect data and stores them automaticly in the database (1 scraping of the nvidia original site/ 1 scraping of the yahoo financial times articles which contains the "nvidia" word). The data are collected for a given date range
--> after 2,3  we have 6 tables in the database, 3 with the amd, apple and nvidia stock values and 3 with the different articles sources
4) Analyses the data using linear regression and attempts to predict nvidia stock values 
5) Analyses the data and results correlations between the sentiment scores of the different sources (of scraping and api) with one day sift
6) Creates plots to compare the amd, nvidia and apple stock values for the selected date range
7) Creates a 3-axis plot with the nvidia stock value,the dates and the sentiment analysis of the 3 different sources articles

To do that in an interactive environment Fastapi labrary is used and everything runs through gui.
It is important to setup the postgres credentials at the utils/helpers.py function in order to python be able to connect to the local database. 
Also set up the necessery environment by typing to the terminal :
python3.12 -m venv venv
pip install -r requests.txt
source venv/bin/activate

And to get to the fastapi gui type to the terminal:
uvicorn main:app --reload
 
and then navigate to the http://127.0.0.1:8000/docs of the activated browser window. 


!!!WARNING!!! In most of the scripts database modifivations have to be made, change username for example. 


In order to run the application you have to first activate FastAPI server by running (terminal):

uvicorn main:app --reload

As soon as the server is activated in a different terminal you can run the post requests to mine data from the FT scaper and Yahoo API. Run in a new terminal: 

python3 api_post_client.py 

You will be asked to enter the time period for which you want to aquire data,  start and end date, then the api_post_client.py file will make a post request, spesifically it will call the ascosiated 
"post" function in the main.py file which is charged to run the .py files that will conduct the data mining. 