function bsmodals_error(msg, style="btn-primary") {
    // displays the error modal box with the given message
    var modal = $('#bsmodals-error');
    modal.find('#bsmodals-error-body').html(msg);
    modal.find('#bsmodals-error-close').attr('class', 'btn ' + style);
    modal.modal();
}


function bsmodals_alert(title, msg, style="btn-primary") {
    // displays the alert modal box with the given title and message
    var modal = $('#bsmodals-alert');
    modal.find('#bsmodals-alert-title').html(title);
    modal.find('#bsmodals-alert-body').html(msg);
    modal.find('#bsmodals-alert-close').attr('class', 'btn ' + style);

    modal.modal();
}


function bsmodals_confirm(title, msg, callback, yes_text="Yes",
        yes_style="btn-primary", no_text="No", no_style="btn-secondary") {
    // displays the confirm modal box with the given title and message
    var modal = $('#bsmodals-confirm');
    modal.find('#bsmodals-confirm-title').html(title);
    modal.find('#bsmodals-confirm-body').html(msg);
    modal.find('#bsmodals-confirm-yes').attr('class', 'btn ' + yes_style);
    modal.find('#bsmodals-confirm-yes').html(yes_text);
    modal.find('#bsmodals-confirm-no').attr('class', 'btn ' + no_style);
    modal.find('#bsmodals-confirm-no').html(no_text);

    // register call backs on Yes/No buttons
    var click_id = 'click.bsmodals-confirm';
    var button = modal.find('#bsmodals-confirm-yes')
    button.off(click_id).on(click_id, ()=>{
        callback(true);
        modal.modal('hide');
    });

    button = modal.find('#bsmodals-confirm-no')
    button.off(click_id).on(click_id, ()=>{
        callback(false);
        modal.modal('hide');
    });

    // show dialog
    modal.modal();
}


function bsmodals_entry(title, msg, callback, submit_text="Submit",
        submit_style="btn-primary", cancel_text="Cancel", 
        cancel_style="btn-secondary") {
    // displays the entry modal box with the given title and message
    var modal = $('#bsmodals-entry');
    modal.find('#bsmodals-entry-title').html(title);
    modal.find('#bsmodals-entry-body').html(msg);
    modal.find('#bsmodals-entry-submit').attr('class', 'btn ' + submit_style);
    modal.find('#bsmodals-entry-submit').html(submit_text);
    modal.find('#bsmodals-entry-cancel').attr('class', 'btn ' + cancel_style);
    modal.find('#bsmodals-entry-cancel').html(cancel_text);

    // register call backs on Submit buttons
    var click_id = 'click.bsmodals-entry';
    var button = modal.find('#bsmodals-entry-submit')
    button.off(click_id).on(click_id, ()=>{
        modal.modal('hide');
        var value = $('#bsmodals-entry-field').val();
        callback(value);
    });

    // show dialog
    modal.modal();
}

// -------------------------------------------------------------------------
// Form Dialogs

class FormDialog {
    // Base class for form dialog objects, assumes there is a jQuery object
    // named "modal" pointing to the form DOM
    set_errors(errors) {
        var _this = this;
        $.each(errors, function(key, value) {
            _this.modal.find('[name="' + key + '"]').each(function(){
                // have to do this multiple times because of
                // radio buttons
                $(this).addClass('is-invalid');
                $(this).siblings('.invalid-feedback').text(value[0]);
            });
        });
    }

    set_data(data) {
        var _this = this;
        $.each(data, function(key, value) {
            if( key[0] == '#' ) {
                _this.modal.find(key).each(function() {
                    if($(this).is('input') || $(this).is('select')
                            || $(this).is('textarea')) {
                        $(this).val(value);
                    }
                    else {
                        $(this).html(value);
                    }
                });
            }
            else {
                _this.modal.find('[name="' + key + '"]').each(function(){
                    $(this).val(value);
                });
            }

        });
    }

    clear_errors() {
        this.modal.find('.is-invalid').each(function() {
            $(this).removeClass('is-invalid');
        });
    }

    hide() {
        this.modal.modal('hide');
    }

    get_data() {
        var _this = this;
        var data = {}
        var name, type;
        _this.modal.find('input').not(':button, :submit, :reset')
                .each(function() {
            name = $(this).attr('name');
            type = $(this).attr('type');

            if( type == 'radio' && $(this).prop('checked') ) {
                data[name] = $(this).val();
            }
            else if( type == 'checkbox' ) {
                data[name] = $(this).prop('checked');
            }
            else {
                data[name] = $(this).val();
            }
        });

        _this.modal.find('select').each(function() {
            name = $(this).attr('name');
            data[name] = $(this).val();
        });

        _this.modal.find('textarea').each(function() {
            name = $(this).attr('name');
            data[name] = $(this).val();
        });

        return data;
    }
}


class FormModal extends FormDialog {
    constructor(dialog_id) {
        super();
        this.dialog_id = dialog_id;

        this.callback = undefined;
        this.modal = $('#' + dialog_id);
    }

    show(data) {
        this.set_data(data);
        this.modal.modal();
    }
}


class AJAXModal extends FormDialog {
    constructor(dialog_id) {
        super();
        this.dialog_id = dialog_id;

        this.url = undefined;
        this.callback = undefined;
        this.modal = $('#' + dialog_id);
    }

    show(url, data, callback=undefined, clear_on_success=true) {
        var _this = this;
        this.set_data(data);
        var form = $('#' + this.dialog_id).find("form");

        var click_id = 'click.' + this.dialog_id;
        var button = this.modal.find('#' + this.dialog_id + '-submit')
        button.off(click_id).on(click_id, (e)=>{
            form.submit();
        });

        form.submit(function(e) {
            e.preventDefault();
            var post_data  = _this.get_data();

            $.post(url, post_data, (response)=>{
                _this.modal.find('.is-invalid').each(function() {
                    $(this).removeClass('is-invalid');
                });

                if( response['success'] ) {
                    _this.modal.modal('hide');

                    if( clear_on_success ) {
                        _this.modal.find('form')[0].reset();
                    }
                }
                else {
                    _this.set_errors(response['errors']);
                }

                if( callback != undefined ) {
                    callback(response);
                }
            }, 'json')
            .fail(function() { 
                console.log("JSON call posting form data failed");
            });
        });

        this.modal.modal();
    }
}
