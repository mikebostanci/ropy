#!/usr/bin/env python
"""
@author Jesse Haviland
"""

import ropy as rp
from ropy.backend.PyPlot.EllipsePlot import EllipsePlot


def _fellipse(robot, q=None, opt='trans', centre=[0, 0, 0]):

    ell = EllipsePlot(robot, 'f', opt, centre=centre)
    return ell


def _vellipse(robot, q=None, opt='trans', centre=[0, 0, 0]):

    ell = EllipsePlot(robot, 'v', opt, centre=centre)
    return ell


def _plot_ellipse(
        ellipse, block=True, limits=None,
        jointaxes=True, eeframe=True, shadow=True, name=True):

    if not isinstance(ellipse, EllipsePlot):
        raise TypeError(
            'ellipse must be of type ropy.backend.PyPlot.EllipsePlot')

    env = rp.backend.PyPlot()

    # Add the robot to the figure in readonly mode
    env.launch(ellipse.robot.name + ' ' + ellipse.name, limits=limits)

    env.add(
        ellipse,
        jointaxes=jointaxes, eeframe=eeframe, shadow=shadow, name=name)

    # Keep the plot open
    if block:           # pragma: no cover
        env.hold()

    return env