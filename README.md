# pygments-web
This renders code as syntax highlighted rich text, to be copied-and-pasted in presentations or downloaded as a pdf.

## Dependencies
 * Python 3
  * pip
  * django
  * weasyprint 52.5
  * pygments
  * whitenoise



## Setting up on your computer

Download the repo by opening a terminal and typing 

```console
$ git clone https://github.com/daltonma/pygments-web
... extra stuff ...
$ cd pygments-web/highlight
$
```

Then run `pip install -r requirements.txt`.


## Starting the server

Run `python manage.py runserver`. 
