import numpy as np
from sklearn.ensemble import RandomForestRegressor
from aiohttp import web
import socketio
import pickle
import json
import os

if (not os.path.exists('markDataNature.sav') or not os.path.exists('markDataSocial.sav') or not os.path.exists('meanMark.json')):
    os.system('python3 markPrediction.py')

markNatureModel = pickle.load(open('markDataNature.sav', 'rb'))
markSocialModel = pickle.load(open('markDataSocial.sav', 'rb'))
with open('meanMark.json', encoding='utf8') as json_file:
    meanMark = json.load(json_file)
sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)
subjects = ['math', 'literature', 'english', 'physics', 'chemistry', 'biology', 'history', 'geography', 'civiceducation']

@sio.on('timeElapsed', namespace='/home')
async def timeElapsed():
    """Example of how to send server generated events to clients."""
    second = 0
    minute = 0
    hour = 0
    while True:
        await sio.sleep(1)
        second += 1
        if second == 60:
            second = 0
            minute += 1
            if minute == 60:
                minute = 0
                hour += 1
        await sio.emit('timeElapsed', {'data': '%s : %s : %s' % (hour, minute, second)}, namespace='/home')

async def mainPage(request):
    with open('webMainPage.html', encoding='utf8') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.on('debug', namespace='/home')
async def debug(sid, data):
    print(data)

@sio.on('calMark', namespace='/home')
async def calMark(sid, markSubmit):
    markSubmit = np.array(markSubmit).reshape(1, -1)
    markPrediction = {}
    markDiff = {}

    markPrediction['nature'] = markNatureModel.predict(markSubmit)
    markDiff['nature'] = np.sum(markPrediction['nature'] - meanMark['nature'])

    markPrediction['social'] = markSocialModel.predict(markSubmit)
    markDiff['social'] = np.sum(markPrediction['social'] - meanMark['social'])

    markPrediction['nature'] = (np.round(markPrediction['nature']*4)/4).tolist()
    markPrediction['social'] = (np.round(markPrediction['social']*4)/4).tolist()
    # print(markPrediction)
    await sio.emit('markPrediction', {'data': markPrediction, 'meanMark': meanMark}, room = sid, namespace = '/home')

    markDiff['max'] = max(markDiff['nature'], markDiff['social'])

    if (markDiff['max'] >= 0 and markDiff['max'] < 5):
        await sio.emit('passOrFail', {'data': "Bạn có khả năng đậu Đại học!"}, room=sid, namespace='/home')
    elif (markDiff['max'] >= 5 and markDiff['max'] < 10):
        await sio.emit('passOrFail', {'data': "Bạn có khả năng CAO đậu Đại học!"}, room=sid, namespace='/home')
    elif (markDiff['max'] >= 10):
        await sio.emit('passOrFail', {'data': "Bạn chắc chắn đậu Đại học!"}, room=sid, namespace='/home')
    elif (markDiff['max'] >= -5 and markDiff['max'] < 0):
        await sio.emit('passOrFail', {'data': "Bạn có nguy cơ không đậu Đại học!"}, room=sid, namespace='/home')
    elif (markDiff['max'] < -5):
        await sio.emit('passOrFail', {'data': "Bạn có nguy cơ CAO không đậu Đại học!"}, room=sid, namespace='/home')

@sio.on('disconnect', namespace='/home')
def test_disconnect(sid):
    print('Client disconnected')

app.router.add_static('/static', 'static')
app.router.add_get('/', mainPage)

sio.start_background_task(timeElapsed)
web.run_app(app)
