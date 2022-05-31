def create_my_database():
    import os
    from reminder import db, get_app
    from . import models

    if not os.path.exists('db.sqlite'):
        db.create_all(app=get_app())
