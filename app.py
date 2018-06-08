from sqlalchemy import DateTime, Float, create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func

from flask import Flask, request, jsonify


app = Flask(__name__)
app.debug = True
prod_engine = create_engine('postgresql://usr:pass@localhost:5432/prod', convert_unicode=True)
Session = sessionmaker()
app.Session = Session
Session.configure(bind=prod_engine)

Base = declarative_base()


class Transfer(Base):
    __tablename__ = 'transfers'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="transfers")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(32), unique=True, nullable=False)
    first_name = Column(String(32))
    last_name = Column(String(32))
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    transfers = relationship("Transfer", back_populates="user")


@app.route("/api/loyalty/create_new_user", methods=["POST"])
def create_new_user():
    """
    POST loyalty/user
    JSON payload with email, firstName and lastName,
    creates user
    return success=True/False
    """
    data = request.get_json()
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    user = User(email=email, first_name=first_name, last_name=last_name)

    db_session = app.Session()

    try:
        db_session.add(user)
        db_session.commit()
        return jsonify(dict(
            email=user.email, first_name=user.first_name, id=user.id
        )), 201
    except IntegrityError as e:
        db_session.rollback()
        return jsonify({"error": "could not create user"}), 500
    finally:
        db_session.close()


@app.route("/api/loyalty/create_new_transfer", methods=["POST"])
def create_new_transfer():
    """
    POST loyalty/transfer
    JSON payload with user_id, amount,
    creates transfer
    return success=True/False
    """
    data = request.get_json()
    user_id = int(data.get('user_id'))
    amount = float(data.get('amount'))
    transfer = Transfer(user_id=user_id, amount=amount)

    db_session = app.Session()

    try:
        transfers = db_session.query(Transfer).filter(Transfer.user_id == user_id).all()

        if sum([t.amount for t in transfers]) + amount < 0:
            db_session.rollback()
            return jsonify({"error": "not enough funds"}), 418
        else:
            db_session.add(transfer)
            db_session.commit()
            return jsonify(dict(
                user_id=transfer.user_id, transfer_id=transfer.id,
                amount=transfer.amount
            )), 201
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "could not make transfer"}), 500
    finally:
        db_session.close()



@app.route("/api/loyalty/user/<int:user_id>/transfers", methods=["GET"])
def get_user_transfers(user_id):
    """
    GET loyalty/user/<user_id>/transfers
    returns all transfers as JSON
    """
    db_session = app.Session()

    transfers = db_session.query(Transfer).filter(Transfer.user_id == user_id).all()

    transfers = [dict(id=str(t.id),
                      created=t.created.strftime("%Y-%m-%d %H:%M:%S"),
                      user_id=str(t.user_id),
                      amount=str(t.amount)) for t in transfers]
    # TODO consider returning user does not exists
    return jsonify(dict(transfers=transfers)), 500


if __name__ == "__main__":
    app.run()
