## Profile Pictures Documentation

# Usage
To add a profile picture to the selection:
- Crop the image with https://crop-circle.imageonline.co/
- Add the picture to static/img/profile_pics/
- In the UserProfile model of models.py, add the picture filename and description to PROFILE_PICS_CHOICES tuples.
- Verify that the profile picture exists as an option in the model and that it looks appropriate.