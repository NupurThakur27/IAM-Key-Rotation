import sys, os
from util import FILENAME, read_file
def check_users(users):
    if os.path.exists(FILENAME):
        warned_users=read_file(FILENAME)
        with open(FILENAME, 'a') as f:
            for user in users:
                if user not in warned_users:
                    f.write(user)
        f.close()
    else:
        with open(FILENAME, 'w') as f:
            for user in users:
                f.write(user,'\n')
        f.close()

def main():
    check_users(sys.argv[1:])
    for user in read_file(FILENAME):
        print(user)

if __name__ == "__main__" :
    main()