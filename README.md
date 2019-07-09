# quiplash-clone
A simple clone of Jackbox Games' Quiplash using Flask-Socket.IO created for university (Development of modern web applications, HTW Berlin)

Read more about Quiplash and how it works: https://jackboxgames.com/project/quiplash/

To play:
- change the ip address in player_main.js and server_main.js to your own
- run app.py
- (optional) if you want to play this over the Internet and not in your local network, then you need to forward the port 25565 in your router's settings
- set up the main screen by going to <your_ip>:25565/main_screen (user: admin, password: secret) in your browser
- Every player can connect by going to <your_ip>:25565/play in a browser

4-8 players, one round only

Video demo: https://drive.google.com/file/d/1fq-kUA6M5HuR6Kzq6pAzi0ovW9atg4Co/view

This was my first Python application.

Technologies used: Flask with Flask-Socket.IO on Server Side, Vanilla JavaScript on Client side, SQLite3 Database

Most important thing I learned from using Flask-Socket.IO: Don't use Python modules like Time or Thread. They don't work well with network aynchronous processes.
Use their replacements of eventlet or gevent instead. Alternatively use eventlet monkey patching: https://eventlet.net/doc/patching.html
