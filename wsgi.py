# from waitress import serve
# from flaskwebgui import FlaskUI
from account_mgr import db, app, flask_db_init
from account_mgr.super_admin.routes import seed_super_admin


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # db.drop_all()
        flask_db_init() 
        seed_super_admin()
    # app.run(host="0.0.0.0", debug=True, port=5000)
    app.run(debug=True)
    # serve(app, host='0.0.0.0', port=5000, threads=100)


# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         flask_db_init()
#         seed_super_admin()
#     FlaskUI(
#         app=app,
#         server="flask",
#         port=5000,
#         # width=800,
#         # height=600,
#         fullscreen=True,
#         profile_dir_prefix="flaskwebgui",
#     ).run()


# source venv/Scripts/activate
# pyinstaller -w -F --add-data "account_mgr;account_mgr" main.py
# Miscellaneous expenses refer to the unpredictable and assorted costs that fall outside your standard business expense categories
