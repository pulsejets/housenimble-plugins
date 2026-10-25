"""Public USB protocol client. No private checkout, firmware or credentials required."""
import base64
import hashlib
import json
import time

PREFIX=b'@HN1 '
MAX_PACKAGE=147456

class DeviceError(RuntimeError):
    pass

class Device:
    def __init__(self, stream, timeout=5):
        self.stream=stream
        self.timeout=timeout
        self.sequence=0
        self.token=None

    def request(self, op, **fields):
        self.sequence+=1
        message={'id':self.sequence,'op':op,**fields}
        if self.token:
            message['token']=self.token
        payload=PREFIX+json.dumps(message,separators=(',',':')).encode('utf-8')+b'\n'
        if len(payload)>1800:
            raise DeviceError('USB request too large')
        try:
            written=self.stream.write(payload)
            if written!=len(payload):
                raise DeviceError('Incomplete USB write')
            deadline=time.monotonic()+self.timeout
            while time.monotonic()<deadline:
                line=self.stream.read_until(b'\n',2049)
                if len(line)>2048:
                    continue
                start=line.find(PREFIX)
                if start<0:
                    continue
                try:
                    response=json.loads(line[start+len(PREFIX):])
                except (ValueError,UnicodeError):
                    continue
                if not isinstance(response,dict) or type(response.get('id')) is not int or response['id']!=self.sequence:
                    continue
                if response.get('ok') is not True:
                    # Only bounded protocol error labels; never echo request/token.
                    detail=str(response.get('error','unknown'))[:160]
                    if self.token:
                        detail=detail.replace(self.token,'[redacted]')
                    raise DeviceError('Device rejected operation: '+detail)
                return response
        except OSError as error:
            raise DeviceError('USB connection failed') from error
        raise DeviceError('USB timeout: check cable, port and development-core installation')

    def hello(self):
        status=self.request('hello')
        if status.get('protocol')!=1 or status.get('coreApi')!=1 or status.get('development') is not True:
            raise DeviceError('Device does not offer development protocol/API 1')
        return status

    def pair(self, pin):
        if not isinstance(pin,str) or len(pin)!=6 or not pin.isascii() or not pin.isdigit():
            raise DeviceError('Enter the six digits shown on the device')
        result=self.request('pair',pin=pin)
        token=result.get('token','')
        if len(token)!=64 or any(c not in '0123456789abcdef' for c in token):
            raise DeviceError('Invalid pairing response')
        self.token=token
        return {k:v for k,v in result.items() if k!='token'}

    def upload(self, package):
        if self.token is None:
            raise DeviceError('Pair with the device first')
        if not 22<=len(package)<=MAX_PACKAGE:
            raise DeviceError('Package exceeds development transport limit')
        self.request('begin',size=len(package),sha256=hashlib.sha256(package).hexdigest(),isolated=True)
        for offset in range(0,len(package),768):
            chunk=package[offset:offset+768]
            result=self.request('chunk',offset=offset,data=base64.b64encode(chunk).decode('ascii'))
            if result.get('received')!=offset+len(chunk):
                raise DeviceError('Unexpected upload acknowledgement')
        return self.request('commit')

    def status(self):
        return self.request('status')

    def stop(self):
        return self.request('stop')


def open_serial(port):
    try:
        import serial
    except ImportError as error:
        raise DeviceError('Install USB dependency: python3 -m pip install -r _tools/requirements.txt') from error
    try:
        connection=serial.Serial(port=None,baudrate=115200,timeout=0.1,write_timeout=1,exclusive=True)
        # Opening the console must not intentionally reset the board.
        connection.dtr=False
        connection.rts=False
        connection.port=port
        connection.open()
        return connection
    except (serial.SerialException,OSError) as error:
        raise DeviceError('Cannot open USB port; close other serial monitors and check --port') from error
