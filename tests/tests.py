import unittest
import unittest.mock
import requests
from metar import metar


class TestGetMetar(unittest.TestCase):

    def setUp(self):
        self.metar = metar.Metar()

    def test_get_metar_return_dict(self):
        r = self.metar.get_metar('EPKK')
        self.assertEqual(type(r), dict)

    def test_get_metar_return_metar(self):
        r = self.metar.get_metar('EPKK')
        self.assertEqual(r['station_id'], 'EPKK')
        self.assertEqual(r['errors'], None)

    def test_get_metar_incorrect_code(self):
        r = self.metar.get_metar('XXXX')
        self.assertEqual(
            r['errors'], 'Incorrect airport code or no metar available')

    @unittest.mock.patch('requests.get')
    def test_get_metar_timeout(self, metar_mock):
        metar_mock.side_effect = requests.exceptions.Timeout
        r = self.metar.get_metar('EPKK')
        self.assertEqual(r['errors'], 'Connection timed out')

    @unittest.mock.patch('requests.get')
    def test_get_metar_requesterror(self, metar_mock):
        metar_mock.side_effect = requests.exceptions.ConnectionError()
        r = self.metar.get_metar('EPKK')
        self.assertEqual(r['errors'], 'Failed to connect to metar server')

    def test_get_metar_accept_only_string(self):
        with self.assertRaises(TypeError):
            self.metar.get_metar(1234)
        with self.assertRaises(TypeError):
            self.metar.get_metar(['EPKK'])
        with self.assertRaises(TypeError):
            self.metar.get_metar(['EPKK', 'EPWA'])
        with self.assertRaises(TypeError):
            self.metar.get_metar([0000, 1234])
        with self.assertRaises(TypeError):
            self.metar.get_metar(None)

    def tearDown(self):
        pass


class TestGetMetarForList(unittest.TestCase):

    def setUp(self):
        self.metar = metar.Metar()

    def test_get_metars(self):
        r = self.metar.get_metar_for_list(['EPKK', 'EPWA'])
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0]['station_id'], 'EPKK')
        self.assertEqual(r[1]['station_id'], 'EPWA')

    def test_get_metars_return_empty_list(self):
        r = self.metar.get_metar_for_list(list())
        self.assertEqual(len(r), 0)
        r = self.metar.get_metar_for_list(['XXXX', 'YYYY'])
        self.assertEqual(len(r), 0)

    def tearDown(self):
        pass