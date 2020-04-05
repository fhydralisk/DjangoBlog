import logging
from base.util.db import LastLineConfigManager
from base.models import MiniprogramAppSecret


logger = logging.getLogger(__name__)


class AppSecretManager(LastLineConfigManager):

    CLZ_MODEL = MiniprogramAppSecret
    cls_logger = logger


app_secret_manager = AppSecretManager()
