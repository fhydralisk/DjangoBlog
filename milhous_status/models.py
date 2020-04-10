import datetime
import logging

from dateutil.parser import isoparse

from django.db import models
from base.util import redis

# Create your models here.


class HeartbeatMixin(object):

    @property
    def redis_hb_key(self):
        raise NotImplementedError

    def heartbeat(self):
        try:
            r = redis.get_redis()
            r.set(self.redis_hb_key, datetime.datetime.now().isoformat())
        except:
            logging.exception("Failed to heartbeat.")

    @property
    def is_alive(self):
        try:
            r = redis.get_redis()
            tf = r.get(self.redis_hb_key)
            if tf is None:
                return False

            t = isoparse(tf)
            return (datetime.datetime.now() - t).total_seconds() < 2 * self.update_interval
        except:
            logging.exception("Faild to read heartbeat information")
            return False


class HostMachineType(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="名称")
    icon = models.ImageField(verbose_name="图标")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "服务器类型"


class MilhousHost(models.Model, HeartbeatMixin):
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="主机名称")
    host_desc = models.TextField(verbose_name="主机配置描述")
    host_type = models.ForeignKey(to=HostMachineType, on_delete=models.CASCADE, verbose_name="主机类型")
    update_interval = models.IntegerField(default=10, verbose_name="上报间隔")

    @property
    def redis_hb_key(self):
        return 'host_update_' + self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "服务器"


class MilhousCharacter(models.Model, HeartbeatMixin):
    character = models.CharField(max_length=32, null=False, blank=False, verbose_name="角色名称")
    host = models.ForeignKey(
        to=MilhousHost,
        on_delete=models.SET_NULL,
        verbose_name="主机",
        related_name="characters",
        null=True,
        blank=True
    )
    expire = models.DateTimeField(verbose_name="过期时间")
    photo = models.ImageField(null=True, blank=True, verbose_name="照片")
    update_interval = models.IntegerField(default=120, verbose_name="上报间隔")

    @property
    def redis_hb_key(self):
        return self.character + '_alive_hb'

    def __str__(self):
        return self.character

    class Meta:
        verbose_name = "角色"


class MilhousHostStatistics(models.Model):
    report_date = models.DateTimeField(auto_now_add=True)
    host = models.ForeignKey(to=MilhousHost, on_delete=models.CASCADE)
    usages = models.TextField()


class MilhousCharacterStatistics(models.Model):
    report_date = models.DateTimeField(auto_now_add=True)
    character = models.ForeignKey(to=MilhousCharacter, on_delete=models.CASCADE)
    usages = models.TextField()
