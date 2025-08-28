from repository import Repo
from models import *


# V tej datoteki lahko testiramo funkcionalnost repozitorija,
# brez da zaganjamo celoten projekt.


repo = Repo(admin=False)

# Dobimo vse osebe

knjige = repo.dobi_knjige_po_naslovu('Matilda')


# Jih izpišemo
for k in knjige:
    print(k)

# Izberemo si recimo neko osebo
#o = knjige[0]

# Za to osebo želimo pridobiti vse transakcije

#transakcije = repo.dobi_transakcije_oseba(o.emso)

#for t in transakcije:
#    print(t)