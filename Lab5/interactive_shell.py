from sklearn import linear_model, svm
from joblib import dump, load
import csv, sys, datetime

midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

# prompt
def prompt():
    print("")
    print("> Available Commands are: ")
    print("1. plan trip")
    print("2. exit")

def main():
    svc_model = load('SVC.joblib')
    lr_model = load('LR.joblib')
    while True:
        prompt()
        print("> select a command : ")
        userIn = sys.stdin.readline().strip()
        if len(userIn) < 1 :
            print("Command not recognized")
        else:
            if userIn == "1":
                print("> Trip from 116th street station to 42nd street station...")
                current_ts = (datetime.datetime.now() - midnight).seconds

                switch = "Switch" if svc_model.predict([[current_ts]])[0] else "not Switch"
                elapsed_time = lr_model.predict([[current_ts]])[0]
                print("> You should {0} and will get Destination after {1}s".format(switch, int(elapsed_time)))
                continue
            else:
                sys.exit()

if __name__ == "__main__":
    main()
