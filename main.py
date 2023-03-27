from app import app, db
from app.models import User, Venue, Show, Show_Venue

@app.shell_context_processor
def create_shell_context():
    return {'db':db, 'User':User, 'Venue': Venue, 'Show':Show, 'Show_Venue':Show_Venue}

if __name__ == '__main__':
    app.run(port=5000)