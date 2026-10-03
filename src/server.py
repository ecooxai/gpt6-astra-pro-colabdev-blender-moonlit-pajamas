#!/usr/bin/env python3
"""Serve only public preview files. No project secrets or parent directories."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[1]/'preview'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        if self.path.split('?')[0].endswith(('.json','.html','.js','.css')): self.send_header('Cache-Control','no-store')
        super().end_headers()
if __name__=='__main__': ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','8791'))),Handler).serve_forever()
