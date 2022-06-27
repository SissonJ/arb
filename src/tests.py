import unittest
from BotInfo import BotInfo
from env import mkSeed2, endpoint
from config import chain_id
from utils import calculate_gain_loss, rebalance

class TestGainLoss(unittest.TestCase):
    
    test_config: None
    controller: BotInfo

    def setUp(self):
        self.test_config = {
            "mkSeed": mkSeed2,
            "pairAddrs": {
                "pair1": "secret1wwt7nh3zyzessk8c5d98lpfsw79vzpsnerj6d0",
                "pair2": "secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5",
            },
            "pairQueries": {
                "pair1": "",
                "pair2": "",
            },
            "token1First": {
                "pair1": True,
                "pair2": True,
            },
            "tokenAddrs": {
                "token1": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek",
                "token2": "secret1qfql357amn448duf5gvp9gr48sxx9tsnhupu3d",
            },
            "tokenKeys": {
                "token1": "",
                "token2": "",
            },
            "tokenDecimals":{
                "token1": 6,
                "token2": 6,
            },
            "clientInfo": {
                "endpoint": endpoint,
                "chainID": chain_id,
            },
            "logLocation": "./../logs/test-log.csv",
            "centralLogLoc": "./../logs/test-central.csv",
            "outputLogLoc": "./../logs/test-ouput.log",
            "fee": {
                "gas": 200001,
                "price": "050001uscrt",
            },
        }
        self.controller = BotInfo(self.test_config)
        self.controller.inv = [[4, 100]]
        self.controller.total = [100, 10, 3]

    def test_1(self):
        gain = calculate_gain_loss(self.controller, 9.9, 101, 4.5, 60)
        self.assertEqual(self.controller.inv, [[4, 40], [4.5, 61]], "controller inv test 1")
        self.assertEqual(self.controller.total, [101,9.9,3], "controller total test 1")
        self.assertEqual(gain, (61*4.5-60*4)-.3, "gain test 1")
        gain = calculate_gain_loss(self.controller, 9.8, 102, 4.2, 101)
        self.assertEqual(self.controller.inv, [[4.2, 102]], "controller inv test 2")
        self.assertEqual(self.controller.total, [102,9.8,3], "controller total test 2")
        self.assertAlmostEqual(gain, (102*4.2-61*4.5-40*4)-.3)
        gain = calculate_gain_loss(self.controller, 9.7, 102, 4.3, 50)
        self.assertEqual(self.controller.inv, [[4.2, 102]])
        self.assertEqual(self.controller.total, [102,9.7,3], "controller total test 2")
        self.assertAlmostEqual(gain, -.3)
        gain = calculate_gain_loss(self.controller, 9.6, 103, 4.5, 40)
        self.assertEqual(self.controller.inv, [[4.2, 62],[4.5, 41]])
        self.assertEqual(self.controller.total, [103,9.6,3], "controller total test 2")
        self.assertAlmostEqual(gain, (41*4.5 - 40*4.2) - .3)
        gain = calculate_gain_loss(self.controller, 9.5, 104, 4.6, 40)
        self.assertEqual(self.controller.inv, [[4.2, 62],[4.5, 1],[4.6, 41]])
        self.assertEqual(self.controller.total, [104,9.5,3], "controller total test 2")
        self.assertAlmostEqual(gain, (41*4.6 - 40*4.5) - .3)
        gain = calculate_gain_loss(self.controller, 9.4, 105, 4.7, 104)
        self.assertEqual(self.controller.inv, [[4.7, 105]])
        self.assertEqual(self.controller.total, [105,9.4,3], "controller total test 2")
        self.assertAlmostEqual(gain, (105*4.7 -62*4.2-41*4.6- 1*4.5) - .3)

    def test_rebalance(self):
        self.controller.inv = [[4.2, 10],[4.3,40],[4.4, 100]]
        self.controller.total = [160, 10, 3]
        rebalance(self.controller)
        self.assertEqual(self.controller.inv, [[4.2, 10],[4.3,40],[4.4, 110]])
        self.controller.total = [150, 10, 3]
        rebalance(self.controller)
        self.assertEqual(self.controller.inv, [[4.2, 10],[4.3,40],[4.4, 100]])
        self.controller.total = [1500, 10, 3]
        rebalance(self.controller)
        self.assertEqual(self.controller.inv, [[4.2, 10],[4.3,40],[4.4, 1450]])
        self.controller.total = [40, 10, 3]
        rebalance(self.controller)
        self.assertEqual(self.controller.inv, [[4.2, 10],[4.3,30]])
        self.controller.total = [6, 10, 3]
        rebalance(self.controller)
        self.assertEqual(self.controller.inv, [[4.2, 6]])
        

if __name__ == '__main__':
    unittest.main()