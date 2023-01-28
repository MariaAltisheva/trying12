from pytest_factoryboy import register

import tests.factories

register(tests.factories.UserFactory)

pytest_plugins = 'tests.fixtures'
