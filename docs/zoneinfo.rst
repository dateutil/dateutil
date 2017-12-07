========
zoneinfo
========
.. automodule:: dateutil.zoneinfo
   :members:
   :undoc-members:

.. automodule:: dateutil.zoneinfo.rebuild
   :members: rebuild

zonefile_metadata
-----------------
The zonefile metadata defines the version and exact location of
the timezone database to download. It is used in the ``updatezinfo.py``
script. A json encoded file is included in the source-code, and
within each tar file we produce. The json file is attached here:

.. literalinclude:: ../zonefile_metadata.json
   :language: json
