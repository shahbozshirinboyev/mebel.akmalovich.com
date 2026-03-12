class TopDropdownFiltersMixin:
	"""Render list_filter as top dropdowns with automatic apply on change."""

	change_list_template = "admin/custom/top_filters_change_list.html"
	top_filter_context_name = "top_filter_specs"

	def get_list_filter(self, request):
		"""
		Allow a single string value in list_filter for convenience.
		Django expects a sequence; we coerce string -> one-item tuple.
		"""
		list_filter = super().get_list_filter(request)
		if isinstance(list_filter, str):
			return (list_filter,)
		return list_filter

	def changelist_view(self, request, extra_context=None):
		response = super().changelist_view(request, extra_context=extra_context)
		if not hasattr(response, "context_data") or not response.context_data:
			return response

		cl = response.context_data.get("cl")
		if not cl:
			return response

		filter_specs = getattr(cl, "filter_specs", [])
		if not filter_specs:
			return response

		top_filter_specs = []
		for spec in filter_specs:
			choices = []
			for choice in spec.choices(cl):
				query_string = choice.get("query_string", "")
				choices.append(
					{
						"display": choice.get("display", ""),
						"selected": bool(choice.get("selected", False)),
						"url": f"{request.path}{query_string}" if query_string else request.get_full_path(),
					}
				)

			top_filter_specs.append(
				{
					"title": str(spec.title),
					"choices": choices,
				}
			)

		response.context_data[self.top_filter_context_name] = top_filter_specs
		return response
