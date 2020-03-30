from datetime import datetime
from pony.orm import *
import keys


db = Database()
db.bind(provider=keys.provider, host=keys.host, user=keys.user, passwd=keys.passwd, db=keys.db)

class Human(db.Entity):
    id = PrimaryKey(int, auto=True)
    lastname = Optional(str)
    firstname = Optional(str)
    patronymic = Optional(str)
    birthdate = Optional(str)
    sex = Optional(str)
    login = Optional(str, nullable=True)
    password = Optional(str, nullable=True)
    patient = Optional('Patient')
    doctor = Optional('Doctor')
    administrator = Optional('Administrator')


class Doctor(db.Entity):
    id = PrimaryKey(int, auto=True)
    specialities = Set('Speciality')
    records = Set('Record')
    human = Required(Human)


class Patient(db.Entity):
    id = PrimaryKey(int, auto=True)
    human = Required(Human)
    records = Set('Record')


class Speciality(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Optional(str)
    doctor = Required(Doctor)


class Record(db.Entity):
    id = PrimaryKey(int, auto=True)
    patient = Required(Patient)
    doctors = Set(Doctor)
    time = Optional(datetime)


class Administrator(db.Entity):
    id = PrimaryKey(int, auto=True)
    human = Required(Human)



def test(login, password):
    pattern = r'[^\w+]'
    patient = select(c for c in Human).show()
    print(1)



db.generate_mapping(create_tables=False)