# -*- coding: utf-8 -*-
import datetime

"""Top-level package for OkaPy."""

__author__ = """Valentin Oreiller"""
__email__ = 'valentin.oreiller@gmail.com'
__version__ = '0.1.2'
__container_name__ = ''


__current_year__ = datetime.datetime.now().strftime("%Y")
__release_date__ = "DD.MM.{}".format(__current_year__)
__packagename__ = "okapy"
__github_packagename__ = "okapy"

__container_name__ = "okapy"

__url__ = "https://github.com/Lundin-brain-tumour-research-center/{name}/tree/{version}".format(
    name=__github_packagename__, version=__version__
)