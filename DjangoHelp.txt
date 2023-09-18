### What and Where ###
- Main Folders
    * webapp/
        - Main app folder
    * FlixGo-HTML-Template/
        - Contains the original templates
- Main Files
    * webapp/admin.py
        - Give dashboard access to our database models
            - import and register the models
    * webapp/models.py
        - Create a database model
    * webapp/services.py
        - Any utilization of any services will be written here, such as API or database
    * webapp/urls.py
        - Define URL names with their corresponding views.py function
    * webapp/views.py
        - Handle incoming variables from services and render them to template HTML
    * webapp/templates/
        - HTML files that will be rendered by views.py


### Django Commands ###
- Run local web server inside folder with manage.py
    python3 manage.py runserver
- Create app inside project (one Django project can have multiple separate apps)
    python3 manage.py startapp app_name


### Convert HTML template to show CSS and JS ###
- add {% load static %} to top of page
- With any folder reference, add {% static folder/ %}
    * <img src="images/logo.png> changes to <img src={% static 'images/logo.png' %}>
    * <link rel="stylesheet" href="css/style.css"> changes to <link rel="stylesheet" href={% static 'css/style.css' %}>
    * <script src="js/script.js"></script> changes to <script src={% static 'js/script.js' %}></script>
- create new folder called 'static' and paste all folders (js, css, images, etc.)
    * Do not put HTML files in static


### After creating database model ###
- Migrate database (similar to git staging)
    python3 manage.py makemigrations
- Apply change
    python3 manage.py migrate


### Admin Dashboard ###
- Access dashboard
    localhost:8000/admin
- Enter user and password
    user: admin
    pass: (ask Mark for the password)
- Give dashboard access to our model databases (in admin.py)
    admin.site.register(ToDoList)
- Create new admin user
    python3 manage.py createsuperuser
