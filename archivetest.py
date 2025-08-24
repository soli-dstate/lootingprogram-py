import os
from datetime import datetime

log_dir = './log'
os.makedirs(log_dir, exist_ok=True)

for i in range(1, 51):
    file_path = os.path.join(log_dir, f'log{i}-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.log')
    with open(file_path, 'w') as f:
        f.write("")