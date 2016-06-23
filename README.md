# Django Experimental Platform [![Build Status]
Combining waitroom, forum and chat functionalites....

## Running locally

To run this app locally, you'll need Python, MySQL, and Redis. 

Then, to run:

- Install requirements: `pip install -r requirements.txt` (you almost certainly want to do this in a virtualenv).
- Migrate:  python manage.py migrate`
-
- Or, to run locally with `runserver`, set `DATABASE_URL` and `REDIS_URL` in your environ, then run `python manage.py runserver`.
- Or, to run locally with multiple proceses by setting the environ, then running the two commands (`daphne` and `runworker`) as shown in the `Procfile`.


