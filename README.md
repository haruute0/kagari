# kagari
Just a random bot made by an eccentric college student.

## What can it do?
1. Show us today and tomorrow course schedule accros 3 class.
2. Thats all. :(

## Next?
Nothing

## Local Deployment

1. Please make sure you have `ngrok` installed locally. We need this for tunneling https network for line bot webhook.
2. `pip3 install -r requirements.txt`
3. `python3 app.py`
4. Open new terminal/tab
5. `./ngrok http 5000`
6. Copy `ngrok` https link and paste into webhook field in [https://developers.line.me/](https://developers.line.me/)