from scipy.io import wavfile
import matplotlib.pyplot as plt

k = wavfile.read('prout2.wav')
mess = k[1][100000:200000]
threshold = 200

rising = []
for i,b in enumerate(mess[1:]):
  if mess[i] < threshold and b >= threshold:
    #print(i)
    rising.append(i)

oh = [x - rising[i - 1] for i, x in enumerate(rising[:18])][1:]

moy = sum(oh) / float(len(oh))
half = round(moy/2)
offset = int(half / 2)

print(oh)
print(moy)
print(round(moy))

pic = [128] * len(mess)
poi = []
for i in range(180):
  pic[rising[0] + offset + i * half] = 250
  poi.append(rising[0] + offset + i * half)

plt.plot(mess)
plt.plot(pic)
plt.show()

decoded = []
for i in poi:
  if mess[i] > threshold:
    decoded.append(1)
  else:
    decoded.append(0)

print(decoded)
