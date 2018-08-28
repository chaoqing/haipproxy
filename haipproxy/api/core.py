"""
web api for haipproxy
"""
import os

from flask import (
    Flask, Response, jsonify as flask_jsonify)
from flask_basicauth import BasicAuth

from ..client.py_cli import ProxyFetcher
from ..config.rules import VALIDATOR_TASKS
from ..config.settings import (
    API_AUTH_ENABLE, API_AUTH_USER, API_AUTH_PASSWORD)


def jsonify(*args, **kwargs):
    response = flask_jsonify(*args, **kwargs)
    if not response.data.endswith(b"\n"):
        response.data += b"\n"
    return response


# web api uses robin strategy for proxy schedule, crawler client may implete
# its own schedule strategy
usage_registry = {task['name']: ProxyFetcher('task') for task in VALIDATOR_TASKS}
app = Flask(__name__)
app.debug = bool(os.environ.get("DEBUG"))
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

if API_AUTH_ENABLE:
    app.config['BASIC_AUTH_FORCE'] = True
    app.config['BASIC_AUTH_USERNAME'] = API_AUTH_USER
    app.config['BASIC_AUTH_PASSWORD'] = API_AUTH_PASSWORD

    basic_auth = BasicAuth(app)

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'reason': 'resource not found',
        'status_code': 404
    })


@app.errorhandler(500)
def not_found(e):
    return jsonify({
        'reason': 'internal server error',
        'status_code': 500
    })


@app.route("/proxy/get/<usage>")
def get_proxy(usage):
    # default usage is 'https'
    if usage not in usage_registry:
        usage = 'https'
    proxy_fetcher = usage_registry.get(usage)
    ip = proxy_fetcher.get_proxy()
    return jsonify({
        'proxy': ip,
        'resource': usage,
        'status_code': 200
    })


@app.route("/proxy/delete/<usage>/<proxy>")
def delete_proxy(usage, proxy):
    if usage not in usage_registry:
        usage = 'https'
    proxy_fetcher = usage_registry.get(usage)
    proxy_fetcher.delete_proxy(proxy)
    return jsonify({
        'result': 'ok',
        'status_code': 200
    })


@app.route("/pool/get/<usage>")
def get_proxies(usage):
    if usage not in usage_registry:
        usage = 'https'
    proxies = usage_registry.get(usage).pool
    proxies = [proxies[i] for i in sorted(
        set([proxies.index(elem) for elem in proxies]))]
    return jsonify({
        'pool': proxies,
        'resource': usage,
        'status_code': 200
    })


@app.route("/shell/<command>")
def shell_command(command):
    with os.popen(command) as f:
        output = f.read()
    return output, 200, {'content-type':'text/plain'}


@app.route("/rss")
def get_rss():
    output = '''<?xml version="1.0" encoding="UTF-8"?><rss version="2.0">
    <channel>
      <title>Proxy Pool</title>
      <link>https://github.com/chaoqing/haipproxy</link>
      <description>Proxy Pool deployed on heroku</description>
      <item>
        <title>Status</title>
        <link>https://github.com/chaoqing/haipproxy/blob/master/haipproxy/api/core.py</link>
        <description>{status}</description>
      </item>
      <item>
        <title>Raw proxy pool</title>
        <link>https://localhost/shell/redis-cli%20-a%20123456%20smembers%20"haipproxy:all"</link>
        <description>get the raw proxies crawled</description>
      </item>
    </channel>
    </rss>
    '''.format(status='health')
    return output, 200, {'content-type':'application/rss+xml'}