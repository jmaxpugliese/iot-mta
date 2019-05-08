pos_file = open('acc_164233.txt', 'r')
neg_file = open('acc_115425.txt', 'r')
train_2, temp, res = [], [], []

train_1 = [line.strip().split(' ') for line in neg_file.readlines() if len(line.split(':')) == 1]

for line in pos_file.readlines():
    if len(line.split(' ')) == 1:
        if len(temp) > 5:
            train_2.append(temp[-5:])
        temp = []
    else:
        temp.append(line.strip().split(' '))
"""
for i in range(len(train_2)):
    res.append([str(1)] + [num for l in train_2[i] for num in l if num is not ''])
for i in range(len(train_1) // 5):
    res.append([str(0)] + [num for l in train_1[i * 5: (i + 1) * 5] for num in l if num is not ''])
"""
for i in range(len(train_2)):
    res.append([num for l in train_2[i] for num in l if num is not ''])
for i in range(len(train_1) // 5):
    res.append([num for l in train_1[i * 5: (i + 1) * 5] for num in l if num is not ''])

with open('test.csv', 'w') as file:
    for item in res:
        file.writelines(','.join(item) + '\n')
print('ok')
