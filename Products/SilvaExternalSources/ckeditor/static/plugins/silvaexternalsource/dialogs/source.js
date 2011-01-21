

(function($, CKEDITOR) {

    var API = CKEDITOR.plugins.silvaexternalsource;
    var LIST_SOURCES_REST_URL = '++rest++Products.SilvaExternalSources.source.availables';
    var VALIDATE_REST_URL = '++rest++Products.SilvaExternalSources.source.validate';
    var PARAMETERS_REST_URL = '++rest++Products.SilvaExternalSources.source.parameters';

    var rest_url = function(url) {
        return $('#content-url').attr('href') + '/' + url;
    };

    var load_parameters = function(container, parameters) {
        // Fetch the parameters form.
        $.ajax({
            url: rest_url(PARAMETERS_REST_URL),
            data: parameters,
            dataType: 'html',
            type: 'POST',
            success: function(html) {
                container.html(html);
            },
            error: function() {
                container.html('');
                alert('An unexpected error happened on the server while ' +
                      'retrieving Code source parameters. ' +
                      'The Code Source might be buggy.');
            }
        });
    };

    var create_parameters_fields = function (identifier) {
        return [{
            type: 'html',
            id: 'source_options',
            html: '<div class="' + identifier + '"></div>',
            setup: function(data) {
                if (data.parameters) {
                    var container = $('.' + identifier);

                    load_parameters(container, data.parameters);
                };
            },
            validate: function() {
                var container = $('.' + identifier);
                var parameters = container.find('form').serializeArray();
                var succeeded = true;

                $.ajax({
                    url: rest_url(VALIDATE_REST_URL),
                    data: parameters,
                    dataType: 'json',
                    type: 'POST',
                    async: false,
                    success: function(data) {
                        if (!data['success']) {
                            // First remove all previous errors.
                            container.find('.external_source_error').remove();
                            // Create new error reporting.
                            for (var i=0; i < data['messages'].length; i++) {
                                var error = data['messages'][i];
                                var label = container.find('label[for=' + error.identifier + ']');

                                $('<span class="external_source_error">' +
                                  error.message + '</span>').insertAfter(label);
                            };
                            alert('Some parameters did not validate properly. '+
                                  'Please correct the errors.');
                            succeeded = false;
                        }
                    },
                    error: function() {
                        alert('An unexpected error happened on the server ' +
                              'while validating the code source. The code source ' +
                              'might be buggy.');
                        succeeded = false;
                    }
                });
                return succeeded;
            },
            commit: function(data) {
                var container = $('.' + identifier);

                data.parameters = $.param(container.find('form').serializeArray());
            }
        }, {
            type: 'select',
            id: 'source_align',
            label: 'Source alignement',
            required: true,
            items: [
                ['default', 'default'],
                ['align left', 'source-left'],
                ['align center', 'source-center'],
                ['align right', 'source-right'],
                ['float left', 'source-float-left'],
                ['float right', 'source-float-right']
            ],
            setup: function(data) {
                this.setValue(data.align);
            },
            commit: function(data) {
                data.align = this.getValue();
            }
        }];
    };

    CKEDITOR.dialog.add('silvaexternalsourcenew', function(editor) {
        return {
            title: 'Add a new External Source',
            minWidth: 600,
            minHeight: 400,
            contents: [{
                id: 'external_source_new_page',
                elements: [{
                    type: 'select',
                    id: 'source_type',
                    label: 'Source to add',
                    required: true,
                    items: [],
                    onChange: function(event) {
                        var dialog = this.getDialog();
                        var align_input = dialog.getContentElement(
                            'external_source_new_page', 'source_align').getElement();
                        var container = $('.external_source_add');

                        if (event.data.value) {
                            load_parameters(container, {'identifier': event.data.value});
                            align_input.show();
                        } else {
                            container.html('');
                            align_input.hide();
                        }
                    },
                    setup: function(data) {
                        // Load the list of External Source from the server on setup.
                        var self = this;

                        this.clear();
                        this.add('Select a source to add', '');
                        this.setValue('');
                        $.getJSON(
                            rest_url(LIST_SOURCES_REST_URL),
                            function(sources) {
                                for (var i=0; i < sources.length; i++) {
                                    self.add(sources[i].title, sources[i].identifier);
                                };
                            });
                    },
                    validate: function() {
                        var checker = CKEDITOR.dialog.validate.notEmpty(
                            'You need to select a External Source to add !');

                        return checker.apply(this);
                    }
                }, {
                    type: 'vbox',
                    id: 'source_parameters',
                    children: create_parameters_fields('external_source_add')
                }]
            }],
            onShow: function() {
                var data = {};

                this.setupContent(data);
            },
            onOk: function() {
                var data = {};
                var editor = this.getParentEditor();

                this.commitContent(data);

                var selection = editor.getSelection();
                var ranges = selection.getRanges(true);

                var source = new CKEDITOR.dom.element('div');
                var attributes = {};

                attributes['class'] = 'external-source ' + data.align;
                attributes['contenteditable'] = false;
                attributes['data-silva-settings'] = data.parameters;
                source.setAttributes(attributes);
                ranges[0].insertNode(source);
                selection.selectElement(source);

                API.loadPreview($(source.$));
            }
        };
    });

    CKEDITOR.dialog.add('silvaexternalsourceedit', function(editor) {
        return {
            title: 'External Source Settings',
            minWidth: 600,
            minHeight: 400,
            contents: [{
                id: 'external_source_edit_page',
                elements: create_parameters_fields('external_source_edit')
            }],
            onShow: function() {
                var data = {};
                var editor = this.getParentEditor();
                var source = API.getSelectedSource(editor);
                var parse_alignment = /^external-source\s+([a-z-]+)\s*$/;
                var info_alignment = parse_alignment.exec(
                    source.getAttribute('class'));

                if (info_alignment != null) {
                    data.align = info_alignment[1];
                }
                data.parameters = source.getAttribute('data-silva-settings');

                this.setupContent(data);
            },
            onOk: function() {
                var data = {};
                var editor = this.getParentEditor();
                var source = API.getSelectedSource(editor);

                this.commitContent(data);

                source.setAttribute('class', 'external-source ' + data.align);
                source.setAttribute('data-silva-settings', data.parameters);

                API.loadPreview($(source.$));
            }
        };
    });


})(jQuery, CKEDITOR);

