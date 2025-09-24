def heck(message):
    
hecked_message=""
import socket,threading,time
P=5050;H=6000
def h(c,r,names,a):
 code=c.recv(1024).decode().strip()
 name=c.recv(1024).decode().strip()
 if code not in names: names[code]=set()
 if name in names[code]:c.close();return
 names[code].add(name);r.setdefault(code,[]).append(c)
 while 1:
  try:m=c.recv(1024)
  except:break
  if not m:break
  for x in r[code]:
   try:x.sendall(m)
   except:pass
 names[code].remove(name);r[code].remove(c);c.close()
def s(code):
 r={};names={}
 t=threading.Thread(target=lambda:[b.sendto(code.encode(),("<broadcast>",H))or time.sleep(1)for b in[socket.socket(socket.AF_INET,socket.SOCK_DGRAM)]]);t.daemon=1;t.start()
 x=socket.socket();x.bind(("0.0.0.0",P));x.listen()
 while 1:c,a=x.accept();threading.Thread(target=h,args=(c,r,names,a),daemon=1).start()
def c(code,name):
 ip=None;u=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);u.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1);u.bind(("",H))
 def l():nonlocal ip
 while not ip:
  try:d,a=u.recvfrom(1024)
  except:continue
  if d.decode().strip()==code:ip=a[0]
 threading.Thread(target=l,daemon=1).start()
 while not ip:time.sleep(0.1)
 sck=socket.socket();sck.connect((ip,P))
 sck.sendall(code.encode());sck.sendall(name.encode())
 threading.Thread(target=lambda:[print("\n"+m.decode())for m in iter(lambda:sck.recv(1024),b"")],daemon=1).start()
 def send():[sck.sendall(f"{name}: {hecked_message}".encode())for _ in iter(int,1)]
threading.Thread(target=send,daemon=1).start();name=input("Name: ").strip();code=input("Code: ").strip()
try:c(code,name)
except:s(code)
