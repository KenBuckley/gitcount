This program, asygitcount.py connects to the github REST API (version 3) and queries the API.  
There are two queries provided by this web service.  
1) show the remaining API calls allowed from this program (typically you can make 5000 requests to the API per hour).  
2) show the top github users at a given location (the users are selected based on they number of repos they own) and the idea
   of top relates to the users who have the greatest number of PullRequestEvents that have been "closed" and "merged" in the last period.


The following setup is prepared for Ubuntu 16.04 LTS

```
sudo apt-get update -qq && apt-get install -y python3 python3-setuptools python3-pip
sudo easy_install3 pip
```

```
sudo pip3 install -r requirements.txt
```

Important!!!  
In your environment you need to have set up the environment variables 
 GITHUB_CLIENT_ID   
 GITHUB_CLIENT_SECRET    

You need to get these keys from the autor - or alternatively you may insert your own client_id and Client_secret -however in this case please change the  
'User-Agent': 'KenBuckley-App-TotalUsersPerLocation' to your App's name.   
Your own client_id and
secret can be generated in https://github.com/settings/developers -click on OAuth Apps and click the button 
to "register a new application".  


#### Running the Program ####
Make sure  you have set up the client_id and client_secret first.  
to  run the program type:

```
python3 asygitcount.py
 ```
The server should start with the following type of output:  
2017-09-27 17:38:12+0200 [-] Log opened.  
2017-09-27 17:38:12+0200 [-] Site starting on 8080  
2017-09-27 17:38:12+0200 [-] Starting factory <twisted.web.server.Site object at 0x7f3d8c2889e8>  


From your browser go to the address  
http://localhost:8080/remainingcalls  
Remaining calls to github:5000  

you can also call the server with the following URL:
server/gitcount/<location name>/<number> for example:
http://localhost:8080/gitcount/cardedeu/10  

which gives the following delightful output:  

Username, Num Repos, Pull requests  
mbiarnes,60,2  
dgisbert,10,0  
iclavijos,9,0  
jordilopez,6,0  
KenBuckley,4,2  
jespa007,2,0  
winnethebago,2,0  
jmpuigdollers,2,0  
danimagan,2,0  
IndignatsCardedeu,1,0  


#### Running unittests ####
none in current version
#### Running in Production ####
not production ready -ohh no no no.
Not bad just needs more testing to ensure everything works as expected
in all scenarios.  
### Contribution guidelines ###

* Writing tests
* Code review

