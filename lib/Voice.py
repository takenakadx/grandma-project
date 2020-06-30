import threading
import subprocess

class Say (threading.Thread):
    def __init__(self,queues,fevent,settings):
        self.queues = queues
        self.settings = settings
        self.fevent = fevent
        threading.Thread.__init__(self)

    def saySometing(self,detail):
        text = ""
        is_insert = True
        for i in detail:
            if(i == '('):
                is_insert = False
                continue
            elif(i == ')'):
                is_insert = True
                continue
            text += i if is_insert else ""
        cmd = "./jsay.sh \"{}\"".format(text)
        c = subprocess.Popen(cmd,stdin=subprocess.PIPE,shell=True)
        c.wait()

    def run(self):
        print("say thread started")
        while not self.fevent.wait(timeout=0.01):
            self.saySometing(self.queues["voice"].get())

if __name__ == "__main__":
    say = Say(None,None,None)
    say.saySometing("こんにちは")