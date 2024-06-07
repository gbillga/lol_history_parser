# LOL History

Lol history is a simple tool designed to allow anyone to fetch their past League of Legends games statistics.  

### Getting started
We highly encourage to use python virtual environments when working on new projects.  
Here can be found more info on how to setup venv : https://docs.python.org/3/library/venv.html  
  
  
In order to run the project, project requirements should be installed :  
`pip install -r requirements.txt`  
  
A .env should be created to be able to fetch any data from Riot Games API:  
`echo 'API_KEY="RGAPI-XXXXXXXXXX"' >> .env`

Data can be either refetched from Riot Games API, or can be dvc pulled using `dvc pull` before running the main.py file.  
On first usage, the command will open a Google authentification page to allow data retrieval from Google Drive.

In order to refresh played matches for all users, `AUTO_REFRESH_USER=1` has to be added to .env file