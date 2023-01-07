==============
pythonのエラー
==============

pip install でエラー
============

.. code-block::

  $ pip3 install shpinx
  ERROR: Could not find a version that satisfies the requirement shpinx (from versions: none)
  ERROR: No matching distribution found for shpinx

Invalid syntax
===============

.. code-block::

    /usr/lib/python3/dist-packages/netaddr/strategy/__init__.py:189: SyntaxWarning: "is not" with a literal. Did you mean "!="?
    if word_sep is not '':
  /usr/lib/python3/dist-packages/ryu/lib/packet/cfm.py:271: SyntaxWarning: "is not" with a literal. Did you mean "!="?
    assert interval is not 0
  Traceback (most recent call last):
    File "tracing_of_pipeline.py", line 42, in <module>
      from tracing_net.net.net import TracingNet
    File "/home/vagrant/src/tracing_net/net/net.py", line 13, in <module>
      from mininet.cli import CLI
    File "/usr/local/lib/python3.8/dist-packages/mininet/cli.py", line 40, in <module>
      from mininet.term import makeTerms, runX11
    File "/usr/local/lib/python3.8/dist-packages/mininet/term.py", line 12, in <module>
      from mininet.util import quietRun, errRun
    File "/usr/local/lib/python3.8/dist-packages/mininet/util.py", line 55, in <module>
      import pexpect as oldpexpect
    File "/usr/lib/python3/dist-packages/pexpect/__init__.py", line 75, in <module>
      from .pty_spawn import spawn, spawnu
    File "/usr/lib/python3/dist-packages/pexpect/pty_spawn.py", line 14, in <module>
      from .spawnbase import SpawnBase
    File "/usr/lib/python3/dist-packages/pexpect/spawnbase.py", line 224
      def expect(self, pattern, timeout=-1, searchwindowsize=-1, async=False):
                                                                ^
  SyntaxError: invalid syntax

解決策
----------

.. code-block::

  sudo apt-get -y remove python-pexpect python3-pexpect
  sudo pip3 install --upgrade pexpect
  sudo pip3 install --upgrade lxml