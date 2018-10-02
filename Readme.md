# Backup application

Backup application description

## Working

First I needed to underestand how authentication and authorization process looks now on 
Microsoft Accounts. And it wan't easy, but after reading some manuals and stack overflow 
posts I find out example: https://github.com/microsoftgraph/python-sample-console-app. 

No it's not what works. 

Ok, I get some construction working. First I create in side thread basic http server.
On Microsoft site I register my app and gets `client_id` and `client_secret`.
Next I add some 'custom' `redirect_uri` "http://localhost:PORT/endpoint". And now is the
time to come back to python code. I need to run basic http server on localhost on PORT,
and wait for one request. This http server will be runned in side-thread. In the main flow
I will run default browser with authentication link. This step will require an end user to 
give permission for the app to one's OneDrive account (Files.ReadWrite). As a return for
given agreement Microsoft Authorization page will redirect us to the endpoint we gave it
one step before. And this is how our side-threaded http server will obtain request with 
`code`. 

