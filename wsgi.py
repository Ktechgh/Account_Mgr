# import os
from account_mgr import app, init_db

init_db()
if __name__ == "__main__":
    
    app.run(debug=True)

# if __name__ == "__main__":
#     if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
#         init_db()
#     app.run(debug=True)
