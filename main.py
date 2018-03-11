#!/usr/bin/env python
import os
import jinja2
import webapp2

from models import Sporocilo
from google.appengine.api import users # googlaj google.appengine.api user

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):

        user = users.get_current_user()
        if user:
            logout_url = users.create_logout_url("/")
            logiran = True
            podatki = {"logout_url": logout_url, "logiran": logiran, "user": user}
        else:
            login_url = users.create_login_url("/")
            logiran = False
            podatki = {"login_url": login_url, "logiran": logiran}

        return self.render_template("hello.html", params=podatki)


class RezultatHandler(BaseHandler):
    def post(self):
        user = users.get_current_user()
        rezultat = self.request.get("input-sporocilo")
        eprejemnik = self.request.get("prejemnik")

        sporocilo = Sporocilo(besedilo=rezultat, prejemnik=eprejemnik, email=user.email())
        sporocilo.put()
        return self.write(rezultat)


class ListHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        # Iz baze vzamemo vsa sporocila
        seznam = Sporocilo.query(Sporocilo.izbrisano == False).filter(Sporocilo.email == user.email()).fetch()
        params = {"seznam": seznam}
        return self.render_template("seznam.html", params=params)


class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        # Iz baze vzamemo sporocilo, katerega id je enak podanemu
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        params = {"sporocilo": sporocilo}
        return self.render_template("posamezno_sporocilo.html", params=params)

class UrediHandler(BaseHandler):
    def get(self, sporocilo_id):
        # Iz baze vzamemo sporocilo, katerega id je enak podanemu
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        params = {"sporocilo": sporocilo}
        return self.render_template("posamezno_sporocilo_uredi.html", params=params)

    def post(self, sporocilo_id): # to metodo naredimo zaradi shrani gumba
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id)) # potegnemo staro sporocilo iz baze
        sporocilo.besedilo = self.request.get("nov-text")
        sporocilo.put()
        return self.redirect_to("seznam-sporocil")

class DeleteHandler(BaseHandler):
    def get(self, sporocilo_id):
        # Iz baze vzamemo sporocilo, katerega id je enak podanemu
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        params = {"sporocilo": sporocilo}
        return self.render_template("posamezno_sporocilo_izbrisi.html", params=params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))  # potegnemo staro sporocilo iz baze
        # sporocilo.key.delete()  to dejansko izbrise
        sporocilo.izbrisano = True # to pa samo skrije
        sporocilo.put()
        return self.redirect_to("seznam-sporocil")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam', ListHandler, name="seznam-sporocil"), # ime da lahko redirectamo
    # Na to pot primejo linki oblike /sporocilo/{{poljubne stevke}}
    # sporocilo_id pa je zgolj poimenovanje, ki ga potem uporabimo v metodi,
    # ki se klice ob prihodu na to pot
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/edit', UrediHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/delete', DeleteHandler),
], debug=True)
