.. _getting-started:

Getting started
===============

Install the package from `Pypi <https://pypi.org/project/redmail/>`_:

.. code-block:: console

    pip install redengine

.. _configure:

Configuring Email
-----------------

You can configure your sender by:

.. code-block:: python

   from redmail import EmailSender

   email = EmailSender(
       host='<SMTP HOST>',
       port='<SMTP PORT>',
       user_name='<USER_NAME>',
       password='<PASSWORD>'
   )

.. code-block:: python

   # Or if your SMTP server does not require credentials
   email = EmailSender(
       host='<SMTP HOST>',
       port='<SMTP PORT>',
   )

Alternatively, there is a pre-configured sender for Gmail. 
Please see :ref:`how to configure Gmail <config-gmail>` for more.


Sending Emails
--------------

You can just send emails by calling the method ``send``:

.. code-block:: python

   email.send(
       subject='email subject',
       sender="me@example.com",
       receivers=['you@example.com'],
       text="Hi, this is an email."
   )

Next tutorial covers sending emails more thoroughly.