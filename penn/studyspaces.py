import requests
import datetime
import json
import pytz
import re
import six

from bs4 import BeautifulSoup


BASE_URL = "http://libcal.library.upenn.edu"


class StudySpaces(object):
    def __init__(self):
        pass

    def get_buildings(self):
        """Returns a list of building IDs, building names, and services."""

        soup = BeautifulSoup(requests.get("{}/spaces".format(BASE_URL)).content, "html5lib")
        options = soup.find("select", {"id": "lid"}).find_all("option")
        return [{"id": int(opt["value"]), "name": str(opt.text), "service": "libcal"} for opt in options]

    @staticmethod
    def format_date(date):
        date = pytz.timezone("US/Eastern").localize(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
        return date.isoformat()

    @staticmethod
    def get_room_id_name_mapping(building):
        data = requests.get("{}/spaces?lid={}".format(BASE_URL, building)).content.decode("utf8")
        # find all of the javascript room definitions
        out = {}
        for item in re.findall(r"resources.push\(((?s).*?)\);", data, re.MULTILINE):
            items = {k: v for k, v in re.findall(r'(\w+?):\s*(.*?),', item)}
            out[int(items["eid"])] = {
                "name": items["title"][1:-1].encode().decode("unicode_escape" if six.PY3 else "string_escape"),
                "thumbnail": items["thumbnail"][1:-1]
            }
        return out

    def get_rooms(self, building, start, end):
        """Returns a dictionary matching all rooms given a building id and a date range."""

        mapping = self.get_room_id_name_mapping(building)
        room_endpoint = "{}/process_equip_p_availability.php".format(BASE_URL)
        data = {
            "lid": building,
            "gid": 0,
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "bookings": []
        }
        resp = requests.post(room_endpoint, data=json.dumps(data), headers={'Referer': "{}/spaces?lid={}".format(BASE_URL, building)})
        rooms = {}
        for row in resp.json():
            room_id = int(row["resourceId"][4:])
            if room_id not in rooms:
                rooms[room_id] = []
            rooms[room_id].append({
                "start": self.format_date(row["start"]),
                "end": self.format_date(row["end"]),
                "booked": row["status"] != 0
            })
        return [{
            "room_id": k,
            "times": v,
            "name": mapping[k]["name"] if k in mapping else None,
            "thumbnail": mapping[k]["thumbnail"] if k in mapping else None
        } for k, v in rooms.items()]
