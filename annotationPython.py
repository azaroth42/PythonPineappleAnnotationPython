
import requests
import json
import sys

class Protocol(object):

	endpoint = ""
	cache = {}

	def __init__(self, url, desc=True):
		self.endpoint = url
		self.full_description = desc
		self.cache = {}

	def fetch(self, url=""):
		if not url:
			url = self.endpoint		
		if self.full_description:
			hv = 'return=representation;include="http://www.w3.org/ns/oa#PreferContainedDescriptions"'
		else:
			hv = 'return=representation;include="http://www.w3.org/ns/oa#PreferContainedIRIs"'

		headers = {'Accept': "application/ld+json", 'Prefer': hv}
		p1 = requests.get(url, headers=headers)
		resp = p1.json()
		return resp


class Collection(object):

	def __init__(self, protocol):
		self.protocol = protocol
		self.data = {}

	def load(self):
		self.data = self.protocol.fetch()

	def page(self, url=""):
		if not url:
			if not self.data:
				self.load()
			url = self.data['first']
			if type(url) == dict:
				url = url['id']
		page = self.protocol.fetch(url)
		return page

	def pg_to_ui(self, url):
		stuff = self.protocol.cache.get(url, '')
		if not stuff:
			stuff = len(self.protocol.cache)
			self.protocol.cache[url] = stuff
		return "%s.html" % stuff

	def process(self, url="", follow=True):

		while True:
			resp = self.page(url)

			coll = resp.get('partOf', {})
			ttl = coll.get('total', -1)
			first = coll.get('first', '')
			last = coll.get('last', '')
			modded = coll.get('modified', '')

			start = resp.get('startIndex', -1)
			nxt = resp.get('next', '')
			prev = resp.get('prev', '')

			annos = resp.get('items', [])
			annoL = []
			for a in annos:
				anno = Annotation(a, self.protocol)
				annoL.append(anno)

			html = self.render(start, ttl, first, prev, nxt, last, modded, annoL)
			yield (self.pg_to_ui(url), html)

			if nxt and follow:
				url = nxt
			else:
				raise StopIteration

	def render(self, start, ttl, first, prev, nxt, last, modded, annos):
		# Render page to basic html
		pgL = []
		if start and ttl:
			pgL.append('<div class="hdr">%s-%s of %s</div>' % (start+1, start+len(annos), ttl))
		pgL.append('<div class="annos">')
		for a in annos:
			pgL.append(a.render())
		pgL.append('</div>')
		nav = []
		if first:
			nav.append('<a href="%s">first</a>' % self.pg_to_ui(first))
		if prev:
			nav.append('<a href="%s">previous</a>' % self.pg_to_ui(prev))
		if nxt:
			nav.append('<a href="%s">next</a>' % self.pg_to_ui(nxt))
		if last:
			nav.append('<a href="%s">last</a>' % self.pg_to_ui(last))
		if nav:
			navs = '<div class="nav">' + " | ".join(nav) + "</div>"
			pgL.append(navs)

		html = '\n'.join(pgL)
		return html


class Annotation(object):

	json = {}
	protocol = None

	def __init__(self, data, protocol):
		self.protocol = protocol

		# Ensure that we have the full JSON description
		if type(data) != dict:
			# just a URI, despite asking for full description
			data = protocol.fetch(data)
		elif not data.get('target', {}) and data.get('id', ''):
			# No target = not an annotation ... try and fetch id 
			data = protocol.fetch(data['id'])
		self.json = data

	def render_section(self, what, cls="target", lbl="On: "):
		# Make a thing into a singleton
		if type(what) != list:
			what = [what]
		html = '<div class="%s">%s ' % (cls, lbl)
		for w in what:
			rhtml = self.render_resource(w)
			html += rhtml
		html += '</div>'
		return html

	def render_resource(self, w):
		html = "<i>[Unable to process]</i>"
		if type(w) == dict:
			typ = w.get('type', '')
			if typ == "TextualBody":
				html = w['value']		
			elif typ == "SpecificResource":
				res = w['source']
				return self.render_resource(res)
			elif w.get('id'):
				uri = w['id']
				lbl = w.get('label', "[%s]" % typ)
				html = '<a href="%s">%s</a>' % (uri, lbl)
		else:
			# String URI, no label or other info
			html = '<a href="%s">%s</a>' % (w, w)
		return html

	def render(self):
		# Render annotation to basic HTML

		html = ['<div class="anno">']

		# target, body
		tgt = self.json.get('target', {})
		html.append(self.render_section(tgt))
		body = self.json.get('body', {})
		html.append(self.render_section(body, cls="body", lbl=""))

		# metadata
		## who
		## when
		## rights
		## canonical, via

		html.append('</div>')
		htmlstr = ''.join(html)
		return htmlstr

def write_pages(coll):
	p = Protocol(coll)
	c = Collection(p)
	for (fn, html) in c.process():
		fh = file('data/%s' % fn, 'w')
		fh.write(html)
		fh.close()

if __name__ == "__main__":
	if len(sys.argv) > 1:
		# e.g. http://localhost:8080/annos/
		coll = sys.argv[1]
		write_pages(coll)
	else:
		print "Usage %s <url-to-collection>" % sys.argv[0]

