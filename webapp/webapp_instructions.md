1. Clone the repository (optional)
2. Install the dependencies using the requirements file with the following command
   1.  pip install -r requirements.txt
3. In the root directory create a models folder. This will house the random forest model.
   1. To download the model run the following command from inside the models folder
   2. wget https://www.github.com/Jmete/youtube-dislikes/raw/main/models/rfclf.joblib.pkl
4. From the root folder, run the following command to create the database (default sqlite3)
   1. python manage.py makemigrations
   2. python manage.py migrate
5. to start the server, run the following command from the root folder
   1. python manage.py runserver
6. You can view the webapp at 127.0.0.1:8000 in your browser