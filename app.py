from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Placeholder for active rooms
active_rooms = {}

@app.route('/')
def index():
    return render_template('index.html', rooms=active_rooms)

@app.route('/create_room', methods=['POST'])
def create_room():
    room_code = request.form['room_code']
    if room_code not in active_rooms:
        active_rooms[room_code] = {'status': 'open'}
    return redirect(url_for('index'))

@app.route('/shutdown_room/<room_code>')
def shutdown_room(room_code):
    if room_code in active_rooms:
        active_rooms[room_code]['status'] = 'closed'
    return redirect(url_for('index'))

@app.route('/open_room/<room_code>')
def open_room(room_code):
    if room_code in active_rooms:
        active_rooms[room_code]['status'] = 'open'
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
