import requests
import json


class AnnotationProtocol(object):

	endpoint = ""
	cache = {}

	def __init__(self, url):
		self.endpoint = url
		self.cache = {}

	def fetch(self, url):
		p1 = requests.get(pg)
		resp = p1.json()
		return resp


class Annotation(object):

	def __init__(self, js):
		self.json = js

class Renderer(object):

	def __init__(self):
		pass


def render_resource(what, cls="target", lbl="On: "):
	if type(what) != list:
		what = [what]
	html = '<div class="%s">%s' % (cls, lbl)
	for w in what:
		if type(w) == dict:
			typ = w.get('type', '')
			if typ == "Choice":
				# pick first
			# Resource

			# Choice
			# TextualBody
			# SpecificResource
			pass
		else:
			# String URI
			html += ' <a href="%s">%s</a>' % (w, w)
	html += '</div>'
	return html

def render_anno(anno):
	# Check if anno is URI or description
	if type(anno) != dict:
		anno = fetch(anno)
	elif not anno.get('target', {}) and anno.get('id', ''):
		anno = fetch(anno['id'])

	html = ['<div class="anno">']

	# target, body
	tgt = anno.get('target', {})
	html.append(render_resource(tgt))
	body = anno.get('body', {})
	html.append(render_resource(body, cls="body", lbl=""))

	# metadata
	## who
	## when
	## rights
	## canonical, via

	html.append('</div>')
	htmlstr = ''.join(html)
	return htmlstr

def pg_to_ui(pg):
	return pg

def process_page(pg, follow=True):

	while pg:

		resp = fetch(pg)

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
		for anno in annos:
			# process anno into list
			annoL.append(render_anno(anno))

		# Render page to html
		pgL = []
		if start and ttl:
			pgL.append('<div class="hdr">%s-%s of %s</div>' % (start+1, start+len(annos), ttl))
		pgL.append('<div class="annos">')
		pgL.extend(annoL)
		pgL.append('</div>')
		nav = []
		if first:
			nav.append('<a href="%s">first</a>' % pg_to_ui(first))
		if prev:
			nav.append('<a href="%s">previous</a>' % pg_to_ui(prev))
		if nxt:
			nav.append('<a href="%s">next</a>' % pg_to_ui(nxt))
		if last:
			nav.append('<a href="%s">last</a>' % pg_to_ui(last))
		if nav:
			navs = '<div class="nav">' + " | ".join(nav) + "</div>"
			pgL.append(navs)

		# yield page as a generator
		html = '\n'.join(pgL)
		yield html

		if nxt and follow:
			pg = nxt
		else:
			pg = None

def process_collection(coll):
	c = fetch(coll)
	first = c['first']
	if type(first) == dict:
		first = first['id']
	return process_page(first)

for x in process_collection("http://localhost:8080/annos/"):
	print x
	break
