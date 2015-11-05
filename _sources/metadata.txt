Metadata
========

See the `GeoBlacklight schema <https://github.com/geoblacklight/geoblacklight-schema/blob/master/docs/geoblacklight-schema.markdown>`_ and the `dct_references schema <https://github.com/geoblacklight/geoblacklight-schema/blob/master/docs/dct_references_schema.markdown>`_ for the general structure of a metadata record.


Layer IDs
---------

Layer IDs should conform to `RFC 4122 <https://www.ietf.org/rfc/rfc4122.txt>`_ using a version 5 UUID. The namespace used for constructing a layer's UUID should be ``arrowsmith.mit.edu``. The name should be the layer name. For example::

    import uuid

    ns = uuid.uuid5(uuid.NAMESPACE_DNS, 'arrowsmith.mit.edu')
    uid = uuid.uuid5(ns, 'BD_A8GNS_2003')
    urn = uid.urn

The layer's UUID (``uid`` in the above example) would map to the GeoBlacklight field ``uuid``. The layer's URN (``urn`` in the above example) would map to the GeoBlacklight field ``dc_identifier_s``.


Layer Slugs
-----------

A layer's slug should be constructed with the following steps:

1. Take the first 8 bytes of the layer's UUID.
2. Take a URL safe base64 encoding of those bytes.
3. Remove trailing padding.
4. Append the result to ``mit-``.

For example::

    import uuid
    import base64

    ns = uuid.uuid5(uuid.NAMESPACE_DNS, 'arrowsmith.mit.edu')
    uid = uuid.uuid5(ns, 'BD_A8GNS_2003')
    b64 = base64.urlsafe_b64encode(uid.bytes[:8]).rstrip('=')
    slug = 'mit-%s' % (b64,)
