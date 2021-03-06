PyAlive
=====

A simple python script to check if website is up.  PyAlive issued a GET request to the URLs you specify and if a response code matching an alive code counts as up, anything else is an error.

Alive Codes = {200, 201, 202, 203, 204, 205, 206, 301, 302, 303, 304}

##Command Line Options

* --config *path to the json config file*
* --url *check to see if the supplied URL is alive*
* --notify-on *"errors" or "all" (if you run the job hourly and set this to all, you will get a lot of email)*

##Setup

*(these instructions have been tested on ubuntu linix, YMMV)*

1. Make a copy of the default_pyalive.json file found in this directory and call it whatever you want.
2. Fill out the information in the JSON like this:
    ```JSON
    {
        "urls": ["https://foo.net", "https://www.bar.com"],
        "emails": ["ops@bar.net"],
        "from": "foo@bar.com",
        "smtp": {
            "user": "foo@bar.com",
            "password": "baz",
            "host": "bar.com"
        }
    }
    ```
    - **sites** tells pyalive which sites to check
    - **emails** tells pyalive which emails to notify if there is a problem
    - **smtp** tells pyalive which smtp account to use (pyalive falls back to sendmail if this is omitted)

3. Edit contab using this command
    ```Shell
    $ crontab -e
    ```

4. Add this line to the jobs
    ```Shell
    */30 *  * * * . $HOME/.profile; /path/to/pyalive/pyalive.py --config=/path/to/json/config/pyalive.json
    ```

*Now you're done!*

This job will run every 30 minutes and email you the moment one of these sites returns a [status code][1]
other than 200.

[1]: http://en.wikipedia.org/wiki/List_of_HTTP_status_codes "HTTP Status Codes"