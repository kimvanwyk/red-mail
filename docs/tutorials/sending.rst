.. _sending-emails:

Sending Emails
==============

This section covers the basics of sending emails.
See :ref:`configure` to revise how ``EmailSender``
is configured. At minimum, sending an email requires:

.. code-block:: python

    from email import EmailSender
    email = EmailSender(host='localhost', port=0)

    email.send(
        subject='email subject',
        sender="me@example.com",
        receivers=['you@example.com']
    )

.. note::

    If you don't spesify the ``sender``, the sender is considered to 
    be ``email.sender``. If ``email.sender`` is also missing, the sender
    is then set to be ``email.user_name``. Ensure that any of these is a 
    valid email address. 

.. note::

    Some email providers (such as Gmail) do not allow specifying
    sender. For example, Gmail will outright ignore it and always
    use your own email address.

Sending Email with Text Body
----------------------------

To send an email with plain text message:

.. code-block:: python

   email.send(
       subject='email subject',
       sender="me@example.com",
       receivers=['you@example.com'],
       text="Hi, this is an email."
   )

Sending Email with HTML Body
----------------------------

To send an email with html content:

.. code-block:: python

    email.send(
        subject='email subject',
        sender="me@example.com",
        receivers=['you@example.com'],
        html="""
            <h1>Hi,</h1>
            <p>this is an email.</p>
        """
    )


Sending Email with text and HTML Body
-------------------------------------

You can also include both to your email:

.. code-block:: python

    email.send(
        subject='email subject',
        sender="me@example.com",
        receivers=['you@example.com'],
        text="Hi, this is an email.",
        html="""
            <h1>Hi,</h1>
            <p>this is an email.</p>
        """
    )

.. _send-cc-bcc:

Sending Email with cc and bcc
-----------------------------

You can also include carbon copy (cc) and blind carbon copy (bcc)
to your emails:

.. code-block:: python

    email.send(
        subject='email subject',
        sender="me@example.com",
        receivers=['you@example.com'],
        cc=['also@example.com'],
        bcc=['outsider@example.com']
    )