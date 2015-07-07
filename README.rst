Hieronymus
==========

Lokale Testinstallation
-----------------------
Wir verwenden Vagrant_ um die Testumgebung in einer VM aufzusetzen und Ansible_ fürs Provisioning. In der VM läuft ein Ubuntu Trusty 64 Server.

.. _Vagrant: https://www.vagrantup.com/
.. _Ansible: http://www.ansible.com/home

Zum Loslegen, einfach folgendes eingeben:

.. code::

  vagrant up


Dev on Ubuntu
==============
sudo apt-get install python3 python3-requests python3-flask-sqlalchemy

Dev Server on Mac
==========

Download Vagrant
Dowload and install Virtualbox
sudo easy_install pip
pip install ansible
vagrant up in top dir
