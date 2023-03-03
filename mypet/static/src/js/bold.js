odoo.define('mypet.bold', function (require) {
    "use strict";
    // import packages
    var basic_fields = require('web.basic_fields');
    var registry = require('web.field_registry');

    // widget implementation
    var BoldWidget = basic_fields.FieldChar.extend({
        _renderReadonly: function () {
            this._super();
            var old_html_render = this.$el.html();
            var new_html_render = '<b style="color:red;">' + old_html_render + '</b>'
            this.$el.html(new_html_render);
        },
    });

    registry.add('bold_red', BoldWidget); // add our "bold" widget to the widget registry
});

//Khai báo gói mypet.bold bằng odoo.define. Tên gói của chúng ta sau có thể kế thừa hay mở rộng bằng cách lệnh require().
//"Import" basic_fields, nơi hiện thực widget FieldChar, ta sắp sửa thừa kế để hiệu chỉnh nó.
//Override hàm _renderReadonly() để render text in đậm màu đỏ, bạn có thể thấy thao tác code js, html (nghề của frontend developer) rất rõ ở đây.
//Cuối cùng ta phải khai báo widget này vào registry.
//Lưu ý: trong quá trình dev widget cho Odoo, để có tác dụng mình cần phải Upgrade module. Trong quá trình dev js, Minh còn thường dùng console.log() để in ấn giá trị, cũng như check xem code mới có được áp dụng chưa.