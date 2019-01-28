from unittest import TestCase

from simplifiedpytrends.request import TrendReq


class TestTrendReq(TestCase):

    def test__get_data(self):
        """Should use same values as in the documentation"""
        pytrend = TrendReq()
        self.assertEqual(pytrend.hl, 'en-US')
        self.assertEqual(pytrend.tz, 360)
        self.assertEqual(pytrend.geo, '')
        self.assertTrue(pytrend.cookies['NID'])

    def test_interest_over_time(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.interest_over_time())
