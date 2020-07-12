#! /usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from spatialmath import SE3
from spatialmath.base.argcheck import getvector, verifymatrix
import ropy as rp


class Link(object):
    """
    A link superclass for all link types. A Link object holds all information
    related to a robot joint and link such as kinematics parameters,
    rigid-body inertial parameters, motor and transmission parameters.

    :param theta: kinematic: joint angle
    :type theta: float
    :param d: kinematic - link offset
    :type d: float
    :param alpha: kinematic - link twist
    :type alpha: float
    :param a: kinematic - link length
    :type a: float
    :param sigma: kinematic - 0 if revolute, 1 if prismatic
    :type sigma: int
    :param mdh: kinematic - 0 if standard D&H, else 1
    :type mdh: int
    :param offset: kinematic - joint variable offset
    :type offset: float

    :param qlim: joint variable limits [min max]
    :type qlim: float np.ndarray(1,2)
    :param flip: joint moves in opposite direction
    :type flip: bool

    :param m: dynamic - link mass
    :type m: float
    :param r: dynamic - position of COM with respect to link frame
    :type r:  float np.ndarray(3,1)
    :param I: dynamic - inertia of link with respect to COM
    :type I: float np.ndarray(3,3)
    :param Jm: dynamic - motor inertia
    :type Jm: float
    :param B: dynamic - motor viscous friction (1x1 or 2x1)
    :type B: float or float np.ndarray(2,1)
    :param Tc: dynamic - motor Coulomb friction (1x2 or 2x1)
    :type Tc: float np.ndarray(2,1)
    :param G: dynamic - gear ratio
    :type G: float

    References:
    Robotics, Vision & Control, P. Corke, Springer 2011, Chap 7.
    """

    def __init__(
            self,
            d=0.0,
            alpha=0.0,
            theta=0.0,
            a=0.0,
            sigma=0,
            mdh=0.0,
            offset=0.0,
            qlim=np.zeros(2),
            flip=False,
            m=0.0,
            r=np.zeros(3),
            I=np.zeros((3, 3)),
            Jm=0.0,
            B=np.zeros(2),
            Tc=np.zeros(2),
            G=1.0
            ):

        # Kinematic parameters
        self.sigma = sigma
        self.theta = theta
        self.d = d
        self.alpha = alpha
        self.a = a
        self.mdh = mdh
        self.offset = offset

        self.flip = flip
        self.qlim = qlim

        # Dynamic Parameters
        self.m = m
        self.r = r
        self.I = I
        self.Jm = Jm
        self.B = B
        self.Tc = Tc
        self.G = G

    def __add__(self, l2):
        print(isinstance(l2, Link))
        if isinstance(l2, Link):
            return rp.SerialLink([self, l2])
        else:
            raise TypeError("Cannot add a Link with a non Link object")

    def __str__(self):
        # TODO
        pass

    def __repr__(self):
        self.__str__()

    @property
    def d(self):
        return self._d

    @property
    def alpha(self):
        return self._alpha

    @property
    def theta(self):
        return self._theta

    @property
    def a(self):
        return self._a

    @property
    def sigma(self):
        return self._sigma

    @property
    def mdh(self):
        return self._mdh

    @property
    def offset(self):
        return self._offset

    @property
    def qlim(self):
        return self._qlim

    @property
    def flip(self):
        return self._flip

    @property
    def m(self):
        return self._m

    @property
    def r(self):
        return self._r

    @property
    def I(self):
        return self._I

    @property
    def Jm(self):
        return self._Jm

    @property
    def B(self):
        return self._B

    @property
    def Tc(self):
        return self._Tc

    @property
    def G(self):
        return self._G

    @d.setter
    def d(self, d_new):
        if self.sigma and d_new != 0.0:
            raise ValueError("f is not valid for prismatic joints")
        else:
            self._d = d_new

    @alpha.setter
    def alpha(self, alpha_new):
        self._alpha = alpha_new

    @theta.setter
    def theta(self, theta_new):
        if not self.sigma and theta_new != 0.0:
            raise ValueError("theta is not valid for revolute joints")
        else:
            self._theta = theta_new

    @a.setter
    def a(self, a_new):
        self._a = a_new

    @sigma.setter
    def sigma(self, sigma_new):
        self._sigma = sigma_new

    @mdh.setter
    def mdh(self, mdh_new):
        self._mdh = mdh_new

    @offset.setter
    def offset(self, offset_new):
        self._offset = offset_new

    @qlim.setter
    def qlim(self, qlim_new):
        self._qlim = getvector(qlim_new, 2)

    @flip.setter
    def flip(self, flip_new):
        self._flip = flip_new

    @m.setter
    def m(self, m_new):
        self._m = m_new

    @r.setter
    def r(self, r_new):
        self._r = getvector(r_new, 3, out='col')

    @I.setter
    def I(self, I_new):
        # Try for Inertia Matrix
        try:
            verifymatrix(I_new, (3, 3))
        except (ValueError, TypeError):

            # Try for the moments and products of inertia
            # [Ixx Iyy Izz Ixy Iyz Ixz]
            try:
                Ia = getvector(I_new, 6)
                I_new = np.array([
                    [Ia[0], Ia[3], Ia[5]],
                    [Ia[3], Ia[1], Ia[4]],
                    [Ia[5], Ia[4], Ia[2]]
                ])
            except ValueError:

                # Try for the moments of inertia
                # [Ixx Iyy Izz]
                Ia = getvector(I_new, 3)
                I_new = np.diag(Ia)

        self._I = I_new

    @Jm.setter
    def Jm(self, Jm_new):
        self._Jm = Jm_new

    @B.setter
    def B(self, B_new):
        self._B = getvector(B_new, 2, out='col')

    @Tc.setter
    def Tc(self, Tc_new):

        try:
            # sets Coulomb friction parameters to [F -F], for a symmetric
            # Coulomb friction model.
            Tc = getvector(Tc_new, 1)
            Tc_new = np.array([Tc[0], -Tc[0]])
        except ValueError:
            # [FP FM] sets Coulomb friction to [FP FM], for an asymmetric
            # Coulomb friction model. FP>0 and FM<0.  FP is applied for a
            # positive joint velocity and FM for a negative joint
            # velocity.
            Tc_new = getvector(Tc_new, 2)

        self._Tc = Tc_new

    @G.setter
    def G(self, G_new):
        self._G = G_new

    def A(self, q):
        """
        A Link transform matrix. T = L.A(Q) is the link homogeneous
        transformation matrix (4x4) corresponding to the link variable Q
        which is either the Denavit-Hartenberg parameter THETA (revolute)
        or D (prismatic)

        Notes:
        - For a revolute joint the THETA parameter of the link is ignored,
          and Q used instead.
        - For a prismatic joint the D parameter of the link is ignored, and
          Q used instead.
        - The link offset parameter is added to Q before computation of the
          transformation matrix.

        :param q: Joint angle (radians)
        :type q: float
        :return T: link homogeneous transformation matrix
        :rtype T: float numpy.ndarray((4, 4))
        """

        sa = np.sin(self.alpha)
        ca = np.cos(self.alpha)

        if self.flip:
            q = -q + self.offset
        else:
            q = q + self.offset

        if self.sigma == 0:
            # revolute
            st = np.sin(q)
            ct = np.cos(q)
            d = self.d
        else:
            # prismatic
            st = np.sin(self.theta)
            ct = np.cos(self.theta)
            d = q

        if self.mdh == 0:
            # standard DH
            T = np.array([
                [ct,  -st*ca,   st*sa,   self.a*ct],
                [st,   ct*ca,  -ct*sa,   self.a*st],
                [0,    sa,      ca,      d],
                [0,    0,       0,       1]
            ])
        else:
            # modified DH
            T = np.array([
                [ct,      -st,       0,     self.a],
                [st*ca,    ct*ca,   -sa,   -sa*d],
                [st*sa,    ct*sa,    ca,    ca*d],
                [0,        0,        0,     1]
            ])

        return SE3(T)

    def islimit(self, q):
        """
        Checks if the joint is exceeding a joint limit

        :return: True if joint is exceeded
        :rtype: bool
        """

        if q < self.qlim[0] or q > self.qlim[1]:
            return True
        else:
            return False

    def isrevolute(self):
        """
        Checks if the joint is of revolute type

        :return: Ture if is revolute
        :rtype: bool
        """

        if not self.sigma:
            return True
        else:
            return False

    def isprismatic(self):
        """
        Checks if the joint is of prismatic type

        :return: Ture if is prismatic
        :rtype: bool
        """

        if self.sigma:
            return True
        else:
            return False

    def nofriction(self, coulomb=True, viscous=False):
        """
        Copies the link and returns a link with the same parameters except,
        the Coulomb and/or viscous friction parameter to zero

        :param coulomb: if True, will set the coulomb friction to 0
        :type coulomb: bool
        :param viscous: if True, will set the viscous friction to 0
        :type viscous: bool
        """

        if viscous:
            self.B = [0.0, 0.0]

        if coulomb:
            self.Tc = [0.0, 0.0]

    def friction(self, qd):
        """
        Calculates the joint friction force/torque (1xN) for joint
        velocity QD (1xN). The friction model includes:
        - Viscous friction which is a linear function of velocity.
        - Coulomb friction which is proportional to sign(QD).

        Notes::
        - The friction value should be added to the motor output torque, it has
            a negative value when QD>0.
        - The returned friction value is referred to the output of the gearbox.
        - The friction parameters in the Link object are referred to the motor.
        - Motor viscous friction is scaled up by G^2.
        - Motor Coulomb friction is scaled up by G.
        - The appropriate Coulomb friction value to use in the non-symmetric
            case depends on the sign of the joint velocity, not the motor
            velocity.
        - The absolute value of the gear ratio is used.  Negative gear ratios
            are tricky: the Puma560 has negative gear ratio for joints 1 and
            3.

        :param qd: The joint velocity
        :type qd: float

        :return tau: the friction force/torque
        :rtype tau: float
        """

        tau = self.B * np.abs(self.G) * qd

        if qd > 0:
            tau += self.Tc[0]
        elif qd < 0:
            tau += self.Tc[1]

        return tau


class Revolute(Link):
    """
    A class for revolute link types

    :param d: kinematic - link offset
    :type d: float
    :param alpha: kinematic - link twist
    :type alpha: float
    :param a: kinematic - link length
    :type a: float
    :param sigma: kinematic - 0 if revolute, 1 if prismatic
    :type sigma: int
    :param mdh: kinematic - 0 if standard D&H, else 1
    :type mdh: int
    :param offset: kinematic - joint variable offset
    :type offset: float

    :param qlim: joint variable limits [min max]
    :type qlim: float np.ndarray(1,2)
    :param flip: joint moves in opposite direction
    :type flip: bool

    :param m: dynamic - link mass
    :type m: float
    :param r: dynamic - position of COM with respect to link frame
    :type r:  float np.ndarray(3,1)
    :param I: dynamic - inertia of link with respect to COM
    :type I: float np.ndarray(3,3)
    :param Jm: dynamic - motor inertia
    :type Jm: float
    :param B: dynamic - motor viscous friction (1x1 or 2x1)
    :type B: float or float np.ndarray(2,1)
    :param Tc: dynamic - motor Coulomb friction (1x2 or 2x1)
    :type Tc: float np.ndarray(2,1)
    :param G: dynamic - gear ratio
    :type G: float

    References:
    Robotics, Vision & Control, P. Corke, Springer 2011, Chap 7.
    """

    def __init__(
            self,
            d=0.0,
            alpha=0.0,
            a=0.0,
            mdh=0.0,
            offset=0.0,
            qlim=np.zeros(2),
            flip=False,
            m=0.0,
            r=np.zeros(3),
            I=np.zeros((3, 3)),
            Jm=0.0,
            B=np.zeros(2),
            Tc=np.zeros(2),
            G=1.0
            ):

        theta = 0.0
        sigma = 0

        super(Revolute, self).__init__(
            d, alpha, theta, a, sigma, mdh, offset,
            qlim, flip, m, r, I, Jm, B, Tc, G)


class Prismatic(Link):
    """
    A subclass of the Link class for a prismatic joint: holds all information
    related to a robot link such as kinematics parameters, rigid-body inertial
    parameters, motor and transmission parameters.

    :param theta: kinematic: joint angle
    :type theta: float
    :param d: kinematic - link offset
    :type d: float
    :param alpha: kinematic - link twist
    :type alpha: float
    :param a: kinematic - link length
    :type a: float
    :param sigma: kinematic - 0 if revolute, 1 if prismatic
    :type sigma: int
    :param mdh: kinematic - 0 if standard D&H, else 1
    :type mdh: int
    :param offset: kinematic - joint variable offset
    :type offset: float

    :param qlim: joint variable limits [min max]
    :type qlim: float np.ndarray(1,2)
    :param flip: joint moves in opposite direction
    :type flip: bool

    :param m: dynamic - link mass
    :type m: float
    :param r: dynamic - position of COM with respect to link frame
    :type r:  float np.ndarray(3,1)
    :param I: dynamic - inertia of link with respect to COM
    :type I: float np.ndarray(3,3)
    :param Jm: dynamic - motor inertia
    :type Jm: float
    :param B: dynamic - motor viscous friction (1x1 or 2x1)
    :type B: float or float np.ndarray(2,1)
    :param Tc: dynamic - motor Coulomb friction (1x2 or 2x1)
    :type Tc: float np.ndarray(2,1)
    :param G: dynamic - gear ratio
    :type G: float

    References:
    Robotics, Vision & Control, P. Corke, Springer 2011, Chap 7.
    """

    def __init__(
            self,
            alpha=0.0,
            theta=0.0,
            a=0.0,
            mdh=0.0,
            offset=0.0,
            qlim=np.zeros(2),
            flip=False,
            m=0.0,
            r=np.zeros(3),
            I=np.zeros((3, 3)),
            Jm=0.0,
            B=np.zeros(2),
            Tc=np.zeros(2),
            G=1.0
            ):

        d = 0.0
        sigma = 1

        super(Prismatic, self).__init__(
            d, alpha, theta, a, sigma, mdh, offset,
            qlim, flip, m, r, I, Jm, B, Tc, G)