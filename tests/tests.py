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


class TestParsers(unittest.TestCase):

    def setUp(self):
        self.metar = metar.Metar()
        self.metar_raw_meters = 'EPKK 071100Z 23013KT 8000 -SHSN SCT023CB BKN033 01/M01 Q1008 RESHSNGS'
        self.metar_raw_sm = 'KLAX 071053Z 27004KT 10SM FEW010 FEW250 13/11 A3004 RMK AO2 SLP171 T01280111'

    def test_altimeter_QNH_parse(self):
        r = self.metar._Metar__parse_altimeter('Q1013')
        self.assertEqual({'alt': 1013, 'alt_units': 'hPa'}, r)

    def test_altimeter_ALT_parse(self):
        r = self.metar._Metar__parse_altimeter('A2992')
        self.assertEqual({'alt': 29.92, 'alt_units': 'inHg'}, r)

    def test_altimeter_return_format_error(self):
        r = self.metar._Metar__parse_altimeter('E2992')
        self.assertEqual({'errors': 'Unsupported altimeter format'}, r)
        r = self.metar._Metar__parse_altimeter('2992')
        self.assertEqual({'errors': 'Unsupported altimeter format'}, r)
        r = self.metar._Metar__parse_altimeter('EEAA')
        self.assertEqual({'errors': 'Unsupported altimeter format'}, r)
        r = self.metar._Metar__parse_altimeter('2992A')
        self.assertEqual({'errors': 'Unsupported altimeter format'}, r)

    def test_visibility_meter_parse(self):
        r = self.metar._Metar__parse_visibility(self.metar_raw_meters, '4.79')
        self.assertEqual({'visibility_m': 8000, 'visibility_statute_mi': 4.79}, r)

    def test_visibility_sm_parse(self):
        r = self.metar._Metar__parse_visibility(self.metar_raw_sm, '10.0')
        self.assertEqual(r['visibility_statute_mi'], 10.0)
        self.assertAlmostEqual(r['visibility_m'], 16093)

    def test_visibility_return_incorrect_value_error(self):
        r = self.metar._Metar__parse_visibility(self.metar_raw_sm, 'AAEE')
        self.assertEqual({'errors': 'Incorrect vis_sm value: AAEE'}, r)
        r = self.metar._Metar__parse_visibility(self.metar_raw_sm, '-3.F')
        self.assertEqual({'errors': 'Incorrect vis_sm value: -3.F'}, r)

    def test_visibility_return_parse_error(self):
        r = self.metar._Metar__parse_visibility('923A 42AA', '10.0')
        self.assertEqual({'errors': 'Visibility parsing error'}, r)
