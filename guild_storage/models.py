from django.db import models, transaction

# Create your models here.


class GuildMaterialsStock(models.Model):
    name = models.CharField(max_length=64, verbose_name="物资名称")
    stock = models.DecimalField(verbose_name="库存", decimal_places=4, max_digits=10)
    unit = models.CharField(max_length=6, verbose_name="单位")
    image = models.ImageField(verbose_name="图标")
    order = models.ImageField(verbose_name="排序数")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = verbose_name = "物资"
        ordering = ('-order', )


class GuildMaterialsJournalManager(models.Manager):
    pass


class GuildMaterialsJournal(models.Model):

    material_input = models.ForeignKey(
        to=GuildMaterialsStock,
        related_name="log_input",
        verbose_name="涉及物资",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    amount_input = models.DecimalField(
        verbose_name="输入数量",
        decimal_places=4,
        max_digits=10,
        null=True,
        blank=True,
    )
    material_output = models.ForeignKey(
        to=GuildMaterialsStock,
        related_name="log_output",
        verbose_name="涉及物资",
        on_delete=models.CASCADE,
        null=True,
    )
    amount_output = models.DecimalField(
        verbose_name="输出数量",
        decimal_places=4,
        max_digits=10,
        null=True,
        blank=True,
    )
    input_from = models.CharField(
        verbose_name="从何输入",
        max_length=32,
    )
    output_to = models.CharField(
        verbose_name="输出至",
        max_length=32,
    )
    operate_date = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    comment = models.TextField(verbose_name="备注")

    objects = GuildMaterialsJournalManager()

    def __init__(self, *args, **kwargs):
        super(GuildMaterialsJournal, self).__init__(*args, **kwargs)
        self._original_material_input = self.material_input
        self._original_material_output = self.material_output
        self._original_amount_input = self.amount_input
        self._original_amount_output = self.amount_output

    def delete(self, using=None, keep_parents=False):
        if self.material_output:
            self.material_output.stock += self.amount_output
            self.material_output.save()

        if self.material_input:
            self.material_input.stock -= self.amount_input
            self.material_input.save()

        return super(GuildMaterialsJournal, self).delete(using=using, keep_parents=keep_parents)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        with transaction.atomic():
            if self.pk:
                if self._original_material_input:
                    assert self._original_amount_input is not None
                    self._original_material_input.stock -= self._original_amount_input
                    self._original_material_input.save()

                if self._original_material_output:
                    assert self._original_amount_output is not None
                    self._original_material_output.stock += self._original_amount_output
                    self._original_material_output.save()

            if self.material_input:
                assert self.amount_input is not None
                self.material_input.stock += self.amount_input
                self.material_input.save()

            if self.material_output:
                assert self.amount_output is not None
                self.material_output.stock -= self.amount_output
                self.material_output.save()

            self._original_amount_input = self.amount_input
            self._original_amount_output = self.amount_output

            self._original_material_input = self.material_input
            self._original_material_output = self.material_output

            return super(GuildMaterialsJournal, self).save(
                force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta:
        verbose_name_plural = verbose_name = "物资流水"
        ordering = ('-id', )
