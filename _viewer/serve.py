#!/usr/bin/env python3
"""Tiny static server for the asset gallery (chdir first so a dead spawn-cwd
doesn't break os.getcwd). Usage: python3 _viewer/serve.py [port]"""
import os, sys, functools, http.server, socketserver

os.chdir("/Users/ihsanduru/Documents/assets")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
Handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                            directory="/Users/ihsanduru/Documents/assets")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"serving assets on http://127.0.0.1:{PORT}/")
    httpd.serve_forever()
