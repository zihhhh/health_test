# Flask KitchenSink

Sample bot using [Flask](http://flask.pocoo.org/)



## Clone the repository

```
$ git clone https://github.com/NTHU-SELAB/health-checker-python.git
$ cd health-checker-python
```


## Deploy your changes
```
$ git add .
$ git commit -am '[discription]'
$ git push
```
push後需耐心等待一段時間，請至heroku確認部屬成功後再繼續你的動作


## Automatic deploys
從 heroku 的 Manual deploy 改 Automatic deploys
```
$ git remote add origin https://github.com/NTHU-SELAB/health-checker-python.git
$ git branch -M main
$ git push -u origin main
```
```
$ git add .
$ git commit -am '[discription]'
$ git push origin main
```

## Getting started

```
$ export LINE_CHANNEL_SECRET=YOUR_LINE_CHANNEL_SECRET
$ export LINE_CHANNEL_ACCESS_TOKEN=YOUR_LINE_CHANNEL_ACCESS_TOKEN

$ pip install -r requirements.txt

$ python app.py
```


## Unit Test

`python unittest_main.py`