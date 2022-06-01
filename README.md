# TV Series Reminder (a Flask-based web app)

This is an app, which sends an email reminder to its users every time there is a new episode of their chosen TV Series.
It is based on free [TMDB API](https://developers.themoviedb.org/3/getting-started/introduction).

Any feedback or advise would be really appreciated — I am on my way on becoming a Python developer, so I'd really love to learn from experienced colleagues everything I can.

## Demo
Feel free to try out the app — go to https://tv-series-reminder.herokuapp.com/

![TV Series Reminder](https://i.ibb.co/6vyJFcW/image.png)

## How to run it locally
To run this app locally, stick to the following guide:

0. Clone the project from Github using whenever method you prefer. For example, if you're using PyCharm, here's a [guide on how to do this](https://www.jetbrains.com/help/pycharm/set-up-a-git-repository.html#clone-repo).
1. Create a virtual environment, for example using Virtualenv.
Type the following command to your terminal:
```bash
    virtualenv venv             
```
2. Activate the virtual environment:
```bash
    venv/scripts/activate              
```
3. Install the dependencies from the requirements.txt:
```bash
    pip install -r requirements.txt              
```
4. Set the environmental variables in your venv terminal:

Windows:
```bash
    $env:FLASK_ENV="development"
    $env:DATABASE_URL="sqlite:///db.sqlite"
    $env:SECRET_KEY="your_key"
    $env:API_KEY="your_api_key"
    $env:MAIL_SERVER="your_server"
    $env:MAIL_USERNAME ="your_email"
    $env:MAIL_PASSWORD ="your_password"
    $env:MAIL_PORT="465"
```
Linux / Mac:
```bash
    export FLASK_ENV="development"
    export DATABASE_URL="sqlite:///db.sqlite"
    export SECRET_KEY="your_key"
    export API_KEY="your_api_key"
    export MAIL_SERVER="your_server"
    export MAIL_USERNAME ="your_email"
    export MAIL_PASSWORD ="your_password"
    export MAIL_PORT="465"
```
Make sure to get a relevant API key from [TMDB](https://developers.themoviedb.org/3/getting-started/introduction).
Also, edit the values of email-related variables in order for your users to get the emails.

4. Create the database by typing the following command to the terminal:
```bash
    flask create_tables
```
5. Run the application:
```bash
    flask run
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
