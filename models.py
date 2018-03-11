from google.appengine.ext import ndb


class Sporocilo(ndb.Model):
    besedilo = ndb.StringProperty()
    email = ndb.StringProperty()
    prejemnik = ndb.StringProperty()
    nastanek = ndb.DateTimeProperty(auto_now_add=True)
    izbrisano = ndb.BooleanProperty(default=False) # po defaultu ni izbrisan
