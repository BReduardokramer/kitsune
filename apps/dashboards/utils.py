from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict

import jingo

from dashboards import ACTIONS_PER_PAGE
from sumo_locales import LOCALES
from sumo.utils import paginate
from wiki.events import (ApproveRevisionInLocaleEvent,
                         ReviewableRevisionInLocaleEvent)


def model_actions(model_class, request):
    """Returns paginated actions for the given model."""
    ct = ContentType.objects.get_for_model(model_class)
    actions = request.user.action_inbox.filter(content_type=ct)
    return paginate(request, actions, per_page=ACTIONS_PER_PAGE)


def render_readouts(request, readouts, template, locale=None, extra_data=None):
    """Render a readouts, possibly with overview page.

    Use the given template, pass the template the given readouts, limit the
    considered data to the given locale, and pass along anything in the
    `extra_data` dict to the template in addition to the standard data.

    """
    current_locale = locale or request.locale
    data = {'readouts': SortedDict((slug, class_(request, locale=locale))
                         for slug, class_ in readouts.iteritems()),
            'default_locale': settings.WIKI_DEFAULT_LANGUAGE,
            'default_locale_name':
                LOCALES[settings.WIKI_DEFAULT_LANGUAGE].native,
            'current_locale': current_locale,
            'current_locale_name': LOCALES[current_locale].native,
            'is_watching_approved': ApproveRevisionInLocaleEvent.is_notifying(
                request.user, locale=request.locale),
            'is_watching_locale': ReviewableRevisionInLocaleEvent.is_notifying(
                request.user, locale=request.locale),
            'is_watching_approved_default':
                ApproveRevisionInLocaleEvent.is_notifying(
                    request.user, locale=settings.WIKI_DEFAULT_LANGUAGE)}
    if extra_data:
        data.update(extra_data)
    return jingo.render(request, 'dashboards/' + template, data)