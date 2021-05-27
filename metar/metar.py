import requests
import logging
import re


class Metar:
    def __init__(self):
        logging.basicConfig(level=logging.CRITICAL)
        self.url = 'https://www.aviationweather.gov/adds/dataserver_current/'

    def __parse_altimeter(self, alt):
        try:
            code, value, _ = re.split(r'(\d+)', alt)
        except ValueError:
            return {'errors': 'Unsupported altimeter format'}
        if code not in ('Q', 'A'):
            return {'errors': 'Unsupported altimeter format'}

        if code == 'Q':
            try:
                value = int(value)
                return {
                    'altim_in_hpa': value,
                    'altim_in_hg': round(value * 0.029529983071445, 2)
                }
            except ValueError:
                return {'errors': f'Incorrect altimeter value: {value}'}
                
        else:
            try:
                value = float(''.join([value[:2], '.', value[2:]]))
                return {
                    'altim_in_hpa': round(value * 33.86388666666671),
                    'altim_in_hg': value
                }
            except ValueError:
                return {'errors': f'Incorrect altimeter value: {value}'}

    def __parse_visibility(self, metar, vis_sm):
        try:
            vis_sm = float(vis_sm)
        except ValueError:
            return {'errors': f'Incorrect vis_sm value: {vis_sm}'}

        p = re.compile(r'(?P<vis_m>\b\d{4}\b)|(?P<vis_sm>\d*(\s\d\/\d)?SM)|(?P<cavok>)CAVOK')
        r = re.search(p, metar)
        if r is None:
            return {'errors': 'Visibility parsing error'}
        match = r.groupdict()

        if match['cavok'] is not None:
            return {'visibility_statute_mi': 6.21, 'visibility_m': 10000}

        try:
            vis_sm = float(vis_sm)
        except ValueError:
            return {'errors': 'Visibility parsing error'}

        vis_m = None
        if match['vis_m'] is not None:
            try:
                vis_m = int(match['vis_m'])
            except ValueError:
                return {'errors': 'Visibility parsing error'}

        if not vis_m:
            vis_m = round(vis_sm * 1609.344)

        return {'visibility_statute_mi': vis_sm, 'visibility_m': vis_m}

    def get_metar(self, airport_code):
        if type(airport_code) != str:
            raise TypeError('Airport code must be a string')
        try:
            r = requests.get(
                self.url
                + 'httpparam?dataSource=metars&requestType=retrieve&format=csv&hoursBeforeNow=12&mostRecent=true',
                params={'stationString': airport_code},
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

        alt = re.findall(r'Q\d{4}|A\d{4}', metar['raw_text'])
        t = self.__parse_altimeter(alt[0])
        metar.update(t)

        t = self.__parse_visibility(
            metar['raw_text'], metar['visibility_statute_mi'])
        metar.update(t)

        if 'errors' not in metar:
            metar['errors'] = None

        return metar

    def get_metar_for_list(self, airport_list):
        airport = []
        for code in airport_list:
            m = self.get_metar(code)
            if not m['errors']:
                airport.append(m)
        return airport
