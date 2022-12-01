class RestModal extends FormDialog {
    constructor(dialog_id) {
        super();
        this.dialog_id = dialog_id;

        this.mode = undefined;
        this.url = undefined;
        this.callback = undefined;
        this.modal = $('#' + dialog_id);

        var _this = this;

        var form = $('#' + this.dialog_id).find("form");
        var click_id = 'click.' + this.dialog_id;
        var button = this.modal.find('#' + this.dialog_id + '-submit')
        button.off(click_id).on(click_id, (e)=>{
            form.submit();
        });

        form.submit(function(e) {
            e.preventDefault();
            var data = _this.get_data();

            // reset the error states on the form
            _this.modal.find('.is-invalid').each(function() {
                $(this).removeClass('is-invalid');
            });

            var ajax_type = 'POST';
            if(_this.mode == 'update') {
                ajax_type = 'PUT';
            }
            else if(_this.mode == 'patch') {
                ajax_type = 'PATCH';
            }

            $.ajax({
                url:_this.url,
                type:ajax_type,
                data:data,
                dataType:"json",
                success: function(response) {
                    _this.modal.modal('hide');
                    _this.callback(response);

                    _this.modal.find('form')[0].reset();
                },
                error: function(response) {
                    _this.set_errors(response.responseJSON);
                },
            });
        });
    }

    _do_modal(url, data, callback) {
        this.url = url;
        this.callback = callback;
        this.set_data(data);
        this.modal.modal();
    }

    show_create(url, data, callback=undefined) {
        this.mode = 'create';
        this._do_modal(url, data, callback);
    }

    show_update(url, data, callback=undefined) {
        this.mode = 'update';
        this._do_modal(url, data, callback);
    }

    show_patch(url, data, callback=undefined) {
        this.mode = 'patch';
        this._do_modal(url, data, callback);
    }
}
