import numpy as np
from sklearn.ensemble import RandomForestRegressor
from aiohttp import web
import socketio
import pickle
import os

if (not os.path.exists('markDataNature.sav') or not os.path.exists('markDataSocial.sav')):
    os.system('python3 markPrediction.py')

markNatureModel = pickle.load(open('markDataNature.sav', 'rb'))
markSocialModel = pickle.load(open('markDataSocial.sav', 'rb'))

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
    with open('webMainPage.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.on('calMark', namespace='/home')
async def calMark(sid, markSubmit):
    if (markSubmit[0] == 'nature'):
        markSubmit = np.array(markSubmit[1:]).reshape(1, -1)
        markPrediction = markNatureModel.predict(markSubmit)
    elif (markSubmit[0] == 'social'):
        markSubmit = np.array(markSubmit[1:]).reshape(1, -1)
        markPrediction = markSocialModel.predict(markSubmit)
    else:
        markPrediction = [0]*len(subjects)
    markPrediction = np.round(markPrediction, 1).tolist()
    await sio.emit('markPrediction', {'data': '%s' % (','.join(str(x) for x in markPrediction))}, room = sid, namespace = '/home')

@sio.on('disconnect', namespace='/home')
def test_disconnect(sid):
    print('Client disconnected')

app.router.add_static('/static', 'static')
app.router.add_get('/', mainPage)

#http://0.0.0.0:8080/result?subCom=nature&math0=0&math1=0&math2=0&literature0=0&literature1=0&literature2=0&english0=0&english1=0&english2=0&physics0=0&physics1=0&physics2=0&chemistry0=0&chemistry1=0&chemistry2=0&biology0=0&biology1=0&biology2=0&history0=0&history1=0&history2=0&geography0=0&geography1=0&geography2=0&civiceducation0=0&civiceducation1=0&civiceducation2=0
sio.start_background_task(timeElapsed)
web.run_app(app)
