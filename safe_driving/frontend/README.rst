This is an example of using the `Flask web framework <http://flask.pocoo.org/>`_
along with long-polling (aka `Comet
<https://en.wikipedia.org/wiki/Comet_(programming)>`_, aka reverse AJAX)
techniques to update client state quasi-asynchronously without the benefit of
direct `WebSockets
<https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API>`_ support. The
server-side code runs in Python; the front-end Web page client runs in the
browser (in JavaScript).

This is a "poor man's" form of interactivity. It's suitable if

* refreshes are occasional,
* the delays between updates many seconds long,
* and updates are unidirectional server -> client
  (though bidirectionality can be kludged).

I've successfully used the technique in production apps, but it will become
more-or-less obsolete as soon as quality support for WebSockets becomes simple
and reliable.

As of Summer 2013, WebSockets with Python and Flask became reliable enough.
`flask-ws-example <https://bitbucket.org/jeunice/flask-ws-example>`_
is an updated example that uses WebSockets and Flask.

Even as of mid-2017, Python's multi-threading support remains piecemeal.
Projects like `Jupyter <http://jupyter.org/>`_ show that WebSockets is
fully feasible for sophisticated project teams. It remains slightly outside
the grasp of a single, simple library and set of support modules that works
across both Python 2.7 and Python 3.
