'''
gitCountServ
Queries the github API for repositories.
For the users with most repositories at a given location
determine the number of PullRequestEvents (closed and merged=True)
and list the users in a report.

This webservice is customised to deliver human readable output to a 
web browser -though normally it would serve straight JSON to be a more 
flexibile WebService.
'''

from klein import Klein
import requests
import json
from urllib.parse import urljoin
from ratelimit import rate_limited
from collections import Counter


GITHUB_API = 'https://api.github.com'
GITHUB_API_VERSION = 'application/vnd.github.v3+json'  
GITHUB_CLIENT_ID = 'ZZZZZZZZ'#insert client id here-normally from environment
GITHUB_CLIENT_SECRET = 'SSSSSSSSSS'#insert client secret here-normally from environment
GITHUB_HEADERS_TO = {
                     #cannot use authentication token - max 60 api requests.
                     #'Authentication': 'token %s' % GITHUB_API_TOKEN,
                     'Accept': '%s'%  GITHUB_API_VERSION,
                     #GitHub request app name in header
                     'User-Agent': 'KenBuckley-App-TotalUsersPerLocation'
                    }
MAXUSERS = 20  #the maximum number of users the system will search on .
APPROACHLIMIT = 2000 #when within APPROACHLIMIT calls of reaching RATELIMIT stop. 
                     #ideally it handled by a central supervisor service 

'''
 global variables 
'''
interval_counter = 0 #starts at zero so that we always check our rate limit on
                     #program start
html_out = ""   #the output string to the browser


class BreakoutException(BaseException):
    '''
    User created exception creation
    does nothing itself but facilitates
    clean exit.
    '''
    pass



'''Klein Framework caller '''
app = Klein()

def exitWithMessage(note):
    '''
    This function exits the program gracefully as needed
    (typically when the rate limit is reached.
    '''
    raise BreakoutException(note)  #quit and report to browser  

def getRateLimitRemaining():
    ''' This function checks the amount of queries we
    are allowed to send to the github API.
    Calling this rate_limit url itself does not decrease our rate limit.
    If we exceed the rate limit we will be given a 403 
    and the IP will be banned for a period of time.
    So do not allow this to happen-by putting all calls through 
    this function

    The api documentation lists the call as follows:
    GET /rate_limit
    '''
    url = GITHUB_API + '/rate_limit'
    url += '?client_id=' + GITHUB_CLIENT_ID 
    url += '&client_secret=' + GITHUB_CLIENT_SECRET 
    res=requests.get(url,GITHUB_HEADERS_TO)
    checkStatusCode(res)
    j = json.loads(res.text)
    
    remaining_limit = (j["rate"]["remaining"])
    return remaining_limit


def intervalRateCheck():
    '''
    Check every 10 calls to the github api to see 
    if we are approaching our rate limit.
    If we hit the limit we exit.
    Also doubles as initial check before we start a 
    new query process.

    note: we should really also give a time left to 
          when the counter will reset- TODO
    '''
    if (interval_counter % 10) == 0 :
        if getRateLimitRemaining() < APPROACHLIMIT:
            exitWithMessage("<p>Sorry we are near our rate limit with github\
               at this time. So we have stopped your request.<br>You can check\
               the  remaining call numbers\
               using the /remainingcalls url.<p>")



# The @rate_limited decorator below (currently commented out)
# limits the calls to the api to a max per second.
# used where limiting the calls to an api is on a per second basis
#@rate_limited(20)
def rateLimitedRequest(url,headers):
    '''
    This module seeks to track every API call made by this instance of 
    the service, with the exception of calls to the /rate_limit api. 
    There may be other instances running so we should ideally
    - check with the external supervisor function ( redis etc.) 
       to see if we are allowed to make a call -i.e. to ensure that the sum of
       all API calls to github stay below the threshold
    - update the api-calls-made counter in the supervisor 
    - call the request in a concurrent fashion
    - immediately exit with message to user if we have hit our rate limit

    This version of the code does not have a supervisor function so we 
    simply check every 10 calls to see if we are near our pre-defined 
    APPROACHLIMIT (manually set, it triggers when we have only the 
    APPROACHLIMIT number of calls left)
       -this would allows for aprox 100 threads of the program running in parallel
       -the supervisor should control the amount of calls left- much faster 
         than checking the API constantly
    '''
    intervalRateCheck()  #every 10 calls check if we are near rate limit
    return requests.get(url, headers=headers)


def checkStatusCode(res):
    ''' Generic program wide handling of 
    status codes back from GitHub.
    Here we abort the program if we receive a code
    >= to 400. We hand back the error message to the
    client.
    '''
    if res.status_code >= 400:
        j = json.loads(res.text)
        msg = j.get('message', 'UNDEFINED ERROR (no error description from server)')
        print ('ERROR: %s' % msg)
        print ("res.url:{}".format(res.url))
        exit()
    return  


def printRateLimit(id):
    '''debuging function to assist with 
       limit of remaing calls 
       versus the location as stated in the parameter id
       writes to console.
    '''
    print("id:{} Rate Limit {}".format(id, getRateLimitRemaining()))
    return

def htmlRateLimit(note):
    '''Output function to tell the user the number of calls remaining
    in HTML format
    Does not effect the rate limit set by github
    '''
    return "<p>{}{}</p><br>".format(note, getRateLimitRemaining())

def getReposByUsername(username):
    ''' get all the repositories for the given login

    The api documentation lists the call as follows:
    GET /users/:username/repos
    '''
    url =  GITHUB_API + '/users/' + username  + '/repos' 
    url += '?client_id=' + GITHUB_CLIENT_ID 
    url += '&client_secret=' + GITHUB_CLIENT_SECRET 
    url += '&per_page=100'
    res = rateLimitedRequest(url,GITHUB_HEADERS_TO)
    checkStatusCode(res)
    print("Repos of {}:".format(username),end='') #print without newline at end
    j = json.loads(res.text)
    user_repos_tup=() #tuple 
    for repo in j:
        print('@', end='') #for each repo print a @
        #print("username:{} reponame:{}".format(username,repo["name"]))
        user_repos_tup = user_repos_tup + ((username,repo["name"]),)
    print('E') #end of repos for the user 
    return user_repos_tup 

def getMergedPullRequests(username,repo):
    ''' get all the Pull requests  for the given login
    where the event has characteristics:

         "type": "PullRequestEvent",
          payload": 
               "action": "closed",
          "merged": true,

    The api documentation lists the call as follows:
    GET /repos/:owner/:repo/events 
    '''
    url =  GITHUB_API + '/repos/' + username  + '/' + repo + '/events' 
    url += '?type' + 'owner' #default
    url += '&client_id=' + GITHUB_CLIENT_ID 
    url += '&client_secret=' + GITHUB_CLIENT_SECRET 
    res = rateLimitedRequest(url,GITHUB_HEADERS_TO)
    checkStatusCode(res)
    j = json.loads(res.text)

    #count the PullRequest Events for all the repos
    countMergedTrue =0
    for event in j:
        if event["type"] == "PullRequestEvent":
            if event["payload"]["action"] == "closed":
                if event["payload"]["pull_request"]["merged"] is True:
                    countMergedTrue += 1
                    '''
                    print("type:{} action:{} merged:{}".format(
                        event["type"],
                        event["payload"]["action"],
                        event["payload"]["pull_request"]["merged"]))
                    '''
    return countMergedTrue 
    
def getAllUsersAtLocation(location,maxusers):
    '''
    This function lists all users at a location,
      -sorted by repositories (descending)
      -only users not organisations
      -up to a maximum 20 users

    The api documentation lists the call as follows:
    GET /search/users?q=location:location+type:user+sort:repositories 
    '''
    url = 'https://api.github.com/search/users?'
    url += 'q=location:' + location 
    url += '+type:user+sort:repositories&per_page=' + str(maxusers)
    url += '&client_id=' + GITHUB_CLIENT_ID 
    url += '&client_secret=' + GITHUB_CLIENT_SECRET 

    #rate limited request caller
    res = rateLimitedRequest(url,GITHUB_HEADERS_TO)
    #print('res.url is %s' % res.url)
    checkStatusCode(res)
    return json.loads(res.text)

def main(location,numusers):
    '''
    Here is the main controll flow for the program.
    Note all print() statements are logged to the console
    --they can be removed, here they just serve as 
    a utility to review the program.
    '''
    #limit the selected number of users otherwise 
    #its possible we will hit the max number of 
    #queries against github within a time period
    if numusers > MAXUSERS:
        numusers = MAXUSERS 

    jsonUsers=getAllUsersAtLocation(location,numusers)

    user_repos = () #a tuple structure holding all (username,repo) tuples
    user_repos_single =() # tuple structure (username,repo) for a single user 
    user_repo_merged_count_dict = {} #dictionary with key (username,repo) and count

    #get repos by username
    for item in jsonUsers["items"]:
        username = item["login"]
        user_repos_single = getReposByUsername(username)#username set against /users
        user_repos += user_repos_single   #add to the list of all (users,repos) 
        
        for username_repo in user_repos_single:
            #count merged is true for the user/repo combination
            user_repo_merged_count_dict[username_repo ]= (
                 getMergedPullRequests(username_repo[0],username_repo[1])) 

            print('P', end='') #to console-for each Parsed repo print a P
        print('E') #to-consolefinished printing Ps to console for this user


    #print("user_repo_merged_count_dict: {}".format(user_repo_merged_count_dict))
    
    #make dictionary with {user:count_of_repos}
    countUserRepos=Counter()
    #count each instance of username in the dictionary
    for username,repo in user_repo_merged_count_dict:
        countUserRepos[username] += 1 
    print("countUserRepos:{}".format(countUserRepos))
    
    #make dictionary with {user:sum_of_pull_events}
    countUserEvents=Counter()
    #sum the events for each username
    for username,repo in user_repo_merged_count_dict:
        countUserEvents[username] += user_repo_merged_count_dict[(username,repo)] 
    print("countUserEvents:{}".format(countUserEvents))
    
    output="<p>Username, Num Repos, Pull requests</p><br>"
    for username,repocount in countUserRepos.most_common():
        output += "<p>{},{},{}</p><br>".format(username, 
                                repocount,
                 (countUserEvents[username]))
    print(output) #logged to console
    return output
    

@app.route('/remainingcalls')
def pg_root(request):
    '''
    This URL allows the user to query the 
    remaining number of calls allowed to github
    ''' 
    return htmlRateLimit("Remaining calls to github:") 

@app.route('/gitcount/<string:location>/<int:numUsers>')
def pg_gitcount_amount(request,location,numUsers):
   '''
   This URL allows the user to query the 
   remaining number of calls allowed to github
   BreakoutException is a fake exception to allow us 
   to stop the program at any point and exit with 
   feedback to the users (on say ratelimit exceeded)
   ''' 
   try:
        intervalRateCheck()  #ensure we do not hit rate limit for github 
        html_out = main(location,numUsers)
   except BreakoutException as ex:
        html_out = ex.args[0]
        pass
   return html_out

'''Run the server at ip and port number'''
app.run("localhost", 8080)
# resource = app.resource  #for user when run under twistd
