from django.contrib import admin

# App lar tartibi
APP_ORDER = ['accounts', 'employees', 'finance', 'analytics']
MODEL_ORDERS = {
    'accounts': ['User'],
    'employees': ['Employee', 'Balance', 'MonthBalanceStatistics', 'YearlyBalanceStatistics'],
    'finance': ['IncomeExpense', 'IncomeExpenseStatistics'],
    'analytics': ['FinancialPerformanceIndicator']
}

# Original methodni saqlab qolamiz
original_get_app_list = admin.AdminSite.get_app_list

def custom_get_app_list(self, request):
    app_list = original_get_app_list(self, request)

    # App larni tartiblash
    app_list.sort(key=lambda app: APP_ORDER.index(app['app_label'])
                  if app['app_label'] in APP_ORDER
                  else 999)

    # Har bir app ichidagi modellarni tartiblash
    for app in app_list:
        app_label = app['app_label']
        if app_label in MODEL_ORDERS and MODEL_ORDERS[app_label]:
            model_order = MODEL_ORDERS[app_label]
            app['models'].sort(
                key=lambda model: model_order.index(model['object_name'])
                if model['object_name'] in model_order
                else 999
            )

    return app_list

# Override qilamiz
admin.AdminSite.get_app_list = custom_get_app_list
