import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse

from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.dashboard.views import base
from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.returns.models import Return
from wildlifelicensing.apps.returns.utils import is_return_overdue, is_return_due_soon


def _get_user_applications(user):
    return Application.objects.filter(applicant_profile__user=user)


class TableCustomerView(LoginRequiredMixin, base.TableBaseView):
    """
    This view includes the table definitions and filters for applications, licences and returns for the customers
    as it is displayed on the same page.
    """
    template_name = 'wl/dash_tables_customer.html'

    def _build_data(self):
        data = super(TableCustomerView, self)._build_data()
        # Applications
        data['applications']['columnDefinitions'] = [
            {
                'title': 'Lodge Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'Profile'
            },
            {
                'title': 'Status'
            },
            {
                'title': 'Lodged on'
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        # no filters
        if 'filters' in data['applications']:
            del data['applications']['filters']
        # global table options
        data['applications']['tableOptions'] = {
            'order': [[0, 'desc']]
        }

        data['applications']['ajax']['url'] = reverse('dashboard:data_application_customer')

        # Licences
        data['licences']['columnDefinitions'] = [
            {
                'title': 'Licence Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'Issue Date'
            },
            {
                'title': 'Start Date'
            },
            {
                'title': 'Expiry Date'
            },
            {
                'title': 'Licence',
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['licences']['ajax']['url'] = reverse('dashboard:data_licences_customer')
        # no filters
        if 'filters' in data['licences']:
            del data['licences']['filters']
        # global table options
        data['licences']['tableOptions'] = {
            'order': [[4, 'desc']]
        }

        # Returns
        data['returns']['columnDefinitions'] = [
            {
                'title': 'Lodge Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'Lodged On'
            },
            {
                'title': 'Due On'
            },
            {
                'title': 'Status'
            },
            {
                'title': 'Licence',
                'orderable': False
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['returns']['ajax']['url'] = reverse('dashboard:data_returns_customer')
        # no filters
        if 'filters' in data['returns']:
            del data['returns']['filters']
        # global table options
        data['returns']['tableOptions'] = {
            'order': [[3, 'desc']]
        }

        return data


class DataTableApplicationCustomerView(base.DataTableApplicationBaseView):
    columns = ['lodgement_number', 'licence_type.code', 'applicant_profile', 'customer_status', 'lodgement_date',
               'action']
    order_columns = ['lodgement_number', 'licence_type.code', 'applicant_profile', 'customer_status', 'lodgement_date',
                     '']

    columns_helpers = dict(base.DataTableApplicationBaseView.columns_helpers.items(), **{
        'lodgement_number': {
            'render': lambda self, instance: base.render_lodgement_number(instance)
        },
        'action': {
            'render': lambda self, instance: DataTableApplicationCustomerView.render_action_column(instance),
        },
        'lodgement_date': {
            'render': lambda self, instance: base.render_date(instance.lodgement_date)
        },
    })

    @staticmethod
    def render_action_column(obj):
        status = obj.customer_status
        if status == 'draft':
            return '<a href="{0}">{1}</a>'.format(
                reverse('applications:edit_application', args=[obj.licence_type.code, obj.pk]),
                'Continue application'
            )
        elif status == 'amendment_required' or status == 'id_and_amendment_required':
            return '<a href="{0}">{1}</a>'.format(
                reverse('applications:edit_application', args=[obj.licence_type.code, obj.pk]),
                'Amend application'
            )
        elif status == 'id_required' and obj.id_check_status == 'awaiting_update':
            return '<a href="{0}">{1}</a>'.format(
                reverse('main:identification'),
                'Update ID')
        else:
            return '<a href="{0}"">{1}</a>'.format(
                reverse('applications:view_application', args=[obj.pk]),
                'View application (read-only)'
            )

    def get_initial_queryset(self):
        return _get_user_applications(self.request.user)


class DataTableLicencesCustomerView(base.DataTableBaseView):
    model = WildlifeLicence
    columns = ['licence_number', 'licence_type.code', 'issue_date', 'start_date', 'end_date', 'licence', 'action']
    order_columns = ['licence_number', 'licence_type.code', 'issue_date', 'start_date', 'end_date', '', '']

    columns_helpers = {
        'licence_number': {
            'render': lambda self, instance: base.render_licence_number(instance)
        },
        'issue_date': {
            'render': lambda self, instance: base.render_date(instance.issue_date)
        },
        'start_date': {
            'render': lambda self, instance: base.render_date(instance.start_date)
        },
        'end_date': {
            'render': lambda self, instance: base.render_date(instance.end_date)
        },
        'licence': {
            'render': lambda self, instance: base.render_licence_document(instance)
        },
        'action': {
            'render': lambda self, instance: self._render_action(instance)
        }
    }

    @staticmethod
    def _render_action(instance):
        if not instance.is_renewable:
            return 'Not renewable'
        else:
            try:
                application = Application.objects.get(licence=instance)
                if Application.objects.filter(previous_application=application).exists():
                    return 'Renewed'
            except Application.DoesNotExist:
                pass
            expiry_days = (instance.end_date - datetime.date.today()).days
            if expiry_days <= 30:
                url = reverse('applications:renew_licence', args=(instance.pk,))
                return '<a href="{0}">Renew</a>'.format(url)
            else:
                return 'Renewable in ' + str(expiry_days - 30) + ' days'

    def get_initial_queryset(self):
        return WildlifeLicence.objects.filter(holder=self.request.user)


class DataTableReturnsCustomerView(base.DataTableBaseView):
    model = Return
    columns = ['lodgement_number', 'licence.licence_type.code', 'lodgement_date', 'due_date', 'status', 'licence',
               'action']
    order_columns = ['lodgement_number', 'licence.licence_type.code', 'lodgement_date', 'due_date', 'status', '', '']
    columns_helpers = {
        'lodgement_number': {
            'render': lambda self, instance: instance.lodgement_number
        },
        'lodgement_date': {
            'render': lambda self, instance: base.render_date(instance.lodgement_date)
        },
        'due_date': {
            'render': lambda self, instance: base.render_date(instance.due_date)
        },
        'licence': {
            'render': lambda self, instance: base.render_licence_number(instance.licence),
            'search': lambda self, search: base.build_field_query([
                'licence__licence_number', 'licence__licence_sequence'],
                search),
        },
        'action': {
            'render': lambda self, instance: self._render_action(instance)
        },
        'status': {
            'render': lambda self, instance: self._render_status(instance)
        }
    }

    @staticmethod
    def _render_action(instance):
        if instance.status == 'current':
            url = reverse('returns:enter_return', args=(instance.pk,))
            return '<a href="{0}">Enter Return</a>'.format(url)
        elif instance.status == 'draft':
            url = reverse('returns:enter_return', args=(instance.pk,))
            return '<a href="{0}">Edit Return</a>'.format(url)
        else:
            url = reverse('returns:view_return', args=(instance.pk,))
            return '<a href="{0}">View Return (read-only)</a>'.format(url)

    @staticmethod
    def _render_status(instance):
        status = instance.status
        if status == 'current':
            if is_return_overdue(instance):
                return '<span class="label label-danger">Overdue</span>'
            elif is_return_due_soon(instance):
                return '<span class="label label-warning">Due soon</span>'
            else:
                return 'Current'
        else:
            return dict(Return.STATUS_CHOICES)[status]

    def get_initial_queryset(self):
        return Return.objects.filter(licence__holder=self.request.user).exclude(status='future')
