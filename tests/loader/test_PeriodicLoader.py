from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from loader.PeriodicLoader import PeriodicLoader


class TestPeriodicLoader(IsolatedAsyncioTestCase):
    hash = "0x0"

    def setUp(self):
        self.loader = PeriodicLoader()
