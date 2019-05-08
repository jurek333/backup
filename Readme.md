# Backup application

Backup application description

## Working

The program reads configuration from home directory. There should be client id, secret and redirect url. 
You get this information when you register the backup program at Microsoft Account. [more instructions]

### Auth

How authentication works? Run the one-shot HTTP server listening on registered redirect url. 
Then combine url for geting `code` and open browser with it. You may need to login to Your personal 
Microsoft Account, and give the permision to the backup program. After that browser will be redirected to
the `redirect url` with `code` in query. Using this `code` we can next make POST to token endpoint.

### How data is stored

In root folder on OneDrive, there is a file with configuration for aliases and paths. There you should add your tags/labels and create path for each one. When you run command b <file> <label> application download this map file from OneDrive, search for given label and place given file under the path assigned to the label.