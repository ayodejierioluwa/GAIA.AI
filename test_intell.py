import os, sys
from flask import Flask
from gaia.app import create_app
app = create_app()
with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = "TestAdmin"
    res = c.get('/intelligence-suite')
    print("Status:", res.status_code)
    html = res.data.decode('utf-8')
    print("HTML length:", len(html))
    print("Loader style in HTML?", "loader" in html)
