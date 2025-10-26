# import os
# from account_mgr import app, init_db


# if __name__ == "__main__":
#     init_db()
#     app.run(debug=True)

# if __name__ == "__main__":
#     if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
#         init_db()
#     app.run(debug=True)

import os
from account_mgr import app, init_db


if __name__ == "__main__":
    # Only run migrations & seeding automatically on Render
    if os.getenv("RENDER", "0") == "1":
        init_db()
    app.run(debug=os.getenv("FLASK_ENV") != "production")
