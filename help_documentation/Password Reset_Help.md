Password Reset Documentation
Overview
The pwreset.html helps create the password reset html page. So far, the button is not correctly showing. It's being overridden by the standard button style for whatever reason. It's been decided that the button should be similar to the "sign in" button in the top right corner, which is why the password reset button style was copied from the sign in button style. This can be seen at the bottom of main.css. Once clicked, it needs to give a confirmation message that the username's associated email has been emailed with a one-time password reset link. Not really anything has been done with the actual reset password process. However, Django appears to have one built-in, so it should be able to be imported. This documentation can be found at https://docs.djangoproject.com/en/4.2/topics/auth/default/#module-django.contrib.auth.views . This stack overflow page might also be useful, which is where the django documentation was found (https://stackoverflow.com/questions/32604481/django-customize-reset-password-form).




Usage
To use Password Reset.py:
    -



FAQ


Version information
    - Version 1.0 (current version):  Describe main features and functions.

    - Version 0.0 (10/03/2023): All old versions with their date of last modification.