The following setup is prepared for Ubuntu 16.04 LTS

```
sudo apt-get update -qq && apt-get install -y python3 python3-setuptools python3-pip
sudo easy_install3 pip
```

```
sudo pip3 install -r requirements.txt
```

Important!!!  
Open the file  gitcount.py and insert the client_id and client secret as supplied by the author.  
Insert the key directly into the areas of ZZZs and SSSSs -  
GITHUB_CLIENT_ID = 'ZZZZZZZZ'#insert client id here-normally from environment  
GITHUB_CLIENT_SECRET = 'SSSSSSSSSS'#insert client secret here-normally from environment    

Alternatively you may insert your own client_id and Client_secret -however in this case please change the
'User-Agent': 'KenBuckley-App-TotalUsersPerLocation' to your App's name. Your own client_id and
secret can be generated in https://github.com/settings/developers -click on OAuth Apps and click the button 
to "register a new application".  


#### Running the Program ####
Make sure  you have set up the client_id and client_secret first.  
to  run the program type:

```
python3 gitcount.py
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



### Docker file ###
Dockerfile is not working at the moment - the service runs in the 
the docker file but can't be access as expected - to look at.

#### Running unittests ####
none in current version
#### Running in Production ####
not production ready -ohh no no no.
### Contribution guidelines ###

* Writing tests
* Code review

