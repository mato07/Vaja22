#!/usr/bin/env python
import os
import jinja2
import webapp2

from models import Sporocilo

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
        return self.render_template("hello.html")


class RezultatHandler(BaseHandler):
    def post(self):
        rezultat = self.request.get("input-sporocilo")

        sporocilo = Sporocilo(besedilo=rezultat)
        sporocilo.put()
        return self.write(rezultat)


class ListHandler(BaseHandler):
    def get(self):
        # Iz baze vzamemo vsa sporocila
        seznam = Sporocilo.query().fetch()
        params = {"seznam": seznam}
        return self.render_template("seznam.html", params=params)


class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        # Iz baze vzamemo sporocilo, katerega id je enak podanemu
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        params = {"sporocilo": sporocilo}
        return self.render_template("posamezno_sporocilo.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam', ListHandler),
    # Na to pot primejo linki oblike /sporocilo/{{poljubne stevke}}
    # sporocilo_id pa je zgolj poimenovanje, ki ga potem uporabimo v metodi,
    # ki se klice ob prihodu na to pot
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler)
], debug=True)
