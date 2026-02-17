(function($) {
    $(document).ready(function() {
        function calculateTotal() {
            // For single form (FoodItem or RawItem add)
            var quantity = parseFloat($('input[name="quantity"]').val()) || 0;
            var price = parseFloat($('input[name="price"]').val()) || 0;
            var total = quantity * price;
            var formattedTotal = total.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            $('.field-total_item_price .readonly').text(formattedTotal);
            $('#id_total_item_price').closest('.form-row').find('.readonly').text(formattedTotal);

            var foodTotal = 0;
            var rawTotal = 0;

            // Calculate for each inline group
            $('.inline-group').each(function(index, group) {
                var groupTotal = 0;
                $(group).find('tr').each(function() {
                    var row = this;
                    var qty = parseFloat($(row).find('input[name*="quantity"]').val()) || 0;
                    var prc = parseFloat($(row).find('input[name*="price"]').val()) || 0;
                    var rowTotal = qty * prc;
                    groupTotal += rowTotal;
                    var formattedRowTotal = rowTotal.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    });
                    $(row).find('.total-item-price-display').text(formattedRowTotal);
                    $(row).find('td.field-total_item_price_display').text(formattedRowTotal);
                });

                if (index === 0) {
                    foodTotal = groupTotal;
                } else if (index === 1) {
                    rawTotal = groupTotal;
                }
            });

            var overallTotal = foodTotal + rawTotal;

            // Update food total
            var formattedFoodTotal = foodTotal.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            $('.field-food_items_total .readonly').text(formattedFoodTotal);

            // Update raw total
            var formattedRawTotal = rawTotal.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            $('.field-raw_items_total .readonly').text(formattedRawTotal);

            // Update overall total cost
            var formattedOverallTotal = overallTotal.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            $('.field-total_cost .readonly').text(formattedOverallTotal);
        }

        // Setup event listeners
        $(document).on('input change', 'input[name*="quantity"], input[name*="price"]', function() {
            calculateTotal();
        });

        // Initial calculation
        calculateTotal();

        // Handle inline additions
        $('.add-row a').click(function() {
            setTimeout(calculateTotal, 100);
        });

        $(document).on('formset:added', function() {
            setTimeout(calculateTotal, 100);
        });
    });
})(django.jQuery || jQuery);
