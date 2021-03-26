import requests
import logging


class Metar:
    def __init__(self):
        logging.basicConfig(level=logging.CRITICAL)
        self.url = 'https://www.aviationweather.gov/adds/dataserver_current/'

    def get_metar(self, airport_code):
        if type(airport_code) != str:
            raise TypeError('Airport code must be a string')
        try:
            r = requests.get(
                self.url
                + 'httpparam?dataSource=metars&requestType=retrieve&format=csv&hoursBeforeNow=3&mostRecent=true',
                params={'StationString': airport_code},
            )
        except requests.ConnectionError as e:
            logging.exception(f'{e} on get_metar for code {airport_code}')
            return {'errors': 'Failed to connect to metar server'}
        except requests.Timeout as e:
            logging.exception(f'{e} on get_metar for code {airport_code}')
            return {'errors': 'Connection timed out'}

        errors, warnings, response_time, _, results, metar_raw = r.text.split(
            '\n', maxsplit=5
        )

        if errors != 'No errors':
            logging.error(
                f'Server error "{errors}" on get_metar for code {airport_code}')
            return {'errors': errors}
        if warnings != 'No warnings':
            logging.warn(
                f'Server warning "{warnings}" on get_metar for code {airport_code}')
            return {'errors': warnings}
        if results == '0 results':
            return {'errors': 'Incorrect airport code or no metar available'}

        headers_raw, conditons_raw = metar_raw.split('\n', maxsplit=1)
        headers = headers_raw.split(',')
        conditons = conditons_raw.split(',')
        metar = {}
        metar['sky_conditions'] = []
        for h, c in zip(headers, conditons):
            if h == 'sky_cover':
                metar['sky_conditions'].append({'sky_cover': c})
            elif h == 'cloud_base_ft_agl':
                metar['sky_conditions'][-1].update({'cloud_base_ft_agl': c})
            else:
                metar[h] = c

        # metar = {'errors': None}
        metar.update({'errors': None})
        return metar

    def get_metar_for_list(self, airport_list):
        airport = []
        for code in airport_list:
            m = self.get_metar(code)
            if not m['errors']:
                airport.append(m)
        return airport
