from django.contrib.admin import AdminSite


class OrderedAdminSite(AdminSite):
    """Admin paneldagi app va model tartibini qo'lda boshqaradi."""

    app_order = {
        "users": 10,
        "account": 20,
        "salary": 30,
        "sales": 40,
        "expenses": 50,
    }

    model_order = {
        "users": {
            "User": 10,
        },
        "sales": {
            "Product": 10,
            "Buyer": 20,
            "Sale": 30,
            "SaleItem": 40,
        },
        "account": {
            "Income": 10,
            "Expense": 20,
        },
        "expenses": {
            "FoodProducts": 10,
            "RawMaterials": 20,
            "Expenses": 30,
            "FoodItem": 40,
            "RawItem": 50,
        },
        "salary": {
            "Employee": 10,
            "Salary": 20,
            "SalaryItem": 30,
        },
    }

    # Non-superuserlar uchun admin ro'yxatida ko'rinmaydigan modellar.
    hidden_for_non_superusers = {
        # "sales": {"SaleItem"},
        # "expenses": {"FoodItem", "RawItem"},
        # "salary": {"SalaryItem"},
    }

    def _is_hidden(self, request, app_label, object_name):
        return object_name in self.hidden_for_non_superusers.get(app_label, set())

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label=app_label)

        for app in app_list:
            app["models"] = [
                model
                for model in app["models"]
                if not self._is_hidden(request, app["app_label"], model["object_name"])
            ]
            order_map = self.model_order.get(app["app_label"], {})
            app["models"].sort(
                key=lambda model: (
                    order_map.get(model["object_name"], 999),
                    model["name"].lower(),
                )
            )

        app_list = [app for app in app_list if app["models"]]
        app_list.sort(
            key=lambda app: (
                self.app_order.get(app["app_label"], 999),
                app["name"].lower(),
            )
        )
        return app_list
