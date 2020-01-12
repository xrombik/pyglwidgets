import unittest
import subprocess
import os
import signal
import time
import fcntl


class MyTestCase(unittest.TestCase):

    def test_imports(self):
        import main
        print (u'%s\n%s' % (self, main))

    def test_screenshot(self):
        pid = subprocess.Popen(
            'python main.py &',
            shell=True,
            preexec_fn=os.setsid,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        fd = pid.stdout.fileno()
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        time.sleep(2)
        try:
            rc = pid.stdout.read()
            if 'traceback' in rc:
                self.fail()
        except IOError:
            pass
        os.system('./screenshot.sh')
        os.killpg(pid.pid, signal.SIGTERM)


if __name__ == '__main__':
    unittest.main(failfast=True)
