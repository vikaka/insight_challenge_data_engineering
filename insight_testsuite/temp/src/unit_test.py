import unittest
import datetime


def time_interval(start, end, delta):
        """To generate 60 minute time intervals.

        :param start: start time of log input.
        :param end: end time of log input.
        :param delta: time increments.
        """
        if start == end:
            yield start
        else:
            curr = start
            while curr < end:
                yield curr
                curr += delta

a = datetime.datetime(1995, 7, 19, 13, 32, 1, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))
b = datetime.datetime(1995, 7, 19, 13, 32, 4, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))

X_1 = [datetime.datetime(1995, 7, 19, 13, 32, 1, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000))), datetime.datetime(1995, 7, 19, 13, 32, 2, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000))), datetime.datetime(1995, 7, 19, 13, 32, 3, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))]
X_2 = [datetime.datetime(1995, 7, 19, 13, 32, 1, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))]


class Feature1Test1(unittest.TestCase):

    def test_valid(self):
        self.assertEqual([i for i in time_interval(a, b, datetime.timedelta(seconds=1))], X_1)
        self.assertEqual([i for i in time_interval(a, a, datetime.timedelta(seconds=1))], X_2)

    def test_invalid(self):
        self.assertFalse([i for i in time_interval(b, a, datetime.timedelta(seconds=1))], X_1)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
