# plot-server
A Flask application that provides plot viewing in web browser and API for data uploading.

## Building

Initial setup can be done by (if appropriate version of _virtualenv_ is not installed, you will be informed):

```shell
/bin/bash init.sh
```
You will also need to create database and add user (check _config.py_ files for details). Database migrations are done with:
```bash
cd plot-server/page-server
flask db migrate
```


## Dependencies

Be sure the following services are available (no dev support):

* direnv
* postgres
* pip3

More services are needed for development support:
* direnv
* sass (dart-sass)
