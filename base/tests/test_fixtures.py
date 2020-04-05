from ..test_utils.testcases import WLBaseTestCase
from ..test_utils.fixtures import AbstractFixtures
from ..models.miniprog_app import MiniprogramAppSecret


class TextFixtureGrandparent(AbstractFixtures):
    def setup_fixtures(self):
        MiniprogramAppSecret.objects.create(appid='grandparent', appsecret='baz')


class TestFixtureParent(AbstractFixtures):
    dependencies = [TextFixtureGrandparent()]

    def setup_fixtures(self):
        MiniprogramAppSecret.objects.create(appid='parent', appsecret='foo')
        MiniprogramAppSecret.objects.create(appid='parent2', appsecret='foo2')


class TestFixtures(AbstractFixtures):
    dependencies = [TestFixtureParent()]

    def __init__(self):
        self.parent_appids = set()
        self.parent_count = 0

    def pre_setup_dependencies(self):
        self.parent_count = 0

    def setup_fixtures(self):
        MiniprogramAppSecret.objects.create(appid='test', appsecret='test')
        MiniprogramAppSecret.objects.create(appid='test2', appsecret='test2')

    def on_dependency_model_saved(self, sender, instance, **kwargs):
        self.parent_count += 1
        self.parent_appids.add(instance.appid)


class TestFixtureInstallation(WLBaseTestCase):
    fixture_mixins = [TestFixtures()]

    def testFixtureCount1(self):
        self.assertEqual(MiniprogramAppSecret.objects.count(), 5)

    def testFixtureCount2(self):
        self.assertEqual(MiniprogramAppSecret.objects.count(), 5)

    def testFixtureDependencyReceiver(self):
        test_fixture = self.fixture_mixins[0]
        self.assertSetEqual(test_fixture.parent_appids, {'parent', 'parent2'})
        self.assertEqual(test_fixture.parent_count, 2)
