from flask import Flask, request, jsonify
import requests
import json
app = Flask(__name__)

api_key=''
url='http://175.197.63.177:8000/local/api/'

rooms={}

def run(t, method, h, j, p):
    headers={'x-api-key':api_key}
    headers.update(h)
    #print(url+t)
    if method=='get': r=requests.get(url+t, headers=headers, params=p, timeout=10)
    elif method=='post': r=requests.get(url+t, headers=headers, json=j, timeout=10)
    elif method=='put': r=requests.put(url+t, headers=headers, json=j, timeout=10)
    return r

def f1():
    global rooms
    print('1. 사용가능한 모든 디바이스 찾기')
    r=run('devices', 'get', h={}, j={}, p={})
    print(r.status_code)
    devices1=r.json()
    print(f'got {len(devices1)} devices','\n')

    services1={}
    state1={}
    for d in devices1:
        l,e=d['location'],d['entity']
        if l not in rooms: rooms[l]={}
        if e not in rooms[l]: rooms[l][e]={'state':''}

    print(rooms)
    return rooms

def f2():
    global rooms    # rooms= {l:[e,e,e], l[e,e]..}
    for l in rooms:
        for e in rooms[l]:
            r=run(f"states/{e}", 'get', h={}, j={}, p={})
            print(r.status_code)
            state1=r.json()
            rooms[l][e]=state1['state']
    return rooms

def f3(onoff):
    global rooms    # rooms= {l:[e,e,e], l[e,e]..}
    for l in rooms:
        for e in rooms[l]:
            data={
                "domain": "light",
                "service" : "turn_on" if onoff=='on' else "turn_off",
                "rgb_color" : [255,255,255]
            }
            if 'light' in e or 'switch' in e:
                r=run(f"devices/{e}/cmd", 'post', h={}, j=data, p={})
                print(r.status_code)
    return rooms

def f4():
    global rooms    # rooms= {l:[e,e,e], l[e,e]..}
    for l in rooms:
        for e in rooms[l]:
            if 'sensor' in e:
                data={
                    "id": e,
                    "alias": e+str(i),
                    "trigger": {
                      "state": "off",  # 센서(온도,습도,재실,문열림,조도) 사용을 위한  가이드 및 예시 필요.
                      "entity_id": e
                    },
                    "condition": [
                      {
                        "entity_id": e,
                        "state": "off",
                        "option": "equal"
                      }
                    ],
                    "action": {
                      "url": 'http://20.39.195.245:8000/api/notify'
                      #  curl -H "Content-Type: application/json" --data '{"a":"b"}' http://20.39.195.245:8000/api/notify ==> {"result":"ok"}
                    }
                }
                r=run(f"rules", 'post', h={}, j=data, p={})
                print(r.status_code)
    return rooms



@app.route('/api/<path:path>', methods=['GET', 'POST'])
def _api(path):

    if request.method == 'GET' and path=='search':
        return f1()

    if request.method == 'GET' and path=='status':
        if not rooms: f1()
        return f2()

    if request.method == 'GET' and path=='on':
        f3('on')
        return f2()

    if request.method == 'GET' and path=='off':
        f3('off')
        return f2()

    if request.method == 'GET' and path=='notify':
        f4()
        return f2()


    return jsonify({'result':'ok'})

@app.route('/home', methods=['GET'])
def _home():
    s='''
        <h3>효돌 Matter API Test Drive</h3>
        warning: 사람을 위한 기능이 아니라 효돌이 부를 API이며 JSON으로 리턴합니다.
        <p>

        <li><a href=http://20.39.195.245:8000/api/search>룸별 디바이스 서치</a>
        <li><a href=http://20.39.195.245:8000/api/status>룸별 디바이스 상태</a>
        <li><a href=http://20.39.195.245:8000/api/on>모든 라이트/스위치 온</a>
        <li><a href=http://20.39.195.245:8000/api/off>모든 라이트/스위치 오프</a>
        <li><a href=http://20.39.195.245:8000/api/notify>센서들에 대한 Notify조건 지정 (미완성)</a>
    '''
    return s
