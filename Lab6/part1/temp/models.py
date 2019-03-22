# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Temperature(models.Model):
    temp = models.IntegerField(default=0)
