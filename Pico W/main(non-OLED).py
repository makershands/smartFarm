# This code was written by Juhyun Kim.  

from machine import Pin, I2C, ADC
import network
import time
import urequests
import random
import ahtx0

# 이메일, 위도, 경도 표시하기(자신의 스마트팜 위치를 검색해서 넣어주세요.)
nickname = 'mtinet'      # 닉네임 변수를 자신만의 닉네임으로 수정하세요.
lat = 37.49836           # 위도 변수를 자신의 위도 좌표로 수정하세요.
long = 126.9253          # 경도 변수를 자신의 경도 좌표로 수정하세요.
SSID = "U+Net454C"       # 공유기의 SSID를 따옴표 안에 넣으세요.
password = "DDAE014478"  # 공유기의 password를 따옴표 안에 넣으세요.

# RTDB주소
url = "https://smartfarm-f867f-default-rtdb.firebaseio.com/"
mapUrl = "https://smartfarmlocation-default-rtdb.firebaseio.com/"

# 제어할 핀 번호 설정
led = Pin(1, Pin.OUT) # 생장 LED제어 핀
fan = Pin(5, Pin.OUT) # 팬 제어
moisture = ADC(26) # 수분 감지
light = ADC(27) # 조도 감지

# 온도, 습도 센서 설정 
i2cTH = I2C(1, scl=Pin(15), sda=Pin(14), freq=200000) 
sensor = ahtx0.AHT10(i2cTH)

conversion_factor = 3.3 / 65535 # 측정값 보정 계산식


# 와이파이 연결하기
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    # 와이파이 연결하기
    wlan.connect(SSID, password)  # 12, 13번 줄에 입력한 SSID와 password가 입력됨
    print("Waiting for Wi-Fi connection", end="...")
    print()
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
else:
    print(wlan.ifconfig())
    print("WiFi is Connected")
    print()


# 시간정보 가져오기
from timezoneChange import timeOfSeoul
updatedTime = timeOfSeoul()
# print(type(updatedTime))
print(updatedTime)


# RTDB 초기 세팅이 안되어 있는 경우 초기 세팅하기
myobjInitialize = {
    'led': 0,
    'fan': 0
    }
# RTDB 초기 세팅이 안되어 있는 경우 초기 세팅하기
myobjInitializeGather = {
    '-led-': 0,
    '-fan-': 0
    }
# myobjInitialize를 RTDB로 보내 객체 교체하기, patch는 특정 주소의 데이터가 변경됨
urequests.patch(url+"smartFarm.json", json = myobjInitialize).json()
urequests.patch(mapUrl+"/"+nickname+"/"+"smartFarm.json", json = myobjInitializeGather).json()
print("SmartFarm has been initialized.")


# RTDB 위치 정보 초기 세팅하기
myLocation = {
    'lat': lat,
    'long': long
    }

# myLocation를 RTDB로 보내 객체 교체하기, patch는 특정 주소의 데이터가 변경됨
urequests.patch(url+"location.json", json = myLocation).json()
urequests.patch(mapUrl+"/"+nickname+".json", json = myLocation).json()
print("Location Info has been sent.")
print()


# RTDB 내역 가져오기
response = urequests.get(url+".json").json()
# byte형태의 데이터를 json으로 변경했기 때문에 메모리를 닫아주는 일을 하지 않아도 됨
# print(response)
# print(response['smartFarm'])
# print(response['smartFarm']['led'])


while True:
    # 현재 DB의 정보를 가져옴
    response = urequests.get(url+".json").json() # RTDB 데이터 가져오기

    # 현재 센서로부터 측정된 값을 가져옴
    humidityValue = round(sensor.relative_humidity) # 습도센서
    lightValue = round((light.read_u16()/65535) * 100) # 조도센서 값 읽어오기
    temperatureValue = round(sensor.temperature) # 온도센서 
    moistureValue = round((1 - moisture.read_u16()/65535) * 100) # 수분센서 값 읽어오기
    
    # 현재시간 가져오기
    updatedTime = timeOfSeoul()
    # print(type(updatedTime))
    # print(updatedTime)


    # 읽어온 RTDB값과 센서 값 콘솔에 출력하기
    print("Status Check")
    print("updatedTime:", updatedTime, "LED:", response['smartFarm']['led'], "Fan:", response['smartFarm']['fan'], "Humidity:", humidityValue, "Temperature:", temperatureValue, "Light:", lightValue )
    print()


    # 현재 RTDB의 led 키 값의 상태에 따라 LED 핀(1번)을 제어
    if (response['smartFarm']['led'] == 0) :
        led.value(0)
    else :
        led.value(1)

    # 현재 RTDB의 fan 키 값의 상태에 따라 Fan 핀(5번)을 제어
    if (response['smartFarm']['fan'] == 0) :
        fan.value(0)
    else :
        fan.value(1)



    # 실시간으로 확인된 각 객체 값을 딕셔너리에 넣기
    myobj = {
        'updatedTime': updatedTime,
        'humi': humidityValue,
        'light': lightValue, 
        'temp': temperatureValue,
        'mois': moistureValue
        }

    # 실시간으로 확인된 각 객체 값을 딕셔너리에 넣기
    myobjGather = {
        'updatedTime': updatedTime,
        '-fan-': response['smartFarm']['fan'],
        '-led-': response['smartFarm']['led'],
        'humi': humidityValue,
        'light': lightValue,
        'temp': temperatureValue,
        'mois': moistureValue
        }

    # myobj를 RTDB로 보내 객체 값 교체하기, patch는 정해진 키값에 해당하는 데이터가 변경됨, post는 특정주소를 만들고 데이터를 누적시킴
    urequests.patch(url+"smartFarm.json", json = myobj).json()
    urequests.patch(mapUrl+"/"+nickname+"/"+"smartFarm.json", json = myobjGather).json()

    # 교체한 객체값 콘솔에 출력하기
    print("Message Send")
    print(myobj)
    print()
