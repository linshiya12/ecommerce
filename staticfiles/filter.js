$(document).ready(function(){
    $(".ajaxLoader").hide();

    // Use 'change' event to detect checkbox state changes
    $(".filter-checkbox").on('change', function() {
        var _filterObj = {};

        // Iterate over all filter checkboxes
        $(".filter-checkbox").each(function(index, ele) {
            var _filterVal = $(ele).val();
            var _filterKey = $(ele).data('filter');
            
            // Get checked values for each filter key
            if (!_filterObj[_filterKey]) {
                _filterObj[_filterKey] = [];
            }

            // If the checkbox is checked, add it to the filter object
            if ($(ele).is(':checked')) {
                _filterObj[_filterKey].push(_filterVal);
            }
        });

        // Log the filter object to check the selected filters
        console.log(_filterObj);

        $.ajax({
            url:'/filter-data',
            data:_filterObj,
            datatype:'json',
            beforeSend:function(){
                $(".ajaxLoader").show();
            },
            success:function(res){
                console.log(res);
                $("#filteredProducts").html(res);
                $(".ajaxLoader").hide();
                
            }
        })
    });
});
