# kagari
Just a random bot made by an eccentric college student.

## What can it do?
1. Show us today and tomorrow course schedule accros 3 class.
2. Thats all. :(

## Next?
Nothing

## Local Deployment

### Requirements
1. ngrok
2. pip
3. python3
4. virtualenv

### Development process
1. Please make sure you have `ngrok` installed locally. We need this for tunneling https network for line bot webhook.
2. `pip install virtualenv`
3. `virtualenv env`
4. `cp .env.example .env` Fill your env variables here. `.env` includes in `.gitignore` this file will be ignored when doing `git add`.
5. `source .\env\Scripts\activate`
6. `pip install -r requirements.txt`
7. `python app.py`
8. Open new terminal/tab
9. `./ngrok http 5000`
10. Copy `ngrok` https link and paste into webhook field in [https://developers.line.me/](https://developers.line.me/)
11. Bot has been setup, the development process could continued.