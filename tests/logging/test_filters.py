# -*- coding: utf-8 -*-
import time

from django.test import TestCase
from django.test.utils import override_settings

from django_extensions.logging.filters import RateLimiterFilter

try:
    from unittest.mock import Mock, call, patch
except ImportError:
    from mock import Mock, call, patch

TEST_SUBJECT = 'test_subect'


class RateLimiterFilterTests(TestCase):
    """Tests for RateLimiterFilter."""

    def setUp(self):  # noqa
        self.rate_limiter_filter = RateLimiterFilter()
        self.record = Mock(msg=TEST_SUBJECT)
        self.record.getMessage.return_value = TEST_SUBJECT.encode()
        self.time_patch = patch.object(time, 'time', return_value='test_time')
        self.time_patch.start()

    def tearDown(self):  # noqa
        self.time_patch.stop()

    @override_settings(RATE_LIMITER_FILTER_PREFIX='test_prefix')
    @patch('django.core.cache.cache')
    def test_should_incr_cache_with_custom_prefix_and_return_False(self, m_cache):  # noqa
        m_cache.get_many.return_value = {
            'test_prefix:114392702498ad1d75c1829b9519b8c7': 10,
            'test_prefix:114392702498ad1d75c1829b9519b8c7:count': 1
        }

        result = self.rate_limiter_filter.filter(self.record)

        self.assertIs(m_cache.set.called, False)
        m_cache.incr.assert_called_once_with(
            'test_prefix:114392702498ad1d75c1829b9519b8c7:count')
        self.assertIs(result, False)

    @override_settings(RATE_LIMITER_FILTER_RATE=1)
    @patch('django.core.cache.cache')
    def test_should_set_cache_key_with_custom_rate_and_return_True(self, m_cache):  # noqa
        m_cache.get_many.return_value = {}
        expected_calls = [
            call('ratelimiterfilter:114392702498ad1d75c1829b9519b8c7:count', 1, 61),  # noqa
            call('ratelimiterfilter:114392702498ad1d75c1829b9519b8c7', 'test_time', 1)  # noqa
        ]

        result = self.rate_limiter_filter.filter(self.record)

        self.assertEqual(self.record.msg, '[1x] test_subect')
        m_cache.set.assert_has_calls(expected_calls, any_order=False)
        self.assertIs(result, True)

    @patch('django.core.cache.cache')
    def test_should_modify_record_msg_and_return_True(self, m_cache):
        """Default rate and prefix values."""
        m_cache.get_many.return_value = {
            'ratelimiterfilter:114392702498ad1d75c1829b9519b8c7:count': 999
        }

        result = self.rate_limiter_filter.filter(self.record)

        self.assertEqual(self.record.msg, '[999x] test_subect')
        m_cache.set.assert_called_once_with(
            'ratelimiterfilter:114392702498ad1d75c1829b9519b8c7', 'test_time', 10)  # noqa
        self.assertIs(result, True)
