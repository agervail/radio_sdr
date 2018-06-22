from scipy.io import wavfile
import matplotlib.pyplot as plt

k = wavfile.read('prout6.wav')
message_max_size = 80000
threshold = 150

start = 0
for val in k[1]:
  if val > threshold:
    print(start)
    break
  start += 1

mess = k[1][start - 20:start - 20 + message_max_size]

#plt.plot(mess)
#plt.show()



up = 0
down = 0
last = 0
for i,b in enumerate(mess[1:]):
  if mess[i] < threshold and b >= threshold and up == 0:
    #print(i)
    up = i
  elif mess[i] > threshold and b <= threshold:
    if down == 0:
      down = i
    else:
     last = i

print(up, down, last)

#oh = [x - rising[i - 1] for i, x in enumerate(rising[:18])][1:]

#moy = sum(oh) / float(len(oh))
half = round((down - up) / 6) + 2
print(half)
offset = int(half / 2)

pic = [128] * len(mess)
poi = []
#for i in range(20):
#  pic[up + offset + i * half] = 250
#  poi.append(up + offset + i * half)
i = 0
while up + offset + i * half < last:
  pic[up + offset + i * half] = 250
  poi.append(up + offset + i * half)
  i += 1

plt.plot(mess)
plt.plot(pic)
plt.show()

decoded = []
for i in poi:
  if mess[i] > threshold:
    decoded.append(1)
  else:
    decoded.append(0)

print('bool message[] = {', decoded[0], end='')
for val in decoded[1:]:
  print(',', val, end='')

print('};')
print('int message_size = ', len(decoded), ';')
