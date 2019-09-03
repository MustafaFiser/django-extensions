# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management import call_command

from django_extensions.management.commands.export_emails import Command, full_name

import pytest

from tests.testapp.settings import DATABASES


@pytest.fixture(autouse=True)
def custom_djsettings(settings):  # noqa
    """Custom django settings to avoid warnings in stdout"""
    settings.TEMPLATE_DEBUG = False
    settings.DEBUG = False
    return settings


@pytest.fixture(scope='module')
def django_db_setup():  # noqa
    """Select default database for testing"""
    settings.DATABASES = DATABASES  # noqa


@pytest.fixture(scope='module')  # noqa
def django_db_setup(django_db_setup, django_db_blocker):  # noqa
    """Load to database a set of users, create for export
    emails command testing"""
    with django_db_blocker.unblock():  # noqa
        call_command('loaddata', 'group.json')
        call_command('loaddata', 'user.json')


@pytest.mark.django_db()
def test_do_export_emails_stdout_start(capsys):
    """Testing export_emails command without args.stdout starts."""
    export_emails = Command()
    export_emails.run_from_argv(
        ['manage.py', 'export_emails']
    )

    out, err = capsys.readouterr()
    assert out.startswith('"Mijaíl Bulgakóv')


@pytest.mark.django_db()
def test_do_export_emails_stdout_end(capsys):
    """Testing export_emails command without args.stdout end."""
    export_emails = Command()
    export_emails.run_from_argv(['manage.py', 'export_emails'])

    out, err = capsys.readouterr()
    assert '"Frédéric Mistral" <frederic_mistral@gmail.com>;\n\n' in out


@pytest.mark.django_db()
def test_do_export_emails_format_email(capsys):
    """Testing python manage.py export_emails -f emails"""
    export_emails = Command()
    export_emails.run_from_argv(['manage.py', 'export_emails', '--format=emails'])

    out, err = capsys.readouterr()
    assert 'frederic_mistral@gmail.com' in out


@pytest.mark.django_db()
def test_do_export_emails_address(capsys):
    """Testing python manage export_emails -f address"""
    export_emails = Command()
    export_emails.run_from_argv(['manage.py', 'export_emails', '--format=address'])

    out, err = capsys.readouterr()
    assert '"Frédéric Mistral"' in out


@pytest.mark.django_db()
def test_do_export_emails_format_google(capsys):
    """Testing python manage export_emails -f google"""
    export_emails = Command()
    export_emails.run_from_argv(['manage.py', 'export_emails', '--format=google'])

    out, err = capsys.readouterr()
    assert out.startswith('Name,Email')


@pytest.mark.django_db()
def test_do_export_emails_format_outlook(capsys):
    """Testing python manage.py export_emails -f outlook"""
    export_emails = Command()
    export_emails.run_from_argv(['manage.py', 'export_emails', '--format=outlook'])

    out, err = capsys.readouterr()
    assert out.startswith('Name,E-mail Address')
    assert 'frederic_mistral@gmail.com' in out


@pytest.mark.skipif("sys.version_info < (3, 0)", reason='issues with vobject library on PY2x')
@pytest.mark.django_db()
def test_do_export_emails_format_vcard_start(capsys):
    """Testing python manage.py export_emails -f vcard"""
    export_emails = Command()
    export_emails.run_from_argv(['manage.py', 'export_emails', '--format=vcard'])

    out, err = capsys.readouterr()

    assert 'N:Bulgakóv;Mijaíl;;;' in out
    assert out.startswith('BEGIN:VCARD')


@pytest.mark.django_db()
def test_full_name():
    """Test, getting full name / username"""

    fake_user = {'first_name': 'Allan', 'last_name': 'Poe', 'username': 'allan_poe'}
    name = full_name(**fake_user)
    assert name == "{u} {l}".format(u=fake_user['first_name'], l=fake_user['last_name'])

    fake_user2 = {'first_name': '', 'last_name': '', 'username': 'niccolas'}
    name2 = full_name(**fake_user2)
    assert name2 == fake_user2['username']
