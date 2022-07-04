import os
import subprocess
import sys

os.environ['ROOT_DIR'] = os.path.dirname(os.path.abspath(__file__))
os.environ['bin'] = os.path.join(os.environ['ROOT_DIR'], 'bin')
sys.path.insert(0, os.environ['ROOT_DIR'])
sys.path.insert(1, os.environ['bin'])

varlist = [
        'In',
        'Out',
        'Desulfating',
        'NG' 
        ]

commands = ['temp']


def script(filename):
    _path = os.environ['bin'] + f'\\{filename}.cmd'
    if filename in commands:
        subprocess.Popen(r'%s' % _path, shell=True)


def main(msg):
    key = msg.split('/')
    value = key[2].split(' ')
    print("Key: " + key)
    print("Value: " + value)
    # if value[0] in commands:
    #     try:
    #         script(value[0])
    #     except:
    #         pass
    #     print(f"Running Command {value[0]}: {value[1]}")
    # if value[0] in varlist:
    #     print(f"{value[0]} set to: {value[1]}")


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except:
        pass
