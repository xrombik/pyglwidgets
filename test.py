import unittest
import subprocess
import os
import signal
import time
import fcntl


class MyTestCase(unittest.TestCase):

    def test_imports(self):
        import playground
        print (u'\"%s\"\n\"%s\"' % (self, playground))

    def test_screenshot(self):
        pid = subprocess.Popen(
            'python playground.py &',
            shell=True,
            preexec_fn=os.setsid,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        fd = pid.stdout.fileno()
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        time.sleep(5)
        try:
            rc = pid.stdout.read()
            if 'traceback' in rc:
                print(u"%s" % rc)
                self.fail()
        except IOError:
            pass
        os.killpg(pid.pid, signal.SIGTERM)


if __name__ == '__main__':
    unittest.main(failfast=True)
