
from app import app, User, Session
import unittest
from flask import json


class FlaskAppTests(unittest.TestCase):
    # NOTE: This test file is using production db as a temporary hack.
    # TODO: Setup conftest.py and maybe create a client factory or use mock
    test_email = 'dummy@g.com'
    new_user_email = 'reserved@g.com'

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        try:
            session = Session()
            session.add(User(email=self.test_email))
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

        session = Session()
        self.user_id = session.query(User.id).filter(User.email == self.test_email).scalar()
        session.close()

    def tearDown(self):
        session = Session()
        user = session.query(User).filter(User.email == self.new_user_email).first()
        # TODO make it cascade to the users's transfers
        if user:
            session.delete(user)
            session.commit()
            session.close()
        else:
            session.rollback()

    def test_get_user_transfers(self):
        response = self.app.get('/api/loyalty/user/1/transfers')
        response = json.loads(response.data)
        assert 'transfers' in response
        assert response.get('transfers') == []

    def test_create_new_user(self):
        email = self.new_user_email
        response = self.app.post('/api/loyalty/create_new_user',
                                 data=json.dumps(dict(email=email)),
                                 content_type='application/json')
        response = json.loads(response.data)
        assert response['email'] == email
        assert 'id' in response

    def test_create_new_transfer(self):
        user_id = self.user_id
        response = self.app.post('/api/loyalty/create_new_transfer',
                                 data=json.dumps(
                                     dict(user_id=user_id, amount=2)),
                                 content_type='application/json')
        response = json.loads(response.data)
        assert response['user_id'] is user_id

    def test_create_new_transfer_invalid(self):
        user_id = self.user_id
        response = self.app.post('/api/loyalty/create_new_transfer',
                                 data=json.dumps(
                                     dict(user_id=user_id, amount=-1000)),
                                 content_type='application/json')
        assert response.status_code == 418

    def test_get_user_transfers(self):
        user_id = self.user_id
        response = self.app.post('/api/loyalty/create_new_transfer',
                                 data=json.dumps(
                                     dict(user_id=user_id, amount=2)),
                                 content_type='application/json')
        response = json.loads(response.data)
        assert response['user_id'] is user_id
