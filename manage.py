#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import matplotlib
from matplotlib.pyplot import figure
import mpld3


def main():
    """Run administrative tasks."""

    """
    matplotlib.use('agg')
    matplotlib.use('TkAgg')
    matplotlib.pyplot.switch_backend('Agg')

    fig = figure()
    ax = fig.gca()
    ax.plot([1, 2, 3, 4])

    mpld3.show(fig)
    """

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ipaca.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
