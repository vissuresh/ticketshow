from app import app, db
from app.models import User, Venue, Show, Booking

@app.shell_context_processor
def create_shell_context():
    return {'db':db, 'User':User, 'Venue': Venue, 'Show':Show, 'Booking':Booking}

if __name__ == '__main__':
    app.run(port=8080)