

(function($, CKEDITOR) {

    var API = CKEDITOR.plugins.silvaexternalsource;
    var LIST_SOURCES_REST_URL = '++rest++Products.SilvaExternalSources.source.availables';
    var VALIDATE_REST_URL = '++rest++Products.SilvaExternalSources.source.validate';
    var PARAMETERS_REST_URL = '++rest++Products.SilvaExternalSources.source.parameters';

    var rest_url = function(url) {
        return $('#content-url').attr('href') + '/' + url;
    };

    var load_parameters = function($container, parameters) {
        // Fetch the parameters form.
        $container.html('<p>Fetching source parameters from server ...</p>');
        $.ajax({
            url: rest_url(PARAMETERS_REST_URL),
            data: parameters,
            dataType: 'html',
            type: 'POST',
            success: function(html) {
                $container.html(html);
                var $form = $container.children('form');
                $form.trigger('load-smiform', {form: $form, container: $form});
            },
            error: function() {
                $container.html('');
                alert('An unexpected error happened on the server while ' +
                      'retrieving Code source parameters. ' +
                      'The Code Source might be buggy.');
            }
        });
    };

    var create_parameters_fields = function (parameters_identifier) {
        return [{
            type: 'html',
            id: 'source_options',
            html: '<div class="' + parameters_identifier + '"></div>',
            setup: function(data) {
                var $container = $('.' + parameters_identifier);
                var parameters = [];

                this._.source = {};
                if (data.instance) {
                    var editor = this.getDialog().getParentEditor();

                    this._.source['source_instance'] = data.instance;
                    this._.source['source_text'] = editor.name;
                } else if (data.name) {
                    this._.source['source_name'] = data.name;
                };
                if (data.parameters) {
                    var extra = [{'name': 'source_inline', 'value':1}];
                    parameters = data.parameters;

                    for (var key in this._.source) {
                        extra.push({'name': key, 'value': this._.source[key]});
                    };
                    parameters = parameters + '&' + $.param(extra);
                    load_parameters($container, parameters);
                } else if (data.instance) {

                    for (var key in this._.source) {
                        parameters.push({'name': key, 'value': this._.source[key]});
                    };
                    load_parameters($container, $.param(this._.source));
                };
            },
            validate: function() {
                var $container = $('.' + parameters_identifier);
                var parameters = $container.find('form').serializeArray();
                var succeeded = true;

                // Add keys to identify the source.
                for (var key in this._.source) {
                    parameters.push({'name': key, 'value':this._.source[key]});
                };
                parameters.push({'name': 'source_inline', 'value': 1});

                $.ajax({
                    url: rest_url(VALIDATE_REST_URL),
                    data: parameters,
                    dataType: 'json',
                    type: 'POST',
                    async: false,
                    success: function(data) {
                        if (!data['success']) {
                            // First remove all previous errors.
                            $container.find('.external_source_error').remove();
                            // Create new error reporting.
                            for (var i=0; i < data['messages'].length; i++) {
                                var error = data['messages'][i];
                                var label = $container.find('label[for=' + error.identifier + ']');

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
                var $container = $('.' + parameters_identifier);

                data.parameters = $.param($container.find('form').serializeArray());
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
                this.setValue(data.align || 'default');
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
                        var source_options = dialog.getContentElement(
                            'external_source_new_page', 'source_options');
                        var $container = $('.external_source_add');

                        if (event.data.value) {
                            if (source_options._.source) {
                                source_options._.source.source_name = event.data.value;
                            };
                            load_parameters($container, {'source_name': event.data.value});
                            align_input.show();
                        } else {
                            if (source_options._.source &&
                                source_options._.source.source_name) {
                                delete source_options._.source.source_name;
                            };
                            $container.html('');
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
                    },
                    commit: function(data) {
                        data.name = this.getValue();
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

                var container = new CKEDITOR.dom.element('span');
                container.setAttributes({'class': 'inline-container ' + data.align});
                var source = new CKEDITOR.dom.element('div');
                var attributes = {};

                attributes['class'] = 'external-source ' + data.align;
                attributes['contenteditable'] = false;
                attributes['data-silva-name'] = data.name;
                attributes['data-silva-settings'] = data.parameters;
                source.setAttributes(attributes);
                container.append(source);
                ranges[0].insertNode(container);

                API.loadPreview($(source.$), editor);
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
                data.name = source.getAttribute('data-silva-name');
                data.instance = source.getAttribute('data-silva-instance');
                if (source.hasAttribute('data-silva-settings')) {
                    data.parameters = source.getAttribute('data-silva-settings');
                };

                this.setupContent(data);
            },
            onOk: function() {
                var data = {};
                var editor = this.getParentEditor();
                var source = API.getSelectedSource(editor);

                this.commitContent(data);

                source.setAttribute('class', 'external-source ' + data.align);
                source.setAttribute('data-silva-settings', data.parameters);
                source.getParent().setAttribute('class', 'inline-container ' + data.align);

                API.loadPreview($(source.$), editor);
            }
        };
    });


})(jQuery, CKEDITOR);
