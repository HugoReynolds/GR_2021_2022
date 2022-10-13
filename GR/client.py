# Código baseado em https://docs.python.org/3.6/library/asyncio-stream.html#tcp-echo-client-using-streams
import asyncio
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hmac

conn_port = 1234
max_msg_size = 9999


P = 99494096650139337106186933977618513974146274831566768179581759037259788798151499814653951492724365471316253651463342255785311748602922458795201382445323499931625451272600173180136123245441204133515800495917242011863558721723303661523372572477211620144038809673692512025566673746993593384600667047373692203583
G = 44157404837960328768872680677686802650999163226766694797650810379076416463147265401084491113667624054557335394761604876882446924929840681990106974314935015501571333024773172440352475358750668213444607353872754650805031912866692119819377041901642732455911509867728218394542745330014071040326856846990119719675


class Client:
    """ Classe que implementa a funcionalidade de um CLIENTE. """
    def __init__(self, sckt=None):
        """ Construtor da classe. """
        self.sckt = sckt
        self.msg_cnt = 0

    def process(self, msg=b""):
        """ Processa uma mensagem (`bytestring`) enviada pelo SERVIDOR.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        self.msg_cnt +=1

        if(self.msg_cnt == 1):
            print("MSG 1")
            self.pn = dh.DHParameterNumbers(P, G)
            parameters = self.pn.parameters(default_backend())
            private_key = parameters.generate_private_key()
            self.public_key_client=private_key.public_key().public_numbers().y
            self.private_key=private_key

            new_msg=str(self.public_key_client).encode()
            
            return new_msg if len(new_msg) > 0 else None

        if(self.msg_cnt == 2): 
            print("MSG 2")
            public_key_server = int(msg.decode())
            peer_public_numbers = dh.DHPublicNumbers(public_key_server,self.pn) 
            peer_key = peer_public_numbers.public_key(default_backend())           

            self.shared_key = self.private_key.exchange(peer_key)
            
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'grupo 02 cripto',
                backend=default_backend()
              ).derive(self.shared_key) 
            
            self.derived_key=derived_key
            self.key1=self.derived_key[0:16]
            self.key_mac=self.derived_key[16:32]
            print('Input message to send (quit to finish)')
            new_msg = input().encode()
            if(new_msg.decode() == 'quit'):
                return new_msg if len(new_msg)>0 else None
            aesgcm = AESGCM(self.key1)
            nonce = os.urandom(12)
            encryptMessage = aesgcm.encrypt(nonce, new_msg, None)
            h=hmac.HMAC(self.key_mac,hashes.SHA256(),backend=default_backend())
            h.update(encryptMessage)
            mac_sig = h.finalize()
           
            new_msg=nonce+mac_sig+encryptMessage 
            return new_msg if len(new_msg)>0 else None
        
        else:
            aesgcm = AESGCM(self.key1)
            nonce = msg[0:12]
            mac_server = msg[12:44]
            msg = msg[44:len(msg)]  
            decryptMessage = aesgcm.decrypt(nonce, msg, None)

            txt = decryptMessage.decode()
            print('%r' % (txt))

            h=hmac.HMAC(self.key_mac,hashes.SHA256(),backend=default_backend())
            h.update(msg)
            mac_sig = h.finalize() 
           
            if(mac_server == mac_sig):
               print('Input message to send (quit to finish)')
               new_msg = input().encode()
               if(new_msg.decode() == 'quit'):
                   return new_msg if len(new_msg)>0 else None
               aesgcm = AESGCM(self.key1)
               nonce = os.urandom(12)
               encryptMessage = aesgcm.encrypt(nonce, new_msg, None)
               h=hmac.HMAC(self.key_mac,hashes.SHA256(),backend=default_backend())
               h.update(encryptMessage)
               mac_sig = h.finalize()

               encryptMessage = nonce+mac_sig+encryptMessage
           
               return encryptMessage if len(encryptMessage)>0 else None
            else:
                print("Erro na verificação da palavra-passe")


async def tcp_echo_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', conn_port)
    addr = writer.get_extra_info('peername')
    client = Client(addr)
    msg = client.process()
    while msg:
        writer.write(msg)
        msg = await reader.read(max_msg_size)
        if msg :
            msg = client.process(msg)
        else:
            break
    writer.write(b'\n')
    print('Socket closed!')
    writer.close()

def run_client():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client())

run_client()