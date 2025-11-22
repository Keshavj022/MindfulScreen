import os
import sys
from app import create_app, db
from app.utils.demo_data import initialize_demo_data

app = create_app()

# Initialize database and demo data on startup
with app.app_context():
    db.create_all()

    # Auto-initialize demo data for production
    if os.environ.get('INIT_DEMO_DATA', 'false').lower() == 'true':
        print('Initializing demo data...')
        if initialize_demo_data():
            print('Demo data created successfully!')
        else:
            print('Failed to create demo data.')

if __name__ == '__main__':
    # Command line demo data initialization
    if '--init-demo' in sys.argv:
        with app.app_context():
            print('Initializing demo data...')
            if initialize_demo_data():
                print('Demo data created successfully!')
            else:
                print('Failed to create demo data.')

    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    app.run(debug=debug, host='0.0.0.0', port=port)
