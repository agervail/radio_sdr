from scipy.io import wavfile

def get_data(filename):
    k = wavfile.read('../output.wav')[1]
    message_max_size = 200000
    threshold = 150

    start = 0
    for val in k:
      if val > threshold:
        print(start)
        break
      start += 1

    return k[start - 20:start - 20 + message_max_size]

def round_data(data):
    minV = 128
    maxV = 153
    middle = minV + (maxV - minV) / 2
    return [minV if x < middle else maxV for x in data]
