
# Loyalty API

An API for a loyalty transaction system

- POST loyalty/user
    - JSON payload with email, firstName and lastName,
    - creates user
    - returns user object upon success

- POST loyalty/transfer
    - JSON payload with user_id, amount,
    - creates transfer
    - returns transfer object upon success

- GET loyalty/user/<user_id>/transfers
    - returns all transfers for user

## Setup

- install venv, `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- install docker
- `./tools/setup_db.sh` *you might have to run this twice if you see an error
- `python app.py`

## Tests

Testing infrastructure is not completely set up, uses production db for now.

    Run using `python -m pytest tests/test_app.py`


## Useful Commands

`curl --header "Content-Type: application/json" --request POST --data '{"email":"happy@happy.com","first_name":"Happy"}' http://localhost:5000/api/loyalty/create_new_user`

`curl --header "Content-Type: application/json" --request POST --data '{"user_id":"5","amount":"1000"}' http://localhost:5000/api/loyalty/create_new_transfer`

`curl http://localhost:5000/api/loyalty/user/5/transfers`

`alembic revision --autogenerate -m "Add users and transfers tables"`

`alembic upgrade head`

`alembic downgrade -1`

`PGUSER=usr PGPASSWORD=pass psql -h localhost -p 5432 prod`
