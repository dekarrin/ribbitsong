import unittest
from unittest.mock import patch

from frogcherub import mutations

class TestMutations(unittest.TestCase):

    def test_universe_collapse(self):
        data = {
            "events": [
                {
                    "unrelated": "one",
                    "universes": [
                        {
                            "characters": [
                                "john-egbert"
                            ],
                            "items": [],
                            "location": "/earth/egberthouse/johnsroom",
                            "name": "earth-pre-scratch",
                            "timeline": "/"
                        }
                    ]
                },
                {
                    "unrelated": "two",
                    "universes": [
                        {
                            "characters": [
                                "john-egbert"
                            ],
                            "items": [
                                "fake-arms"
                            ],
                            "location": "/earth/egberthouse/johnsroom",
                            "name": "earth-pre-scratch",
                            "timeline": "/"
                        },
                        {
                            "characters": [
                                "dave-strider"
                            ],
                            "items": [],
                            "location": "/earth/striderhouse/davesroom",
                            "name": "earth-pre-scratch",
                            "timeline": "/"
                        }
                    ]
                }
            ]
        }
        
        expected = {
            "events": [
                {
                    "unrelated": "one",
                    "universes": [
                        {
                            "name": "earth-pre-scratch",
                            "timelines": [
                                {
                                    "path": "/",
                                    "locations": [
                                        {
                                            "path": "/earth/egberthouse/johnsroom",
                                            "characters": [
                                                "john-egbert"
                                            ],
                                            "items": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "unrelated": "two",
                    "universes": [
                        {
                            "name": "earth-pre-scratch",
                            "timelines": [
                                {
                                    "path": "/",
                                    "locations": [
                                        {
                                            "path": "/earth/egberthouse/johnsroom",
                                            "characters": [
                                                "john-egbert"
                                            ],
                                            "items": [
                                                "fake-arms"
                                            ]
                                        },
                                        {
                                            "path": "/earth/striderhouse/davesroom",
                                            "characters": [
                                                "dave-strider"
                                            ],
                                            "items": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        rows_changed = mutations.universe_collapse(data)

        self.assertEqual(rows_changed, 2)
        self.assertEqual(data, expected)

