# coding=utf-8
from __future__ import unicode_literals

from django.db.models.signals import post_save


class AbstractFixtures(object):

    dependencies = None
    parent = None

    def setup(self, parent=None):
        self.parent = parent

        self.pre_setup_dependencies()
        self.setup_dependencies()
        self.post_setup_dependencies()

        self.pre_setup_fixtures()
        post_save.connect(self.signal_dependency_model_saved)
        self.setup_fixtures()
        post_save.disconnect(self.signal_dependency_model_saved)
        self.post_setup_fixtures()

    def pre_setup_fixtures(self):
        pass

    def setup_fixtures(self):
        raise NotImplementedError

    def post_setup_fixtures(self):
        pass

    def pre_setup_dependencies(self):
        pass

    def post_setup_dependencies(self):
        pass

    def setup_dependencies(self):
        dependencies = self.get_dependencies()
        if dependencies is not None:
            for dependency in dependencies:
                dependency.setup(self)

    def signal_dependency_model_saved(self, sender, instance, **kwargs):
        if self.parent is not None:
            # shut model creating signal in receiver.
            post_save.disconnect(self.signal_dependency_model_saved)
            self.parent.on_dependency_model_saved(sender=sender, instance=instance, **kwargs)
            post_save.connect(self.signal_dependency_model_saved)

    def on_dependency_model_saved(self, sender, instance, **kwargs):
        """
        Called when dependency created a model.
        ***Don't create any model in this method.***
        If model creation, i.e. related dependency object, is needed, record the related dependencies, and set it up in
        setup_fixtures method.
        :param sender:
        :param instance:
        :param kwargs:
        :return:
        """

    def get_dependencies(self):
        return self.dependencies
