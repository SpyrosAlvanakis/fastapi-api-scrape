# fastapi-api-scrape
This repository contains code which after creating a database in postgres:
1) Uses 2 api calls methods to collect data and stores them automaticly in the database (1 api for the stock values of Nvidia, apple and amd/ 1 api for random news sites relative with nvidia news from finnhub). The data are collected for a given date range
2) Uses 2 scrape methods to collect data and stores them automaticly in the database (1 scraping of the nvidia original site/ 1 scraping of the yahoo financial times articles which contains the "nvidia" word). The data are collected for a given date range
--> after 1,2  we have 6 tables in the database, 3 with the amd, apple and nvidia stock values and 3 with the different articles sources
3) Analyses the data using linear regression and attempts to predict nvidia stock values 
4) Analyses the data and results correlations between the sentiment scores of the different sources (of scraping and api) with one day sift
5) Creates plots to compare the amd, nvidia and apple stock values for the selected date range
6) Creates a 3-axis plot with the nvidia stock value,the dates and the sentiment analysis of the 3 different sources articles

To do that in an interactive environment Fastapi labrary is used and everything runs through gui.
It is important to setup the postgres credentials at the utils/helpers.py function in order to python be able to connect to the local database. 
Also set up the necessery environment by typing to the terminal:
python3.11 -m venv .fastapi_env
pip install -r requests.txt
source .fastapi_env/bin/activate

To run the fastapi application gui, type to the terminal:
uvicorn main:app --reload
 
and then navigate to the http://127.0.0.1:8000/docs of the activated browser window. 


!!!WARNING!!! 
In order for the 

