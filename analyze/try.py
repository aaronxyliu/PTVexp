import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
import time


def test():
    for i in range(10):
        time.sleep(1.1)
        logger.leftTimeEstimator(9 - i)

if __name__ == '__main__':
    test()
    logger.close()